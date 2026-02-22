from fastapi import FastAPI, HTTPException
from detection_engine.response_diff import ResponseDiff
from detection_engine.evidence_engine import EvidenceEngine
from detection_engine.confidence_score import ConfidenceScore
from detection_engine.vulnerability_mapper import VulnerabilityMapper
from utils.logger import get_logger

app = FastAPI(title="Detection Service")
logger = get_logger("DetectionService")


@app.post("/detect")
def detect(payload_result: dict):
    try:
        # -----------------------------
        # Step 1 — Input validation
        # -----------------------------
        baseline = payload_result["baseline"]
        results = payload_result["results"]
        reflection = payload_result["reflection_probe"]["is_reflected"]
        payload_type = payload_result["payload_decision"]["recommended_payload_type"]

        if not isinstance(results, list) or not results:
            raise HTTPException(422, "Results must be a non-empty list")
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
            "type": vuln["type"],
            "severity": vuln["severity"],
            "confidence": confidence,
            "owasp_category": vuln["owasp_category"],
            "evidence": evidence
        }

    except KeyError as e:
        logger.error(f"Missing field: {e}")
        raise HTTPException(422, f"Missing field: {e}")

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Detection engine failure")
        raise HTTPException(500, "Detection service failure")