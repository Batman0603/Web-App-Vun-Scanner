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