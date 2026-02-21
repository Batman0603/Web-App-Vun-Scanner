"""
Manages HTTP sessions and requests for the crawler.

This module provides a wrapper around the `requests` library to handle
persistent sessions, timeouts, and error handling for HTTP GET requests.
"""
import requests
from requests.exceptions import RequestException
from utils.logger import get_logger

logger = get_logger("SessionManager")

class SessionManager:
    """
    A wrapper for `requests.Session` to perform HTTP requests.

    This class maintains a persistent session across multiple requests,
    which can improve performance by reusing TCP connections.
    """
    def __init__(self, timeout: int = 5):
        """
        Initializes the SessionManager.

        Args:
            timeout (int): The default timeout in seconds for requests.
        """
        self.session = requests.Session()
        self.timeout = timeout

    def get(self, url: str):
        """
        Performs an HTTP GET request for the given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            requests.Response or None: The response object on success, or None if
                                       a request-related error occurs.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error(f"GET request failed for {url}: {e}")
            return None