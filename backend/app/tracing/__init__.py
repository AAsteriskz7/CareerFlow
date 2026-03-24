"""LangSmith tracing initialisation.

Call ``setup_tracing()`` once at application startup. When the
LANGCHAIN_TRACING_V2 env-var is ``true`` LangSmith automatically captures
every LangChain / LangGraph call.  This module makes the setup explicit and
provides a context manager for ad-hoc run tagging.
"""

from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


def setup_tracing(project: str | None = None) -> None:
    """Configure LangSmith environment variables for automatic tracing.

    Args:
        project: Override the LangSmith project name. Defaults to the value
                 already set in the environment or ``'CareerFlow'``.
    """
    from app.config import settings

    if settings.langchain_tracing_v2 and settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = project or settings.langchain_project
        logger.info("LangSmith tracing enabled for project '%s'", os.environ["LANGCHAIN_PROJECT"])
    else:
        logger.info(
            "LangSmith tracing disabled. "
            "Set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to enable."
        )


@contextmanager
def trace_run(run_name: str, tags: list[str] | None = None) -> Generator[None, None, None]:
    """Context manager that attaches metadata to a LangSmith run.

    Usage::

        with trace_run("resume_tailor", tags=["swe", "google"]):
            result = graph.invoke(state)

    When tracing is disabled this is a no-op.
    """
    try:
        from langsmith import trace  # type: ignore[import]

        with trace(run_name, tags=tags or []):
            yield
    except ImportError:
        yield
