import pytest
from src.annotation import DefaultAnnotator, FuriganaAnnotator
from src.models import AnnotateRequest, Language, AnnotatedTextSegment, Annotation
from src.segmentation import Lexeme, PhoneticSystem, Pronunciation
from src.pronunciation import CjkPronunciationEntry, PronunciationDatum


@pytest.fixture
def mock_furigana_provider():
    return {
        "私": [
            CjkPronunciationEntry(
                text="私",
                pronunciation="わたし",
                per_char=[PronunciationDatum(indices=(0, 1), pronunciation="わたし")],
            )
        ],
        "人間": [
            CjkPronunciationEntry(
                text="人間",
                pronunciation="にんげん",
                per_char=[
                    PronunciationDatum(indices=(0, 1), pronunciation="にん"),
                    PronunciationDatum(indices=(1, 2), pronunciation="げん"),
                ],
            )
        ],
        "人": [
            CjkPronunciationEntry(
                text="人",
                pronunciation="ひと",
                per_char=[PronunciationDatum(indices=(0, 1), pronunciation="ひと")],
            )
        ],
        "常": [
            CjkPronunciationEntry(
                text="常",
                pronunciation="つね",
                per_char=[PronunciationDatum(indices=(0, 1), pronunciation="つね")],
            )
        ],
        "先生": [
            CjkPronunciationEntry(
                text="先生",
                pronunciation="せんせい",
                per_char=[
                    PronunciationDatum(indices=(0, 1), pronunciation="せん"),
                    PronunciationDatum(indices=(1, 2), pronunciation="せい"),
                ],
            )
        ],
        "呼ぶ": [
            CjkPronunciationEntry(
                text="呼ぶ",
                pronunciation="よぶ",
                per_char=[PronunciationDatum(indices=(0, 1), pronunciation="よ")],
            )
        ],
    }


@pytest.fixture
def lexemes():
    # original sentence: 私はその人を常に先生と呼んでいた
    return [
        Lexeme(surface="私", pronunciation=Pronunciation(PhoneticSystem.HIRAGANA, "わたし")),
        Lexeme(surface="は", pronunciation=Pronunciation(PhoneticSystem.HIRAGANA, "は")),
        Lexeme("その"),
        Lexeme(surface="人", pronunciation=Pronunciation(PhoneticSystem.HIRAGANA, "ひと")),
        Lexeme(surface="を"),
        Lexeme(surface="常", pronunciation=Pronunciation(PhoneticSystem.HIRAGANA, "つね")),
        Lexeme("に"),
        Lexeme(surface="先生", pronunciation=Pronunciation(PhoneticSystem.HIRAGANA, "せんせい")),
        Lexeme("と"),
        Lexeme("呼んで", "呼ぶ", Pronunciation(PhoneticSystem.HIRAGANA, "よぶ")),
        Lexeme("いた", "いる"),
    ]


class TestDefaultAnnotator:
    def test_default_annotator_can_annotate(self):
        """Test DefaultAnnotator can annotate any request"""
        annotator = DefaultAnnotator()
        request = AnnotateRequest(base_text="こんにちは", language=Language.JAPANESE)
        assert annotator.can_annotate(request) is True
        request = AnnotateRequest(base_text="你好", language=Language.CHINESE)
        assert annotator.can_annotate(request) is True

    def test_default_annotator_annotate(self):
        """Test DefaultAnnotator annotate"""
        annotator = DefaultAnnotator()
        lexemes = [Lexeme('これ'), Lexeme('は'), Lexeme("漢字"), Lexeme('だ')]
        result = annotator.annotate(lexemes)
        assert len(result) == 4
        assert result == [
            AnnotatedTextSegment(indices=(0, 2), annotations=None),
            AnnotatedTextSegment(indices=(2, 3), annotations=None),
            AnnotatedTextSegment(indices=(3, 5), annotations=[]),
            AnnotatedTextSegment(indices=(5, 6), annotations=None),
        ]

class TestFuriganaAnnotator:

    def test_furigana_annotate(self, mock_furigana_provider, lexemes):
        """Test FuriganaAnnotator annotate"""
        annotator = FuriganaAnnotator(mock_furigana_provider)
        result = annotator.annotate(lexemes)
        expected = [
            AnnotatedTextSegment(indices=(0, 1), annotations=[Annotation(indices=(0, 1), annotation_text="わたし")]),
            AnnotatedTextSegment(indices=(1, 2)),
            AnnotatedTextSegment(indices=(2, 4)),
            AnnotatedTextSegment(indices=(4, 5), annotations=[Annotation(indices=(4, 5), annotation_text="ひと")]),
            AnnotatedTextSegment(indices=(5, 6)),
            AnnotatedTextSegment(indices=(6, 7), annotations=[Annotation(indices=(6, 7), annotation_text="つね")]),
            AnnotatedTextSegment(indices=(7, 8)),
            AnnotatedTextSegment(indices=(8, 10), annotations=[
                Annotation(indices=(8, 9), annotation_text="せん"),
                Annotation(indices=(9, 10), annotation_text="せい")
            ]),
            AnnotatedTextSegment(indices=(10, 11)),
            AnnotatedTextSegment(indices=(11, 14), annotations=[
                Annotation(indices=(11, 12), annotation_text="よ")
            ]),
            AnnotatedTextSegment(indices=(14, 16))
        ]
        assert result == expected
