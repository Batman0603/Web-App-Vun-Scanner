REMEDIATION_GUIDE = {
    "SQL Injection": [
        "Use prepared statements",
        "Apply server-side input validation",
        "Use ORM parameter binding",
    ],
    "Cross-Site Scripting": [
        "Escape user input",
        "Apply Content Security Policy (CSP)",
    ],
}

class RemediationEngine:
    @staticmethod
    def add(vulns: list) -> list:
        for v in vulns:
            v["remediation"] = REMEDIATION_GUIDE.get(
                v["type"], ["General security hardening"]
            )
        return vulns