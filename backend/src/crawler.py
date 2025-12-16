"""Website crawling and URL discovery module"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import List, Set
import time
from src.logger import crawler_logger


def get_all_urls(base_url: str, sitemap_url: str) -> List[str]:
    """
    Discover and return all accessible URLs from the specified website using the sitemap.

    Args:
        base_url: The base URL of the website to crawl
        sitemap_url: The URL of the sitemap.xml file

    Returns:
        List of all discovered page URLs within the specified domain
    """
    crawler_logger.info(f"Starting URL discovery from sitemap: {sitemap_url}")

    try:
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        crawler_logger.error(f"Failed to fetch sitemap: {e}")
        raise

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        crawler_logger.error(f"Failed to parse sitemap XML: {e}")
        raise

    urls = set()
    # Handle both regular sitemaps and sitemap indexes
    for element in root.iter():
        if element.tag.endswith('loc'):
            url = element.text.strip()
            if is_valid_url_for_domain(url, base_url):
                urls.add(url)

    # Convert to list and return
    url_list = list(urls)
    crawler_logger.info(f"Discovered {len(url_list)} URLs from sitemap")
    return url_list


def is_valid_url_for_domain(url: str, base_url: str) -> bool:
    """
    Check if the URL is within the specified domain.

    Args:
        url: URL to validate
        base_url: Base URL defining the allowed domain

    Returns:
        True if URL is within the domain, False otherwise
    """
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc

    # Check if domains match (including subdomains)
    return url_domain == base_domain or url_domain.endswith('.' + base_domain)


def validate_url_accessibility(url: str) -> bool:
    """
    Validate that a URL is accessible and returns a successful response.

    Args:
        url: URL to validate

    Returns:
        True if URL is accessible, False otherwise
    """
    try:
        response = requests.head(url, timeout=10)
        return response.status_code < 400
    except requests.RequestException:
        return False


def respect_rate_limiting(delay: float = 1.0):
    """
    Implement rate limiting by sleeping for the specified delay.

    Args:
        delay: Delay in seconds between requests
    """
    time.sleep(delay)