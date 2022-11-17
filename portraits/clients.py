import base64
import os
import typing as t
from pathlib import Path

import requests

from . import config
from .io import UrlSaver
from .types import Depiction, SubjectPhoto
from .types import PhotosResponse


def release_model(model: Depiction, error: str = None):
    url = f"{config.PORTRAITS_BASE_URL}/api/model/{model.id}/release"
    response = requests.post(url, json={"error": error})
    response.raise_for_status()
    assert response.json() == {"success": True}


def upload_photo(photo_id: str, photo_path: Path, base_url=config.PORTRAITS_BASE_URL):
    photo_content = base64.b64encode(photo_path.read_bytes()).decode()
    url = f"{base_url}/api/photo/{photo_id}"
    response = requests.post(url, json={"photo_content": photo_content})
    response.raise_for_status()


def get_photos(base_url=config.PORTRAITS_BASE_URL) -> t.Optional[PhotosResponse]:
    url = f"{base_url}/api/photo"
    if os.environ.get('PORTRAITS_DRY_RUN', 'false') == 'true':
        response = requests.get(url)
    else:
        response = requests.post(url)
    response.raise_for_status()
    json = response.json()
    if not json:
        return None
    return PhotosResponse.from_dict(json)


def get_model(base_url=config.PORTRAITS_BASE_URL) -> t.Optional[Depiction]:
    url = f"{base_url}/api/model/train"
    if os.environ.get('PORTRAITS_DRY_RUN', 'false') == 'true':
        response = requests.get(url)
    else:
        response = requests.post(url)
    response.raise_for_status()
    json = response.json()
    if not json:
        return None
    return Depiction.from_dict(json)


def download_photos(path: Path, photos: t.Sequence[SubjectPhoto], save_url: UrlSaver):
    path.mkdir(parents=True, exist_ok=True)

    for photo in photos:
        photo_path = path / photo.file_name
        if photo_path.exists():
            print(f"ℹ️  Photo {photo.file_name} already downloaded")
            continue
        save_url(photo.url, photo_path)
