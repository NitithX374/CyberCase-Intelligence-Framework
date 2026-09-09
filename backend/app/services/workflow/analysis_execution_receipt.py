from copy import deepcopy

from app.services.workflow.chat_run_locks import lock_owned_running_run, lock_run_thread


async def persist_analysis_receipt(session_factory, run_id, worker_id, receipt):
    async with session_factory() as db, db.begin():
        thread = await lock_run_thread(db, run_id)
        run = await lock_owned_running_run(db, run_id, worker_id)
        if thread is None or run is None:
            raise RuntimeError("Analysis receipt lost run ownership")
        payload = dict(run.request_payload)
        previous = payload.get("analysis_execution")
        if (
            isinstance(previous, dict)
            and previous.get("run_attempt") != run.attempt_count
        ):
            history = list(payload.get("analysis_previous_attempts", []))
            history.append(previous)
            payload["analysis_previous_attempts"] = history
        current = deepcopy(receipt)
        current["run_attempt"] = run.attempt_count
        payload["analysis_execution"] = current
        run.request_payload = payload
        await db.flush()
