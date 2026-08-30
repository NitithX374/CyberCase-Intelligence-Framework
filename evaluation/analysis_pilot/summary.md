# Analysis-Isolation Pilot: RAW_DIRECT vs EXTRACTED_STATE Summary

- **Evaluation Date**: 2026-08-18 03:23:23
- **Analysis Model**: `openai/gpt-5.6-luna` (temperature=0.0, max_tokens=2048)
- **Extraction Model**: `openai/gpt-5.6-luna` (prompt=openai/gpt-5.6-luna)
- **Judge Model**: `qwen/qwen3.8-27b` (temperature=0.0)
- **Prompt Version**: `pilot_analysis_v1`
- **Cases Evaluated**: 10 (Stratified 4 Scenarios × 2 Languages)

## Primary Metrics Summary

| Condition | Supported Probe Coverage | Epistemic Probe Violation Rate | Factual Error Probe Rate |
| :--- | :---: | :---: | :---: |
| **RAW_DIRECT** | 100.0% | 6.2% | 4.2% |
| **EXTRACTED_STATE** | 92.5% | 0.0% | 4.2% |

> Note: Supported Probe Coverage measures recall of known supported facts (higher is better). Epistemic Probe Violation Rate measures assertion of ungrounded causal/attribution/negation/certainty claims (lower is better). Factual Error Probe Rate measures susceptibility to swapped entities/timestamps.

## Epistemic Violation Breakdown by Type

| Condition | Certainty Strengthening | Causality Insertion | Attribution Insertion | Negation Flip |
| :--- | :---: | :---: | :---: | :---: |
| **RAW_DIRECT** | 0.0% (0/4) | 0.0% (0/4) | 0.0% (0/4) | 25.0% (1/4) |
| **EXTRACTED_STATE** | 0.0% (0/4) | 0.0% (0/4) | 0.0% (0/4) | 0.0% (0/4) |

## Per-Case Results

| Case ID | Lang | Scenario | Condition | Supported Cov. | Epistemic Viol. | Factual Error | Ext. Status | Latency |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `sv-en-001` | en | email_execution | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 6811ms |
| `sv-en-001` | en | email_execution | EXTRACTED_STATE | 75.0% | 0.0% | 0.0% | `candidate` | 10268ms |
| `sv-th-053` | th | email_execution | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 9560ms |
| `sv-th-053` | th | email_execution | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 8136ms |
| `sv-en-002` | en | forwarded_attachment | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 6823ms |
| `sv-en-002` | en | forwarded_attachment | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 6534ms |
| `sv-th-054` | th | forwarded_attachment | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 9310ms |
| `sv-th-054` | th | forwarded_attachment | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 7211ms |
| `sv-en-004` | en | mail_endpoint_review | RAW_DIRECT | 100.0% | 25.0% | 0.0% | N/A | 7752ms |
| `sv-en-004` | en | mail_endpoint_review | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 7183ms |
| `sv-th-052` | th | mail_endpoint_review | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 10612ms |
| `sv-th-052` | th | mail_endpoint_review | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 7061ms |
| `sv-en-003` | en | received_document | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 9102ms |
| `sv-en-003` | en | received_document | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 5814ms |
| `sv-th-051` | th | received_document | RAW_DIRECT | 100.0% | 0.0% | 25.0% | N/A | 10667ms |
| `sv-th-051` | th | received_document | EXTRACTED_STATE | 100.0% | 0.0% | 25.0% | `candidate` | 7009ms |
| `sv-en-005` | en | email_execution | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 5923ms |
| `sv-en-005` | en | email_execution | EXTRACTED_STATE | 50.0% | 0.0% | 0.0% | `candidate` | 6902ms |
| `sv-th-057` | th | email_execution | RAW_DIRECT | 100.0% | 0.0% | 0.0% | N/A | 8092ms |
| `sv-th-057` | th | email_execution | EXTRACTED_STATE | 100.0% | 0.0% | 0.0% | `candidate` | 8007ms |

## Selected Pilot Dataset Cases

