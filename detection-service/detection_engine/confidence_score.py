class ConfidenceScore:
    """
    Calculates confidence score (0.0 - 1.0)
    """

    @staticmethod
    def calculate(evidence_count: int) -> float:
        if evidence_count == 0:
            return 0.1
        if evidence_count == 1:
            return 0.4
        if evidence_count == 2:
            return 0.7
        return 0.9