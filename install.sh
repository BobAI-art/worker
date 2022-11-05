#!/usr/bin/env bash
# install conda?

conda create -n sd -y
conda activate sd
pip install -r requirements.txt
# put token to ~/.huggingface/token


# https://huggingface.co/runwayml/stable-diffusion-v1-5# huggingface-cli login
git lfs install
