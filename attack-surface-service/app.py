from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
from services.surface_service import SurfaceService
from utils.logger import get_logger

logger = get_logger("AttackSurfaceService")

app = FastAPI(
    title="Attack Surface Service",
    description="Analyzes crawler output to identify the attack surface of a web application.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Form(BaseModel):
    """Represents an HTML form discovered on a page."""
    action: Optional[str] = Field(None, example="/login", description="The form's action attribute (URL).")
    method: Optional[str] = Field("GET", example="POST", description="The HTTP method used for form submission.")
    inputs: List[str] = Field([], example=["username", "password"], description="A list of input field names in the form.")

class AnalyzeRequest(BaseModel):
    """Represents the data for a single crawled page."""
    url: str = Field(..., example="https://example.com/login", description="The URL of the crawled page.")
    forms: List[Form] = Field([], description="A list of forms found on the page.")

class CrawlerOutput(BaseModel):
    """The input payload from the crawler service, containing all crawl results."""
    base_url: Optional[str] = Field(None, example="https://example.com", description="The base URL where the crawl started.")
    depth: Optional[int] = Field(None, example=2, description="The depth of the crawl.")
    total_pages: Optional[int] = Field(None, example=50, description="Total number of pages discovered by the crawler.")
    data: List[AnalyzeRequest] = Field(..., description="A list of results for each page crawled.")

class AttackPoint(BaseModel):
    """Represents a single attack point (URL with parameters)."""
    url: str = Field(..., example="https://example.com/search", description="The target URL for the attack.")
    method: str = Field(..., example="GET", description="The HTTP method to use.")
    parameters: List[str] = Field([], example=["q", "category"], description="The parameters that can be manipulated.")

class AnalyzeResponse(BaseModel):
    """The response from the analysis, detailing the identified attack surface."""
    total_attack_points: int = Field(..., example=15, description="The total number of unique attack points found.")
    attack_surface: List[AttackPoint] = Field(..., description="A list of all identified attack points.")


@app.get("/health", summary="Health Check", description="Checks if the service is running.")
def health():
    """A simple endpoint to confirm that the service is up and running."""
    return {"status": "Attack Surface Service Running"}

@app.post("/analyze",
          response_model=AnalyzeResponse,
          summary="Analyze Crawler Output",
          description="Processes the output from the crawler service to identify and list all potential attack points, such as URLs with parameters and forms.")
def analyze_surface(payload: CrawlerOutput):
    """
    Analyzes the crawled web application data to build an attack surface map.

    - **Receives** a list of pages and forms from the crawler service.
    - **Processes** each page to identify unique URLs and their parameters.
    - **Aggregates** these findings into a comprehensive list of attack points.
    - **Returns** the total count and a detailed list of the attack surface.
    """

    if not payload.data:
        raise HTTPException(status_code=400, detail="Crawler output required. The 'data' field cannot be empty.")

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
        raise HTTPException(status_code=500, detail="An internal server error occurred during analysis.")