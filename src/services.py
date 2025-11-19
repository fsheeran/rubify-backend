from typing import Iterator, Generic, TypeVar
from .segmentation import Lexeme, SegmentationProvider
from .annotation import AnnotationProvider, DefaultAnnotator
from .models import AnnotateRequest, AnnotatedTextSegment

import logging

logging.getLogger(__name__)


class SegmentationFailed(Exception):
    pass


class AnnotationFailed(Exception):
    pass


T = TypeVar("T")


class PriorityRegistry(Generic[T]):
    def __init__(self):
        self.registry: list[tuple[T, int]] = []

    def register(self, item: T, priority: int):
        self.registry.append((item, priority))
        self.registry.sort(key=lambda x: x[1], reverse=True)

    def __iter__(self) -> Iterator[T]:
        for item, _ in self.registry:
            yield item


# TODO there might be a way to refactor the prioritization logic out of these two services


class SegmentationService:
    def __init__(self, registry: PriorityRegistry[SegmentationProvider]):
        self.registry = registry

    def segment(self, annotate_request: AnnotateRequest) -> list[Lexeme]:
        for segmenter in self.registry:
            if segmenter.can_segment(annotate_request):
                result = segmenter.segment(annotate_request.base_text)
            if result:
                return result
            else:
                logging.error(
                    f"Attempted to segment with segmenter of type {segmenter.__class__.__name__} but failed."
                )
        raise SegmentationFailed(f"No suitable segmenter found for {annotate_request}.")


class SegmentAnnotationService:
    def __init__(self, registry: PriorityRegistry[AnnotationProvider]):
        self.registry = registry

    def annotate(
        self, annotate_request: AnnotateRequest, lexemes: list[Lexeme]
    ) -> list[AnnotatedTextSegment]:
        for annotator in self.registry:
            if annotator.can_annotate(annotate_request):
                try:
                    return annotator.annotate(lexemes)
                except Exception as e:
                    logging.error(
                        f"Annotator {annotator.__class__.__name__} failed with error: {e}; skipping."
                    )
        raise AnnotationFailed(f"No suitable annotator found for {annotate_request}")