1. **`sv-en-001`** (EN, `email_execution`)
   - *Narrative*: Analyst-001-A owned account-001-primary. account-001-primary sent email-001 at 2025-04-01T08:00Z, and it included attachment-001.zip. attachment-001.zip was stored as document-001.exe, and it executed process-001. process-001 ran on endpoint-001-A at 2025-04-01T09:10Z. account-001-secondary authenticated on endpoint-001-B at 2025-04-01T08:00Z; account-001-secondary may have signed in from 198.51.100.2 at 2025-04-01T08:50Z. Employee-001-B submitted credentials to email-001 at 2025-04-01T08:30Z; endpoint-001-B may not have connected to 192.0.2.2.
2. **`sv-th-053`** (TH, `email_execution`)
   - *Narrative*: Analyst-053-A เป็นเจ้าของ account-053-primary. account-053-primary ส่ง email-053 เมื่อ 2025-04-13T08:00Z และสิ่งดังกล่าว มี attachment-053.zip. attachment-053.zip ถูกจัดเก็บเป็น document-053.exe และสิ่งดังกล่าว เรียกใช้งาน process-053. process-053 ทำงานบน endpoint-053-A เมื่อ 2025-04-13T09:10Z. account-053-secondary ยืนยันตัวตนบน endpoint-053-B เมื่อ 2025-04-13T08:00Z; account-053-secondary อาจลงชื่อเข้าใช้จาก 198.51.100.54 เมื่อ 2025-04-13T08:50Z. Employee-053-B ส่งข้อมูลรับรองไปยัง email-053 เมื่อ 2025-04-13T08:30Z; endpoint-053-B อาจไม่ได้เชื่อมต่อไปยัง 192.0.2.54.
3. **`sv-en-002`** (EN, `forwarded_attachment`)
   - *Narrative*: account-002-primary forwarded email-002 at 2025-04-02T08:00Z. email-002 contained attachment-002.zip, and it was saved as document-002.exe. document-002.exe opened process-002, and it ran on endpoint-002-A at 2025-04-02T09:10Z. Analyst-002-A owned account-002-primary; account-002-secondary authenticated on endpoint-002-B at 2025-04-02T08:00Z. Employee-002-B submitted credentials to email-002 at 2025-04-02T08:30Z; account-002-secondary may have signed in from 198.51.100.3 at 2025-04-02T08:50Z. endpoint-002-B may not have connected to 192.0.2.3.
4. **`sv-th-054`** (TH, `forwarded_attachment`)
   - *Narrative*: account-054-primary ส่งต่อ email-054. email-054 บรรจุ attachment-054.zip และสิ่งดังกล่าว ถูกบันทึกเป็น document-054.exe. document-054.exe เปิด process-054 และสิ่งดังกล่าว ทำงานบน endpoint-054-A เมื่อ 2025-04-14T09:10Z. Analyst-054-A เป็นเจ้าของ account-054-primary; account-054-secondary ยืนยันตัวตนบน endpoint-054-B. Employee-054-B ส่งข้อมูลรับรองไปยัง email-054 เมื่อ 2025-04-14T08:30Z; account-054-secondary อาจลงชื่อเข้าใช้จาก 198.51.100.55 เมื่อ 2025-04-14T08:50Z. endpoint-054-B อาจไม่ได้เชื่อมต่อไปยัง 192.0.2.55.
5. **`sv-en-004`** (EN, `mail_endpoint_review`)
   - *Narrative*: Employee-004-B submitted credentials to email-004. account-004-secondary authenticated on endpoint-004-B at 2025-04-04T08:00Z; endpoint-004-B may not have connected to 192.0.2.5. account-004-primary sent email-004 at 2025-04-04T08:00Z. email-004 contained attachment-004.zip, and it was stored as document-004.exe. document-004.exe opened process-004, and it ran on endpoint-004-A at 2025-04-04T09:10Z. Analyst-004-A owned account-004-primary; account-004-secondary may have signed in from 198.51.100.5 at 2025-04-04T08:50Z.
