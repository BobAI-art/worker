import typing as t
from . import config
from . import io


def get_s3_path(path: str) -> str:
    root = config.ROOT.as_posix()
    if not path.startswith(root):
        print("❌  Path must be a subpath of the root")
    assert path.startswith(root)
    return path[len(root) + 1 :]


def pull_s3(path: str, run: io.CommandRunner):
    path_on_s3 = get_s3_path(path)
    print(f"ℹ️  Pull {path} from S3")

    run(
        [
            "aws",
            "s3",
            "sync",
            f"s3://{config.MODEL_STORE_BUCKET_NAME}/{path_on_s3}",
            path,
            "--region",
            config.MODEL_STORE_REGION,
            "--exclude",
            ".git/*",
        ]
    )


def copy_to_s3(path: str, run: io.CommandRunner):
    path_on_s3 = get_s3_path(path)
    print(f"ℹ️  Copying {path_on_s3} to S3")

    run(
        [
            "aws",
            "s3",
            "cp",
            path,
            f"s3://{config.MODEL_STORE_BUCKET_NAME}/{path_on_s3}",
            "--region",
            config.MODEL_STORE_REGION,
        ]
    )


def push_s3(path: str, run: io.CommandRunner):
    path_on_s3 = get_s3_path(path)
    print(f"ℹ️  Pushing {path} to S3")

    run(
        [
            "aws",
            "s3",
            "sync",
            path,
            f"s3://{config.MODEL_STORE_BUCKET_NAME}/{path_on_s3}",
            "--region",
            config.MODEL_STORE_REGION,
            "--exclude",
            ".git/*",
        ]
    )
