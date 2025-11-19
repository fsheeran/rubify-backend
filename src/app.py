from typing import Annotated

from fastapi import FastAPI, Depends

from .pronunciation import load_furigana_json

from .annotation import AnnotationProvider, DefaultAnnotator, FuriganaAnnotator

from .models import AnnotateRequest

from .services import PriorityRegistry, SegmentationService, SegmentAnnotationService
from .segmentation import DefaultSegmenter, JapaneseSegmenter, SegmentationProvider

furigana_provider = load_furigana_json(
    # todo : yank this out into a env variable or something
    "JmdictFurigana.json"
)


async def get_segmentation_service():
    registry = PriorityRegistry[SegmentationProvider]()
    registry.register(JapaneseSegmenter(), 1)
    registry.register(DefaultSegmenter(), 0)

    service = SegmentationService(registry)
    return service


async def get_segment_annotation_service():
    registry = PriorityRegistry[AnnotationProvider]()
    registry.register(FuriganaAnnotator(furigana_provider), 1)
    registry.register(DefaultAnnotator(), 0)

    service = SegmentAnnotationService(registry)

    return service


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/annotate", response_model_exclude_none=True)
def annotate_base_text(
    request: AnnotateRequest,
    segmentation_service: SegmentationService = Depends(get_segmentation_service),
    segment_annotation_service: SegmentAnnotationService = Depends(
        get_segment_annotation_service
    ),
):
    segments = segmentation_service.segment(request)
    return segment_annotation_service.annotate(request, segments)

    # return [
    #     (
    #         TextSegmentModel(
    #             indices=indices,
    #             annotations=[
    #                 AnnotationModel(indices=an_ind, annotation_text=text)
    #                 for an_ind, text in annotations
    #             ],
    #         )
    #         if annotations
    #         else TextSegmentModel(indices=indices)
    #     )
    #     for indices, annotations in annotator.annotate(
    #         request.base_text, request.language
    #     )
    # ]
