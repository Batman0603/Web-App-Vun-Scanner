class ResponseDiff:
    """
    Compares baseline response with injected responses.
    """

    @staticmethod
    def diff(baseline_length: int, injected_length: int) -> dict:
        delta = injected_length - baseline_length

        return {
            "length_delta": delta,
            "significant": abs(delta) > 20  # threshold
        }