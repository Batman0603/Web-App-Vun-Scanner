from bs4 import BeautifulSoup

class ContextDetector:

    @staticmethod
    def detect(marker: str, response_text: str, content_type: str) -> str:
        try:
            ct = (content_type or "").lower()

            if "application/json" in ct and marker in response_text:
                return "json"

            soup = BeautifulSoup(response_text, "lxml")

            if soup.find(string=lambda s: s and marker in s):
                return "html"

            if f'value="{marker}"' in response_text:
                return "attribute"

            if f'"{marker}"' in response_text or f"'{marker}'" in response_text:
                return "js"

            return "unknown"
        except Exception:
            return "unknown"