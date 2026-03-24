"""Node C — Interview Simulator.

Analyses the tailored resume against the job description to generate a
custom mock-interview script and technical prep questions.
"""

from __future__ import annotations

import json
import logging

from app.graph.state import GraphState
from app.schemas import InterviewQuestion, InterviewScript, Persona

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a senior hiring manager and technical interviewer with experience
across Software Engineering, Product Management, Operations, and Design roles.

Given a tailored resume and a job description, generate a realistic mock
interview script that will help the candidate prepare thoroughly.

Return your answer as valid JSON that conforms exactly to this schema:
{schema}

Guidelines:
- Include a mix of Behavioural, Technical, and role-specific questions.
- Behavioural questions should reference specific experiences from the resume
  (e.g. "Tell me about your time at SlatePath.ai as CTO…").
- Technical questions should reflect the technologies and skills in the JD.
- Each question should have a brief hint about what a strong answer covers.
- prep_resources should list 3-5 concrete study topics or resources.
"""

_USER_PROMPT = """\
Tailored resume:
\"\"\"
{resume_json}
\"\"\"

Job description:
\"\"\"
{job_description}
\"\"\"

Interview script (JSON only, no markdown fences):
"""


def interview_simulator_node(state: GraphState) -> GraphState:
    """LangGraph node that generates a custom mock-interview script.

    Args:
        state: Current graph state. Expects ``state['resume']`` and
               ``state['request']`` to be populated.

    Returns:
        Updated state with ``state['interview_script']`` populated.
    """
    request = state["request"]
    resume = state.get("resume")

    interview_script = _generate_interview_script(
        job_description=request.job_description,
        company=request.company or "the company",
        role=request.role or "the role",
        resume=resume,
    )
    state["interview_script"] = interview_script
    return state


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _generate_interview_script(
    job_description: str,
    company: str,
    role: str,
    resume,
) -> InterviewScript:
    """Call the LLM to produce a structured interview script."""
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage

    from app.config import settings

    schema_json = json.dumps(InterviewScript.model_json_schema(), indent=2)

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.3,
        api_key=settings.openai_api_key,
    )

    resume_json = "(no resume available)"
    if resume is not None:
        try:
            resume_json = resume.model_dump_json(indent=2)
        except Exception:
            resume_json = str(resume)

    system_msg = SystemMessage(content=_SYSTEM_PROMPT.format(schema=schema_json))
    user_msg = HumanMessage(
        content=_USER_PROMPT.format(
            resume_json=resume_json,
            job_description=job_description,
        )
    )

    response = llm.invoke([system_msg, user_msg])
    raw = response.content.strip()

    try:
        data = json.loads(raw)
        data.setdefault("role", role)
        data.setdefault("company", company)
        return InterviewScript.model_validate(data)
    except Exception as exc:
        logger.error("Failed to parse interview script JSON: %s\nRaw output:\n%s", exc, raw)
        return InterviewScript(role=role, company=company)
