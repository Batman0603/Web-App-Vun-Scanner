from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from report_engine.normalizer import Normalizer
from report_engine.owasp_mapper import OWASPMapper
from report_engine.remediation import RemediationEngine
from report_engine.summary_builder import SummaryBuilder
from report_engine.report_builder import ReportBuilder
from renderers.json_renderer import JSONRenderer
from renderers.html_renderer import HTMLRenderer
from renderers.pdf_renderer import PDFRenderer
from utils.logger import get_logger

# -----------------------------
# App & Logger
# -----------------------------
app = FastAPI(title="Report Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = get_logger("ReportService")

class ReportRequest(BaseModel):
    target: Optional[str] = Field(None, example="https://example.com")
    targets: Optional[List[str]] = None
    format: Optional[str] = Field("json", example="pdf")
    vulnerabilities: Optional[List[Dict[str, Any]]] = None
    findings: Optional[List[Dict[str, Any]]] = None

@app.post("/report")
def generate_report(payload: ReportRequest):
    try:
        logger.info("Received report generation request")

        # Handle both 'vulnerabilities' and 'findings' (from detection-service)
        if payload.vulnerabilities is None and payload.findings is None:
            raise HTTPException(status_code=400, detail="No vulnerabilities or findings payload provided.")

        vulns = payload.vulnerabilities if payload.vulnerabilities is not None else payload.findings
        if vulns is None:
            vulns = []

        chosen_target = payload.target
        if not chosen_target and payload.targets:
            chosen_target = payload.targets[0]
        if not chosen_target and len(vulns):
            chosen_target = vulns[0].get("target")
        target = chosen_target or "Unknown Target"

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
            "Report generated successfully | target=%s | vulns=%d | format=%s",
            target,
            len(vulns),
            payload.format,
        )

        output_format = (payload.format or "json").lower()
        if output_format == "pdf":
            html_report = HTMLRenderer.render(report)
            pdf_bytes = PDFRenderer.render(html_report)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=report.pdf"},
            )

        if output_format != "json":
            raise HTTPException(status_code=400, detail="Invalid format. Supported formats: json, pdf.")

        return JSONRenderer.render(report)

    except KeyError as e:
        logger.error("Missing required field: %s", e)
        raise HTTPException(status_code=422, detail=f"Missing field: {e}")

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail="Report generation failed")