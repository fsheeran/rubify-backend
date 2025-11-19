# need to use regex since standard library re does not support matching unicode properties
from typing import Protocol
from difflib import get_close_matches
from .cjk_util import is_han, segment_on_han

from .segmentation import Lexeme
from .pronunciation import CjkPronunciationProvider
from .models import AnnotateRequest, AnnotatedTextSegment, Annotation, Language

import logging

logging.getLogger(__name__)


class AnnotationProvider(Protocol):
    def annotate(self, lexemes: list[Lexeme]) -> list[AnnotatedTextSegment]: ...
    def can_annotate(self, request: AnnotateRequest) -> bool: ...


class DefaultAnnotator:
    def annotate(self, lexemes: list[Lexeme]) -> list[AnnotatedTextSegment]:
        index = 0
        segments = []
        for lexeme in lexemes:
            if is_han(lexeme.surface):
                segments.append(AnnotatedTextSegment(indices=(index, index + len(lexeme.surface)), annotations=[]))
            else:
                segments.append(AnnotatedTextSegment(indices=(index, index + len(lexeme.surface))))
            index += len(lexeme.surface)
        return segments

    def can_annotate(self, request: AnnotateRequest) -> bool:
        return True


class FuriganaAnnotator:

    def __init__(self, pronunciation_provider: CjkPronunciationProvider):
        self.pronunciation_provider = pronunciation_provider

    def annotate(self, lexemes: list[Lexeme]) -> list[AnnotatedTextSegment]:
        segments = []
        segment_start = 0
        for lexeme in lexemes:
            indices = (segment_start, segment_start + len(lexeme.surface))
            if not is_han(lexeme.surface):
                segments.append(AnnotatedTextSegment(indices=indices))
                segment_start = indices[1]
                continue

            try:
                furigana_entries = self.pronunciation_provider[lexeme.base_form if lexeme.base_form else lexeme.surface]
            except KeyError:
                furigana_entries = None
            if not furigana_entries:
                segments.extend(segment_on_han(lexeme.surface, segment_start))
                segment_start = indices[1]
                continue

            best_fit_pronunciation = get_close_matches(lexeme.pronunciation.value, [entry.pronunciation for entry in furigana_entries], n=1)
            if not best_fit_pronunciation:
                segments.extend(segment_on_han(lexeme.surface, segment_start))
                segment_start = indices[1]
                continue
            best_fit = next(entry for entry in furigana_entries if entry.pronunciation == best_fit_pronunciation[0])

            annotations = []
            for fg_indices, pronunciation in best_fit.per_char:
                if pronunciation:
                    annotations.append(
                        Annotation(
                            indices=(
                                segment_start + fg_indices[0],
                                segment_start + fg_indices[1],
                            ),
                            annotation_text=pronunciation,
                        )
                    )

            segments.append(
                AnnotatedTextSegment(
                    indices= indices,
                    annotations=annotations,
                )
            )
            segment_start += len(lexeme.surface)
        return segments

    def can_annotate(self, request: AnnotateRequest) -> bool:
        return request.language == Language.JAPANESE