
from __future__ import annotations

from pydantic import BaseModel

from app.services.case_analysis import case_analysis
from app.services.case_analysis.pipeline_config import read_pipeline
from app.services.case_analysis.provider_stage import resolve_target


async def invoke_gap_stage(
    *,
    config_value: dict[str, object],
    stage: str,
    system: str,
    content: dict[str, object],
    schema: type[BaseModel],
) -> BaseModel:
    config = read_pipeline(config_value)
    calls: list[dict[str, object]] = []
    return await case_analysis.request_stage(
        client=None,
        target=resolve_target(config),
        config=config,
        stage=f"gap_{stage}",
        system=system,
        content=content,
        schema=schema,
        calls=calls,
    )

__all__ = ["invoke_gap_stage"]
