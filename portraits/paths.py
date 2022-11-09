from pathlib import Path

from .config import ROOT
from .types import Model


def make_model_path(owner_id: str, model_id: str):
    return ROOT / "model-data" / owner_id / model_id

def prompts_outdir(owner_id: str, model_id: str) -> Path:
    return make_model_path(owner_id, model_id) / "prompts"

def model_path(model: Model) -> Path:
    return make_model_path(model.owner_id, model.id)


def regularizations_path(model: Model) -> Path:
    return (
        ROOT / "regularizations" / model.parent_model_code / model.regularization.code
    )


def photos_path(model: Model) -> Path:
    return model_path(model) / "photos"
