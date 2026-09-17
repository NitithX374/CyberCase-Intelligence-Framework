from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from typing_extensions import TypedDict


class FollowUpMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    root_ordinal: int
    round: int
    source_analysis_id: str
    source_revision: int
    gap: dict[str, object]
    answer: dict[str, object]
    clarification_session_id: str
    workflow_thread_id: str
    target_information: str | None


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    action: Literal["conversation", "follow_up"]
    analysis_trace: dict[str, object]
    chat_followup: FollowUpMetadata


_metadata_adapter = TypeAdapter(MessageMetadata)


def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")
