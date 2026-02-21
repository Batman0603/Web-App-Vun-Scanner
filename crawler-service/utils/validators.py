"""
Provides validation functions for crawler inputs like URL and depth.
"""
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_url(url: str) -> str:
    """
    Validates that a string is a well-formed HTTP/HTTPS URL.

    Checks for presence, a valid scheme (http or https), and a network location
    (domain). Strips leading/trailing whitespace.

    Args:
        url (str): The URL string to validate.

    Raises:
        ValidationError: If the URL is empty, malformed, or has an unsupported scheme.

    Returns:
        str: The validated and stripped URL.
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    url = url.strip()
    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"Invalid URL format: '{url}'")

    if parsed.scheme not in ["http", "https"]:
        raise ValidationError(f"Invalid URL scheme '{parsed.scheme}'. Must be http or https.")

    return url


def validate_depth(depth: int, max_limit: int = 5) -> int:
    """
    Validates the crawl depth.

    Checks that the depth is a non-negative integer and does not exceed a
    maximum limit.

    Args:
        depth (int): The crawl depth to validate.
        max_limit (int): The maximum allowed depth.

    Raises:
        ValidationError: If depth is not an integer, is negative, or exceeds the limit.

    Returns:
        int: The validated depth.
    """
    if not isinstance(depth, int):
        raise ValidationError("Depth must be an integer.")

    if depth < 0:
        raise ValidationError("Depth cannot be negative")

    if depth > max_limit:
        raise ValidationError(f"Depth cannot exceed the maximum limit of {max_limit}")

    return depth