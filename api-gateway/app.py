from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional

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

@app.post("/scan")
async def scan_website(request: ScanRequest):
    """Orchestrate the full vulnerability scanning workflow."""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: Crawler Service
            print(f"Starting crawl for {request.url} with depth {request.depth}")
            crawler_response = await client.post(
                f"{SERVICES['crawler']}/crawl",
                json={"url": request.url, "depth": request.depth}
            )
            crawler_response.raise_for_status()
            crawler_data = crawler_response.json()
            print(f"Crawler found {len(crawler_data.get('forms', []))} forms and {len(crawler_data.get('links', []))} links")

            # Step 2: Attack Surface Service
            print("Analyzing attack surface...")
            surface_response = await client.post(
                f"{SERVICES['attack_surface']}/analyze",
                json={"data": crawler_data.get("data", [])}
            )
            surface_response.raise_for_status()
            surface_data = surface_response.json()
            print(f"Attack surface analysis complete: {len(surface_data.get('attack_objects', []))} attack objects")

            # Step 3: Payload Service
            print("Generating payloads...")
            payload_response = await client.post(
                f"{SERVICES['payload']}/bulk-inject",
                json={"attack_surface": surface_data.get("attack_surface", [])}
            )
            payload_response.raise_for_status()
            payload_data = payload_response.json()
            print(f"Payload generation complete: {len(payload_data.get('payloads', []))} payload sets")

            # Step 4: Detection Service
            print("Running detection...")
            detection_response = await client.post(
                f"{SERVICES['detection']}/detect",
                json=payload_data.get("detailed_results", payload_data)
            )
            detection_response.raise_for_status()
            detection_data = detection_response.json()
            print(f"Detection complete: {detection_data.get('vulnerabilities_found', 0)} vulnerabilities found")

            # Step 5: Report Service
            print("Generating report...")
            report_response = await client.post(
                f"{SERVICES['report']}/report",
                json={
                    "target": request.url,
                    "format": "json",
                    "findings": detection_data.get("findings", [])
                }
            )
            report_response.raise_for_status()
            report_data = report_response.json()
            print("Report generation complete")

            return {
                "status": "success",
                "url": request.url,
                "depth": request.depth,
                "crawler_results": crawler_data,
                "attack_surface": surface_data,
                "payloads": payload_data,
                "detection": detection_data,
                "report": report_data
            }

    except httpx.HTTPStatusError as e:
        print(f"HTTP error in service call: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "API Gateway Running"}