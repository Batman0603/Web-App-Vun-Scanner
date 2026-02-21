from payload_engine.payload_loader import PayloadLoader
from payload_engine.context_detector import ContextDetector
from payload_engine.payload_selector import PayloadSelector
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger("Injector")

class Injector:
    def __init__(self):
        self.http = HTTPClient()
        self.loader = PayloadLoader()

    def inject(self, attack_object: dict) -> dict:
        url = attack_object.get("url")
        method = attack_object.get("method", "GET").upper()
        param = attack_object.get("parameter")

        if not url or not param:
            return {"error": "Invalid attack object"}

        marker = "CTX_TEST_123"

        baseline = self.http.send(
            method,
            url,
            params={param: marker} if method == "GET" else None,
            data={param: marker} if method == "POST" else None
        )

        if not baseline:
            return {"error": "Baseline request failed"}

        context = ContextDetector.detect(
            marker,
            baseline.text,
            baseline.headers.get("Content-Type", "")
        )

        payload_type = PayloadSelector.select(context)
        payloads = self.loader.load(payload_type)

        results = []

        for payload in payloads:
            response = self.http.send(
                method,
                url,
                params={param: payload} if method == "GET" else None,
                data={param: payload} if method == "POST" else None
            )

            if response:
                results.append({
                    "payload": payload,
                    "status": response.status_code,
                    "length": len(response.text)
                })

        return {
            "target": url,
            "parameter": param,
            "method": method,
            "context": context,
            "payload_type": payload_type,
            "baseline_length": len(baseline.text),
            "results": results
        }