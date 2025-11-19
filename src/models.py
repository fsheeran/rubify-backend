from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Language(Enum):
    JAPANESE = "jpn"
    CHINESE = "zho"


class AnnotateRequest(BaseModel):
    base_text: str
    language: Language

    def __repr__(self):
        return f"AnnotateRequest(language={self.language})"


class Annotation(BaseModel):
    indices: tuple[int, int]
    annotation_text: Optional[str] = None


class AnnotatedTextSegment(BaseModel):
    indices: tuple[int, int]
    annotations: Optional[list[Annotation]] = None
