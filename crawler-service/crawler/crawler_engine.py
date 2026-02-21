from urllib.parse import urljoin
from collections import deque
from utils.logger import get_logger
from crawler.session_manager import SessionManager
from crawler.link_extractor import extract_links
from crawler.form_parser import extract_forms

logger = get_logger("CrawlerEngine")

class CrawlerEngine:

    def __init__(self, base_url: str, max_depth: int = 2):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.session_manager = SessionManager()

    def crawl(self):
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