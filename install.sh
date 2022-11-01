#!/usr/bin/env bash
# install conda?

conda create -n sd  python=3.10 -y
conda activate sd
pip install -r requirements.txt
# put token to ~/.huggingface/token
# huggingface-cli login
git lfs install
