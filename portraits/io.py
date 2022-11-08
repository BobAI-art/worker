import glob
import subprocess
from pathlib import Path
import typing as t

import requests
from typing_extensions import Protocol

import main
from scripts import stable_txt2img


class UrlSaver(Protocol):
    def __call__(self, url: str, path: Path):
        ...


def save_url(url: str, path: Path):
    with open(path, "wb") as f:
        f.write(requests.get(url, stream=True).raw.read())


CommandRunner = t.Callable[[t.Sequence[str]], None]

run: CommandRunner = subprocess.run  # type: ignore

Mkdirer = t.Callable[[Path], None]


def mkdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


Trainer = t.Callable[[t.Sequence[str]], None]

train = main.train

ImageGenerator = t.Callable[[t.Sequence[str]], None]
image_generator = stable_txt2img.main

LastCheckpointGetter = t.Callable[[], str]


def get_last_checkpoint() -> str:
    return glob.glob("logs/*/checkpoints/last.ckpt")[0]
