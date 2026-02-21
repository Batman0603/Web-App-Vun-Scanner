from pathlib import Path
from utils.logger import get_logger

logger = get_logger("PayloadLoader")

class PayloadLoader:
    def __init__(self, mode="dummy"):
        self.base_path = Path("payloads") / mode

    def load(self, payload_type: str) -> list:
        file_path = self.base_path / f"{payload_type}.txt"

        if not file_path.exists():
            logger.warning(f"Payload file missing: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payloads = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

            logger.info(f"Loaded {len(payloads)} payloads from {file_path}")
            return payloads

        except Exception as e:
            logger.error(f"Failed to load payloads: {e}")
            return []