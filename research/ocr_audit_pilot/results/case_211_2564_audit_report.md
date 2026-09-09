# OCR Consistency Audit Report: Case 211/2564

- **Target Document**: `F:\งานอัยการ\Dataset\รายงานการสอบสวน 211-2564.docx`
- **Case Identifier**: คดีอาญาที่ ๒๑๑/๒๕๖๔ (สน.สุทธิสาร)
- **Offense**: ทำให้เสียทรัพย์ (ป.อ. มาตรา ๓๕๘)
- **Audit Type**: Intra-document recurring factual mention consistency audit under untrusted OCR conditions.
- **Audit Date**: 2026-09-09

---

## 1. Summary of Inconsistency Candidates

| Metric | Count |
| :--- | :---: |
| **Total Candidate Inconsistencies** | **11** |
| High-Risk Candidates | 5 |
| Medium-Risk Candidates | 2 |
| Low-Risk Candidates | 4 |
| Ambiguous Candidates | 2 |

### Distribution by Factual Category

| Category | Count | Primary Risk Manifestation |
| :--- | :---: | :--- |
| **TECHNICAL_IDENTIFIER** | 1 | Vehicle registration plate drift (`ทศ ๔๙๐๒` vs `ทห๙๙๐๒`) |
| **NUMBER_QUANTITY** | 1 | Seized evidence count jump (`๑ ชิ้น` vs `9 ชิ้น`) |
| **DATE_TIME** | 3 | Chronological inversion of report sign-off date; shift hours distortion |
| **LOCATION** | 2 | Bank name scanning stutter; tunnel portal lexical variation |
| **PERSON_NAME** | 3 | Surname whitespace split; placeholder drafting contamination (`นายทอง`, `นายดำ`) |
| **OTHER_FACTUAL_ELEMENT** | 1 | Punctuation noise in calendar year (`พ.ศ. ๒๕. ๖๔`) |

---

## 2. High & Medium Risk Findings Details

### [OCR-I-001] Taxi Vehicle License Plate Drift
- **Category**: `TECHNICAL_IDENTIFIER`
- **Risk Level**: **HIGH**
- **Potential Effect**: `IDENTIFIER_CHANGE`, `WRONG_ENTITY_SURFACE_FORM`, `AMBIGUITY`
- **Observed Surface Forms**:
  1. `ทศ ๔๙๐๒ กรุงเทพ` (Sheet 1, Para [38] — Accused statement)
  2. `ทห๙๙๐๒ กรุงเทพฯ` (Sheet 2, Para [47] — Garage owner statement)
  3. `ทศ ๙๙๐๒ กรุงเทพฯ` (Sheet 3, Para [52] — Investigation summary)
  4. `ทห๙๙๐๒ กทม` (Sheet 3, Para [52] — Accused confession)
  5. `ทห ๙๙๐๒ กรุงเทพฯ` (Sheet 3, Para [54] — Investigator analysis)
- **Mechanism**: Visual glyph confusions between Thai consonants `ศ` $\leftrightarrow$ `ห` and Thai numerals `๔` (4) $\leftrightarrow$ `๙` (9), alongside spacing and province abbreviation variations.

### [OCR-I-002] Physical Stone Evidence Quantity Jump
- **Category**: `NUMBER_QUANTITY`
- **Risk Level**: **HIGH**
- **Potential Effect**: `NUMERIC_CHANGE`, `AMBIGUITY`
- **Observed Surface Forms**:
  1. `๑ ชิ้น` (Sheet 1, Para [26], [34]; Sheet 3, Para [52] — narrative & witness testimony)
  2. `9 ชิ้น` (Sheet 1, Para [36] — formal physical evidence list entry `๑.๒.๑`)
- **Mechanism**: Visual curve/swirl substitution between Thai numeral `๑` and Arabic digit `9`. Creates a major evidence discrepancy between 1 piece and 9 pieces.

### [OCR-I-004] Investigation Report Sign-off Date Inversion
- **Category**: `DATE_TIME`
- **Risk Level**: **HIGH**
- **Potential Effect**: `DATE_CHANGE`, `AMBIGUITY`
- **Observed Surface Forms**:
  1. `๒๑ มิถุนายน` (Sheet 1, Para [05] — Cover date)
  2. `3 มิถุนายน ๒๕๖๔` (Sheet 3, Para [62] — Investigating officer signature)
- **Mechanism**: Arabic numeral `3` misrecognized from Thai numeral `๒` or `๒๑`. This creates an impossible chronology: Para [22] cites a court detention warrant from `๑๖ มิถุนายน ๒๕๖๔`, which the 3 June sign-off date would predate by 13 days.

### [OCR-I-003] Daily Operating Shift End Time
- **Category**: `DATE_TIME`
- **Risk Level**: **MEDIUM**
- **Potential Effect**: `DATE_CHANGE`, `AMBIGUITY`
- **Observed Surface Forms**:
  1. `๑๔.๐๐ น.` (Sheet 1, Para [38] — Accused statement: shift ends at 14:00)
  2. `๐๔.๐๐ น.` (Sheet 2, Para [47] — Garage owner: shift ends at 04:00)
- **Mechanism**: Digit substitution in the tens place of the hour (`๑` $\leftrightarrow$ `๐`). Shifts an ordinary 12-hour evening shift (16:00–04:00) into an unlikely 22-hour continuous shift (16:00–14:00).

### [OCR-I-005] Supervisory Review Date Corruption
- **Category**: `DATE_TIME`
- **Risk Level**: **MEDIUM**
- **Potential Effect**: `DATE_CHANGE`, `AMBIGUITY`
- **Observed Surface Forms**:
  1. `๒) มิถุนายน ๒๕๖๔` (Sheet 4, Para [72] — Deputy Superintendent signature)
  2. `๒๓ มิถุนายน ๒๕๖๔` (Sheet 4, Para [76] — Superintendent signature)
- **Mechanism**: Closing parenthesis `)` substituted for Thai digit `๒` or `๑` in the day-of-month slot.

### [OCR-I-010 & 011] Case Template Placeholder Contamination
- **Category**: `PERSON_NAME`
- **Risk Level**: **HIGH** (Ambiguous Referent)
- **Observed Surface Forms**:
  - Complainant: `นายมณธนัฐ ติสสพงษ์กุล` vs. `นายทอง` (Table 0)
  - Accused: `นายไพรวัลย์ แอ้ชัยภูมิ` vs. `นายดำ` (Table 0)
- **Context**: Table 0 appended to the file is a legal drafting/exercise prompt that replaced real party names with traditional placeholder names (`นายทอง`, `นายดำ`). Naive entity extractors will falsely split parties or invent co-conspirators.

---

## 3. Methodological Implications for Attribution & Summarization

1. **Faithful Quoting Propagates Error**: A strict extractive baseline (B2-lite / B3-core) will produce **100% citation validity** by directly quoting `9 ชิ้น` or `ทศ ๔๙๐๒`, yet commit a **document-fidelity failure** against case reality.
2. **Need for Pre-generation Consistency Checks**: LLM grounding without intra-document entity reconciliation cannot resolve OCR corruptions; an auditing pass is necessary to flag conflicting variants before generating definitive claims.
