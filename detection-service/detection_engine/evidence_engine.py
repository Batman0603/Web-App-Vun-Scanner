class EvidenceEngine:
    """
    Extracts evidence from response differences.
    """

    @staticmethod
    def extract(diff_result: dict, payload: str) -> list:
        evidence = []

        if diff_result["significant"]:
            evidence.append(
                f"Response length changed significantly using payload '{payload}'"
            )

        return evidence