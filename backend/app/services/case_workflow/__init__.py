"""Running an analysis, and answering a question about one.

Both are a single model call that the caller is waiting for, so both happen in
the request that asked for them. There is no run row, no queue, no claiming and
no polling: the process doing the work is the process that was asked, and
``validate_single_process_runtime`` guarantees there is only one.

The database is never held across a model call. Each function reads what it
needs in one short transaction, thinks with the connection released, and writes
what it produced in another.
"""

from app.services.case_workflow.analysis import (
    analysis_freshness,
    external_context,
    get_latest_case_analysis,
    read_case_for_analysis,
    run_case_analysis,
    store_analysis,
)
from app.services.case_workflow.answering import (
    answer_case_question,
    answer_history,
    answer_instruction,
    sent_exchange,
)
from app.services.case_workflow.shared import (
    CaseUnderAnalysis,
    CaseWorkflowError,
    next_ordinal,
    owned_case,
)

__all__ = [
    "CaseUnderAnalysis",
    "CaseWorkflowError",
    "analysis_freshness",
    "answer_case_question",
    "answer_history",
    "answer_instruction",
    "external_context",
    "get_latest_case_analysis",
    "next_ordinal",
    "owned_case",
    "read_case_for_analysis",
    "run_case_analysis",
    "sent_exchange",
    "store_analysis",
]
