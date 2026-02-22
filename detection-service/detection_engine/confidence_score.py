class ConfidenceScore:

    @staticmethod
    def calculate(evidence: dict) -> int:
        score = 0

        if evidence["reflection"]:
            score += 30

        if evidence["error_pattern"]:
            score += 20

        if evidence["consistent_anomaly"]:
            score += 10

        return min(score, 100)