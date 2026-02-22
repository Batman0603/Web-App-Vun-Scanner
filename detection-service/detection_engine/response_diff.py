class ResponseDiff:
    LENGTH_THRESHOLD = 20

    @staticmethod
    def analyze(baseline: dict, results: list) -> dict:
        diffs = []
        base_len = baseline.get("length", 0)
        base_status = baseline.get("status")

        for r in results:
            diffs.append({
                "payload": r.get("payload"),
                "length_delta": abs(r.get("length", 0) - base_len),
                "status_changed": r.get("status") != base_status
            })

        return {
            "baseline_length": base_len,
            "diffs": diffs
        }