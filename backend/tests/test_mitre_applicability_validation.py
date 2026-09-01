from uuid import uuid4

import pytest

from app.services.case_analysis.mitre_applicability_validation import (
    validate_mitre_applicability,
)
from app.services.chat.raw_evidence import RawEvidenceSource


SEMANTIC_FIXTURES = [
    ("phone_theft_th", "โทรศัพท์มือถือที่วางไว้บนโต๊ะสูญหาย", "SKIP", None),
    ("laptop_theft_th", "คนร้ายนำโน้ตบุ๊กออกจากห้องพัก", "SKIP", None),
    (
        "cctv_assault_th",
        "คดีทำร้ายร่างกายมีกล้องวงจรปิดบันทึกภาพคนเดินออกจากอาคาร",
        "SKIP",
        None,
    ),
    ("transfer_fraud_th", "ผู้เสียหายโอนเงินเพื่อซื้อสินค้าที่ไม่ส่งมา", "SKIP", None),
    (
        "computer_property_dispute_th",
        "คู่กรณีพิพาทกันเรื่องกรรมสิทธิ์เครื่องคอมพิวเตอร์",
        "SKIP",
        None,
    ),
    ("computer_theft_en", "A desktop computer was physically stolen.", "SKIP", None),
    (
        "powershell_th",
        "พบ PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23",
        "RETRIEVE",
        "PowerShell.exe เชื่อมต่อไปยัง 198.51.100.23",
    ),
    (
        "unknown_login_th",
        "บัญชีอีเมลถูกเข้าสู่ระบบจากอุปกรณ์ที่ไม่รู้จัก",
        "RETRIEVE",
        "ถูกเข้าสู่ระบบจากอุปกรณ์ที่ไม่รู้จัก",
    ),
    (
        "phishing_th",
        "อีเมลปลอมพาไปยังหน้าเว็บที่ขโมยรหัสผ่าน",
        "RETRIEVE",
        "หน้าเว็บที่ขโมยรหัสผ่าน",
    ),
    (
        "web_shell_en",
        "SQL injection was followed by a web shell upload.",
        "RETRIEVE",
        "SQL injection was followed by a web shell upload",
    ),
    (
        "ransomware_execution_en",
        "Ransomware executed and encrypted files on the workstation.",
        "RETRIEVE",
        "Ransomware executed and encrypted files",
    ),
    (
        "remote_control_en",
        "RustDesk was used to remotely control the workstation without authorization.",
        "RETRIEVE",
        "remotely control the workstation without authorization",
    ),
    (
        "mixed_case_en",
        "A laptop was stolen. Later, its account logged in from an unknown device.",
        "RETRIEVE",
        "account logged in from an unknown device",
    ),
    ("ambiguous_account_th", "พบข้อมูลบัญชีผู้ใช้ในโทรศัพท์", "SKIP", None),
    ("ambiguous_system_th", "มีการใช้งานระบบ", "SKIP", None),
    ("ambiguous_ip_th", "มี IP address ระบุอยู่ในเอกสาร", "SKIP", None),
]


@pytest.mark.parametrize(
    ("case_name", "content", "decision", "trigger"),
    SEMANTIC_FIXTURES,
    ids=[fixture[0] for fixture in SEMANTIC_FIXTURES],
)
def test_semantic_fixture_contract(
    case_name: str,
    content: str,
    decision: str,
    trigger: str | None,
) -> None:
    source = RawEvidenceSource(message_id=uuid4(), content=content)
    payload = {
        "decision": decision,
        "source_message_ids": [str(source.message_id)] if trigger else [],
        "trigger_text": [trigger] if trigger else [],
    }
    result = validate_mitre_applicability(payload, [source])
    assert result.decision == decision, case_name
    assert result.failure_code is None


def test_mixed_sources_cite_only_the_cyber_source() -> None:
    theft = RawEvidenceSource(message_id=uuid4(), content="A laptop was stolen.")
    login = RawEvidenceSource(
        message_id=uuid4(),
        content="The email account logged in from an unknown device.",
    )
    result = validate_mitre_applicability(
        {
            "decision": "RETRIEVE",
            "source_message_ids": [str(login.message_id)],
            "trigger_text": ["logged in from an unknown device"],
        },
        [theft, login],
    )
    assert result.decision == "RETRIEVE"
    assert result.source_message_ids == [str(login.message_id)]


def test_multi_message_behavior_can_cite_each_authoritative_source() -> None:
    email = RawEvidenceSource(
        message_id=uuid4(),
        content="The victim received a fake login email.",
    )
    credentials = RawEvidenceSource(
        message_id=uuid4(),
        content="The victim entered credentials on the linked website.",
    )
    result = validate_mitre_applicability(
        {
            "decision": "RETRIEVE",
            "source_message_ids": [
                str(email.message_id),
                str(credentials.message_id),
            ],
            "trigger_text": [
                "received a fake login email",
                "entered credentials on the linked website",
            ],
        },
        [email, credentials],
    )
    assert result.decision == "RETRIEVE"
    assert set(result.source_message_ids) == {
        str(email.message_id),
        str(credentials.message_id),
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"decision": "RETRIEVE", "source_message_ids": [], "trigger_text": []},
        {
            "decision": "RETRIEVE",
            "source_message_ids": ["unknown-assistant-message"],
            "trigger_text": ["PowerShell"],
        },
        {
            "decision": "RETRIEVE",
            "source_message_ids": ["unknown-rag-context"],
            "trigger_text": ["PowerShell"],
        },
        {
            "decision": "RETRIEVE",
            "source_message_ids": ["source"],
            "trigger_text": ["invented trigger"],
        },
        {
            "decision": "RETRIEVE",
            "source_message_ids": ["source"],
            "trigger_text": ["powershell executed"],
        },
        {
            "decision": "RETRIEVE",
            "source_message_ids": ["source"],
            "trigger_text": [""],
        },
        {
            "decision": "SKIP",
            "source_message_ids": [],
            "trigger_text": [],
            "reasoning": "extra output is forbidden",
        },
    ],
)
def test_invalid_or_unattributable_output_fails_closed(payload: object) -> None:
    source = RawEvidenceSource(message_id=uuid4(), content="PowerShell executed")
    result = validate_mitre_applicability(payload, [source])
    assert result.decision == "SKIP"
    assert result.source_message_ids == []
    assert result.trigger_text == []
    assert result.failure_code is not None


def test_trigger_must_be_an_exact_source_span() -> None:
    source = RawEvidenceSource(message_id=uuid4(), content="PowerShell executed")
    result = validate_mitre_applicability(
        {
            "decision": "RETRIEVE",
            "source_message_ids": [str(source.message_id)],
            "trigger_text": ["powershell executed"],
        },
        [source],
    )
    assert result.decision == "SKIP"
    assert result.failure_code == "mitre_applicability_invalid_grounding"
