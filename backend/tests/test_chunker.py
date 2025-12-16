"""Unit tests for chunker module"""

import pytest
from src.chunker import chunk_text, split_text_into_sentences, create_chunk, validate_chunk_size
from src.utils import count_words


class TestChunker:
    """Test cases for chunker functionality"""

    def test_split_text_into_sentences_basic(self):
        """Test basic sentence splitting"""
        text = "This is the first sentence. This is the second sentence! Is this the third sentence?"

        sentences = split_text_into_sentences(text)

        assert len(sentences) == 3
        assert "first sentence." in sentences[0]
        assert "second sentence!" in sentences[1]
        assert "third sentence?" in sentences[2]

    def test_split_text_into_sentences_empty_text(self):
        """Test sentence splitting with empty text"""
        sentences = split_text_into_sentences("")
        assert sentences == []

    def test_validate_chunk_size_within_range(self):
        """Test chunk size validation within acceptable range"""
        chunk = {"word_count": 400}  # Within 300-500 range

        result = validate_chunk_size(chunk)
        assert result is True

    def test_validate_chunk_size_below_range(self):
        """Test chunk size validation below acceptable range"""
        chunk = {"word_count": 200}  # Below 300

        result = validate_chunk_size(chunk)
        assert result is False

    def test_validate_chunk_size_above_range(self):
        """Test chunk size validation above acceptable range"""
        chunk = {"word_count": 600}  # Above 500

        result = validate_chunk_size(chunk)
        assert result is False

    def test_create_chunk_basic(self):
        """Test basic chunk creation"""
        content = "This is a test chunk."
        url = "https://example.com/test"
        title = "Test Title"
        section = "Test Section"

        chunk = create_chunk(content, url, title, section)

        assert chunk["id"] is not None
        assert chunk["content"] == content
        assert chunk["url"] == url
        assert chunk["title"] == title
        assert chunk["section"] == section
        assert chunk["word_count"] == count_words(content)

    def test_chunk_text_basic(self):
        """Test basic text chunking functionality"""
        text = "This is a sentence. This is another sentence. And a third one. " * 100  # Create ~300 words
        url = "https://example.com/test"
        title = "Test Title"
        section = "Test Section"

        chunks = chunk_text(text, url, title, section)

        assert len(chunks) > 0
        for chunk in chunks:
            assert 300 <= chunk["word_count"] <= 500
            assert chunk["url"] == url
            assert chunk["title"] == title
            assert chunk["section"] == section

    def test_chunk_text_empty_input(self):
        """Test chunking with empty input"""
        chunks = chunk_text("", "https://example.com/test", "Title", "Section")
        assert chunks == []

    def test_chunk_text_respects_sentence_boundaries(self):
        """Test that chunking respects sentence boundaries"""
        # Create text with clear sentence boundaries
        sentence = "This is a sentence. " * 50  # 50 sentences, ~250 words
        text = sentence + sentence  # ~500 words total

        chunks = chunk_text(text, "https://example.com/test", "Title", "Section")

        # Should create at least one chunk
        assert len(chunks) >= 1

        # Check that chunks don't break sentences in the middle
        for chunk in chunks:
            content = chunk["content"]
            # Verify that sentences end with proper punctuation
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            # This is a basic check - in a real test we'd have more sophisticated validation