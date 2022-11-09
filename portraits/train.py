import os
from pathlib import Path

from .clients import get_model, download_photos, release_model
from . import huggingface
from . import io
from .config import ROOT
from .io import Mkdirer
from .paths import regularizations_path, photos_path, model_path
from .store import pull_s3, push_s3, copy_to_s3
from .types import Model, FetchRegularization, GenerateRegularization
import typing as t


def make_regularizations(
    parent_model_path: str,
    model: Model,
    run: io.CommandRunner,
    mkdir: Mkdirer,
    image_generator: io.ImageGenerator,
):
    path = regularizations_path(model)
    mkdir(path)
    regularization = model.regularization

    if isinstance(regularization, FetchRegularization):
        if (path / "samples").exists():
            print("ℹ️  Regularizations already downloaded")
            return
        run(["git", "clone", regularization.source, path.as_posix()])
        run(["mv", (path / regularization.prompt).as_posix(), (path / "samples").as_posix()])
        return

    pull_s3(path.as_posix(), run=run)
    if (path / "samples" / "00199.jpg").exists():
        print(f"ℹ️  Regularizations for {model.id} already downloaded")
        return

    assert isinstance(regularization, GenerateRegularization)
    image_generator(
        [
            "--ddim_eta",
            "0.0",
            "--n_samples",
            "1",
            "--n_iter",
            str(regularization.count),
            "--scale",
            "10.0",
            "--ddim_steps",
            "50",
            "--ckpt",
            parent_model_path,
            "--prompt",
            regularization.prompt,
            "--outdir",
            path.as_posix(),
            "--skip_grid",
        ]
    )

    push_s3(path.as_posix(), run=run)
    return path / "samples"


def train_model(
    save_url: io.UrlSaver = io.save_url,
    model_dowloader=huggingface.download_parent_model,
    run: io.CommandRunner = io.run,
    train: io.Trainer = io.train,
    image_generator: io.ImageGenerator = io.image_generator,
    mkdir: io.Mkdirer = io.mkdir,
    get_last_checkpoint: io.LastCheckpointGetter = io.get_last_checkpoint,
):
    return pure_train_model(
        save_url,
        model_dowloader,
        run,
        train,
        image_generator,
        mkdir,
        get_last_checkpoint,
    )


def pure_train_model(
    save_url: io.UrlSaver,
    model_dowloader,
    run: io.CommandRunner,
    train: io.Trainer,
    image_generator: io.ImageGenerator,
    mkdir: io.Mkdirer,
    get_last_checkpoint: io.LastCheckpointGetter,
):
    model = get_model()
    if not model:
        print("No models to train")
        return
    try:
        print(f"Training model {model.name} ({model.id})")
        print("ℹ️  Downloading photos")
        download_photos(
            photos_path(model), model.subject.subject_photos, save_url=save_url
        )
        print("ℹ️  Downloading parent model")
        parent_model_path = model_dowloader(model.parent_model)
        print(f"ℹ️  Parent model downloaded to {parent_model_path}")
        print("ℹ️  Generating Regularization images")
        make_regularizations(
            parent_model_path,
            model,
            run=run,
            image_generator=image_generator,
            mkdir=mkdir,
        )
        print("ℹ️  Training model")
        do_train(parent_model_path, model, train=train)
        print("ℹ️  Model trained")
        print("ℹ️  Uploading model to file store")
        upload_model(model, run=run, get_last_checkpoint=get_last_checkpoint)
    except Exception as e:
        print(f"❌  Error while training PORTRAITS_DRY_RUNmodel {model.name} ({model.id}): {e}")
        if os.environ.get('PORTRAITS_DRY_RUN', 'false') != 'true':
            release_model(model, error=str(e))
        raise
    else:
        if os.environ.get('PORTRAITS_DRY_RUN', 'false') != 'true':
            release_model(model)
        print(f"✅  Model {model.name} ({model.id}) trained")
        run(["rm", "-rf", (ROOT / "logs").as_posix()])


def upload_model(
    model: Model, run: io.CommandRunner, get_last_checkpoint: io.LastCheckpointGetter
):
    path = model_path(model)
    checkpoint_path = get_last_checkpoint()
    target_path = path / "model.ckpt"
    run(["mv", checkpoint_path, target_path.as_posix()])
    copy_to_s3(Path(target_path).as_posix(), run=run)


def do_train(
    parent_model_path, model: Model, train: t.Callable[[t.Sequence[str]], None]
):
    train_params = [
            "--base",
            "configs/stable-diffusion/v1-finetune_unfrozen.yaml",
            "-t",
            "--actual_resume",
            parent_model_path,
            "--reg_data_root",
            (regularizations_path(model) / "samples").as_posix(),
            "-n",
            model.id,
            "--gpus",
            "0,",
            "--data_root",
            photos_path(model).as_posix(),
            "--max_training_steps",
            "2020",  # TODO: make it configurable
            "--class_word",
            model.regularization.prompt,
            "--token",
            model.subject.slug,
            "--no-test",
            "--portraits-model-id",
            model.id,
        ]
    print("ℹ️  Start traing train with params", train_params)
    train(train_params)


if __name__ == "__main__":
    train_model()