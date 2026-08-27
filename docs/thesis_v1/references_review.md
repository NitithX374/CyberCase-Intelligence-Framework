# References Review

ตรวจเมื่อ 27 สิงหาคม 2569 โดยใช้หน้า publisher/standards body/official project เป็นหลัก DOI ที่ไม่จำเป็นสำหรับ official software documentation ไม่ได้ถูกสร้างเพิ่ม

## LLM

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `vaswani2017attention` | VERIFIED | NeurIPS proceedings: title, authors, 2017 | Transformer background |

## RAG และ Retrieval

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `lewis2020rag` | VERIFIED | NeurIPS 2020 proceedings | RAG foundation |
| `karpukhin2020dpr` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2020.emnlp-main.550` | dense retrieval |
| `cormack2009rrf` | VERIFIED | ACM DOI `10.1145/1571941.1572114` | rank fusion |
| `chen2024bgem3` | VERIFIED | arXiv `2402.03216` author metadata | multilingual dense/sparse embedding |

## Grounding, factuality และ calibration

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `rashkin2023measuring` | VERIFIED | ACL Anthology/Computational Linguistics, DOI `10.1162/coli_a_00486` | source attribution |
| `gao2023alce` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2023.emnlp-main.398` | citation correctness/completeness |
| `min2023factscore` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2023.emnlp-main.741` | atomic factuality |
| `scire2024fenice` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2024.findings-acl.841` | NLI/claim factuality |
| `jiang2021calibrating` | VERIFIED | ACL Anthology/TACL, DOI `10.1162/tacl_a_00407` | calibration |
| `geng2024survey` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2024.naacl-long.366` | calibration survey |

## Clarification และ Follow-up

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `kumar2020clarq` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2020.acl-main.651` | clarification dataset |
| `lee2023clarification` | VERIFIED | ACL Anthology, DOI `10.18653/v1/2023.findings-emnlp.772` | ambiguity/clarification pipeline |

## MITRE ATT&CK และ Cyber Threat Intelligence

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `mitreAttack` | VERIFIED | official `attack.mitre.org` | ATT&CK definitions |
| `oasisStix21` | VERIFIED | OASIS Standard, 10 June 2021 | STIX 2.1 |

## Forensic / Investigative AI

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `michelet2024report` | VERIFIED | FSI: Digital Investigation 48 (2024), DOI `10.1016/j.fsidi.2023.301683` | LLM-assisted forensic report writing |

## Cybersecurity LLM

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `scanlon2023digitalforensics` | VERIFIED | FSI: Digital Investigation 46 (2023), DOI `10.1016/j.fsidi.2023.301609` | benefits/risks of LLMs in digital forensics |

## System Technologies

| Key | Status | Verification source | ใช้ใน thesis |
|---|---|---|---|
| `fastapiDocs` | VERIFIED | official FastAPI documentation | technology reference |
| `nextjsDocs` | VERIFIED | official Next.js documentation | technology reference |
| `pydanticDocs` | VERIFIED | official Pydantic documentation | technology reference |
| `sqlalchemyDocs` | VERIFIED | official SQLAlchemy documentation | technology reference |
| `postgresqlDocs` | VERIFIED | official PostgreSQL 16 docs | technology reference |
| `qdrantDocs` | VERIFIED | official Qdrant docs | technology reference |
| `neo4jDocs` | VERIFIED | official Neo4j docs | technology reference |

## ช่องว่างของเอกสารอ้างอิง

1. ยังไม่มีแหล่งอ้างอิงที่ผ่านการคัดเลือกสำหรับภาระงานจริงของอัยการ/ผู้สืบสวน จึงไม่กล่าวตัวเลขหรือแนวโน้มเชิงปริมาณในบทที่ 1
2. ยังไม่มีงาน peer-reviewed ที่ตรงกับ claim–evidence–gap workflow ของ CyberCase ทั้งระบบ; thesis จึงอธิบายเป็น system design ไม่ใช่ novelty
3. OCR/HTR ในบทที่ 2 อธิบายในระดับแนวคิดและสถานะ implementation ยังไม่อ้าง benchmark/model paper เพราะยังไม่ได้เลือก final ingestion method
4. ก่อน final submission ควรตรวจรูปแบบชื่อผู้แต่งที่มี diacritics (`Scirè`, `Gaëtan`, `Büttcher`, `Rocktäschel`) กับระบบจัดบรรณานุกรมที่มหาวิทยาลัยใช้; BibTeX ฉบับนี้ใช้ ASCII ในบาง key/author fields เพื่อ compatibility
5. System documentation citations ควรใส่เฉพาะหากคู่มือรูปเล่มยอมรับ web references และควรปรับ access date ให้ตรงวัน freeze ฉบับส่ง
