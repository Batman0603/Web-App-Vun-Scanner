from utils.logger import get_logger
from utils.http_client import send_injected_request

logger = get_logger("Injector")


class Injector:
    def inject_all(
        self,
        url: str,
        method: str,
        parameter: str,
        context: str,
        payloads: list[str],
    ) -> list[dict]:

        results = []

        for payload in payloads:
            logger.info(f"Injecting payload: {payload}")

            status, length = send_injected_request(
                url=url,
                method=method,
                parameter=parameter,
                context=context,
                payload=payload,
            )

            results.append({
                "payload": payload,
                "status": status,
                "length": length
            })

        return results