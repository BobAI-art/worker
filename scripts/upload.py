import argparse
from pathlib import Path

from portraits.clients import  upload_photo


def photo_path(path):
    new_path = Path(path).expanduser().resolve()
    if not new_path.exists():
        raise argparse.ArgumentTypeError(f"Path {path} does not exist")
    return new_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("photo_id", type=str, help="the model id to render")
    parser.add_argument("photo_path", type=photo_path)

    args = parser.parse_args()

    upload_photo(photo_id=args.photo_id,  photo_path=args.photo_path)
