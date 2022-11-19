import os
from pathlib import Path

from PIL.Image import Image
from einops import rearrange
from pytorch_lightning import seed_everything
from torch import autocast

from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.ddpm import LatentDiffusion
from portraits.clients import upload_photo
from portraits.types import PhotosResponse
import numpy as np
import torch


def get_model(model_path: Path) -> LatentDiffusion:
    model = LatentDiffusion(
        linear_start=0.00085,
        linear_end=0.012,
        num_timesteps_cond=1,
        log_every_t=200,
        timesteps=1000,
        first_stage_key="jpg",
        cond_stage_key="txt",
        image_size=64,
        channels=4,
        cond_stage_trainable=False,
        conditioning_key="crossattn",
        monitor="val/loss_simple_ema",
        scale_factor=0.18215,
        use_ema=False,
        personalization_config={
            "target": "ldm.modules.embedding_manager.EmbeddingManager",
            "params": {
                "placeholder_strings": ["*"],
                "initializer_words": ["sculpture"],
                "per_image_tokens": False,
                "num_vectors_per_token": 1,
                "progressive_words": False,
            },
        },
        unet_config={
            "target": "ldm.modules.diffusionmodules.openaimodel.UNetModel",
            "params": {
                "image_size": 32,
                "in_channels": 4,
                "out_channels": 4,
                "model_channels": 320,
                "attention_resolutions": [4, 2, 1],
                "num_res_blocks": 2,
                "channel_mult": [1, 2, 4, 4],
                "num_heads": 8,
                "use_spatial_transformer": True,
                "transformer_depth": 1,
                "context_dim": 768,
                "use_checkpoint": True,
                "legacy": False,
            },
        },
        first_stage_config={
            "target": "ldm.models.autoencoder.AutoencoderKL",
            "params": {
                "embed_dim": 4,
                "monitor": "val/rec_loss",
                "ddconfig": {
                    "double_z": True,
                    "z_channels": 4,
                    "resolution": 256,
                    "in_channels": 3,
                    "out_ch": 3,
                    "ch": 128,
                    "ch_mult": [1, 2, 4, 4],
                    "num_res_blocks": 2,
                    "attn_resolutions": [],
                    "dropout": 0.0,
                },
                "lossconfig": {"target": "torch.nn.Identity"},
            },
        },
        cond_stage_config={"target": "ldm.modules.encoders.modules.FrozenCLIPEmbedder"},
    )
    pl_sd = torch.load(model_path, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model.load_state_dict(sd, strict=False)
    if torch.cuda.is_available():
        model.cuda()
    return model


def generate(photos: PhotosResponse, model_path: Path):
    model = get_model(model_path)
    # device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    sampler = DDIMSampler(model)
    precision_scope = autocast

    sample_path = Path("samples")
    sample_path.mkdir(exist_ok=True)
    base_count = len(os.listdir(sample_path.as_posix()))

    latent_channels = 4
    downsampling_factor = 8
    with torch.no_grad():
        with precision_scope("cuda" if torch.cuda.is_available() else "cpu"):
            with model.ema_scope():
                uc = model.get_learned_conditioning([""])

                for photo in photos.photos:
                    print(f"Generating image for {photo}")
                    seed_everything(photo.seed)

                    c = model.get_learned_conditioning([photo.prompt])

                    shape = [
                        latent_channels,
                        photo.height // downsampling_factor,
                        photo.width // downsampling_factor,
                    ]

                    samples_ddim, _ = sampler.sample(
                        S=photo.ddim,
                        conditioning=c,
                        batch_size=1,
                        shape=shape,
                        verbose=False,
                        unconditional_guidance_scale=photo.guidance,
                        unconditional_conditioning=uc,
                        eta=0,
                        x_T=None,
                    )

                    x_samples_ddim = model.decode_first_stage(samples_ddim)
                    x_samples_ddim = torch.clamp(
                        (x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0
                    )

                    for x_sample in x_samples_ddim:
                        x_sample = 255.0 * rearrange(
                            x_sample.cpu().numpy(), "c h w -> h w c"
                        )
                        image_path = sample_path / f"{base_count:05}.jpg"
                        Image.fromarray(x_sample.astype(np.uint8)).save(image_path.as_posix())

                        upload_photo(
                            photo_id=photo.id,
                            photo_path=image_path,
                        )

                        base_count += 1
