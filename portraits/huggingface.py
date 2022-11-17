from typing_extensions import Protocol

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.commands.user import _login as _login_cli

from . import config
from .types import Style


class ModelDownloader(Protocol):
    def __call__(self, parent_model: Style) -> str:
        ...


def download_parent_model(parent_model: Style) -> str:
    _login_cli(hf_api=HfApi(), token=config.HUGGINGFACE_TOKEN)
    return hf_hub_download(
        repo_id=parent_model.repo_id,
        filename=parent_model.filename,
        use_auth_token=True,
    )
