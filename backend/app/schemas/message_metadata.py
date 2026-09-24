from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from typing_extensions import TypedDict

from app.services.analysis.contracts import CaseAnalysisTrace


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    action: Literal["conversation"]
    analysis_trace: dict[str, object]


_metadata_adapter = TypeAdapter(MessageMetadata)


def message_trace(trace: CaseAnalysisTrace) -> dict[str, object]:
    return {
        "version": trace.version,
        "validation_status": trace.validation_status,
        "analysis_mode": trace.analysis_mode,
        "summary": trace.summary,
        "claims": [claim.model_dump(mode="json") for claim in trace.claims],
        "grounding": trace.grounding.model_dump(mode="json") if trace.grounding else None,
    }


def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")
