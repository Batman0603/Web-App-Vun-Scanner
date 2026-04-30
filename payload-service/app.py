from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

from utils.logger import get_logger
from utils.http_client import send_baseline_request
from payload_engine.payload_loader import PayloadLoader
from payload_engine.injector import Injector
from utils.http_client import send_reflection_probe
from payload_engine.context_detector import ContextDetector
from payload_engine.payload_selector import PayloadSelector

# These modules belong to the detection-service and are not in the payload-service path
# from detection_engine.response_diff import ResponseDiff
# from detection_engine.evidence_engine import EvidenceEngine
# from detection_engine.confidence_score import ConfidenceScore
# from detection_engine.vulnerability_mapper import VulnerabilityMapper

app = FastAPI(title="Payload Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("PayloadService")

REFLECTION_MARKER = "REFLECT_TEST_123"

# ---------------------------
# Initialize Engines (ONCE)
# ---------------------------

loader = PayloadLoader()
injector = Injector()

# ---------------------------
# Request Contract
# ---------------------------

class AttackPoint(BaseModel):
    url: HttpUrl
    method: str
    parameters: List[str]

class BulkInjectRequest(BaseModel):
    total_attack_points: Optional[int] = None
    attack_surface: List[AttackPoint]

class InjectRequest(BaseModel):
    url: HttpUrl
    method: str
    parameter: str
    context: Optional[str] = Field(None, description="Injection context: query, form, or header")


# ---------------------------
# Health Check
# ---------------------------

@app.get("/health")
def health():
    return {"status": "Payload Service Running"}


def run_injection_logic(url: str, method: str, parameter: str, context_override: Optional[str] = None):
    """
    Encapsulates the core injection logic to be reused by both 
    single and bulk injection endpoints.
    """
    method = method.upper().strip()
    if method not in {"GET", "POST"}:
        raise HTTPException(status_code=400, detail=f"Invalid HTTP method: {method}")

    # Infer context if not provided
    if not context_override:
        context = "query" if method == "GET" else "form"
    else:
        context = context_override.lower().strip()

    if context not in {"query", "form", "header"}:
        raise HTTPException(status_code=400, detail=f"Invalid context: {context}")

    parameter = parameter.strip()
    if not parameter:
        raise HTTPException(status_code=400, detail="Parameter name cannot be empty")

    try:
        # ---------------------------
        # STEP 2 — Baseline Request
        # ---------------------------
        baseline = send_baseline_request(
            url=url,
            method=method,
            parameter=parameter,
            context=context,
        )

        logger.info(f"Baseline response length: {baseline.get('length', 0)}")

        # Optimization: If the target doesn't accept the method, don't bother injecting
        if baseline.get("status") in [404, 405]:
            logger.warning(f"Skipping injection for {url} - Baseline returned {baseline.get('status')}")
            return {"target": url, "parameter": parameter, "status": "skipped", "reason": "invalid_baseline"}

        # ---------------------------
        # STEP 3 — Reflection Probe
        # ---------------------------
        is_reflected, content_type, response_snippet = send_reflection_probe(
            url=url,
            method=method,
            parameter=parameter,
            context=context,
            marker=REFLECTION_MARKER,
        )

        detected_context = "unknown"
        if is_reflected:
            detected_context = ContextDetector.detect(
                marker=REFLECTION_MARKER,
                response_text=response_snippet,
                content_type=content_type,
            )

        recommended_payload_type = PayloadSelector.select(detected_context)

        # ---------------------------
        # STEP 4 — Load Payloads
        # ---------------------------
        try:
            payloads = loader.load(recommended_payload_type)
            logger.debug(f"Loaded {len(payloads)} {recommended_payload_type} payloads")
        except Exception as e:
            logger.warning(f"Failed to load payloads for type {recommended_payload_type}: {e}")
            # Fallback or empty list
            payloads = []

        # ---------------------------
        # STEP 5 — Inject Payloads
        # ---------------------------
        try:
            results = injector.inject_all(
                url=url,
                method=method,
                parameter=parameter,
                context=context,
                payloads=payloads,
            )
        except Exception as e:
            logger.error(f"Injection error: {e}")
            results = []

        response_data = {
            "engine_version": "v2",
            "target": url,
            "parameter": parameter,
            "method": method,
            "context": context,

            # STEP 2 — BASELINE EVIDENCE
            "baseline": baseline,

            # STEP 3 — REFLECTION PROBE
            "reflection_probe": {
                "marker": REFLECTION_MARKER,
                "is_reflected": is_reflected,
                "content_type": content_type,
            },

            # STEP 4 — CONTEXT DETECTION
            "reflection_context": {
                "detected": detected_context
            },

            # STEP 5 — PAYLOAD DECISION
            "payload_decision": {
                "detected_context": detected_context,
                "recommended_payload_type": recommended_payload_type,
                "executed_payload_type": recommended_payload_type
            },

            # STEP 6 — INJECTION RESULTS
            "results": results if isinstance(results, list) else []
        }

        logger.info(
            "Evidence collected | baseline_len=%s | payloads=%d",
            baseline.get("length"),
            len(results),
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# ---------------------------
# Injection Endpoints
# ---------------------------

@app.post("/inject")
def inject(request: InjectRequest):
    """
    Endpoint for a single injection point.
    """
    try:
        return run_injection_logic(
            url=str(request.url),
            method=request.method,
            parameter=request.parameter,
            context_override=request.context
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in /inject")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/bulk-inject")
def bulk_inject(request: BulkInjectRequest):
    """
    Processes the full output from the Attack Surface Service.
    """
    logger.info(f"Starting bulk injection for {len(request.attack_surface)} attack points")
    final_results = []

    for point in request.attack_surface:
        for param in point.parameters:
            result = run_injection_logic(
                url=str(point.url),
                method=point.method,
                parameter=param
            )
            final_results.append(result)

    return {
        "total_processed": len(final_results),
        "detailed_results": final_results
    }

# The /analyze logic should be handled by the detection-service on port 8002
# @app.post("/analyze")
# def analyze(payload_response: dict):
#     try:
#         diff = ResponseDiff.analyze(
#             payload_response["baseline"],
#             payload_response["results"]
#         )
#
#         payload_response["response_diff"] = diff
#
#         evidence = EvidenceEngine.extract(payload_response)
#         score = ConfidenceScore.calculate(evidence)
#
#         payload_type = payload_response["payload_decision"]["recommended_payload_type"]
#         vuln = VulnerabilityMapper.map(payload_type, score)
#
#         return {
#             "type": vuln["type"],
#             "confidence": score,
#             "severity": vuln["severity"],
#             "owasp_category": vuln["owasp_category"],
#             "evidence": evidence
#         }
#
#     except KeyError as e:
#         raise HTTPException(422, f"Missing field: {e}")
#
#     except Exception:
#         raise HTTPException(500, "Detection service failure")