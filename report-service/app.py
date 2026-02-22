from fastapi import FastAPI, HTTPException

from report_engine.normalizer import Normalizer
from report_engine.owasp_mapper import OWASPMapper
from report_engine.remediation import RemediationEngine
from report_engine.summary_builder import SummaryBuilder
from report_engine.report_builder import ReportBuilder
from renderers.json_renderer import JSONRenderer
from utils.logger import get_logger

# -----------------------------
# App & Logger
# -----------------------------
app = FastAPI(title="Report Service")
logger = get_logger("ReportService")


@app.post("/report")
def generate_report(payload: dict):
    try:
        logger.info("Received report generation request")

        # -----------------------------
        # Step 1 — Input validation
        # -----------------------------
        target = payload["target"]
        vulns = payload["vulnerabilities"]

        # -----------------------------
        # Step 2 — Normalize
        # -----------------------------
        vulns = Normalizer.normalize(vulns)

        # -----------------------------
        # Step 3 — OWASP validation
        # -----------------------------
        OWASPMapper.validate(vulns)

        # -----------------------------
        # Step 4 — Remediation
        # -----------------------------
        vulns = RemediationEngine.add(vulns)

        # -----------------------------
        # Step 5 — Summary
        # -----------------------------
        summary = SummaryBuilder.build(vulns)

        # -----------------------------
        # Step 6 — Report build
        # -----------------------------
        report = ReportBuilder.build(target, vulns)
        report["summary"] = summary

        logger.info(
            "Report generated successfully | target=%s | vulns=%d",
            target,
            len(vulns),
        )

        return JSONRenderer.render(report)

    except KeyError as e:
        logger.error("Missing required field: %s", e)
        raise HTTPException(status_code=422, detail=f"Missing field: {e}")

    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail="Report generation failed")