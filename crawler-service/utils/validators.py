from urllib.parse import urlparse


class ValidationError(Exception):
    pass


def validate_url(url: str) -> str:
    """
    Validate target URL format.
    Raises ValidationError if invalid.
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        raise ValidationError("Invalid URL format")

    if parsed.scheme not in ["http", "https"]:
        raise ValidationError("Only HTTP/HTTPS allowed")

    return url


def validate_depth(depth: int, max_limit: int = 5) -> int:
    """
    Validate crawling depth.
    """
    if depth < 0:
        raise ValidationError("Depth cannot be negative")

    if depth > max_limit:
        raise ValidationError(f"Depth cannot exceed {max_limit}")

    return depth


def validate_url(url: str) -> str:
    if not url:
        raise ValidationError("URL cannot be empty.")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValidationError(f"Invalid URL scheme '{parsed.scheme}'. Must be http or https.")

    if not parsed.netloc:
        raise ValidationError(f"Invalid URL: '{url}'. No domain found.")

    return url.strip()


def validate_depth(depth: int) -> int:
    if not isinstance(depth, int):
        raise ValidationError("Depth must be an integer.")

    if depth < 1:
        raise ValidationError("Depth must be at least 1.")

    if depth > 10:
        raise ValidationError("Depth cannot exceed 10 to prevent excessive crawling.")

    return depth