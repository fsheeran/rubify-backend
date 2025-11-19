from typing import NamedTuple, Protocol
from .models import AnnotateRequest, Language
import sudachipy
import logging
from enum import Enum
from .cjk_util import segment_on_han, katakana_to_hiragana

logging.getLogger(__name__)


class PhoneticSystem(Enum):
    HIRAGANA = "hiragana"


class Pronunciation(NamedTuple):
    phonetic_system: PhoneticSystem
    value: str


class Lexeme(NamedTuple):
    """Class for representing lexemes produced from segmentation"""

    surface: str
    # if a lexeme is invariant, base_form will be None; otherwise, it contains the uninflected form of the lexeme
    base_form: str | None = None
    pronunciation: Pronunciation | None = None


class SegmentationProvider(Protocol):
    def segment(self, text: str) -> list[Lexeme]: ...

    def can_segment(self, request: AnnotateRequest) -> bool: ...


class DefaultSegmenter:
    def __init__(self):
        pass

    def segment(base_text: str) -> list[Lexeme]:
        return segment_on_han(base_text)


class JapaneseSegmenter:

    def __init__(self):
        super().__init__()
        self.tokenizer = sudachipy.Dictionary().create()

    def segment(self, text: str) -> list[Lexeme]:

        segments = [
            Lexeme(
                token.surface(),
                (
                    token.normalized_form()
                    if token.normalized_form() != token.surface()
                    else None
                ),
                Pronunciation(PhoneticSystem.HIRAGANA, katakana_to_hiragana(token.reading_form()))
            )
            for token in self.tokenizer.tokenize(text)
        ]
        if "".join(token.surface for token in segments) != text:
            logging.error(
                f"Tokenization failed for {text}; sudachi tokenization does not cover whole text"
            )
            return []
        return segments

    def can_segment(self, request: AnnotateRequest) -> bool:
        return request.language == Language.JAPANESE


class ChineseSegmenter:
    def segment(self, text: str) -> list[Lexeme]:
        raise NotImplementedError()

    def can_segment(self, request: AnnotateRequest) -> bool:
        return request.language == Language.CHINESE
