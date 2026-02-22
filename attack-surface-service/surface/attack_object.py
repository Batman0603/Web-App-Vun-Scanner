from typing import Dict, Any


class AttackObject:
    def __init__(
        self,
        url: str,
        method: str,
        parameter: str,
        context: str,
    ):
        self.url = url
        self.method = method
        self.parameter = parameter
        self.context = context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "method": self.method,
            "parameter": self.parameter,
            "context": self.context,
        }