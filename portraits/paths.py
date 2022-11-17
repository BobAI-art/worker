from pathlib import Path

from .config import ROOT
from .types import Depiction


def make_model_path(owner_id: str, model_id: str):
    return ROOT / "model-data" / owner_id / model_id

def generated_photos_outdir() -> Path:
    return ROOT / "generated-photos"

def model_path(model: Depiction) -> Path:
    return make_model_path(model.owner_id, model.id)


def regularizations_path(model: Depiction) -> Path:
    return (
        ROOT / "regularizations" / model.style_slug / model.regularization.code
    )


def photos_path(model: Depiction) -> Path:
    return model_path(model) / "photos"
