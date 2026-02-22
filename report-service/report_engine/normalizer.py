class Normalizer:
    @staticmethod
    def normalize(vulns: list) -> list:
        normalized = []
        for v in vulns:
            normalized.append({
                "type": v["type"],
                "severity": v["severity"],
                "confidence": v["confidence"],
                "owasp": v["owasp_category"],
                "evidence": v.get("evidence", {})
            })
        return normalized