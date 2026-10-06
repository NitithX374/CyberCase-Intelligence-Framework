from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from time import perf_counter

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.analysis.view_model import (
    VIEW_LIBRARY_VERSION,
    VIEW_MODEL_ID,
    VIEW_MODEL_REVISION,
    load_view_model,
)
from app.config import settings
from app.errors import CaseAnalysisFailure
from app.trace.claims import CaseAnalysisClaim
from app.trace.support import item_support
from app.trace.trace import CaseImpactItem, CaseInvolvedParty, CaseTimelineItem
from app.trace.view_fields import CaseClaimSpan, CaseViewExtraction

VIEW_STRUCTURES = {
    "party": [
        "name::str::Named person, organization or identifiable account mentioned in the claim",
        "role::str::Explicit noun phrase identifying the party's role, such as complainant or victim; not an action or verb phrase; absent if unstated",
    ],
    "timeline_event": [
        "time::str::Explicit date or time expression attached to the event",
        "event::str::The event occurring at that time, not a proposed or unrelated event",
    ],
    "impact": [
        "description::str::Explicit reported loss, damage, affected asset or service interruption; preserve uncertainty",
    ],
}


class SelectedField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    start: int = Field(ge=0, strict=True)
    end: int = Field(gt=0, strict=True)
    confidence: float = Field(ge=0, le=1)

    def resolve(self, claim: CaseAnalysisClaim) -> tuple[str, CaseClaimSpan]:
        original = claim.text[self.start : self.end]
        if self.end > len(claim.text) or self.end <= self.start or original.strip() != self.text:
            raise ValueError("GLiNER2 field does not match its original Claim span")
        start = self.start + len(original) - len(original.lstrip())
        end = self.end - len(original) + len(original.rstrip())
        return claim.text[start:end], CaseClaimSpan(claim_id=claim.claim_id, start=start, end=end)


class SelectedParty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: SelectedField | None = None
    role: SelectedField | None = None


class SelectedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: SelectedField | None = None
    event: SelectedField | None = None


class SelectedImpact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: SelectedField | None = None


class SelectedViews(BaseModel):
    model_config = ConfigDict(extra="forbid")

    party: list[SelectedParty]
    timeline_event: list[SelectedEvent]
    impact: list[SelectedImpact]

    @field_validator("party", "timeline_event", "impact", mode="before")
    @classmethod
    def empty_sdk_structure(cls, value: object) -> object:
        return [] if isinstance(value, dict) and not value else value


@dataclass
class DerivedCaseViews:
    parties: list[CaseInvolvedParty]
    timeline: list[CaseTimelineItem]
    impacts: list[CaseImpactItem]
    extraction: CaseViewExtraction


def full_claim_span(claim: CaseAnalysisClaim) -> CaseClaimSpan:
    return CaseClaimSpan(claim_id=claim.claim_id, start=0, end=len(claim.text))


def materialize_views(claim: CaseAnalysisClaim, selected: SelectedViews):
    shared = {
        "claim_ids": [claim.claim_id],
        "support": item_support([claim.claim_id], {claim.claim_id: claim}),
    }
    parties = []
    for candidate in selected.party:
        fields = {key: value.resolve(claim) for key, value in candidate if value is not None}
        if "name" in fields:
            parties.append(
                CaseInvolvedParty(
                    name=fields["name"][0],
                    role=fields["role"][0] if "role" in fields else None,
                    field_spans={key: value[1] for key, value in fields.items()},
                    **shared,
                )
            )
    timeline = []
    for candidate in selected.timeline_event:
        fields = {key: value.resolve(claim) for key, value in candidate if value is not None}
        if {"time", "event"} <= fields.keys():
            timeline.append(
                CaseTimelineItem(
                    time=fields["time"][0],
                    event=claim.text,
                    field_spans={"time": fields["time"][1], "event": full_claim_span(claim)},
                    **shared,
                )
            )
    impacts = []
    for candidate in selected.impact:
        if candidate.description is not None:
            candidate.description.resolve(claim)
            impacts.append(
                CaseImpactItem(
                    description=claim.text,
                    field_spans={"description": full_claim_span(claim)},
                    **shared,
                )
            )
    return parties, timeline, impacts


def consolidated(rows, fields):
    indexed = {}
    for row in rows:
        key = tuple(getattr(row, field) for field in fields)
        if key in indexed:
            previous = indexed[key]
            indexed[key] = previous.model_copy(
                update={
                    "claim_ids": list(dict.fromkeys([*previous.claim_ids, *row.claim_ids])),
                }
            )
        else:
            indexed[key] = row
    if len(indexed) > 64:
        raise ValueError("Case views exceed the existing 64-item display limit")
    return list(indexed.values())


def derive_claim_views(claims: Sequence[CaseAnalysisClaim]) -> DerivedCaseViews:
    started = perf_counter()
    eligible = [claim for claim in claims if claim.supporting_citations]
    excluded = [claim.claim_id for claim in claims if not claim.supporting_citations]
    parties, timeline, impacts = [], [], []
    if eligible:
        raw_results = load_view_model().extract([claim.text for claim in eligible], VIEW_STRUCTURES)
        try:
            for claim, raw in zip(eligible, raw_results, strict=True):
                party_rows, event_rows, impact_rows = materialize_views(
                    claim, SelectedViews.model_validate(raw)
                )
                parties.extend(party_rows)
                timeline.extend(event_rows)
                impacts.extend(impact_rows)
            parties = consolidated(parties, ("name", "role"))
            timeline = consolidated(timeline, ("time", "event"))
            impacts = consolidated(impacts, ("description",))
        except (ValueError, ValidationError) as error:
            raise CaseAnalysisFailure(
                "case_view_invalid",
                "GLiNER2 returned invalid Claim view spans or records",
                500,
            ) from error
    return DerivedCaseViews(
        parties,
        timeline,
        impacts,
        CaseViewExtraction(
            model=VIEW_MODEL_ID,
            revision=VIEW_MODEL_REVISION,
            library_version=VIEW_LIBRARY_VERSION,
            device=settings.case_view_device,
            threshold=settings.case_view_threshold,
            input_claim_ids=[claim.claim_id for claim in eligible],
            excluded_claim_ids=excluded,
            duration_ms=(perf_counter() - started) * 1000,
        ),
    )
