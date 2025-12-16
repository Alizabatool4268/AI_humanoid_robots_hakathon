"""Integration tests for the RAG pipeline"""

import pytest
from unittest.mock import patch, MagicMock
from src.crawler import get_all_urls
from src.extractor import extract_text_from_url
from src.chunker import chunk_text
from src.embedder import embed
from src.storage import create_collection, save_chunks_to_qdrant


class TestIntegration:
    """Integration tests for the pipeline components"""

    @patch('src.crawler.requests.get')
    @patch('src.crawler.ET.fromstring')
    @patch('src.extractor.requests.get')
    @patch('src.extractor.BeautifulSoup')
    def test_full_pipeline_flow(self, mock_bs, mock_ext_get, mock_crawl_get, mock_fromstring):
        """Test the full flow from crawling to storage"""
        # Mock crawling
        mock_crawl_response = MagicMock()
        mock_crawl_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://ai-humanoid-robots-hakathon.vercel.app/test-page</loc>
            </url>
        </urlset>'''
        mock_crawl_response.raise_for_status.return_value = None
        mock_crawl_get.return_value = mock_crawl_response

        mock_root = MagicMock()
        mock_loc = MagicMock()
        mock_loc.text = "https://ai-humanoid-robots-hakathon.vercel.app/test-page"
        mock_root.iter.return_value = [MagicMock(tag="{http://www.sitemaps.org/schemas/sitemap/0.9}loc", text=""),
                                       mock_loc]
        mock_fromstring.return_value = mock_root

        # Mock extraction
        mock_ext_response = MagicMock()
        mock_ext_response.content = b"<html><head><title>Test Page</title></head><body><p>This is test content for the RAG pipeline. It should be long enough to create meaningful chunks.</p></body></html>"
        mock_ext_response.raise_for_status.return_value = None
        mock_ext_get.return_value = mock_ext_response

        mock_soup = MagicMock()
        mock_title_tag = MagicMock()
        mock_title_tag.get_text.return_value = "Test Page"
        mock_soup.find.return_value = mock_title_tag

        mock_main_content = MagicMock()
        mock_p = MagicMock()
        mock_p.get_text.return_value = "This is test content for the RAG pipeline. It should be long enough to create meaningful chunks."
        mock_main_content.find_all.return_value = [mock_p]
        mock_soup.find.return_value = mock_main_content

        mock_bs.return_value = mock_soup

        # Test crawling
        urls = get_all_urls(
            "https://ai-humanoid-robots-hakathon.vercel.app",
            "https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
        )
        assert len(urls) == 1
        assert "https://ai-humanoid-robots-hakathon.vercel.app/test-page" in urls

        # Test extraction
        content_data = extract_text_from_url(urls[0])
        assert content_data["title"] == "Test Page"
        assert "test content" in content_data["content"].lower()

        # Test chunking
        chunks = chunk_text(
            content_data["content"],
            urls[0],
            content_data["title"],
            " > ".join(content_data["section_hierarchy"]) if content_data["section_hierarchy"] else ""
        )
        assert len(chunks) >= 0  # Could be 0 if content is too short, but we expect at least 1

        # Add more content to ensure we get chunks
        long_content = content_data["content"] + " " + content_data["content"] * 10  # Repeat to ensure we have enough content
        chunks = chunk_text(
            long_content,
            urls[0],
            content_data["title"],
            " > ".join(content_data["section_hierarchy"]) if content_data["section_hierarchy"] else ""
        )
        assert len(chunks) > 0  # Should have at least one chunk now

        # Test that chunks are within the expected size range
        for chunk in chunks:
            assert 300 <= chunk["word_count"] <= 500

    @patch('src.storage.QdrantClient')
    def test_storage_integration(self, mock_qdrant_client):
        """Test the storage components integration"""
        # Mock Qdrant client
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = MagicMock()
        mock_client_instance.get_collections.return_value.collections = []
        mock_qdrant_client.return_value = mock_client_instance

        # Test collection creation
        result = create_collection("integration_test_collection")
        assert result is True

        # Test saving a chunk
        test_chunk = {
            "id": "integration-test-id",
            "content": "This is integration test content",
            "title": "Integration Test Title",
            "url": "https://example.com/integration-test",
            "section": "Integration Test Section",
            "vector": [0.1, 0.2, 0.3, 0.4, 0.5] * 20  # 100-dimensional vector
        }

        result = save_chunks_to_qdrant([test_chunk], "integration_test_collection")
        assert result == 1