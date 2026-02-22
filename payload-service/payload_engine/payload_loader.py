from pathlib import Path
from utils.logger import get_logger

logger = get_logger("PayloadLoader")


class PayloadLoader:
    def __init__(self, base_dir: str = "payloads"):
        self.base_dir = Path(base_dir)

    def load(self, payload_type: str) -> list[str]:
        """
        Load payloads from payloads/<type>.txt
        Returns list of payload strings.
        """

        payload_file = self.base_dir / "dummy" / f"{payload_type}.txt"

        if not payload_file.exists():
            logger.warning(f"Payload file not found: {payload_file}")
            return []

        payloads: list[str] = []

        try:
            with payload_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        payloads.append(line)

            logger.info(
                f"Loaded {len(payloads)} payloads from {payload_file}"
            )
            return payloads

        except Exception as e:
            logger.error(f"Failed loading payloads: {e}")
            return []