6. **`sv-th-052`** (TH, `mail_endpoint_review`)
   - *Narrative*: Employee-052-B ส่งข้อมูลรับรองไปยัง email-052. account-052-secondary ยืนยันตัวตนบน endpoint-052-B เมื่อ 2025-04-12T08:00Z; endpoint-052-B อาจไม่ได้เชื่อมต่อไปยัง 192.0.2.53. account-052-primary ส่ง email-052 เมื่อ 2025-04-12T08:00Z. email-052 บรรจุ attachment-052.zip และสิ่งดังกล่าว ถูกจัดเก็บเป็น document-052.exe. document-052.exe เปิด process-052 และสิ่งดังกล่าว ทำงานบน endpoint-052-A เมื่อ 2025-04-12T09:10Z. Analyst-052-A เป็นเจ้าของ account-052-primary; account-052-secondary อาจลงชื่อเข้าใช้จาก 198.51.100.53 เมื่อ 2025-04-12T08:50Z.
7. **`sv-en-003`** (EN, `received_document`)
   - *Narrative*: account-003-secondary may have signed in from 198.51.100.4 at 2025-04-03T08:50Z; endpoint-003-B may not have connected to 192.0.2.4. Analyst-003-A owned account-003-primary. account-003-secondary authenticated on endpoint-003-B; account-003-primary received email-003. email-003 included attachment-003.zip, and it was saved as document-003.exe. document-003.exe executed process-003, and it ran on endpoint-003-A at 2025-04-03T09:10Z. Employee-003-B submitted credentials to email-003 at 2025-04-03T08:30Z.
8. **`sv-th-051`** (TH, `received_document`)
   - *Narrative*: account-051-secondary อาจลงชื่อเข้าใช้จาก 198.51.100.52 เมื่อ 2025-04-11T08:50Z; endpoint-051-B อาจไม่ได้เชื่อมต่อไปยัง 192.0.2.52. Analyst-051-A เป็นเจ้าของ account-051-primary. account-051-secondary ยืนยันตัวตนบน endpoint-051-B; account-051-primary ได้รับ email-051. email-051 มี attachment-051.zip และสิ่งดังกล่าว ถูกบันทึกเป็น document-051.exe. document-051.exe เรียกใช้งาน process-051 และสิ่งดังกล่าว ทำงานบน endpoint-051-A เมื่อ 2025-04-11T09:10Z. Employee-051-B ส่งข้อมูลรับรองไปยัง email-051 เมื่อ 2025-04-11T08:30Z.
9. **`sv-en-005`** (EN, `email_execution`)
   - *Narrative*: Analyst-005-A owned account-005-primary. account-005-primary sent email-005 at 2025-04-05T08:00Z, and it included attachment-005.zip. attachment-005.zip was stored as document-005.exe, and it executed process-005. process-005 ran on endpoint-005-A at 2025-04-05T09:10Z. account-005-secondary authenticated on endpoint-005-B at 2025-04-05T08:00Z; account-005-secondary may have signed in from 198.51.100.6 at 2025-04-05T08:50Z. Employee-005-B submitted credentials to email-005 at 2025-04-05T08:30Z; endpoint-005-B may not have connected to 192.0.2.6.
10. **`sv-th-057`** (TH, `email_execution`)
   - *Narrative*: Analyst-057-A เป็นเจ้าของ account-057-primary. account-057-primary ส่ง email-057 และสิ่งดังกล่าว มี attachment-057.zip. attachment-057.zip ถูกจัดเก็บเป็น document-057.exe และสิ่งดังกล่าว เรียกใช้งาน process-057. process-057 ทำงานบน endpoint-057-A เมื่อ 2025-04-17T09:10Z. account-057-secondary ยืนยันตัวตนบน endpoint-057-B; account-057-secondary อาจลงชื่อเข้าใช้จาก 198.51.100.58 เมื่อ 2025-04-17T08:50Z. Employee-057-B ส่งข้อมูลรับรองไปยัง email-057 เมื่อ 2025-04-17T08:30Z; endpoint-057-B อาจไม่ได้เชื่อมต่อไปยัง 192.0.2.58.