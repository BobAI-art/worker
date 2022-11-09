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
class ParentModel:
    repo_id: str
    filename: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            repo_id=d["repo_id"],
            filename=d["filename"],
        )


@dataclass(frozen=True)
class Model:
    id: str
    name: str
    owner_id: str
    parent_model_code: str
    regularization: t.Union[GenerateRegularization, FetchRegularization]
    subject: Subject
    parent_model: ParentModel

    @classmethod
    def from_dict(cls, d):
        subject = Subject.from_dict(d.pop("subject"))
        regularization_class = REGULARIZATION_CLASSES[d["regularization"]["type"]]
        regularization = regularization_class.from_dict(d.pop("regularization"))
        parent_model = ParentModel.from_dict(d.pop("parent_model"))
        return cls(
            subject=subject,
            regularization=regularization,
            parent_model=parent_model,
            **d,
        )


@dataclass(frozen=True)
class Prompt:
    id: str
    class_: str
    prompt: str
    subject: str

    def render(self):
        return self.prompt.replace("<MODEL>", f"{self.subject} {self.class_}")

    @classmethod
    def from_dict(cls, d):
        class_ = d.pop("class")
        return cls(**d,
                   class_=class_)


@dataclass(frozen=True)
class PromptResponse:
    model_id: str
    owner_id: str
    prompts: t.Sequence[Prompt]

    @classmethod
    def from_dict(cls, d):
        prompts = [Prompt.from_dict(prompt) for prompt in d.pop("prompts")]
        return cls(prompts=prompts, **d)
