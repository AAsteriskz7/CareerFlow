"""LlamaIndex memory layer — document ingestion and vectorisation.

Responsibilities
----------------
* Load markdown/text documents from ``data/resumes/``, ``data/essays/``, and
  ``data/cover_letters/``.
* Attach metadata so each chunk knows which :class:`~app.schemas.Persona` it
  belongs to and what document type it is.
* Build (or reload from disk) a persistent ``VectorStoreIndex``.
* Expose a :func:`get_retriever` factory used by LangGraph nodes to perform
  similarity search at query time.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from app.config import settings
from app.schemas import Persona

if TYPE_CHECKING:
    from llama_index.core import VectorStoreIndex
    from llama_index.core.retrievers import VectorIndexRetriever

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Persona metadata mapping
# ---------------------------------------------------------------------------
# Maps each data sub-directory name to the Persona enum value it represents.
_PERSONA_BY_DIR: dict[str, Persona] = {
    "software_engineering": Persona.SOFTWARE_ENGINEERING,
    "product_management": Persona.PRODUCT_MANAGEMENT,
    "operations_marketing": Persona.OPERATIONS_MARKETING,
    "ui_ux_design": Persona.UI_UX_DESIGN,
}

_DOC_TYPE_BY_DIR: dict[str, str] = {
    "resumes": "resume",
    "essays": "essay",
    "cover_letters": "cover_letter",
}

# Module-level cache so the index is only built once per process.
_index_cache: VectorStoreIndex | None = None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def build_index(force_rebuild: bool = False) -> "VectorStoreIndex":
    """Build (or reload) the LlamaIndex ``VectorStoreIndex``.

    On the first call the index is constructed from all documents found under
    ``data/``.  Subsequent calls return the cached instance unless
    *force_rebuild* is ``True``.

    The index is persisted to ``settings.llama_index_storage_dir`` so that
    restarting the server doesn't re-embed everything from scratch.

    Args:
        force_rebuild: When ``True``, ignore any cached or persisted index and
                       rebuild from source documents.

    Returns:
        A ready-to-query :class:`VectorStoreIndex`.
    """
    global _index_cache

    if _index_cache is not None and not force_rebuild:
        return _index_cache

    from llama_index.core import (
        Settings as LlamaSettings,
        SimpleDirectoryReader,
        StorageContext,
        VectorStoreIndex,
        load_index_from_storage,
    )
    from llama_index.core.schema import Document
    from llama_index.embeddings.openai import OpenAIEmbedding  # type: ignore[import]

    # Configure the embedding model.
    LlamaSettings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=settings.openai_api_key or os.environ.get("OPENAI_API_KEY", ""),
    )

    storage_dir = Path(settings.llama_index_storage_dir)

    # Try loading from persisted storage first.
    if storage_dir.exists() and not force_rebuild:
        try:
            logger.info("Loading existing index from %s", storage_dir)
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            _index_cache = load_index_from_storage(storage_context)
            return _index_cache
        except Exception as exc:
            logger.warning("Could not load persisted index (%s). Rebuilding…", exc)

    # Build fresh index from source documents.
    documents: list[Document] = _load_documents()

    if not documents:
        logger.warning(
            "No documents found under '%s'. Index will be empty.", settings.data_dir
        )

    logger.info("Building vector index from %d document(s)…", len(documents))
    _index_cache = VectorStoreIndex.from_documents(documents, show_progress=True)

    # Persist for future restarts.
    storage_dir.mkdir(parents=True, exist_ok=True)
    _index_cache.storage_context.persist(persist_dir=str(storage_dir))
    logger.info("Index persisted to %s", storage_dir)

    return _index_cache


def get_retriever(
    persona: Persona | None = None,
    doc_type: str | None = None,
    top_k: int = 5,
) -> "VectorIndexRetriever":
    """Return a retriever pre-filtered to a persona and/or document type.

    Args:
        persona:  Only return chunks tagged with this persona.
        doc_type: One of ``'resume'``, ``'essay'``, or ``'cover_letter'``.
        top_k:    Maximum number of nodes to retrieve.

    Returns:
        A configured :class:`VectorIndexRetriever` ready for ``.retrieve()``.
    """
    index = build_index()

    # Build metadata filters if requested.
    filters = None
    if persona or doc_type:
        from llama_index.core.vector_stores import (
            ExactMatchFilter,
            MetadataFilters,
            FilterOperator,
        )

        conditions: list[ExactMatchFilter] = []
        if persona:
            conditions.append(
                ExactMatchFilter(key="persona", value=persona.value, operator=FilterOperator.EQ)
            )
        if doc_type:
            conditions.append(
                ExactMatchFilter(key="doc_type", value=doc_type, operator=FilterOperator.EQ)
            )

        filters = MetadataFilters(filters=conditions)

    return index.as_retriever(similarity_top_k=top_k, filters=filters)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _load_documents() -> list:
    """Walk the data directory and load all supported documents with metadata."""
    from llama_index.core.schema import Document

    data_root = Path(settings.data_dir).resolve()
    docs: list[Document] = []

    for doc_type_dir in data_root.iterdir():
        if not doc_type_dir.is_dir():
            continue

        doc_type = _DOC_TYPE_BY_DIR.get(doc_type_dir.name)
        if doc_type is None:
            continue

        # Resumes are organised into persona sub-directories.
        if doc_type == "resume":
            for persona_dir in doc_type_dir.iterdir():
                if not persona_dir.is_dir():
                    continue
                persona = _PERSONA_BY_DIR.get(persona_dir.name)
                docs.extend(
                    _read_dir(persona_dir, doc_type=doc_type, persona=persona)
                )
        else:
            docs.extend(_read_dir(doc_type_dir, doc_type=doc_type, persona=None))

    return docs


def _read_dir(
    directory: Path,
    doc_type: str,
    persona: Persona | None,
) -> list:
    """Load every text/markdown file in *directory* as a ``Document``."""
    from llama_index.core.schema import Document

    docs: list[Document] = []
    for file_path in sorted(directory.rglob("*")):
        if file_path.suffix not in {".md", ".txt", ".pdf"}:
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("Skipping %s: %s", file_path, exc)
            continue

        metadata: dict = {
            "source": str(file_path.relative_to(directory.parent.parent)),
            "doc_type": doc_type,
            "filename": file_path.name,
        }
        if persona:
            metadata["persona"] = persona.value

        docs.append(Document(text=text, metadata=metadata))

    return docs
