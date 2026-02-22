import re

SQL_ERROR_PATTERNS = [
    r"sql syntax",
    r"mysql",
    r"syntax error",
    r"unclosed quotation",
    r"odbc",
]

class EvidenceEngine:

    @staticmethod
    def extract(payload_result: dict) -> dict:
        evidence = {
            "reflection": False,
            "error_pattern": False,
            "consistent_anomaly": False,
        }

        # -----------------------------
        # Reflection evidence
        # -----------------------------
        evidence["reflection"] = (
            payload_result
            .get("reflection_probe", {})
            .get("is_reflected", False)
        )

        # -----------------------------
        # Error pattern detection
        # -----------------------------
        snippet = (
            payload_result
            .get("baseline", {})
            .get("snippet", "")
            .lower()
        )

        for pattern in SQL_ERROR_PATTERNS:
            if re.search(pattern, snippet):
                evidence["error_pattern"] = True
                break

        # -----------------------------
        # Consistency / anomaly analysis
        # -----------------------------
        diffs = (
            payload_result
            .get("response_diff", {})
            .get("diffs", [])
        )

        anomaly_count = sum(
            1 for d in diffs
            if d.get("length_delta", 0) > 20 or d.get("status_changed")
        )

        evidence["consistent_anomaly"] = anomaly_count >= 2

        return evidence