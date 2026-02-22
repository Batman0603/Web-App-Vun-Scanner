import requests
from utils.logger import get_logger

logger = get_logger("HttpClient")

DEFAULT_TIMEOUT = 10  # seconds


def send_baseline_request(
    url: str,
    method: str,
    parameter: str,
    context: str,
):
    """
    Sends a baseline HTTP request.
    Returns baseline evidence dict.
    """

    try:
        safe_value = "baseline"
        params = None
        data = None
        headers = {}

        if context == "query":
            params = {parameter: safe_value}
        elif context == "form":
            data = {parameter: safe_value}
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif context == "header":
            headers[parameter] = safe_value

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
        )

        body = response.text or ""
        snippet = body[:2000]

        return {
            "status": response.status_code,
            "length": len(body),
            "content_type": response.headers.get("Content-Type", ""),
            "snippet": snippet,
        }

    except requests.exceptions.Timeout:
        raise RuntimeError("Baseline request timed out")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Baseline request error: {str(e)}")

def send_injected_request(
    url: str,
    method: str,
    parameter: str,
    context: str,
    payload: str,
):
    """
    Sends HTTP request with injected payload.
    Returns (status_code, response_length).
    """

    try:
        params = None
        data = None
        headers = {}

        if context == "query":
            params = {parameter: payload}

        elif context == "form":
            data = {parameter: payload}
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        elif context == "header":
            headers[parameter] = payload

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
        )

        return response.status_code, len(response.text or "")

    except requests.exceptions.Timeout:
        return 0, 0

    except requests.exceptions.RequestException:
        return 0, 0

def send_reflection_probe(
    url: str,
    method: str,
    parameter: str,
    context: str,
    marker: str,
):
    """
    Sends a harmless reflection probe.
    Returns (is_reflected, content_type, response_snippet)
    """

    try:
        params = None
        data = None
        headers = {}

        if context == "query":
            params = {parameter: marker}

        elif context == "form":
            data = {parameter: marker}
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        elif context == "header":
            headers[parameter] = marker

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
        )

        content_type = response.headers.get("Content-Type", "")
        body = response.text or ""

        # limit body size (safety)
        snippet = body[:2000]

        is_reflected = marker in body

        return is_reflected, content_type, snippet

    except requests.exceptions.RequestException:
        return False, "", ""