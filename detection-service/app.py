from fastapi import FastAPI
from detection_engine.response_diff import ResponseDiff
from detection_engine.evidence_engine import EvidenceEngine
from detection_engine.confidence_score import ConfidenceScore
from detection_engine.vulnerability_mapper import VulnerabilityMapper
from utils.logger import get_logger

app = FastAPI(title="Detection Service")
logger = get_logger("DetectionService")


@app.post("/detect")
def detect(payload_result: dict):
    baseline_length = payload_result.get("baseline_length")
    payload_type = payload_result.get("payload_type")
    results = payload_result.get("results", [])

    evidence = []

    for result in results:
        diff = ResponseDiff.diff(
            baseline_length,
            result.get("length", baseline_length)
        )

        ev = EvidenceEngine.extract(diff, result.get("payload"))
        evidence.extend(ev)

    confidence = ConfidenceScore.calculate(len(evidence))
    vuln_type = (
        VulnerabilityMapper.map(payload_type)
        if confidence > 0.5
        else None
    )

    return {
        "is_vulnerable": confidence > 0.5,
        "confidence": confidence,
        "vulnerability_type": vuln_type,
        "evidence": evidence
    }