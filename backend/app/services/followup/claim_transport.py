from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


GAP_ANALYSIS_CLAIM_LIMIT = 64
GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS = 1_000


class GapAnalysisClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    text: str = Field(min_length=1, max_length=GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS)
    claim_type: Literal["reported", "analytical_inference", "unknown"]
    epistemic_status: Literal[
        "reported",
        "suspected",
        "contradicted",
        "not_established",
        "unknown",
        "not_confirmed",
    ]


def build_gap_analysis_claim_transport(
    claims: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    if len(claims) > GAP_ANALYSIS_CLAIM_LIMIT:
        raise ValueError("Gap Analysis claim transport exceeds the v3 claim limit")
    transported: list[GapAnalysisClaim] = []
    for claim in claims:
        value = dict(claim)
        text = value.get("text")
        if isinstance(text, str):
            value["text"] = text.strip()[:GAP_ANALYSIS_CLAIM_TEXT_MAX_CHARS]
        transported.append(GapAnalysisClaim.model_validate(value))
    claim_ids = [claim.claim_id for claim in transported]
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("Gap Analysis claim transport requires unique claim IDs")
    return [claim.model_dump(mode="json") for claim in transported]
