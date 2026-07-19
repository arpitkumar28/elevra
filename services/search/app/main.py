from app.schemas import SearchHit, SearchRequest, SearchResponse
from fastapi import FastAPI

app = FastAPI(title="Elevra Search Service", version="0.1.0")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "search"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    return SearchResponse(
        hits=[
            SearchHit(
                id="opp_scholarship_global_ai",
                title=f"{request.query} Scholars Program",
                type="scholarship",
                provider="Elevra Verified Network",
                score=0.94,
            )
        ],
        estimated_total_hits=1,
        processing_time_ms=12,
    )
