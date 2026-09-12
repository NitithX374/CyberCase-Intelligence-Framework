"""Register the case, chat, retrieval, and report ORM models."""

from app.models.case import Case  # noqa: F401
from app.models.caseMaterials import (  # noqa: F401
    CaseDocument,
    CaseEvidenceSnapshot,
    DocumentExtraction,
    EvidenceRevision,
    EvidenceSource,
)
from app.models.caseRun import CaseAnalysisResult, CaseRun  # noqa: F401
from app.models.chat import ChatMessage, ChatThread  # noqa: F401
from app.models.ragContext import RagContext  # noqa: F401
from app.models.report import CaseReport, ChatReport  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "Case",
    "CaseDocument",
    "CaseEvidenceSnapshot",
    "CaseAnalysisResult",
    "CaseReport",
    "CaseRun",
    "ChatMessage",
    "ChatReport",
    "ChatThread",
    "DocumentExtraction",
    "EvidenceRevision",
    "EvidenceSource",
    "RagContext",
    "User",
]
