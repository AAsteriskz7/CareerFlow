"""Node A — Resume Tailor.

Pulls the correct base resume for the requested :class:`~app.schemas.Persona`
and rewrites it so that every impact metric aligns with the job description.
Hallucination-prevention is enforced by grounding all edits in retrieved
source chunks — the LLM is explicitly instructed *not* to invent facts.
"""

from __future__ import annotations

import json
import logging

from app.graph.state import GraphState
from app.schemas import ExperienceEntry, Persona, Resume

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are an expert resume writer with deep knowledge of applicant tracking
systems (ATS) and modern hiring practices.

RULES — follow them strictly:
1. Use ONLY the source resume chunks provided. Do NOT invent companies,
   titles, dates, projects, or metrics that are not present in the chunks.
2. Reorder and rephrase bullet points to maximise alignment with the job
   description while keeping every claim truthful.
3. Return your answer as valid JSON that conforms exactly to this schema:
   {schema}

If a field is unknown, use an empty string or empty list — never make up data.
"""

_USER_PROMPT = """\
Target job description:
\"\"\"
{job_description}
\"\"\"

Source resume chunks (ground truth — do not hallucinate beyond this):
\"\"\"
{resume_chunks}
\"\"\"

Tailored resume (JSON only, no markdown fences):
"""


def resume_tailor_node(state: GraphState) -> GraphState:
    """LangGraph node that tailors the resume to the job description.

    Args:
        state: Current graph state containing the orchestration request and
               retrieved resume chunks.

    Returns:
        Updated state with ``state['resume']`` populated.
    """
    request = state["request"]
    persona: Persona = state.get("persona", request.persona)

    # ── Retrieve relevant resume chunks ──────────────────────────────────────
    chunks = _retrieve_chunks(persona, request.job_description)
    state["retrieved_resume_chunks"] = chunks

    # ── Call the LLM ─────────────────────────────────────────────────────────
    resume = _generate_tailored_resume(
        job_description=request.job_description,
        resume_chunks=chunks,
        persona=persona,
    )
    state["resume"] = resume
    return state


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _retrieve_chunks(persona: Persona, query: str, top_k: int = 8) -> list[str]:
    """Retrieve the most relevant resume chunks for this persona."""
    try:
        from app.memory import get_retriever

        retriever = get_retriever(persona=persona, doc_type="resume", top_k=top_k)
        nodes = retriever.retrieve(query)
        return [node.get_content() for node in nodes]
    except Exception as exc:
        logger.warning("Resume retrieval failed (%s). Proceeding without context.", exc)
        return []


def _generate_tailored_resume(
    job_description: str,
    resume_chunks: list[str],
    persona: Persona,
) -> Resume:
    """Call the LLM to produce a tailored resume JSON."""
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage

    from app.config import settings

    schema_json = json.dumps(Resume.model_json_schema(), indent=2)

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,  # zero temp to minimise hallucinations
        api_key=settings.openai_api_key,
    )

    system_msg = SystemMessage(content=_SYSTEM_PROMPT.format(schema=schema_json))
    user_msg = HumanMessage(
        content=_USER_PROMPT.format(
            job_description=job_description,
            resume_chunks="\n---\n".join(resume_chunks) or "(no source chunks available)",
        )
    )

    response = llm.invoke([system_msg, user_msg])
    raw = response.content.strip()

    try:
        data = json.loads(raw)
        # Stamp the persona on every experience entry.
        for exp in data.get("experience", []):
            exp.setdefault("persona_tags", [persona.value])
        data["persona"] = persona.value
        return Resume.model_validate(data)
    except Exception as exc:
        logger.error("Failed to parse resume JSON: %s\nRaw output:\n%s", exc, raw)
        # Return a minimal valid resume so the pipeline doesn't crash.
        return Resume(name="", persona=persona)
