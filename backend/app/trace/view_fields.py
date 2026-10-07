from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.trace.claims import ClaimIds


class CaseClaimSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$")
    start: int = Field(ge=0, strict=True)
    end: int = Field(gt=0, strict=True)

    @model_validator(mode="after")
    def ordered_offsets(self):
        if self.end <= self.start:
            raise ValueError("Claim span end must follow its start")
        return self


class CaseViewFieldIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    view: Literal["party", "timeline_event", "impact"]
    record_index: int = Field(ge=0)
    field: Literal["name", "role", "time", "event", "description"]
    text: str = Field(min_length=1)
    reason: Literal["unresolved", "ambiguous"]
    claim_id: str = Field(pattern=r"^A-\d{2,}$")


class CaseViewExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str = Field(default="legacy", min_length=1, max_length=200)
    model: str
    revision: str | None = Field(default=None, pattern=r"^[a-f0-9]{40}$")
    library_version: str | None = None
    device: str | None = None
    threshold: float | None = Field(default=None, gt=0, lt=1)
    quantization: str | None = None
    runtime_revision: str | None = Field(default=None, pattern=r"^[a-f0-9]{40}$")
    field_resolution_issues: list[CaseViewFieldIssue] = Field(default_factory=list)
    input_claim_ids: ClaimIds
    excluded_claim_ids: ClaimIds
    duration_ms: float = Field(ge=0)
    status: Literal["completed", "failed", "skipped"] = "completed"
    warning: str | None = Field(default=None, max_length=200)
    items_dropped: int = Field(default=0, ge=0)
