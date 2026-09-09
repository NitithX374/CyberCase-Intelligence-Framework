from copy import deepcopy

from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure


class ClaimAnchoredFailure(CaseAnalysisFailure):
    def __init__(
        self, code: str, message: str, receipt: dict[str, object] | None = None
    ):
        super().__init__(code, message)
        self.receipt = deepcopy(receipt or {})
