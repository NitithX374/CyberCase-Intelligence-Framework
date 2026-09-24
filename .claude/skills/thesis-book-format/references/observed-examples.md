# What the example books actually did

Read on 2026-09-23 from `F:\ตัวอย่างเล่ม นศ 256x\ตัวอย่างเล่ม นศ\`. This file is
the evidence behind `SKILL.md`; it records what was seen and what was not, so a
rule can be checked rather than trusted.

## The books

| File | Read? |
|---|---|
| **Enhanced Golf Swing Evaluation with MediaPipe.docx** | **fully — the English model** |
| เว็บแอปพลิเคชันตรวจสอบชนิดงูด้วย Machine Learning.pdf (84 p) | front matter, ch.1, four body pages rendered |
| TransportationManagementSystem.pdf (67 p) | full contents |
| โครงงานระบบตรวจจับและแจ้งเตือนการรุกล้ำของรถขุด.pdf (127 p) | contents page 1 only |
| ระบบจัดสรรงานและติดตามผลการช่วยเหลือลูกค้าองค์กร.pdf (123 p) | not read |
| การพัฒนาระบบสำรวจเก็บข้อมูลแหล่งน้ำ 3 มิติ … RTK.pdf (115 p) | not read |
| Freemason.pdf (111 p) | not read |
| Account Receivable (UI).pdf (74 p) | not read |
| เว็บแอปพลิเคชันบอร์ดประชาสัมพันธ์ออนไลน์.pdf / .docx (73 p) | not read |
| TransportationManagementSystem.docx | not read |

## The English book — measured, not inferred

Read with `python-docx`: 867 paragraphs, 15 tables, 38 inline images.

Page A4; margins left 1.5″, right 1.0″, top 1.5″, bottom 1.0″.

Styles as defined in the file:

```
Normal      TH SarabunPSK 16pt
Heading 1   TH SarabunPSK 20pt bold, centred, 20pt before / 6pt after
Heading 2   TH SarabunPSK 16pt bold, left,    18pt before / 6pt after
Caption     bold; every caption paragraph is centre-aligned
```

TH SarabunPSK carries the English text as well — there is no separate Latin
body font.

Style usage across the document: Caption 231, Normal 195, List Paragraph 85,
table of figures 52, toc 2 ×25, Heading 2 ×25, toc 1 ×10, Heading 1 ×6. Six
Heading 1 paragraphs is six chapters. The Caption count far exceeds the 53
captioned objects because ordinary body paragraphs around figures were left in
the Caption style — sloppiness in the source, not a convention to copy.

### Heading tree, verbatim

```
Chapter 1 / Introduction
  1.1 Background and Importance of the Project
  1.2 Objective
  1.3 Scope
  1.4 Expected Benefits
  1.5 Timeline
  1.6 Report Outline
Chapter 2 / Literature Review
  2.1 Related Studies
  2.2 Preliminary
Chapter 3 / Methodology
  3.1 Co-op Journey
  3.2 Dataset Pre-processing
Chapter 4 / System Development
  4.1 Data preparation   4.2 Train model   4.3 Test model   4.4 Evaluate process
Chapter 5 / Experiment
  5.1 Dataset   5.2 Training   5.3 Evaluation Metrics
  5.4 Results and Discussion   5.5 Evaluation for web application
  5.6 Web Application Overview
Chapter 6 / Conclusion
  6.1 Main Finding   6.2 Limitations   6.3 Problem Encountered
  6.4 Solution of the Problems   6.5 Personal Achievements during Co-op
