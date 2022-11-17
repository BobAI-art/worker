import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()


HUGGINGFACE_TOKEN = os.environ["HUGGINGFACE_TOKEN"]
PORTRAITS_BASE_URL = os.environ["PORTRAITS_BASE_URL"]
MODEL_STORE_REGION = os.environ.get("MODEL_STORE_REGION", "eu-west-2")
MODEL_STORE_BUCKET_NAME = os.environ["MODEL_STORE_BUCKET_NAME"]

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]


PHOTO_STORE_REGION = "s3.eu-west-2"
