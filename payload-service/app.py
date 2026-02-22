from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from utils.logger import get_logger
from utils.http_client import send_baseline_request
from payload_engine.payload_loader import PayloadLoader
from payload_engine.injector import Injector
from utils.http_client import send_reflection_probe
from payload_engine.context_detector import ContextDetector
from payload_engine.payload_selector import PayloadSelector

app = FastAPI(title="Payload Service")
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

class InjectRequest(BaseModel):
    url: HttpUrl
    method: str
    parameter: str
    context: str


# ---------------------------
# Health Check
# ---------------------------

@app.get("/health")
def health():
    return {"status": "Payload Service Running"}


# ---------------------------
# Injection Endpoint
# ---------------------------

@app.post("/inject")
def inject(request: InjectRequest):
    try:
        method = request.method.upper().strip()

        if method not in {"GET", "POST"}:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid HTTP method: {request.method}"
            )

        context = request.context.lower().strip()
        if context not in {"query", "form", "header"}:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid context: {request.context}"
            )

        parameter = request.parameter.strip()
        if not parameter:
            raise HTTPException(
                status_code=400,
                detail="Parameter name cannot be empty"
            )

        logger.info(
            f"Validated inject request | url={request.url} "
            f"| method={method} | param={parameter} | context={context}"
        )

        # ---------------------------
        # STEP 2 — Baseline Request
        # ---------------------------
        try:
            baseline = send_baseline_request(
                url=str(request.url),
                method=method,
                parameter=parameter,
                context=context,
            )
        except RuntimeError as e:
            logger.error(f"Baseline failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Baseline request failed: {str(e)}"
            )


        logger.info(f"Baseline response length: {baseline.get('length', 0)}")

        # ---------------------------
        # STEP 3 — Reflection Probe
        # ---------------------------
        is_reflected, content_type, response_snippet = send_reflection_probe(
            url=str(request.url),
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
        payloads = loader.load("sqli")
        logger.info(f"Loaded {len(payloads)} SQLi payloads")

        # ---------------------------
        # STEP 5 — Inject Payloads
        # ---------------------------
        try:
            results = injector.inject_all(
                url=str(request.url),
                method=method,
                parameter=parameter,
                context=context,
                payloads=payloads,
            )
        except Exception as e:
            logger.error(f"Injection error: {e}")
            results = []

        # ---------------------------
        # Final Response
        # ---------------------------
        response = {
            "engine_version": "v2",
            "target": request.url,
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

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/analyze")
def analyze(payload_response: dict):
    try:
        diff = ResponseDiff.analyze(
            payload_response["baseline"],
            payload_response["results"]
        )

        payload_response["response_diff"] = diff

        evidence = EvidenceEngine.extract(payload_response)
        score = ConfidenceScore.calculate(evidence)

        payload_type = payload_response["payload_decision"]["recommended_payload_type"]
        vuln = VulnerabilityMapper.map(payload_type, score)

        return {
            "type": vuln["type"],
            "confidence": score,
            "severity": vuln["severity"],
            "owasp_category": vuln["owasp_category"],
            "evidence": evidence
        }

    except KeyError as e:
        raise HTTPException(422, f"Missing field: {e}")

    except Exception:
        raise HTTPException(500, "Detection service failure")