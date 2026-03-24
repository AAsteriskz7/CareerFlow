"""Backend test suite — exercises schema validation, node logic (with mocked
LLM / retriever), and the FastAPI endpoints.

Run with:
    cd backend && pytest -v
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_resume_defaults(self):
        from app.schemas import Resume, Persona

        r = Resume(name="Alice")
        assert r.name == "Alice"
        assert r.experience == []
        assert r.education == []
        assert r.persona is None

    def test_cover_letter_word_count(self):
        from app.schemas import CoverLetter

        cl = CoverLetter(company="Acme", role="SWE", prose="Hello world this is four words plus one")
        assert cl.word_count > 0

    def test_interview_script_defaults(self):
        from app.schemas import InterviewScript

        s = InterviewScript(role="PM", company="Google")
        assert s.questions == []
        assert s.estimated_duration_minutes == 45

    def test_orchestration_request_default_persona(self):
        from app.schemas import OrchestrationRequest, Persona

        req = OrchestrationRequest(job_description="We need an SWE")
        assert req.persona == Persona.SOFTWARE_ENGINEERING

    def test_persona_enum_values(self):
        from app.schemas import Persona

        assert Persona.SOFTWARE_ENGINEERING.value == "software_engineering"
        assert Persona.UI_UX_DESIGN.value == "ui_ux_design"


# ---------------------------------------------------------------------------
# Graph state tests
# ---------------------------------------------------------------------------


class TestGraphState:
    def test_state_is_typeddict(self):
        from app.graph.state import GraphState

        state: GraphState = {"error": None}
        state["error"] = "test"
        assert state["error"] == "test"


# ---------------------------------------------------------------------------
# Resume tailor node — mocked LLM
# ---------------------------------------------------------------------------


class TestResumeTailorNode:
    def _make_state(self):
        from app.schemas import OrchestrationRequest, Persona

        req = OrchestrationRequest(
            job_description="We need a senior Python engineer.",
            company="TechCorp",
            role="Senior SWE",
            persona=Persona.SOFTWARE_ENGINEERING,
        )
        return {"request": req, "persona": Persona.SOFTWARE_ENGINEERING, "error": None}

    def test_node_populates_resume(self):
        from app.graph.nodes.resume_tailor import resume_tailor_node
        from app.schemas import Resume, Persona

        fake_resume = Resume(name="Jane Doe", persona=Persona.SOFTWARE_ENGINEERING)
        fake_response = MagicMock()
        fake_response.content = fake_resume.model_dump_json()

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response

        with (
            patch("app.graph.nodes.resume_tailor._retrieve_chunks", return_value=[]),
            patch("langchain_openai.ChatOpenAI", return_value=mock_llm),
        ):
            state = self._make_state()
            result = resume_tailor_node(state)

        assert "resume" in result
        assert result["resume"].name == "Jane Doe"

    def test_node_handles_bad_json_gracefully(self):
        from app.graph.nodes.resume_tailor import resume_tailor_node

        fake_response = MagicMock()
        fake_response.content = "NOT VALID JSON {{{"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response

        with (
            patch("app.graph.nodes.resume_tailor._retrieve_chunks", return_value=[]),
            patch("langchain_openai.ChatOpenAI", return_value=mock_llm),
        ):
            state = self._make_state()
            result = resume_tailor_node(state)

        # Should return a minimal resume rather than raising.
        assert "resume" in result
        assert result["resume"].name == ""


# ---------------------------------------------------------------------------
# Cover letter humanizer node — mocked LLM
# ---------------------------------------------------------------------------


class TestCoverLetterHumanizerNode:
    def _make_state(self):
        from app.schemas import OrchestrationRequest, Persona, Resume

        req = OrchestrationRequest(
            job_description="Looking for a product leader.",
            company="Startup Inc",
            role="Head of Product",
            persona=Persona.PRODUCT_MANAGEMENT,
        )
        resume = Resume(name="Bob Smith", persona=Persona.PRODUCT_MANAGEMENT)
        return {
            "request": req,
            "persona": Persona.PRODUCT_MANAGEMENT,
            "resume": resume,
            "error": None,
        }

    def test_node_populates_cover_letter(self):
        from app.graph.nodes.cover_letter_humanizer import cover_letter_humanizer_node

        fake_response = MagicMock()
        fake_response.content = (
            "I am writing to express my genuine enthusiasm for the Head of Product "
            "role at Startup Inc. Throughout my career I have led cross-functional "
            "teams to deliver meaningful outcomes for users."
        )

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response

        with (
            patch(
                "app.graph.nodes.cover_letter_humanizer._retrieve_essay_chunks",
                return_value=[],
            ),
            patch("langchain_openai.ChatOpenAI", return_value=mock_llm),
        ):
            state = self._make_state()
            result = cover_letter_humanizer_node(state)

        assert "cover_letter" in result
        assert result["cover_letter"].company == "Startup Inc"
        assert len(result["cover_letter"].prose) > 0


# ---------------------------------------------------------------------------
# Interview simulator node — mocked LLM
# ---------------------------------------------------------------------------


class TestInterviewSimulatorNode:
    def _make_state(self):
        from app.schemas import OrchestrationRequest, Persona, Resume

        req = OrchestrationRequest(
            job_description="UX designer with Figma experience.",
            company="DesignCo",
            role="Senior UX Designer",
            persona=Persona.UI_UX_DESIGN,
        )
        resume = Resume(name="Carol", persona=Persona.UI_UX_DESIGN)
        return {
            "request": req,
            "persona": Persona.UI_UX_DESIGN,
            "resume": resume,
            "error": None,
        }

    def test_node_populates_interview_script(self):
        from app.graph.nodes.interview_simulator import interview_simulator_node
        from app.schemas import InterviewScript

        script = InterviewScript(
            role="Senior UX Designer",
            company="DesignCo",
            questions=[],
            prep_resources=["Figma docs"],
        )
        fake_response = MagicMock()
        fake_response.content = script.model_dump_json()

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response

        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            state = self._make_state()
            result = interview_simulator_node(state)

        assert "interview_script" in result
        assert result["interview_script"].company == "DesignCo"

    def test_node_handles_bad_json_gracefully(self):
        from app.graph.nodes.interview_simulator import interview_simulator_node

        fake_response = MagicMock()
        fake_response.content = "{{INVALID}}"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = fake_response

        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            state = self._make_state()
            result = interview_simulator_node(state)

        assert "interview_script" in result


# ---------------------------------------------------------------------------
# FastAPI endpoint tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    from app.main import app

    return TestClient(app)


class TestEndpoints:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_orchestrate_returns_200(self, client):
        from app.schemas import OrchestrationResponse, Persona, Resume, CoverLetter, InterviewScript

        fake_result = {
            "resume": Resume(name="Test User", persona=Persona.SOFTWARE_ENGINEERING),
            "cover_letter": CoverLetter(
                company="ACME", role="SWE", prose="A genuine letter full of authentic prose."
            ),
            "interview_script": InterviewScript(role="SWE", company="ACME"),
        }

        with patch("app.graph.router.run_pipeline", return_value=fake_result):
            resp = client.post(
                "/orchestrate",
                json={
                    "job_description": "Senior Python engineer at ACME.",
                    "company": "ACME",
                    "role": "SWE",
                    "persona": "software_engineering",
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["resume"]["name"] == "Test User"
        assert body["cover_letter"]["company"] == "ACME"
        assert "interview_script" in body

    def test_orchestrate_500_on_pipeline_error(self, client):
        with patch("app.graph.router.run_pipeline", side_effect=RuntimeError("boom")):
            resp = client.post(
                "/orchestrate",
                json={
                    "job_description": "A job",
                    "company": "Co",
                    "role": "Dev",
                    "persona": "software_engineering",
                },
            )
        assert resp.status_code == 500
