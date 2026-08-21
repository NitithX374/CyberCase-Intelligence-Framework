from __future__ import annotations;


class ReportServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ReportGenerationConflict(ReportServiceError):
    pass


class ReportNotFound(ReportServiceError):
    pass
