import regex as re
from src.cjk_util import (
    katakana_to_hiragana,
    segment_on_han,
    is_han_regexp,
    contains_han_regexp,
)
from src.models import AnnotatedTextSegment, Annotation


def assert_regex_match(regex: re.Pattern, string: str, span: tuple[int, int]):
    match = regex.match(string)
    assert match.span() == span
    assert match.string == string


class TestIsHan:
    def test_is_han_regexp_chinese_characters(self):
        """Test is_han with Chinese characters"""
        assert_regex_match(is_han_regexp, "漢", (0, 1))

    def test_is_han_regexp_japanese_hiragana(self):
        """Test is_han with Japanese hiragana"""
        assert is_han_regexp.match("あ") is None
        assert is_han_regexp.match("こんにちは") is None

    def test_is_han_regexp_japanese_katakana(self):
        """Test is_han with Japanese katakana"""
        assert is_han_regexp.match("ア") is None
        assert is_han_regexp.match("カタカナ") is None

    def test_is_han_regexp_korean_hangul(self):
        """Test is_han with Korean Hangul characters"""
        # Hangul is not Han script
        assert is_han_regexp.match("안") is None

    def test_contains_han_regexp(self):
        """Test contains_han_regexp"""
        assert_regex_match(contains_han_regexp, "漢字", (0, 2))

        assert contains_han_regexp.match("こんにちは") is None

        assert_regex_match(contains_han_regexp, "漢字です", (0, 4))
        assert_regex_match(contains_han_regexp, "です漢字", (0, 4))


class TestKatakanaToHiragana:
    def test_katakana_to_hiragana_basic(self):
        """Test basic katakana to hiragana conversion"""
        result = katakana_to_hiragana("カタカナ")
        assert result == "かたかな"

    def test_katakana_to_hiragana_hiragana_unchanged(self):
        """Test that hiragana remains unchanged"""
        text = "ひらがな"
        result = katakana_to_hiragana(text)
        # Should remain the same
        assert result == "ひらがな"

    def test_katakana_to_hiragana_mixed(self):
        """Test katakana to hiragana with mixed characters"""
        text = "カタカナとひらがな"
        result = katakana_to_hiragana(text)
        assert result == "かたかなとひらがな"


class TestSegmentOnHan:
    def test_segment_on_han_all_han(self):
        """Test segment_on_han with all Han characters"""
        text = "漢字"
        result = segment_on_han(text)
        assert result == [
            AnnotatedTextSegment(
                indices=(0, 1), annotations=[Annotation(indices=(0, 1))]
            ),
            AnnotatedTextSegment(
                indices=(1, 2), annotations=[Annotation(indices=(1, 2))]
            ),
        ]

    def test_segment_on_han_no_han(self):
        """Test segment_on_han with no Han characters"""
        text = "こんにちは"
        result = segment_on_han(text)
        assert result == [AnnotatedTextSegment(indices=(0, 5), annotations=None)]

    def test_segment_on_han_mixed(self):
        """Test segment_on_han with mixed Han and non-Han"""
        text = "漢字です"
        result = segment_on_han(text)
        assert result == [
            AnnotatedTextSegment(
                indices=(0, 1), annotations=[Annotation(indices=(0, 1))]
            ),
            AnnotatedTextSegment(
                indices=(1, 2), annotations=[Annotation(indices=(1, 2))]
            ),
            AnnotatedTextSegment(indices=(2, 4), annotations=None),
        ]

    def test_segment_on_han_with_offset(self):
        """Test segment_on_han with offset"""
        text = "漢字です"
        result = segment_on_han(text, index_offset=1)
        assert result == [
            AnnotatedTextSegment(
                indices=(1, 2), annotations=[Annotation(indices=(1, 2))]
            ),
            AnnotatedTextSegment(
                indices=(2, 3), annotations=[Annotation(indices=(2, 3))]
            ),
            AnnotatedTextSegment(indices=(3, 5), annotations=None),
        ]

    def test_segment_on_han_interleaved(self):
        """Test segment_on_han with interleaved Han and non-Han"""
        text = "打ち合わせ"
        result = segment_on_han(text)
        assert result == [
            AnnotatedTextSegment(
                indices=(0, 1), annotations=[Annotation(indices=(0, 1))]
            ),
            AnnotatedTextSegment(indices=(1, 2), annotations=None),
            AnnotatedTextSegment(
                indices=(2, 3), annotations=[Annotation(indices=(2, 3))]
            ),
            AnnotatedTextSegment(indices=(3, 5), annotations=None),
        ]

    def test_segment_on_han_ends_with_han(self):
        """Test segment_on_han with ends with Han"""
        text = "です漢字"
        result = segment_on_han(text)
        assert result == [
            AnnotatedTextSegment(indices=(0, 2), annotations=None),
            AnnotatedTextSegment(
                indices=(2, 3), annotations=[Annotation(indices=(2, 3))]
            ),
            AnnotatedTextSegment(
                indices=(3, 4), annotations=[Annotation(indices=(3, 4))]
            ),
        ]
