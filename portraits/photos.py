import os
import traceback
from functools import partial, singledispatch
from pathlib import Path
from time import sleep

from portraits import io
from portraits.clients import get_photos, upload_photo
from portraits.config import ROOT
from portraits.huggingface import download_parent_model
from portraits.io import CommandRunner
from portraits.paths import make_model_path
from portraits.paths import generated_photos_outdir
from portraits.store import pull_s3
from portraits.types import PhotosResponse, PhotoSource, Style, PhotoSourceAWS


def fetch_model(owner_id: str, model_id: str, run: CommandRunner) -> Path:
    path = make_model_path(owner_id, model_id)
    target = path / "model.ckpt"
    if target.exists():
        target.touch()
        print(f"ℹ️  Model {model_id} already downloaded")
        return target
    pull_s3(path.as_posix(), run=run)
    return target


@singledispatch
def fetch_source(source: PhotoSource, run: io.CommandRunner):
    raise NotImplementedError(f"Unknown source type {type(source)}")


@fetch_source.register
def _fetch_source_huggingface(source: Style, run: io.CommandRunner) -> Path:
    return Path(download_parent_model(source))


@fetch_source.register
def _fetch_source_aws(source: PhotoSourceAWS, run: io.CommandRunner) -> Path:
    pull_s3( (ROOT / source.path).as_posix(), run=run)
    return Path(ROOT / source.path / 'model.ckpt')


def pure_process_photos(run: CommandRunner, image_generator: io.ImageGenerator, mkdir: io.Mkdirer):
    photos = get_photos()
    if not photos:
        print("No photos to process")
        return

    print(f"ℹ️  Processing {len(photos.photos)} photos")
    path = fetch_source(photos.source, run)

    outdir = generated_photos_outdir()
    mkdir(outdir)
    to_generate = [', '.join(p.prompts) for p in photos.photos]
    image_generator([
            "--ddim_eta",
            "0.0",
            "--n_samples",
            "1",
            "--scale",
            "10.0",
            "--ddim_steps",
            "50",
            "--ckpt",
            path.as_posix(),
            "--outdir",
            outdir.as_posix(),
            "--skip_grid",
        ], external_prompts=to_generate, on_prompt_save=partial(on_prompt_save, prompts=photos))


def on_prompt_save(idx: int, path: str, prompts: PhotosResponse):
    the_prompt = prompts.photos[idx]
    print(f"ℹ️  Uploading {path} for {the_prompt.id}")

    upload_photo(
        photo_id=the_prompt.id,
        photo_path=Path(path),
    )


def process_photos():
    return pure_process_photos(
        run=io.run,
        image_generator=io.image_generator,
        mkdir=io.mkdir,
    )


if __name__ == "__main__":
    if os.environ.get('PORTRAITS_DRY_RUN') == 'true':
        process_photos()
    else:
        while True:
            try:
                process_photos()
            except Exception as e:
                print(f"❌  Error: {e}")
                traceback.print_exc()
            sleep(1)
