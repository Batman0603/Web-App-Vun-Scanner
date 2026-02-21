from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

def extract_links(html: str, base_url: str) -> Set[str]:
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