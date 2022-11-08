import argparse
from pathlib import Path

from portraits.clients import  upload_image_from_path


def photo_path(path):
    new_path = Path(path).expanduser().resolve()
    if not new_path.exists():
        raise argparse.ArgumentTypeError(f"Path {path} does not exist")
    return new_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("model_id", type=str, help="the model id to render")
    parser.add_argument("image_path", type=photo_path)
    parser.add_argument("category", type=str, help="the category to render")
    parser.add_argument("--prompt", type=str, nargs="?", default="a painting of a virus monster playing guitar",
                        help="the prompt to render")

    args = parser.parse_args()

    upload_image_from_path(model_id=args.model_id, category=args.category, prompt=args.prompt, image_path=args.image_path)
