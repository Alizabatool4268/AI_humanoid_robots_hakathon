"""Unit tests for storage module"""

import pytest
from unittest.mock import patch, MagicMock
from src.storage import create_collection, save_chunk_to_qdrant, save_chunks_to_qdrant


class TestStorage:
    """Test cases for storage functionality"""

    @patch('src.storage.QdrantClient')
    def test_create_collection_new(self, mock_qdrant_client):
        """Test creating a new collection"""
        # Mock Qdrant client
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = MagicMock()
        mock_client_instance.get_collections.return_value.collections = []
        mock_qdrant_client.return_value = mock_client_instance

        result = create_collection("test_collection")

        assert result is True
        mock_client_instance.create_collection.assert_called_once()
        call_args = mock_client_instance.create_collection.call_args
        assert call_args[0][0] == "test_collection"

    @patch('src.storage.QdrantClient')
    def test_create_collection_exists(self, mock_qdrant_client):
        """Test creating a collection that already exists"""
        # Mock Qdrant client
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = MagicMock()
        mock_client_instance.get_collections.return_value.collections = [mock_collection]
        mock_qdrant_client.return_value = mock_client_instance

        result = create_collection("test_collection")

        assert result is True
        # create_collection should not be called if collection already exists
        mock_client_instance.create_collection.assert_not_called()

    @patch('src.storage.QdrantClient')
    def test_save_chunk_to_qdrant_success(self, mock_qdrant_client):
        """Test successfully saving a chunk to Qdrant"""
        # Mock Qdrant client
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Create a test chunk
        test_chunk = {
            "id": "test-id",
            "content": "This is test content",
            "title": "Test Title",
            "url": "https://example.com",
            "section": "Test Section",
            "vector": [0.1, 0.2, 0.3]
        }

        result = save_chunk_to_qdrant(test_chunk, "test_collection")

        assert result is True
        mock_client_instance.upsert.assert_called_once()
        call_args = mock_client_instance.upsert.call_args
        assert call_args[1]["collection_name"] == "test_collection"
        points = call_args[1]["points"]
        assert len(points) == 1
        assert points[0].id == "test-id"
        assert points[0].vector == [0.1, 0.2, 0.3]
        assert points[0].payload["text"] == "This is test content"

    @patch('src.storage.QdrantClient')
    def test_save_chunk_to_qdrant_exception(self, mock_qdrant_client):
        """Test exception handling when saving a chunk to Qdrant"""
        # Mock Qdrant client to raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.upsert.side_effect = Exception("Connection Error")
        mock_qdrant_client.return_value = mock_client_instance

        # Create a test chunk
        test_chunk = {
            "id": "test-id",
            "content": "This is test content",
            "title": "Test Title",
            "url": "https://example.com",
            "section": "Test Section",
            "vector": [0.1, 0.2, 0.3]
        }

        result = save_chunk_to_qdrant(test_chunk, "test_collection")

        assert result is False

    @patch('src.storage.QdrantClient')
    def test_save_chunks_to_qdrant_success(self, mock_qdrant_client):
        """Test successfully saving multiple chunks to Qdrant"""
        # Mock Qdrant client
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Create test chunks
        test_chunks = [
            {
                "id": "test-id-1",
                "content": "This is test content 1",
                "title": "Test Title 1",
                "url": "https://example.com/1",
                "section": "Test Section 1",
                "vector": [0.1, 0.2, 0.3]
            },
            {
                "id": "test-id-2",
                "content": "This is test content 2",
                "title": "Test Title 2",
                "url": "https://example.com/2",
                "section": "Test Section 2",
                "vector": [0.4, 0.5, 0.6]
            }
        ]

        result = save_chunks_to_qdrant(test_chunks, "test_collection")

        assert result == 2  # Should return the number of successfully saved chunks
        mock_client_instance.upsert.assert_called_once()
        call_args = mock_client_instance.upsert.call_args
        assert call_args[1]["collection_name"] == "test_collection"
        points = call_args[1]["points"]
        assert len(points) == 2
        assert points[0].id == "test-id-1"
        assert points[1].id == "test-id-2"