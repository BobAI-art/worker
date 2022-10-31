#!/usr/bin/env bash
set -ex

PROJECT_NAME=${PROJECT_NAME:-project}
STEPS=${STEPS:-2000}
CLASS_WORD="person"
TOKEN=${TOKEN:-"theAvatar"}

DATASET=${DATASET:-person_ddim}  # "man_euler", "man_unsplash", "person_ddim", "woman_ddim", "blonde_woman"
REGULARIZATION_IMAGES="$(pwd)/regularization_images/${DATASET}"
MODEL=${MODEL:-model.ckpt}
TRAINING_IMAGES=${TRAINING_IMAGES:-"$(pwd)/training_images"}

python main.py --base configs/stable-diffusion/v1-finetune_unfrozen.yaml \
 -t \
 --actual_resume "${MODEL}" \
 --reg_data_root "${REGULARIZATION_IMAGES}" \
 -n "${PROJECT_NAME}" \
 --gpus 0, \
 --data_root "${TRAINING_IMAGES}" \
 --max_training_steps "${STEPS}" \
 --class_word "${CLASS_WORD}" \
 --token "${TOKEN}" \
 --no-test
