"""Unit tests for crawler module"""

import pytest
from unittest.mock import patch, MagicMock
from src.crawler import get_all_urls, is_valid_url_for_domain


class TestCrawler:
    """Test cases for crawler functionality"""

    def test_is_valid_url_for_domain_same_domain(self):
        """Test that URLs in the same domain are validated correctly"""
        base_url = "https://example.com"
        test_url = "https://example.com/page1"

        result = is_valid_url_for_domain(test_url, base_url)
        assert result is True

    def test_is_valid_url_for_domain_subdomain(self):
        """Test that URLs in subdomains are validated correctly"""
        base_url = "https://example.com"
        test_url = "https://blog.example.com/page1"

        result = is_valid_url_for_domain(test_url, base_url)
        assert result is True

    def test_is_valid_url_for_domain_different_domain(self):
        """Test that URLs in different domains are rejected"""
        base_url = "https://example.com"
        test_url = "https://otherdomain.com/page1"

        result = is_valid_url_for_domain(test_url, base_url)
        assert result is False

    @patch('src.crawler.requests.get')
    @patch('src.crawler.ET.fromstring')
    def test_get_all_urls_success(self, mock_fromstring, mock_get):
        """Test successful URL discovery from sitemap"""
        # Mock sitemap content
        mock_response = MagicMock()
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://ai-humanoid-robots-hakathon.vercel.app/page1</loc>
            </url>
            <url>
                <loc>https://ai-humanoid-robots-hakathon.vercel.app/page2</loc>
            </url>
        </urlset>'''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock XML parsing
        mock_root = MagicMock()
        mock_loc1 = MagicMock()
        mock_loc1.text = "https://ai-humanoid-robots-hakathon.vercel.app/page1"
        mock_loc2 = MagicMock()
        mock_loc2.text = "https://ai-humanoid-robots-hakathon.vercel.app/page2"
        mock_root.iter.return_value = [MagicMock(tag="{http://www.sitemaps.org/schemas/sitemap/0.9}loc", text=""),
                                       mock_loc1,
                                       MagicMock(tag="{http://www.sitemaps.org/schemas/sitemap/0.9}loc", text=""),
                                       mock_loc2]
        mock_fromstring.return_value = mock_root

        # Execute the function
        urls = get_all_urls(
            "https://ai-humanoid-robots-hakathon.vercel.app",
            "https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
        )

        # Verify the results
        assert len(urls) == 2
        assert "https://ai-humanoid-robots-hakathon.vercel.app/page1" in urls
        assert "https://ai-humanoid-robots-hakathon.vercel.app/page2" in urls

    @patch('src.crawler.requests.get')
    def test_get_all_urls_request_exception(self, mock_get):
        """Test that request exceptions are properly handled"""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            get_all_urls(
                "https://ai-humanoid-robots-hakathon.vercel.app",
                "https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
            )