from functools import partial
from pathlib import Path
from time import sleep

from portraits import io
from portraits.clients import get_prompts, delete_prompt
from portraits.clients import upload_image_from_path
from portraits.io import CommandRunner
from portraits.paths import make_model_path
from portraits.paths import prompts_outdir
from portraits.store import pull_s3
from portraits.types import PromptResponse


def fetch_model(owner_id: str, model_id: str, run: CommandRunner) -> Path:
    path = make_model_path(owner_id, model_id)
    target = path / "model.ckpt"
    if target.exists():
        target.touch()
        print(f"ℹ️  Model {model_id} already downloaded")
        return target
    pull_s3(path.as_posix(), run=run)
    return target


def pure_process_prompts(run: CommandRunner, image_generator: io.ImageGenerator, mkdir: io.Mkdirer):
    prompts = get_prompts()
    if not prompts:
        print("No prompts to process")
        return

    print(f"ℹ️  Processing {len(prompts.prompts)} prompts")

    checkpoint = fetch_model(prompts.owner_id, prompts.model_id, run)
    outdir = prompts_outdir(prompts.owner_id, prompts.model_id)
    mkdir(outdir)
    to_generate = [[p.render()] for p in prompts.prompts]
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
            checkpoint.as_posix(),

            "--outdir",
            outdir.as_posix(),
            "--skip_grid",
        ], external_prompts=to_generate, on_prompt_save=partial(on_prompt_save, prompts=prompts))


def on_prompt_save(idx: int, path: str, prompts: PromptResponse):
    the_prompt = prompts.prompts[idx]
    upload_image_from_path(
        model_id=prompts.model_id,
        category="generated-image",
        prompt=the_prompt.prompt,
        image_path=Path(path),
    )
    delete_prompt(the_prompt.id)


def process_prompts():
    return pure_process_prompts(
        run=io.run,
        image_generator=io.image_generator,
        mkdir=io.mkdir,
    )


if __name__ == "__main__":
    while True:
        try:
            process_prompts()
        except Exception as e:
            print(f"❌  Error: {e}")
        sleep(1)
