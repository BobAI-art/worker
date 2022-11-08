from pathlib import Path

from .config import ROOT
from .types import Model


def model_path(model: Model) -> Path:
    return ROOT / "model-data" / model.owner_id / model.id


def regularizations_path(model: Model) -> Path:
    return (
        ROOT / "regularizations" / model.parent_model_code / model.regularization.code
    )


def photos_path(model: Model) -> Path:
    return model_path(model) / "photos"
