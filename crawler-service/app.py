from utils.logger import get_logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crawler.crawler_engine import CrawlerEngine
from utils.validators import validate_url, validate_depth, ValidationError

app = FastAPI(title="Crawler Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("CrawlerAPI")


@app.post("/crawl")
def crawl_target(payload: dict):
    try:
        # Validate inputs
        base_url = validate_url(payload.get("url"))
        depth = validate_depth(payload.get("depth", 2))

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
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during crawling"
        )