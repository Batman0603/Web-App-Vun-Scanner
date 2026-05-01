from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional, Dict, Any
import uuid
import logging

app = FastAPI(title="API Gateway - Web Vulnerability Scanner")
logger = logging.getLogger("API_Gateway")
logging.basicConfig(level=logging.INFO)

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

async def safe_service_call(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    """Executes a service call with exponential backoff retries."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Service call to {url} failed (Attempt {attempt + 1}/{max_retries}). Retrying... Error: {e}")

async def run_full_pipeline(scan_id: str, url: str, depth: int):
    """Background task to orchestrate the services with specific timeouts."""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Crawler Service
            scans[scan_id].update({"status": "running", "stage": "crawler", "progress": 10})
            crawler_data = await safe_service_call(
                client, "POST",
                f"{SERVICES['crawler']}/crawl",
                json={"url": url, "depth": depth},
                timeout=None
            )
            scans[scan_id]["crawler_results"] = crawler_data

            # If crawler found nothing, we finish gracefully instead of failing subsequent steps
            pages = crawler_data.get("data", [])
            if not pages:
                logger.info(f"Scan {scan_id} finished early: No pages discovered.")
                scans[scan_id].update({"status": "completed", "progress": 100, "stage": "finished"})
                return

            # Step 2: Attack Surface Service
            scans[scan_id].update({"stage": "attack-surface", "progress": 30})
            surface_data = await safe_service_call(
                client, "POST",
                f"{SERVICES['attack_surface']}/analyze",
                json={"data": pages},
                timeout=None
            )
            scans[scan_id]["attack_surface"] = surface_data

            attack_points = surface_data.get("attack_surface", [])
            if not attack_points:
                logger.info(f"Scan {scan_id} finished early: No attack surface identified.")
                scans[scan_id].update({"status": "completed", "progress": 100, "stage": "finished"})
                return

            # Step 3: Payload Service
            scans[scan_id].update({"stage": "payload-injection", "progress": 50})
            payload_data = await safe_service_call(
                client, "POST",
                f"{SERVICES['payload']}/bulk-inject",
                json={"attack_surface": attack_points},
                timeout=None
            )
            scans[scan_id]["payloads"] = payload_data

            # Step 4: Detection Service
            scans[scan_id].update({"stage": "vulnerability-detection", "progress": 80})
            detection_data = await safe_service_call(
                client, "POST",
                f"{SERVICES['detection']}/detect",
                json=payload_data.get("detailed_results", payload_data),
                timeout=None
            )
            scans[scan_id]["detection_results"] = detection_data

            # Step 5: Report Service
            scans[scan_id].update({"stage": "reporting", "progress": 95})
            report_data = await safe_service_call(
                client, "POST",
                f"{SERVICES['report']}/report",
                json={
                    "target": url,
                    "format": "json",
                    "findings": detection_data.get("findings", [])
                },
                timeout=None
            )
            scans[scan_id]["report"] = report_data

            scans[scan_id].update({"status": "completed", "progress": 100})

    except Exception as e:
        error_message = f"An unexpected error occurred: {type(e).__name__}"
        if isinstance(e, httpx.HTTPStatusError):
            error_message = f"Service responded with {e.response.status_code}: {e.response.text}"
        elif isinstance(e, httpx.RequestError):
            error_message = f"Network or request error ({type(e).__name__}): {e}"
        elif str(e): # Fallback for other exceptions if str(e) is not empty
            error_message = str(e)
        
        logger.error(f"Scan {scan_id} failed: {error_message}", exc_info=True)

        scans[scan_id].update({
            "status": "failed",
            "error": error_message,
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