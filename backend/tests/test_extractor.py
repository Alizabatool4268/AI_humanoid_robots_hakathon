"""Unit tests for extractor module"""

import pytest
from unittest.mock import patch, MagicMock
from src.extractor import extract_text_from_url, clean_text, build_section_hierarchy


class TestExtractor:
    """Test cases for extractor functionality"""

    def test_clean_text_removes_extra_whitespace(self):
        """Test that extra whitespace is properly removed"""
        raw_text = "  This   is  a   test   text.  "
        expected = "This is a test text."

        result = clean_text(raw_text)
        assert result == expected

    def test_clean_text_handles_empty_string(self):
        """Test that empty strings are handled properly"""
        raw_text = ""
        expected = ""

        result = clean_text(raw_text)
        assert result == expected

    def test_build_section_hierarchy_with_headings(self):
        """Test that section hierarchy is built correctly from headings"""
        content_elements = [
            {'type': 'h1', 'text': 'Main Title', 'level': 1},
            {'type': 'h2', 'text': 'Section 1', 'level': 2},
            {'type': 'h3', 'text': 'Subsection 1.1', 'level': 3},
            {'type': 'h2', 'text': 'Section 2', 'level': 2},
        ]

        hierarchy = build_section_hierarchy(content_elements)

        assert 'Main Title' in hierarchy
        assert 'Main Title > Section 1' in hierarchy
        assert 'Main Title > Section 1 > Subsection 1.1' in hierarchy
        assert 'Main Title > Section 2' in hierarchy

    def test_build_section_hierarchy_empty_input(self):
        """Test that empty input returns empty hierarchy"""
        hierarchy = build_section_hierarchy([])
        assert hierarchy == []

    @patch('src.extractor.requests.get')
    @patch('src.extractor.BeautifulSoup')
    def test_extract_text_from_url_success(self, mock_bs, mock_get):
        """Test successful content extraction from URL"""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"<html><head><title>Test Title</title></head><body><p>Test content.</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_title_tag = MagicMock()
        mock_title_tag.get_text.return_value = "Test Title"
        mock_soup.find.return_value = mock_title_tag

        # Mock content elements
        mock_main_content = MagicMock()
        mock_p = MagicMock()
        mock_p.get_text.return_value = "Test content."
        mock_main_content.find_all.return_value = [mock_p]
        mock_soup.find.return_value = mock_main_content

        mock_bs.return_value = mock_soup

        # Execute the function
        result = extract_text_from_url("https://example.com/test")

        # Verify the results
        assert result["title"] == "Test Title"
        assert "Test content." in result["content"]
        assert isinstance(result["section_hierarchy"], list)

    @patch('src.extractor.requests.get')
    def test_extract_text_from_url_request_exception(self, mock_get):
        """Test that request exceptions are properly handled"""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            extract_text_from_url("https://example.com/test")