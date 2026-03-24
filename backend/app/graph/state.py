"""Shared graph state definition used across all LangGraph nodes."""

from __future__ import annotations

from typing import TypedDict

from app.schemas import (
    CoverLetter,
    InterviewScript,
    OrchestrationRequest,
    Persona,
    Resume,
)


class GraphState(TypedDict, total=False):
    """Mutable state object threaded through every node in the LangGraph."""

    # ── Inputs ────────────────────────────────────────────────────────────────
    request: OrchestrationRequest

    # ── Intermediate artefacts ────────────────────────────────────────────────
    retrieved_resume_chunks: list[str]
    retrieved_essay_chunks: list[str]

    # ── Final outputs ─────────────────────────────────────────────────────────
    resume: Resume
    cover_letter: CoverLetter
    interview_script: InterviewScript

    # ── Runtime metadata ──────────────────────────────────────────────────────
    persona: Persona
    error: str | None
