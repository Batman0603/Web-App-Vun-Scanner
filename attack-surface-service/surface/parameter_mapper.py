from typing import List, Dict
from urllib.parse import urlparse, parse_qs
from utils.logger import get_logger

logger = get_logger("ParameterMapper")


class ParameterMapper:

    @staticmethod
    def extract_from_url(url: str) -> List[str]:
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            return list(query_params.keys())
        except Exception as e:
            logger.error(f"Failed extracting query params: {e}")
            return []

    @staticmethod
    def extract_from_forms(forms: List[Dict]) -> List[str]:
        params = []
        try:
            for form in forms:
                inputs = form.get("inputs", [])
                for inp in inputs:
                    if isinstance(inp, str):
                        params.append(inp)
                    elif isinstance(inp, dict) and "name" in inp:
                        params.append(inp["name"])
            return params
        except Exception as e:
            logger.error(f"Failed extracting form params: {e}")
            return []