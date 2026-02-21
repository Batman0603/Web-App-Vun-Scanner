class PayloadSelector:

    CONTEXT_TO_PAYLOAD = {
        "html": "xss",
        "attribute": "xss",
        "js": "xss",
        "json": "sqli",
        "unknown": "sqli"
    }

    @staticmethod
    def select(context: str) -> str:
        return PayloadSelector.CONTEXT_TO_PAYLOAD.get(context, "sqli")