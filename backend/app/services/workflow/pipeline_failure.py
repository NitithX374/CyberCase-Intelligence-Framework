from __future__ import annotations

from typing import Any
from uuid import UUID

from app.services.workflow.pipeline_dependencies import PipelineDependencies


async def record_failure(
    dependencies: PipelineDependencies,
    run_id: UUID,
    worker_id: str,
    error_code: str,
    error_message: str,
    followup_metadata_json: dict[str, Any] | None = None,
) -> None:
    async with dependencies.session_factory() as failure_db:
        await dependencies.worker_type(failure_db).fail_run(
            run_id,
            worker_id,
            error_code,
            error_message,
            followup_metadata_json=followup_metadata_json,
        )
