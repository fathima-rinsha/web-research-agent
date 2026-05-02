import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import run_research

app = FastAPI(
    title="Web Research Agent API",
    description="AI-powered research agent using Claude + web search",
    version="1.0.0",
)

# Serve static files (the React frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Request / Response models ──────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    executive_summary: str = ""
    key_findings: list = []
    analysis: str = ""
    conclusion: str = ""
    sources: list = []
    search_queries: list = []
    error: str = ""
    parse_error: bool = False


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the React frontend."""
    return FileResponse("static/index.html")


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Run the AI research agent on a given topic.
    Returns a structured report with findings, analysis, and sources.
    """
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    if len(topic) > 500:
        raise HTTPException(status_code=400, detail="Topic must be under 500 characters.")

    try:
        # Run the synchronous agent in a thread pool to avoid blocking the event loop
        result = await asyncio.to_thread(run_research, topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
