from app.agents import AGENTS, AgentCapability
from fastapi import FastAPI

app = FastAPI(title="Elevra AI Engine", version="0.1.0")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-engine"}


@app.get("/agents", response_model=list[AgentCapability])
async def list_agents() -> list[AgentCapability]:
    return AGENTS


@app.post("/recommendations/preview")
async def preview_recommendations(profile: dict[str, object]) -> dict[str, object]:
    return {
        "profileSignals": profile,
        "recommendations": [
            {
                "id": "opp_scholarship_global_ai",
                "score": 0.94,
                "reason": "Matches AI interest, portfolio readiness, and scholarship timeline.",
            }
        ],
    }
