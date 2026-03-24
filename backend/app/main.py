"""CareerFlow FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import OrchestrationRequest, OrchestrationResponse
from app.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle handler."""
    # Initialise LangSmith tracing before anything else.
    setup_tracing()

    # Pre-warm the LlamaIndex vector index so the first request isn't slow.
    try:
        from app.memory import build_index

        logger.info("Pre-warming vector index…")
        build_index()
    except Exception as exc:
        logger.warning("Index pre-warm failed (%s). Index will build on first request.", exc)

    yield  # application runs here

    logger.info("CareerFlow backend shutting down.")


app = FastAPI(
    title="CareerFlow API",
    description=(
        "Context-Aware Career Orchestration Engine — resume tailoring, "
        "cover letter humanising, and interview simulation."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the Next.js dev server (port 3000) and any configured frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """Simple liveness probe."""
    return {"status": "ok", "version": app.version}


@app.post("/orchestrate", response_model=OrchestrationResponse, tags=["pipeline"])
async def orchestrate(request: OrchestrationRequest) -> OrchestrationResponse:
    """Run the full CareerFlow pipeline for a given job description.

    This endpoint:
    1. Routes the request through the LangGraph (resume tailor → cover letter
       humanizer → interview simulator).
    2. Returns a fully-structured JSON payload ready for the frontend.

    Raises:
        HTTPException 500: If the pipeline fails unexpectedly.
    """
    try:
        from app.graph.router import run_pipeline
        from app.tracing import trace_run

        with trace_run(
            "orchestrate",
            tags=[request.persona.value, request.company or "unknown"],
        ):
            result = run_pipeline(request)

        resume = result.get("resume")
        cover_letter = result.get("cover_letter")
        interview_script = result.get("interview_script")

        if resume is None or cover_letter is None or interview_script is None:
            raise ValueError("Pipeline returned incomplete results.")

        return OrchestrationResponse(
            resume=resume,
            cover_letter=cover_letter,
            interview_script=interview_script,
        )
    except Exception as exc:
        logger.exception("Pipeline error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/index/rebuild", tags=["admin"])
async def rebuild_index() -> dict:
    """Force a rebuild of the LlamaIndex vector store from source documents."""
    try:
        from app.memory import build_index

        build_index(force_rebuild=True)
        return {"status": "ok", "message": "Index rebuilt successfully."}
    except Exception as exc:
        logger.exception("Index rebuild failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
