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


class CaseViewExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: Literal["gliner2"] = "gliner2"
    model: str
    revision: str = Field(pattern=r"^[a-f0-9]{40}$")
    library_version: str
    device: str
    threshold: float = Field(gt=0, lt=1)
    input_claim_ids: ClaimIds
    excluded_claim_ids: ClaimIds
    duration_ms: float = Field(ge=0)
