import os
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.commands.user import _login as _login_cli
import requests
import typing as t
from scripts import stable_txt2img

from svarog import Svarog

ROOT = Path(__file__).parent.absolute()

HUGGINGFACE_TOKEN=os.environ['HUGGINGFACE_TOKEN']
PORTRAITS_BASE_URL=os.environ['PORTRAITS_BASE_URL']


def make_datetime(dt, date_str, _):
    return dt.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")


svarog = Svarog(True)
svarog.register_forge(datetime, make_datetime)


@dataclass(frozen=True)
class TrainingPhoto:
    id: str
    url: str


@dataclass(frozen=True)
class ParentModel:
    repo_id: str
    filename: str


# TODO: different types of regularization images
@dataclass(frozen=True)
class Regularization:
    type: str
    prompt: str
    count: int


@dataclass(frozen=True)
class Model:
    id: str
    slug: str
    created: datetime
    owner_id: str
    training_photo: t.Sequence[TrainingPhoto]
    parent_model: ParentModel
    regularization: Regularization


def get_models():
    url = f"{PORTRAITS_BASE_URL}/api/to-train"
    response = requests.get(url)
    response.raise_for_status()
    json = response.json()
    return svarog.forge(t.Sequence[Model], json)


def download_photos(path: Path, photos: t.Sequence[TrainingPhoto]):
    path.mkdir(parents=True, exist_ok=True)

    for photo in photos:
        photo_path = path / f"{photo.id}.png"
        if photo_path.exists():
            print(f"ℹ️  Photo {photo.id} already downloaded")
            continue
        with open(photo_path, 'wb') as f:
            f.write(requests.get(photo.url, stream=True).raw.read())


def model_path(model: Model) -> Path:
    return ROOT / "model-data" / model.id


def regularizations_path(model: Model) -> Path:
    return model_path(model) / "regularizations"


def photos_path(model: Model) -> Path:
    return model_path(model) / "photos"


def download_parent_model(parent_model: ParentModel) -> str:
    _login_cli(hf_api=HfApi(), token=HUGGINGFACE_TOKEN)
    return hf_hub_download(
        repo_id=parent_model.repo_id,
        filename=parent_model.filename,
        use_auth_token=True
    )


def make_regularizations(parent_model_path: str, model: Model):
    path = regularizations_path(model)
    path.mkdir(parents=True, exist_ok=True)

    stable_txt2img.main([
        "--ddim_eta", "0.0", "--n_samples", "1", "--n_iter", str(model.regularization.count),
        "--scale", "10.0", "--ddim_steps", "50", "--ckpt", parent_model_path, "--prompt", model.regularization.prompt,
        "--outdir", regularizations_path(model).as_posix()
    ])


def train_model():
    models = get_models()
    if not models:
        print("No models to train")
        return
    model = models[0]
    print(f"Training model {model.slug} ({model.id})")
    print("ℹ️  Downloading photos")
    download_photos(photos_path(model), model.training_photo)
    print("ℹ️  Downloading parent model")
    parent_model_path = download_parent_model(model.parent_model)
    print(f"ℹ️  Parent model downloaded to {parent_model_path}")
    print("ℹ️  Generating Regularization images")
    make_regularizations(parent_model_path, model)


if __name__ == "__main__":
    train_model()
