import glob
import subprocess
from pathlib import Path
import typing as t

import requests
from typing_extensions import Protocol



class UrlSaver(Protocol):
    def __call__(self, url: str, path: Path):
        ...


def save_url(url: str, path: Path):
    with open(path, "wb") as f:
        f.write(requests.get(url, stream=True).raw.read())


CommandRunner = t.Callable[[t.Sequence[str]], None]


def run(args: t.Sequence[str]):
    print(f"ℹ️  Running: {' '.join(args)}")
    subprocess.run(args, check=True)


Mkdirer = t.Callable[[Path], None]


def mkdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


Trainer = t.Callable[[t.Sequence[str]], None]

def train(args: t.Sequence[str]):
    import main
    return main.train(args)

ImageGenerator = t.Callable[[t.Sequence[str]], None]


def image_generator(args: t.Sequence[str], external_prompts=None, on_prompt_save=None):
    from scripts import stable_txt2img
    return stable_txt2img.main(args, external_prompts=external_prompts, on_prompt_save=on_prompt_save)


LastCheckpointGetter = t.Callable[[], str]


def get_last_checkpoint() -> str:
    return glob.glob("logs/*/checkpoints/last.ckpt")[0]
