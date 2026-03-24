"""LangGraph orchestration router — the stateful graph that wires together
the three specialist nodes (Resume Tailor → Cover Letter Humanizer →
Interview Simulator) into a single runnable pipeline.

Usage
-----
>>> from app.graph.router import build_graph
>>> graph = build_graph()
>>> result = graph.invoke({"request": request_obj, "persona": Persona.SOFTWARE_ENGINEERING})
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_graph():
    """Construct and compile the CareerFlow LangGraph.

    The graph topology is a simple linear chain:

        [START] → resume_tailor → cover_letter_humanizer → interview_simulator → [END]

    Each node receives the full :class:`~app.graph.state.GraphState` and
    returns an updated copy. LangGraph merges the returned keys back into
    the shared state automatically.

    Returns:
        A compiled :class:`langgraph.graph.CompiledGraph` ready for
        ``.invoke()`` or ``.astream()``.
    """
    from langgraph.graph import StateGraph, END

    from app.graph.state import GraphState
    from app.graph.nodes.resume_tailor import resume_tailor_node
    from app.graph.nodes.cover_letter_humanizer import cover_letter_humanizer_node
    from app.graph.nodes.interview_simulator import interview_simulator_node

    builder = StateGraph(GraphState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("resume_tailor", resume_tailor_node)
    builder.add_node("cover_letter_humanizer", cover_letter_humanizer_node)
    builder.add_node("interview_simulator", interview_simulator_node)

    # ── Wire edges ────────────────────────────────────────────────────────────
    builder.set_entry_point("resume_tailor")
    builder.add_edge("resume_tailor", "cover_letter_humanizer")
    builder.add_edge("cover_letter_humanizer", "interview_simulator")
    builder.add_edge("interview_simulator", END)

    return builder.compile()


# ---------------------------------------------------------------------------
# Module-level singleton (lazy initialisation)
# ---------------------------------------------------------------------------
_graph = None


def get_graph():
    """Return the compiled graph, building it once on first access."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_pipeline(request: Any, persona=None) -> dict:
    """High-level helper: run the full orchestration pipeline.

    Args:
        request: An :class:`~app.schemas.OrchestrationRequest` instance.
        persona: Optional override for the persona (defaults to
                 ``request.persona``).

    Returns:
        A dict containing ``resume``, ``cover_letter``, and
        ``interview_script`` keys (populated Pydantic models).
    """
    from app.schemas import Persona

    graph = get_graph()

    initial_state = {
        "request": request,
        "persona": persona or request.persona,
        "error": None,
    }

    logger.info(
        "Starting CareerFlow pipeline | persona=%s | company=%s | role=%s",
        initial_state["persona"],
        request.company,
        request.role,
    )

    final_state = graph.invoke(initial_state)

    logger.info("Pipeline complete.")
    return {
        "resume": final_state.get("resume"),
        "cover_letter": final_state.get("cover_letter"),
        "interview_script": final_state.get("interview_script"),
    }
