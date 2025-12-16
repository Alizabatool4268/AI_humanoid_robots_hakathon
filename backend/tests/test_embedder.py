"""Unit tests for embedder module"""

import pytest
from unittest.mock import patch, MagicMock
from src.embedder import embed


class TestEmbedder:
    """Test cases for embedder functionality"""

    @patch('src.embedder.cohere.Client')
    def test_embed_basic(self, mock_cohere_client):
        """Test basic embedding functionality"""
        # Mock Cohere client and response
        mock_client_instance = MagicMock()
        mock_client_instance.embed.return_value = MagicMock()
        mock_client_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_cohere_client.return_value = mock_client_instance

        # Create test chunks
        test_chunks = [
            {"id": "1", "content": "This is the first chunk.", "url": "https://example.com", "title": "Title", "section": "Section", "word_count": 5},
            {"id": "2", "content": "This is the second chunk.", "url": "https://example.com", "title": "Title", "section": "Section", "word_count": 5}
        ]

        # Execute embedding
        result = embed(test_chunks)

        # Verify the results
        assert len(result) == 2
        assert "vector" in result[0]
        assert "vector" in result[1]
        assert result[0]["embedding_model"] is not None
        assert result[1]["embedding_model"] is not None

        # Verify that the embed method was called with the right parameters
        mock_client_instance.embed.assert_called_once()
        call_args = mock_client_instance.embed.call_args
        assert "texts" in call_args.kwargs
        assert call_args.kwargs["input_type"] == "search_document"

    @patch('src.embedder.cohere.Client')
    def test_embed_empty_chunks(self, mock_cohere_client):
        """Test embedding with empty chunks list"""
        mock_client_instance = MagicMock()
        mock_cohere_client.return_value = mock_client_instance

        result = embed([])

        # Should return empty list
        assert result == []
        # Should not call the embed method
        mock_client_instance.embed.assert_not_called()

    @patch('src.embedder.cohere.Client')
    def test_embed_exception_handling(self, mock_cohere_client):
        """Test that exceptions during embedding are properly handled"""
        # Mock an exception during embedding
        mock_client_instance = MagicMock()
        mock_client_instance.embed.side_effect = Exception("API Error")
        mock_cohere_client.return_value = mock_client_instance

        test_chunks = [
            {"id": "1", "content": "This is a test chunk.", "url": "https://example.com", "title": "Title", "section": "Section", "word_count": 5}
        ]

        # Should raise the exception
        with pytest.raises(Exception, match="API Error"):
            embed(test_chunks)