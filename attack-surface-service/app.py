from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel
from services.surface_service import SurfaceService
from utils.logger import get_logger

logger = get_logger("AttackSurfaceService")

app = FastAPI(title="Attack Surface Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Form(BaseModel):
    action: Optional[str] = None
    method: Optional[str] = "GET"
    inputs: List[str] = []

class AnalyzeRequest(BaseModel):
    url: str
    forms: List[Form] = []

class CrawlerOutput(BaseModel):
    base_url: Optional[str] = None
    depth: Optional[int] = None
    total_pages: Optional[int] = None
    data: List[AnalyzeRequest] = []

@app.get("/health")
def health():
    return {"status": "Attack Surface Service Running"}

@app.post("/analyze")
def analyze_surface(payload: CrawlerOutput):

    if not payload.data:
        raise HTTPException(status_code=400, detail="Crawler output required")

    try:
        # Convert Pydantic models to dicts for the service
        surface_data = [p.model_dump() for p in payload.data]
        surface = SurfaceService.build_attack_surface(surface_data)

        return {
            "total_attack_points": len(surface),
            "attack_surface": surface
        }

    except Exception as e:
        logger.error(f"Analyze failed: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")