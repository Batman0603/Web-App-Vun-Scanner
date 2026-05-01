from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional, Dict, Any
import uuid

app = FastAPI(title="API Gateway - Web Vulnerability Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    depth: int = 2

SERVICES = {
    "crawler": "http://crawler-service:8001",
    "attack_surface": "http://attack-surface-service:8002",
    "payload": "http://payload-service:8003",
    "detection": "http://detection-service:8004",
    "report": "http://report-service:8005",
}

# In-memory storage for scan states (Replace with Redis/DB for production)
scans: Dict[str, Any] = {}

async def run_full_pipeline(scan_id: str, url: str, depth: int):
    """Background task to orchestrate the services with specific timeouts."""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Crawler Service
            scans[scan_id].update({"status": "running", "stage": "crawler", "progress": 10})
            crawler_response = await client.post(
                f"{SERVICES['crawler']}/crawl",
                json={"url": url, "depth": depth},
                timeout=60.0  # Crawler timeout
            )
            crawler_response.raise_for_status()
            crawler_data = crawler_response.json()
            scans[scan_id]["crawler_results"] = crawler_data

            # Step 2: Attack Surface Service
            scans[scan_id].update({"stage": "attack-surface", "progress": 30})
            surface_response = await client.post(
                f"{SERVICES['attack_surface']}/analyze",
                json={"data": crawler_data.get("data", [])},
                timeout=20.0  # Attack surface timeout
            )
            surface_response.raise_for_status()
            surface_data = surface_response.json()
            scans[scan_id]["attack_surface"] = surface_data

            # Step 3: Payload Service
            scans[scan_id].update({"stage": "payload-injection", "progress": 50})
            payload_response = await client.post(
                f"{SERVICES['payload']}/bulk-inject",
                json={"attack_surface": surface_data.get("attack_surface", [])},
                timeout=120.0  # Payload timeout (long running)
            )
            payload_response.raise_for_status()
            payload_data = payload_response.json()
            scans[scan_id]["payloads"] = payload_data

            # Step 4: Detection Service
            scans[scan_id].update({"stage": "vulnerability-detection", "progress": 80})
            detection_response = await client.post(
                f"{SERVICES['detection']}/detect",
                json=payload_data.get("detailed_results", payload_data),
                timeout=30.0  # Detection timeout
            )
            detection_response.raise_for_status()
            detection_data = detection_response.json()
            scans[scan_id]["detection"] = detection_data

            # Step 5: Report Service
            scans[scan_id].update({"stage": "reporting", "progress": 95})
            report_response = await client.post(
                f"{SERVICES['report']}/report",
                json={
                    "target": url,
                    "format": "json",
                    "findings": detection_data.get("findings", [])
                },
                timeout=15.0  # Reporting timeout
            )
            report_response.raise_for_status()
            report_data = report_response.json()
            print(report_response.json())
            scans[scan_id]["report"] = report_data

            scans[scan_id].update({"status": "completed", "progress": 100})

    except Exception as e:
        scans[scan_id].update({
            "status": "failed",
            "error": str(e),
            "progress": 100
        })

@app.post("/scan")
async def scan_website(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a scan in the background and return a scan_id immediately."""
    scan_id = str(uuid.uuid4())
    scans[scan_id] = {
        "status": "started",
        "stage": "initialization",
        "progress": 0,
        "url": request.url,
        "depth": request.depth
    }
    
    background_tasks.add_task(run_full_pipeline, scan_id, request.url, request.depth)
    
    return {"scan_id": scan_id, "status": "started"}

@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Check the current status and progress of a scan."""
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans[scan_id]
 
@app.get("/health")
def health():
    return {"status": "API Gateway Running"}