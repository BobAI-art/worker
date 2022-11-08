import glob
import json
import typing as t
from dataclasses import dataclass
from pathlib import Path

import pytest
import requests_mock

from portraits.config import ROOT
from portraits.store import pull_s3
from portraits.train import pure_train_model
from portraits.types import Model, ParentModel

TESTS_PATH = Path(__file__).parent
EXAMPLES = TESTS_PATH / "examples"

ALL_EXAMPLES = glob.glob(str(EXAMPLES / "*"))


@dataclass(frozen=True)
class Example:
    model: Model
    json: str
    expected_commands: str


@pytest.fixture(params=ALL_EXAMPLES)
def example(request):
    with (Path(request.param) / "model.json").open("r") as f:
        model_json = f.read()
        model = Model.from_dict(json.loads(model_json))
    with (Path(request.param) / "expected.sh").open("r") as f:
        expected_commands = f.read().strip()
    return Example(model=model, json=model_json, expected_commands=expected_commands)


@pytest.fixture
def model(example) -> Model:
    return Model.from_dict(json.loads(example.json))


def test_get_models():
    pass
    # model = get_model("http://localhost:3000")
    # release_model(model, error="test error")


def test_pull_s3():
    commands = []

    def run(command: t.Sequence[str]):
        commands.append(command)

    pull_s3((ROOT / "foo" / "bar").as_posix(), run=run)

    assert commands == [
        [
            "aws",
            "s3",
            "sync",
            "s3://portraits-model-store/foo/bar",
            f"{ROOT}/foo/bar",
            "--no-progress",
            "--region",
            "eu-west-2",
            "--exclude",
            ".git/*",
        ]
    ]


@pytest.fixture
def fake_io():
    return FakeIO()


class FakeIO:
    def __init__(self):
        self.commands = []

    def run(self, command: t.Sequence[str]):
        self.commands.append(" ".join(command).replace(ROOT.as_posix(), "."))

    def save_url(self, url: str, path: Path):
        self.run(["wget", url, "-O", path.as_posix()])
        return path

    def model_downloaded(self, parent_model: ParentModel):
        self.run(
            [
                "python",
                "-m",
                "download_model",
                parent_model.repo_id,
                parent_model.filename,
            ]
        )
        return "/some/path"

    def train(self, args: t.Sequence[str]):
        self.run(["python", "-m", "train", *args])

    def get_last_checkpoint(self):
        return (
            Path("logs/Default/fetch-stable-diffusion-regularization/model.ckpt")
            .absolute()
            .as_posix()
        )

    def image_generator(self, args: t.Sequence[str]):
        self.run(["python", "-m", "image_generator", *args])

    def mkdir(self, path: Path):
        self.run(["mkdir", "-p", path.as_posix()])


def test_train_model(fake_io: FakeIO, example):
    with requests_mock.Mocker() as m:
        m.post("http://localhost:3000/api/model/train", json=json.loads(example.json))
        m.post(
            f"http://localhost:3000/api/model/{example.model.id}/release",
            json={"success": True},
        )

        pure_train_model(
            save_url=fake_io.save_url,
            model_dowloader=fake_io.model_downloaded,
            run=fake_io.run,
            train=fake_io.train,
            get_last_checkpoint=fake_io.get_last_checkpoint,
            image_generator=fake_io.image_generator,
            mkdir=fake_io.mkdir,
        )

    assert "\n".join(fake_io.commands) == example.expected_commands
