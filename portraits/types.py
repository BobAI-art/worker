from dataclasses import dataclass
import typing as t
from enum import Enum


@dataclass(frozen=True)
class SubjectPhoto:
    url: str

    @property
    def file_name(self):
        return self.url.split("/")[-1]

    @classmethod
    def from_string(cls, s):
        return cls(
            url=s,
        )


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
    regularization: str

    @property
    def code(self):
        return f"fetch-{self.prompt}"

    @property
    def prompt(self):
        return self.source.split("/")[-1].split(".")[0].lower().split("-")[-1]

    @classmethod
    def from_dict(cls, d: t.Mapping[str, t.Any]):
        return cls(source=d["source"], regularization=d['regularization'])


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
    slug: str
    subject_photos: t.Sequence[SubjectPhoto]

    @classmethod
    def from_dict(cls, d):
        subject_photos = [
            SubjectPhoto.from_string(photo) for photo in d.pop("subject_photos")
        ]
        return cls(subject_photos=subject_photos, slug=d["slug"])


@dataclass(frozen=True)
class Style:
    repo_id: str
    filename: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            repo_id=d["repo_id"],
            filename=d["filename"],
        )


@dataclass(frozen=True)
class Depiction:
    id: str
    name: str
    owner_id: str
    style_slug: str
    regularization: t.Union[GenerateRegularization, FetchRegularization]
    subject: Subject
    style: Style

    @classmethod
    def from_dict(cls, d):
        subject = Subject.from_dict(d.pop("subject"))
        regularization_class = REGULARIZATION_CLASSES[d["regularization"]["type"]]
        regularization = regularization_class.from_dict(d.pop("regularization"))
        style = Style.from_dict(d.pop("style"))
        return cls(
            subject=subject,
            regularization=regularization,
            style=style,
            **d,
        )


@dataclass(frozen=True)
class Photo:
    id: str
    prompts: t.List[str]

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass(frozen=True)
class PhotoSourceAWS:
    path: str

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


PhotoSource = t.Union[Style, PhotoSourceAWS]


@dataclass(frozen=True)
class PhotosResponse:
    source: PhotoSource
    photos: t.Sequence[Photo]

    @classmethod
    def from_dict(cls, d):
        photos = [Photo.from_dict(photo) for photo in d.pop("photos")]
        source = d.pop("source")
        source_type = source.pop("source")
        if source_type == "huggingface":
            source = Style.from_dict(source)
        elif source_type == "aws":
            source = PhotoSourceAWS.from_dict(source)
        else:
            raise ValueError(f"Unknown source type: {source['source']}")
        return cls(photos=photos, source=source)
