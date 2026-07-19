from uuid import uuid4

from app.schemas import CrawlJob, CrawlRequest
from fastapi import FastAPI

app = FastAPI(title="Elevra Crawler Service", version="0.1.0")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "crawler"}


@app.post("/crawl-jobs", response_model=CrawlJob, status_code=202)
async def create_crawl_job(request: CrawlRequest) -> CrawlJob:
    return CrawlJob(
        id=str(uuid4()),
        status="queued",
        source_url=request.source_url,
        priority=request.priority,
    )
