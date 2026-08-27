# Figures and Tables Plan

## Figures

| No. | Title | Chapter | Purpose | Source | Status |
|---|---|---|---|---|---|
| Figure 3-1 | CyberCase System Architecture | 3 | แสดง service boundaries และ external context | `diagrams/architecture.mmd` | CAN GENERATE FROM CODE |
| Figure 3-2 | Evidence Trust Boundary | 3 | แยก authoritative/derived/external/preview | `diagrams/trust_boundary.mmd` | CAN GENERATE FROM CODE |
| Figure 3-3 | CyberCase Use Case Diagram | 3 | แสดง use cases ของ persona ผู้ใช้ | `diagrams/use_case.puml` | CAN GENERATE FROM CODE |
| Figure 3-4 | Initial Analysis Sequence | 3 | message → RAG → analysis → gap → persist | `diagrams/initial_analysis_sequence.mmd` | CAN GENERATE FROM CODE |
| Figure 3-5 | Ask Question Sequence | 3 | ยืนยัน context reuse/no fresh RAG | `diagrams/ask_sequence.mmd` | CAN GENERATE FROM CODE |
| Figure 3-6 | Add Information and Clarification Sequence | 3 | แสดง action ที่กลายเป็น evidence | `diagrams/followup_sequence.mmd` | CAN GENERATE FROM CODE |
| Figure 3-7 | Report Generation Sequence | 3 | snapshot/idempotency/validation/PDF | `diagrams/report_sequence.mmd` | CAN GENERATE FROM CODE |
| Figure 3-8 | Simplified Database ER Diagram | 3 | แสดงห้าตาราง current baseline | `diagrams/er_diagram.mmd` | CAN GENERATE FROM CODE |
| Figure 3-9 | Proposed Claim–Evidence–Gap Model | 3/6 | แสดง target architecture ที่ยังไม่ครบ | ต้องสร้างหลัง freeze contract | TODO |
| Figure 5-1 | Case Intake | 5 | แสดง input และ navigation | current frontend runtime | SCREENSHOT REQUIRED |
| Figure 5-2 | Document Preview and Warning | 5 | แสดง preview-only boundary | current dirty working tree | SCREENSHOT REQUIRED |
| Figure 5-3 | Case Overview with Source Popover | 5 | แสดง analysis/provenance UX | หลังแก้ v3 reader หรือระบุ known gap | SCREENSHOT REQUIRED |
| Figure 5-4 | Awaiting Follow-up Chat | 5 | แสดงคำถามหนึ่งข้อและ answer action | seeded demo thread | SCREENSHOT REQUIRED |
| Figure 5-5 | Case Materials | 5 | แสดง raw user evidence labels | seeded demo thread | SCREENSHOT REQUIRED |
| Figure 5-6 | MITRE Technical Context | 5 | แสดง external context label | cyber fixture | SCREENSHOT REQUIRED |
| Figure 5-7 | Non-Cyber Technical Context Empty State | 5 | แสดง generalization behavior | general fixture | SCREENSHOT REQUIRED |
| Figure 5-8 | Report Workspace and Version History | 5 | แสดง persisted reports | seeded report data | SCREENSHOT REQUIRED |
| Figure 5-9 | Thai PDF Report | 5 | ตรวจ typography/sections/limitations | generated current report | SCREENSHOT REQUIRED |
| Figure 5-10 | Safe Error Modal | 5 | แสดง controlled conflict/error | controlled test/demo | SCREENSHOT REQUIRED |

## Tables

| No. | Title | Chapter | Purpose | Source | Status |
|---|---|---|---|---|---|
| Table 1-1 | Project Scope and Status | 1 | แยก implemented/ongoing/out-of-scope | implemented matrix | AVAILABLE |
| Table 2-1 | Theory-to-Design Implications | 2 | เชื่อม literature กับ architecture | Chapter 2 refs + code | AVAILABLE |
| Table 3-1 | Actors and Responsibilities | 3 | แยก persona/system services | route/auth audit | AVAILABLE |
| Table 3-2 | Main Use Case Descriptions | 3 | precondition/flow/result | routes/workflow | AVAILABLE |
| Table 3-3 | Evidence Trust Classes | 3 | authority boundary | raw evidence/prompt code | AVAILABLE |
| Table 3-4 | Failure Policies | 3 | เปรียบเทียบ fail-closed/fail-open | services/tests | AVAILABLE |
| Table 4-1 | Development Technologies | 4 | actual versions/constraints | manifests/Dockerfiles | AVAILABLE |
| Table 4-2 | Error and Idempotency Handling | 4 | implementation behavior | services/migrations | AVAILABLE |
| Table 5-1 | Component Development Status | 5 | current completion picture | repository audit | AVAILABLE |
| Table 5-2 | Automated Test Results | 5 | exact verified counts | 2026-08-27 tool runs | AVAILABLE |
| Table 5-3 | Exploratory Experiment Results | 5 | separate executed artifacts from final eval | research/experiments | AVAILABLE |
| Table 6-1 | V2 Development Priorities | 6 | priority/owner/evidence gate | revision notes | TODO |

## Rendering notes

- Export Mermaid/PlantUML ด้วย font ที่รองรับภาษาไทยและใช้ขาวดำให้พิมพ์ได้
- ทุก screenshot ต้องมี commit hash, working-tree status และ seed/demo-data note ในคำบรรยายภาพ
- ปิดบัง secrets, tokens, email/identifiers ที่ไม่ใช่ synthetic
- อย่าใช้ screenshot จากเอกสารเก่าหาก route/contract ไม่ตรง current checkout
- Figure 3-9 ต้องมีคำว่า “Proposed/Ongoing” อยู่ในภาพ ไม่พึ่งคำบรรยายใต้ภาพอย่างเดียว

