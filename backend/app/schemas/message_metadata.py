from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from typing_extensions import TypedDict


class FollowUpMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    root_ordinal: int
    round: int
    gap_id: str
    gap_key: str
    topic: str
    selected_gap_detail: dict[str, object]


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    action: Literal["conversation", "follow_up"]
    analysis_trace: dict[str, object]
    chat_followup: FollowUpMetadata


_metadata_adapter = TypeAdapter(MessageMetadata)


def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")
