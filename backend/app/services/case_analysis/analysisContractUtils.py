from __future__ import annotations

import re
from typing import Literal


def formatIdentifier(value: object, prefix: str, aliases: str) -> object:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


_format_identifier = formatIdentifier

CaseClaimType = Literal["reported", "analytical_inference", "unknown"]
CaseEpistemicStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
    "not_confirmed",
]
CaseAnalysisMode = Literal["case_overview", "question_answer"]


__all__ = [
    "CaseAnalysisMode",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "_format_identifier",
    "formatIdentifier",
]
