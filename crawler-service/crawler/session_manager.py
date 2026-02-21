import requests
from requests.exceptions import RequestException
from utils.logger import get_logger

logger = get_logger("SessionManager")

class SessionManager:
    def __init__(self, timeout: int = 5):
        self.session = requests.Session()
        self.timeout = timeout

    def get(self, url: str):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error(f"GET request failed for {url}: {e}")
            return None