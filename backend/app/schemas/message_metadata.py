from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from typing_extensions import TypedDict


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    action: Literal["conversation"]
    analysis_trace: dict[str, object]


_metadata_adapter = TypeAdapter(MessageMetadata)


def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")
