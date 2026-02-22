from utils.datetime_utils import now_iso

class ReportBuilder:

    @staticmethod
    def build(target: str, vulns: list) -> dict:
        return {
            "target": target,
            "generated_at": now_iso(),
            "vulnerabilities": vulns,
        }