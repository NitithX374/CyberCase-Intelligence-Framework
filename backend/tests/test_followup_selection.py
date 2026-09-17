import pytest

from app.schemas.case_followups import CaseFollowUpAnswer
from app.services.followup.contracts import answer_indicates_unavailable
from app.services.followup.case_followup import (
    CaseFollowUpError,
    CaseFollowUpHistoryError,
)


def test_answer_indicates_unavailable() -> None:
    # Thai phrases
    assert answer_indicates_unavailable("ไม่มีข้อมูลครับ") is True
    assert answer_indicates_unavailable("ยังไม่ทราบค่ะ") is True
    assert answer_indicates_unavailable("ไม่รู้") is True
    assert answer_indicates_unavailable("ไม่สามารถระบุได้") is True
    assert answer_indicates_unavailable("ไม่มีเลย") is True

    # English phrases
    assert answer_indicates_unavailable("unknown") is True
    assert answer_indicates_unavailable("unavailable") is True
    assert answer_indicates_unavailable("not provided") is True
    assert answer_indicates_unavailable("i don't know") is True
    assert answer_indicates_unavailable("n/a") is True
    assert answer_indicates_unavailable("idk") is True

    # Factual responses should NOT be marked as unavailable
    assert answer_indicates_unavailable("IP 192.168.1.1") is False
    assert answer_indicates_unavailable("ผู้ใช้งานคือ Admin สมชาย") is False
    assert answer_indicates_unavailable("เกิดเหตุเวลา 14:30 น.") is False


def test_case_followup_answer_validation() -> None:
    # answered requires an answer
    with pytest.raises(ValueError, match="Answered follow-ups require an answer"):
        CaseFollowUpAnswer(gap_id="G-01", disposition="answered", answer=None)
    with pytest.raises(ValueError, match="Answered follow-ups require an answer"):
        CaseFollowUpAnswer(gap_id="G-01", disposition="answered", answer="   ")

    # unavailable/skipped cannot include an answer
    with pytest.raises(ValueError, match="Unavailable or skipped follow-ups cannot include an answer"):
        CaseFollowUpAnswer(gap_id="G-01", disposition="unavailable", answer="known")
    with pytest.raises(ValueError, match="Unavailable or skipped follow-ups cannot include an answer"):
        CaseFollowUpAnswer(gap_id="G-01", disposition="skipped", answer="some info")

    # valid answered normalizes fields
    ans = CaseFollowUpAnswer(gap_id="  G-01  ", disposition="answered", answer="  factual answer  ")
    assert ans.gap_id == "G-01"
    assert ans.answer == "factual answer"

    # valid skipped allows None answer
    skipped = CaseFollowUpAnswer(gap_id="G-02", disposition="skipped", answer=None)
    assert skipped.gap_id == "G-02"
    assert skipped.answer is None


def test_legacy_followup_engine_removed() -> None:
    import app.services.followup as followup_pkg

    # Legacy modules are not exported and do not exist
    assert not hasattr(followup_pkg, "select_followup_gap")
    assert not hasattr(followup_pkg, "evaluate_followup_outcome")
    assert not hasattr(followup_pkg, "AnthropicFollowUpPolicy")
    assert not hasattr(followup_pkg, "FollowUpDecision")
    assert not hasattr(followup_pkg, "FollowUpExchange")

    with pytest.raises(ModuleNotFoundError):
        import app.services.followup.decision  # noqa: F401

    with pytest.raises(ModuleNotFoundError):
        import app.services.followup.policy  # noqa: F401

