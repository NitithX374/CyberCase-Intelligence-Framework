from typing import Annotated

from pydantic import Field, TypeAdapter

from app.services.case_analysis.contracts import AnalysisTrace, AnalysisTraceV3


ReadableAnalysisTrace = Annotated[
    AnalysisTrace | AnalysisTraceV3,
    Field(discriminator="version"),
]

_analysis_trace_reader = TypeAdapter(ReadableAnalysisTrace)


def read_analysis_trace(payload: object) -> ReadableAnalysisTrace:
    return _analysis_trace_reader.validate_python(payload)


__all__ = ["ReadableAnalysisTrace", "read_analysis_trace"]
