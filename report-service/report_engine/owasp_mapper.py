class OWASPMapper:
    @staticmethod
    def validate(vulns: list) -> None:
        for v in vulns:
            if not v["owasp"].startswith("A"):
                raise ValueError("Invalid OWASP category")