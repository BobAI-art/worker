from dataclasses import dataclass
from datetime import datetime
import typing as t
from enum import Enum

from .config import PHOTO_STORE_REGION
from .helpers import make_datetime


@dataclass(frozen=True)
class SubjectPhoto:
    id: str
    path: str
    bucket: str
    subject_slug: str

    @property
    def url(self):
        return f"https://{self.bucket}.{PHOTO_STORE_REGION}.amazonaws.com/{self.path}"

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass(frozen=True)
class GenerateRegularization:
    prompt: str
    count: int

    @property
    def code(self):
        return f"generate-{self.prompt}"

    @classmethod
    def from_dict(cls, d):
        return cls(prompt=d["prompt"], count=d["count"])


@dataclass(frozen=True)
class FetchRegularization:
    source: str

    @property
    def code(self):
        return f"fetch-{self.prompt}"

    @property
    def prompt(self):
        return self.source.split("/")[-1].split(".")[0].lower().split("-")[-1]

    @classmethod
    def from_dict(cls, d: t.Mapping[str, t.Any]):
        return cls(source=d["source"])


REGULARIZATION_CLASSES = {
    "fetch": FetchRegularization,
    "generate": GenerateRegularization,
}


class State(Enum):
    CREATED = "CREATED"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"


@dataclass(frozen=True)
class Subject:
    id: str
    slug: str
    created: datetime
    description: str
    owner_id: str
    subject_photos: t.Sequence[SubjectPhoto]

    @classmethod
    def from_dict(cls, d):
        subject_photos = [
            SubjectPhoto.from_dict(photo) for photo in d.pop("subject_photos")
        ]
        return cls(subject_photos=subject_photos, **d)


@dataclass(frozen=True)
class ParentModel:
    repo_id: str
    filename: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            repo_id=d["repoId"],
            filename=d["filename"],
        )


@dataclass(frozen=True)
class Model:
    id: str
    name: str
    owner_id: str
    subject_slug: str
    created: datetime
    state: State
    parent_model_code: str
    regularization: t.Union[GenerateRegularization, FetchRegularization]
    subject: Subject
    parent_model: ParentModel

    @classmethod
    def from_dict(cls, d):
        created = make_datetime(d.pop("created"))
        state = State(d.pop("state"))
        subject = Subject.from_dict(d.pop("subject"))
        regularization_class = REGULARIZATION_CLASSES[d["regularization"]["type"]]
        regularization = regularization_class.from_dict(d.pop("regularization"))
        parent_model = ParentModel.from_dict(d.pop("parent_model"))
        return cls(
            created=created,
            state=state,
            subject=subject,
            regularization=regularization,
            parent_model=parent_model,
            **d,
        )
