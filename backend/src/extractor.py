"""Content extraction from HTML module"""

import requests
from bs4 import BeautifulSoup, Comment
from typing import Dict, List, Any
import re
from src.logger import extractor_logger


def extract_text_from_url(url: str) -> Dict[str, Any]:
    """
    Extract meaningful content from a single webpage URL.

    Args:
        url: The URL of the webpage to extract content from

    Returns:
        Dictionary with title, content, and section_hierarchy
    """
    extractor_logger.info(f"Extracting content from: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        extractor_logger.error(f"Failed to fetch URL {url}: {e}")
        raise

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract page title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "No Title"

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
        script.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Find main content areas (prioritize main content over sidebars)
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article')) or soup

    # Extract headings, paragraphs, and lists
    content_elements = []

    # Extract headings (h1-h6) with their hierarchy
    headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for heading in headings:
        content_elements.append({
            'type': heading.name,
            'text': clean_text(heading.get_text()),
            'level': int(heading.name[1])  # Extract number from h1, h2, etc.
        })

    # Extract paragraphs
    paragraphs = main_content.find_all('p')
    for p in paragraphs:
        text = clean_text(p.get_text())
        if text:  # Only add non-empty paragraphs
            content_elements.append({
                'type': 'p',
                'text': text,
                'level': None
            })

    # Extract list items
    list_items = main_content.find_all(['li'])
    for li in list_items:
        text = clean_text(li.get_text())
        if text:  # Only add non-empty list items
            content_elements.append({
                'type': 'li',
                'text': text,
                'level': None
            })

    # Combine all content into a single string
    content_parts = []
    for element in content_elements:
        content_parts.append(element['text'])

    full_content = ' '.join(content_parts)

    # Build section hierarchy based on headings
    section_hierarchy = build_section_hierarchy(content_elements)

    result = {
        "title": title,
        "content": full_content,
        "section_hierarchy": section_hierarchy
    }

    extractor_logger.info(f"Successfully extracted content from {url} with {len(full_content)} characters")
    return result


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and normalizing.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def build_section_hierarchy(content_elements: List[Dict]) -> List[str]:
    """
    Build a section hierarchy based on headings in the content.

    Args:
        content_elements: List of content elements with type and text

    Returns:
        List of section titles representing the hierarchy
    """
    hierarchy = []
    current_path = []

    for element in content_elements:
        if element['type'] in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = element['level']
            text = element['text']

            # Adjust current path based on heading level
            if level == 1:
                current_path = [text]
            elif level == 2:
                current_path = current_path[:1] + [text]
            elif level == 3:
                current_path = current_path[:2] + [text]
            elif level == 4:
                current_path = current_path[:3] + [text]
            elif level == 5:
                current_path = current_path[:4] + [text]
            elif level == 6:
                current_path = current_path[:5] + [text]

            # Update hierarchy with current path
            if current_path not in hierarchy:
                hierarchy.append(' > '.join(current_path))

    return hierarchy