import requests
from requests.exceptions import RequestException
from utils.logger import get_logger

logger = get_logger("HTTPClient")

class HTTPClient:
    def __init__(self, timeout=5):
        self.session = requests.Session()
        self.timeout = timeout

    def send(self, method, url, params=None, data=None):
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                timeout=self.timeout
            )
            return response
        except RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None