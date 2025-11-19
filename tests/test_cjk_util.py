import pytest
from src.cjk_util import is_han, katakana_to_hiragana, segment_on_han
from src.models import AnnotatedTextSegment


class TestIsHan:
    def test_is_han_chinese_characters(self):
        """Test is_han with Chinese characters"""
        assert is_han("漢") is True
        assert is_han("字") is True
        assert is_han("你好") is True

    def test_is_han_japanese_hiragana(self):
        """Test is_han with Japanese hiragana"""
        assert is_han("あ") is False
        assert is_han("こんにちは") is False

    def test_is_han_japanese_katakana(self):
        """Test is_han with Japanese katakana"""
        assert is_han("ア") is False
        assert is_han("カタカナ") is False

    def test_is_han_korean_hangul(self):
        """Test is_han with Korean Hangul characters"""
        # Hangul is not Han script
        assert is_han("안") is False
        assert is_han("녕하세요") is False

    def test_is_han_mixed_cjk(self):
        """Test is_han with mixed CJK characters"""
        assert is_han("漢あ") is True  # Starts with Han
        assert is_han("あ漢") is True  # Starts with non-Han (hiragana)


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
        assert result == [AnnotatedTextSegment(indices=(0, 2), annotations=[])]


    def test_segment_on_han_no_han(self):
        """Test segment_on_han with no Han characters"""
        text = "こんにちは"
        result = segment_on_han(text)
        assert result == [AnnotatedTextSegment(indices=(0, 5), annotations=None)]

    def test_segment_on_han_mixed(self):
        """Test segment_on_han with mixed Han and non-Han"""
        text = "漢字です"
        result = segment_on_han(text)
        assert result == [AnnotatedTextSegment(indices=(0, 2), annotations=[]), AnnotatedTextSegment(indices=(2, 4), annotations=None)]

    def test_segment_on_han_with_offset(self):
        """Test segment_on_han with offset"""
        text = "漢字です"
        result = segment_on_han(text, index_offset=1)
        assert result == [AnnotatedTextSegment(indices=(1, 3), annotations=[]), AnnotatedTextSegment(indices=(3, 5), annotations=None)]

    def test_segment_on_han_ends_with_han(self):
        """Test segment_on_han with ends with Han"""
        text = "です漢字"
        result = segment_on_han(text)
        assert result == [AnnotatedTextSegment(indices=(0, 2), annotations=None), AnnotatedTextSegment(indices=(2, 4), annotations=[])]

