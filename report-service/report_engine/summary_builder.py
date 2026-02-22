class SummaryBuilder:
    @staticmethod
    def build(vulns: list) -> dict:
        return {
            "total": len(vulns),
            "high": sum(1 for v in vulns if v["severity"] == "High"),
            "medium": sum(1 for v in vulns if v["severity"] == "Medium"),
            "low": sum(1 for v in vulns if v["severity"] == "Low"),
        }