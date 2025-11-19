import regex as re
from collections import OrderedDict

from .models import AnnotatedTextSegment


_kata_to_hira = OrderedDict(
    {
        chr((ord("ア") - ord("あ")) + codepoint): chr(codepoint)
        for codepoint in range(ord("ぁ"), ord("ゖ") + 1)
    }
)
_han_regexp = re.compile(r".*\p{Script=Han}.*", flags=re.U)
is_han = lambda test_str: bool(_han_regexp.match(test_str))


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
    segments = []
    curr_segment_start = -1
    for i in range(len(text)):
        is_curr_han = bool(is_han(text[i]))
        if curr_segment_start < 0:
            curr_segment_start = i - 1
            continue

        if bool(is_han(text[curr_segment_start])) != is_curr_han:
            segments.append(
                AnnotatedTextSegment(
                    indices=(curr_segment_start + index_offset, i + index_offset),
                    annotations=None if is_curr_han else [])
            )
            curr_segment_start = -1
    if curr_segment_start >= 0:
        segments.append(
            AnnotatedTextSegment(
                indices=(curr_segment_start + index_offset, len(text) + index_offset),
                annotations=[] if is_han(text[curr_segment_start]) else None,
            )
        )

    return segments
