import regex as re
from collections import OrderedDict

from .models import AnnotatedTextSegment, Annotation


_kata_to_hira = OrderedDict(
    {
        chr((ord("ア") - ord("あ")) + codepoint): chr(codepoint)
        for codepoint in range(ord("ぁ"), ord("ゖ") + 1)
    }
)
is_han_regexp = re.compile(r"\p{Script=Han}", flags=re.U)
contains_han_regexp = re.compile(r".*\p{Script=Han}.*", flags=re.U)


def katakana_to_hiragana(string: str) -> str:
    return "".join(
        [
            (
                c
                if c < next(iter(_kata_to_hira))
                or c > next(iter(reversed(_kata_to_hira)))
                else _kata_to_hira[c]
            )
            for c in string
        ]
    )


def segment_on_han(text: str, index_offset: int = 0) -> list[AnnotatedTextSegment]:
    annotated_segments = [
        AnnotatedTextSegment(
            indices=(i + index_offset, i + 1 + index_offset), annotations=[Annotation(indices=(i + index_offset, i + 1 + index_offset))]
        )
        for i, ch in enumerate(text)
        if is_han_regexp.match(ch)
    ]

    if not annotated_segments:
        return [AnnotatedTextSegment(indices=(0, len(text)), annotations=None)]

    segments = (
        [AnnotatedTextSegment(indices=(index_offset, annotated_segments[0].indices[0] + index_offset))]
        if annotated_segments[0].indices[0] > index_offset
        else []
    )
    for segment in annotated_segments:
        if segments and segments[-1].indices[1] < segment.indices[0]:
            segments.append(
                AnnotatedTextSegment(
                    indices=(segments[-1].indices[1], segment.indices[0])
                )
            )
        segments.append(segment)

    if segments[-1].indices[1] < len(text):
        segments.append(
            AnnotatedTextSegment(indices=(segments[-1].indices[1], len(text) + index_offset))
        )

    return segments