```

A `Heading 1` paragraph holds both lines — `Chapter 3`, newline, `Methodology`.

Only two heading levels exist. `3.4.2.1 Login System (Figure 3-6)` and
`3.2.2.3 Angular Features:` are ordinary paragraphs, so chapter 3's design
subsections (System Architecture, Use Case Diagram, Use Case description, ER,
Data Dictionary) never appear in the contents at all.

This book is a **co-op report** — 3.1 Co-op Journey and 6.5 Personal
Achievements during Co-op belong to that, not to the general format. Chapter 3
in a project book carries the design work instead.

### Caption placement — checked in body order

Walking the document body in order, every single case is object first, caption
after:

```
TABLE <7 rows>          →  Caption  "Table 1-1 Gantt Chart"
IMG                     →  Caption  "Figure 3-1 Examples of all 3 shooting angles"
TABLE <8 rows>          →  Caption  "Table 3-3 Use Case description: Sign up"
IMG                     →  Caption  "Figure 3-9 ER Diagram"
```

So **table captions sit below the table in the English book**, the opposite of
the Thai books. Numbering is a Word SEQ field: the caption's runs are
`'Figure '`, `''`, `''`, `''`, `'3'`, `''`, … — a field result, not typed text.
Body references are written `(Figure 3-6)` and `Table 3-2`, with the hyphen.

### Figures by chapter

- ch.3 — 9 figures: shooting angles, pose landmarks, HPE before/after, variable
  assignment, swing sequences, **System Architecture Overview**, two **Use Case
  Diagrams**, **ER Diagram**.
- ch.4 — 10 figures, **all screenshots of code**, each followed by a line-range
  walkthrough (`Lines 1-9  Import necessary libraries and modules:`). A listing
  too long for one screenshot continues as `Train model (2)`, `(3)`.
- ch.5 — 12 figures: a feature-correlation plot, five confusion matrices, then
  UI screenshots (`Homepage Before Login`, `Sign Up Page`, `Video Upload Page
  (2)`…), plus 7 metric tables.
- ch.1 and ch.3 each open with a table: `Table 1-1 Gantt Chart` for the
  timeline, `Table 3-1 Co-op Journey`.

Front matter lists are `LIST OF TABLES` then `LIST OF FIGURES`, each with a
`Table  …  Page` / `Figure  …  Page` header row.

## The Thai books — spine cross-check

All three read agree on six chapters: บทนำ · ทฤษฎีที่เกี่ยวข้อง · การวิเคราะห์และ
การออกแบบ *or* ขั้นตอนและวิธีการดำเนินงาน · การพัฒนาระบบ · ผลการดำเนินโครงงาน ·
บทสรุปและแนวทางการพัฒนาต่อ — then บรรณานุกรม and ภาคผนวก.

Chapter 1 sections match the English book's 1.1–1.5. The excavator book splits
the last one into `1.5 ทรัพยากรที่ใช้ในการจัดทำโครงงาน` and `1.6 ระยะเวลาในการ
ดำเนินงาน`. None of the Thai books has a Report Outline section; the English
book's `1.6 Report Outline` is its own.

Chapter 2 varies: the snake book has ทฤษฎีที่เกี่ยวข้อง / งานวิจัยที่เกี่ยวข้อง /
เครื่องมือ, while the transportation book is a flat list of one technology per
section with no related-work subsection at all.

Chapter 3 contents differ by book — the snake book does System Architecture,
Use Case Diagram, Use Case Description, Activity Diagram, Data Dictionary,
Class Diagram; the transportation book does System Architecture Design, ER
Diagram, Data Table, Flowchart, and has no use case or class diagram.

Two formatting points where the Thai books differ and the English book governs:

- **Table captions go above** the table in the Thai books, below in the English
  one.
- A figure is often followed by `คำอธิบาย ภาพที่ 3-1` and a numbered list. The
  English book has no equivalent; it explains in body text.

Visual style agrees across both languages: `ภาพที่ 3-2 use case diagram` in the
snake book is black on white — square system boundary, stick-figure actor
outside, ellipses inside, dashed `<<include>>` / `<<extend>>` arrows, no fills.
Its `ภาพที่ 3-1 System Architecture` is the exception: an icon diagram of a
person, a monitor and a database cylinder with labels on the arrows.

## Still unverified

- Bibliography style — no book's reference pages were read.
- Whether the English book has a Thai abstract as well.
- Appendix conventions beyond the snake book's ก/ข/ค lettering.
