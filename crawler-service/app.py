from typing import List, Optional

from pydantic import BaseModel, Field

from utils.logger import get_logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crawler.crawler_engine import CrawlerEngine
from utils.validators import validate_url, validate_depth, ValidationError

app = FastAPI(
    title="Crawler Service",
    description="A service to crawl web applications and discover pages and forms.",
    version="1.0.0",
)

# --- Pydantic Models for API Schema ---

class CrawlRequest(BaseModel):
    """Request model for the /crawl endpoint."""
    url: str = Field(..., example="https://example.com", description="The target URL to start crawling from.")
    depth: int = Field(2, ge=0, le=5, description="The maximum crawl depth. Must be between 0 and 5.")

class FormDetail(BaseModel):
    """Details of an extracted HTML form."""
    action: Optional[str]
    method: str
    inputs: List[str]

class CrawlPageResult(BaseModel):
    """Results from crawling a single page."""
    url: str
    forms: List[FormDetail]

class CrawlResponse(BaseModel):
    """Response model for a successful crawl operation."""
    base_url: str
    depth: int
    total_pages: int
    data: List[CrawlPageResult]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("CrawlerAPI")


@app.post("/crawl",
          response_model=CrawlResponse,
          summary="Crawl a target URL",
          description="Starts a crawl on the given URL up to a specified depth, extracting links and forms from all discovered pages within the same domain.")
def crawl_target(payload: CrawlRequest):
    """
    Initiates a web crawl based on the provided URL and depth.

    - **Validates** the input URL and depth using custom validators.
    - **Initializes** the `CrawlerEngine`.
    - **Executes** the crawl and collects page links and forms.
    - **Returns** a structured result of the crawl.
    """
    try:
        # Pydantic handles basic validation; custom validators add more specific checks.
        base_url = validate_url(payload.url)
        depth = validate_depth(payload.depth)

        logger.info(f"Starting crawl for {base_url} with depth {depth}")

        crawler = CrawlerEngine(base_url, depth)
        results = crawler.crawl()

        return {
            "base_url": base_url,
            "depth": depth,
            "total_pages": len(results),
            "data": results
        }

    except ValidationError as ve:
        logger.warning(f"Validation failed: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Unexpected error during crawl for {payload.url}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected internal server error occurred during crawling."
        )