import base64
from pathlib import Path

import requests
import typing as t
from . import config
from .types import Model, SubjectPhoto
from .io import UrlSaver


def release_model(model: Model, error: str = None):
    url = f"{config.PORTRAITS_BASE_URL}/api/model/{model.id}/release"
    response = requests.post(url, json={"error": error})
    response.raise_for_status()
    assert response.json() == {"success": True}


def upload_image_from_path(model_id: str, category: str, prompt: t.Optional[str], image_path: Path,base_url=config.PORTRAITS_BASE_URL):
    upload_image(model_id=model_id, category=category, prompt=prompt,
                 image_content=base64.b64encode(image_path.read_bytes()).decode(), base_url=base_url)

def upload_image(model_id: str, category: str, prompt: t.Optional[str], image_content: str,base_url=config.PORTRAITS_BASE_URL):
    url = f"{base_url}/api/model/{model_id}/image"
    response = requests.post(url, json={"category": category, "prompt": prompt, "image_content": image_content})
    response.raise_for_status()
    json = response.json()
    if not json:
        return None
    return json


def get_model(base_url=config.PORTRAITS_BASE_URL) -> t.Optional[Model]:
    url = f"{base_url}/api/model/train"
    response = requests.post(url)
    response.raise_for_status()
    json = response.json()
    if not json:
        return None
    return Model.from_dict(json)


def download_photos(path: Path, photos: t.Sequence[SubjectPhoto], save_url: UrlSaver):
    path.mkdir(parents=True, exist_ok=True)

    for photo in photos:
        photo_path = path / f"{photo.id}.png"
        if photo_path.exists():
            print(f"ℹ️  Photo {photo.id} already downloaded")
            continue
        save_url(photo.url, photo_path)
