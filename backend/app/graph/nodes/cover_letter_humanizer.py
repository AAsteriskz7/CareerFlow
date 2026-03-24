"""Node B — Cover Letter Humanizer.

Uses past essays and cover letters as few-shot examples to replicate the
user's authentic writing style.

Enforced guardrails
-------------------
* Written in flowing prose (no bullet points).
* All corporate jargon is stripped out.
* Strictly avoids adding any information not present in the source materials.
"""

from __future__ import annotations

import logging

from app.graph.state import GraphState
from app.schemas import CoverLetter, Persona

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a professional writer that specialises in authentic, human cover
letters. You have studied the author's past writing samples extensively.

RIGID GUARDRAILS — violating any of these is a critical failure:
1. Write exclusively in flowing prose paragraphs. NEVER use bullet points,
   numbered lists, or dashes to structure your sentences.
2. Eliminate all corporate jargon. Banned phrases include (but are not
   limited to): "synergies", "leverage", "bandwidth", "circle back",
   "deep dive", "move the needle", "low-hanging fruit", "boilerplate",
   "value-add", "thought leader", "scalable", "best-of-breed".
3. Replicate the tone, vocabulary, and sentence rhythm of the provided
   writing samples. The letter must sound like the author, not a template.
4. Do NOT fabricate experiences. Ground every claim in the provided resume
   and essay excerpts.
5. Return only the cover letter body text — no subject line, no sign-off
   placeholder.
"""

_USER_PROMPT = """\
Past writing samples (few-shot style examples):
\"\"\"
{essay_chunks}
\"\"\"

Tailored resume context:
\"\"\"
{resume_summary}
\"\"\"

Target company:  {company}
Target role:     {role}

Job description:
\"\"\"
{job_description}
\"\"\"

Write the cover letter now (prose only, no bullets, no jargon):
"""


def cover_letter_humanizer_node(state: GraphState) -> GraphState:
    """LangGraph node that generates a humanised cover letter.

    Args:
        state: Current graph state. Expects ``state['resume']`` to be populated
               by the resume tailor node.

    Returns:
        Updated state with ``state['cover_letter']`` populated.
    """
    request = state["request"]
    persona: Persona = state.get("persona", request.persona)
    resume = state.get("resume")

    # ── Retrieve writing samples ──────────────────────────────────────────────
    essay_chunks = _retrieve_essay_chunks(request.job_description)
    state["retrieved_essay_chunks"] = essay_chunks

    # ── Summarise resume for grounding ────────────────────────────────────────
    resume_summary = _summarise_resume(resume)

    # ── Generate cover letter ─────────────────────────────────────────────────
    cover_letter = _generate_cover_letter(
        job_description=request.job_description,
        company=request.company or "the company",
        role=request.role or "the role",
        essay_chunks=essay_chunks,
        resume_summary=resume_summary,
    )
    state["cover_letter"] = cover_letter
    return state


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _retrieve_essay_chunks(query: str, top_k: int = 6) -> list[str]:
    """Fetch past essays and cover letters to use as few-shot style examples."""
    try:
        from app.memory import get_retriever

        chunks: list[str] = []
        for doc_type in ("essay", "cover_letter"):
            retriever = get_retriever(doc_type=doc_type, top_k=top_k // 2 or 3)
            nodes = retriever.retrieve(query)
            chunks.extend(node.get_content() for node in nodes)
        return chunks
    except Exception as exc:
        logger.warning("Essay retrieval failed (%s). Proceeding without samples.", exc)
        return []


def _summarise_resume(resume) -> str:
    """Create a compact plain-text summary of the tailored resume."""
    if resume is None:
        return "(no resume context available)"

    lines: list[str] = [f"Name: {resume.name}"]
    if resume.summary:
        lines.append(f"Summary: {resume.summary}")
    for exp in resume.experience[:5]:  # top 5 most relevant roles
        lines.append(
            f"- {exp.title} at {exp.company} ({exp.start_date} – {exp.end_date}): "
            + "; ".join(exp.bullets[:2])
        )
    for proj in resume.projects[:3]:
        lines.append(f"- Project: {proj.name} — {proj.description}")
    return "\n".join(lines)


def _generate_cover_letter(
    job_description: str,
    company: str,
    role: str,
    essay_chunks: list[str],
    resume_summary: str,
) -> CoverLetter:
    """Call the LLM to produce a humanised cover letter."""
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage

    from app.config import settings

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.7,  # slight creativity for natural prose
        api_key=settings.openai_api_key,
    )

    system_msg = SystemMessage(content=_SYSTEM_PROMPT)
    user_msg = HumanMessage(
        content=_USER_PROMPT.format(
            essay_chunks="\n---\n".join(essay_chunks) or "(no writing samples available)",
            resume_summary=resume_summary,
            company=company,
            role=role,
            job_description=job_description,
        )
    )

    response = llm.invoke([system_msg, user_msg])
    prose = response.content.strip()

    return CoverLetter(company=company, role=role, prose=prose)
