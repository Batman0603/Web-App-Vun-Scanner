"""
Core crawling logic for discovering web pages and forms.

This module contains the main engine that performs a breadth-first search (BFS)
on a target website to map its structure.
"""
from urllib.parse import urljoin
from collections import deque
from utils.logger import get_logger
from crawler.session_manager import SessionManager
from crawler.link_extractor import extract_links
from crawler.form_parser import extract_forms

logger = get_logger("CrawlerEngine")

class CrawlerEngine:
    """
    Manages the crawling process for a given base URL.

    It uses a breadth-first search (BFS) algorithm to discover pages
    within the same domain, up to a specified maximum depth. For each
    page, it extracts links and forms.
    """

    def __init__(self, base_url: str, max_depth: int = 2):
        """
        Initializes the CrawlerEngine.

        Args:
            base_url (str): The starting URL for the crawl.
            max_depth (int): The maximum depth to crawl from the base URL.
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.session_manager = SessionManager()

    def crawl(self):
        """
        Executes the crawling process.

        Returns:
            list: A list of dictionaries, where each dictionary contains the
                  'url' and a list of 'forms' found on that page.
        """
        queue = deque([(self.base_url, 0)])
        results = []

        while queue:
            current_url, depth = queue.popleft()

            if depth > self.max_depth:
                continue

            if current_url in self.visited:
                continue

            logger.info(f"Crawling: {current_url}")
            self.visited.add(current_url)

            response = self.session_manager.get(current_url)
            if response is None:
                continue

            try:
                links = extract_links(response.text, self.base_url)
                forms = extract_forms(response.text)

                results.append({
                    "url": current_url,
                    "forms": forms
                })

                for link in links:
                    if link not in self.visited:
                        queue.append((link, depth + 1))

            except Exception as e:
                logger.error(f"Parsing error at {current_url}: {e}")
                continue

        return results