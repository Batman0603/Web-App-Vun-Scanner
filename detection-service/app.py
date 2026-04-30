from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Union, Dict
from detection_engine.response_diff import ResponseDiff
from detection_engine.evidence_engine import EvidenceEngine
from detection_engine.confidence_score import ConfidenceScore
from detection_engine.vulnerability_mapper import VulnerabilityMapper
from utils.logger import get_logger

app = FastAPI(title="Detection Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("DetectionService")

@app.get("/health", summary="Health Check")
def health():
    """Check if the Detection Service is reachable."""
    return {"status": "Detection Service Running"}

def run_detection_logic(payload_result: dict):
    """Internal logic to analyze a single injection result."""
    try:
        # Handle 'skipped' results from Payload Service
        if payload_result.get("status") == "skipped":
            return None

        baseline = payload_result.get("baseline")
        results = payload_result.get("results")
        reflection = payload_result.get("reflection_probe", {}).get("is_reflected", False)
        payload_type = payload_result.get("payload_decision", {}).get("recommended_payload_type", "unknown")

        if not baseline or not isinstance(results, list) or not results:
            return None

        # -----------------------------
        # Step 2–4 — Diff analysis
        # -----------------------------
        response_diff = ResponseDiff.analyze(
            baseline=baseline,
            results=results
        )


        # -----------------------------
        # Step 5–6 — Evidence extraction
        # -----------------------------
        payload_result["response_diff"] = response_diff

        evidence = EvidenceEngine.extract(payload_result)

        # -----------------------------
        # Step 7 — Confidence scoring
        # -----------------------------
        confidence = ConfidenceScore.calculate(evidence)

        # -----------------------------
        # Step 8 — Vulnerability mapping
        # -----------------------------
        vuln = VulnerabilityMapper.map(payload_type, confidence)

        return {
            "target": payload_result.get("target"),
            "parameter": payload_result.get("parameter"),
            "type": vuln["type"],
            "severity": vuln["severity"],
            "confidence": confidence,
            "owasp_category": vuln["owasp_category"],
            "evidence": evidence
        }
    except Exception as e:
        logger.error(f"Detection logic failed for a single result: {e}")
        return None


@app.post("/detect")
def detect(payload_result: Union[Dict, List] = Body(...), debug: bool = False):
    """
    Endpoint to analyze injection results. 
    Handles both single results and the bulk 'detailed_results' structure.
    """
    try:
        # Normalize input: Extract 'detailed_results' if present, or wrap single dict in list
        if isinstance(payload_result, dict) and "detailed_results" in payload_result:
            data_to_process = payload_result["detailed_results"]
        elif isinstance(payload_result, dict):
            data_to_process = [payload_result]
        else:
            data_to_process = payload_result

        all_findings = []
        for item in data_to_process:
            finding = run_detection_logic(item)
            if finding:
                all_findings.append(finding)

        # Filter for actual vulnerabilities (where confidence > 0)
        vulnerabilities = [f for f in all_findings if debug or f.get("confidence", 0) > 0]

        targets = [item.get("target") for item in data_to_process if item.get("target")]
        unique_targets = list(dict.fromkeys(targets))

        response = {
            "total_scanned": len(data_to_process),
            "vulnerabilities_found": len(vulnerabilities),
            "findings": vulnerabilities
        }

        if len(unique_targets) == 1:
            response["target"] = unique_targets[0]
        elif len(unique_targets) > 1:
            response["targets"] = unique_targets

        return response

    except KeyError as e:
        logger.error(f"Missing field: {e}")
        raise HTTPException(422, f"Missing field: {e}")

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Detection engine failure")
        raise HTTPException(500, "Detection service failure")