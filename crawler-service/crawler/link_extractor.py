"""
Extracts hyperlinks from HTML content.

This module uses BeautifulSoup to parse HTML and find all `<a>` tags,
extracting their `href` attributes. It handles relative URLs, filters
for links within the same domain, and cleans URL fragments.
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

def extract_links(html: str, base_url: str) -> Set[str]:
    """
    Parses HTML to find and return all unique, in-domain links.

    Args:
        html (str): The HTML content of the page as a string.
        base_url (str): The base URL of the page, used to resolve relative links
                        and filter by domain.

    Returns:
        Set[str]: A set of unique, absolute URLs found within the HTML that
                  belong to the same domain as the base_url.
    """
    soup = BeautifulSoup(html, "lxml")
    links = set()
    base_domain = urlparse(base_url).netloc

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only crawl same domain and http/https
        if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
            clean_url = parsed._replace(fragment="").geturl()
            links.add(clean_url)

    return links