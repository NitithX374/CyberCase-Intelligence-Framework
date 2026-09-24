---
name: thesis-book-format
description: The department's project book format in English — chapter spine, front matter, page setup, figure and table captions, and the diagram style its own example books use. Use when writing, restructuring or reviewing any chapter of the book, when producing a figure or table for it, or when deciding what a chapter should contain.
---

# Project book format

## Where this comes from

`F:\ตัวอย่างเล่ม นศ 256x\ตัวอย่างเล่ม นศ\` holds the books the department handed
out as examples. **One of them is written in English —
`Enhanced Golf Swing Evaluation with MediaPipe.docx` — and that is the model to
follow.** Everything below was measured or read out of it. The Thai books are a
cross-check for the chapter spine only; where they disagree with the English
book on formatting, the English book wins, because it is the format this book
is written in.

`references/observed-examples.md` records what each book actually did, so a rule
here can be traced back rather than trusted.

## Page setup

| | |
|---|---|
| Page | A4 (8.27 × 11.69 in) |
| Margins | left 1.5″, right 1.0″, top 1.5″, bottom 1.0″ |
| Body font | TH SarabunPSK 16 pt — used for English text too |
| Body alignment | justified |
| Heading 1 | TH SarabunPSK 20 pt bold, centred, 20 pt before / 6 pt after |
| Heading 2 | TH SarabunPSK 16 pt bold, left, 18 pt before / 6 pt after |
| Caption | bold, centred |

Heading 1 is one paragraph holding two lines: `Chapter 3` then the chapter
title on the next line.

Heading 2 is `3.1 Section Title`. **Deeper levels are not heading styles** —
`3.4.2.1 Login System` is an ordinary body paragraph in the example. Follow
that, or the table of contents fills with four-level noise.

## The chapter spine

Six chapters. The English example runs:

| Ch | Title | Sections |
|----|-------|----------|
| 1 | Introduction | Background and Importance of the Project · Objective · Scope · Expected Benefits · Timeline · Report Outline |
| 2 | Literature Review | Related Studies · Preliminary |
| 3 | Methodology | the design work: System Architecture · Use Case Diagram · Use Case Description tables · ER Diagram · Data Dictionary |
| 4 | System Development | one section per step of the build |
| 5 | Experiment | Dataset · Training · Evaluation Metrics · Results and Discussion · Web Application Overview |
| 6 | Conclusion | Main Finding · Limitations · Problem Encountered · Solution of the Problems |

Then the bibliography, then appendices.

The Thai books agree on the six-chapter spine and on chapters 1, 2, 4 and 6.
They title chapter 3 การวิเคราะห์และการออกแบบ or ขั้นตอนและวิธีการดำเนินงาน and
chapter 5 ผลการดำเนินโครงงาน, which is the same work under different names.

Chapter 5 is where the system is shown running and measured; chapter 6 closes
it. A book that stops at chapter 4 is not finished, whatever its word count.

## What each chapter's figures are

Three chapters want three different kinds of picture, and this is the part most
easily got wrong.

- **Chapter 3 — diagrams.** Use case, ER, architecture. Drawn plain.
- **Chapter 4 — screenshots of source code.** One per thing being explained,
  captioned `Figure 4-1 Train model`, and followed by a line-range walkthrough:
  `Lines 1-9  Import necessary libraries and modules: …`. Prose about code with
  no screenshot is not the convention here. Long listings continue as
  `Figure 4-6 Train model (2)`, `Figure 4-7 Train model (3)`.
- **Chapter 5 — screenshots of the running interface** (`Figure 5-7 Homepage
  Before Login`) and result plots such as confusion matrices, plus metric
  tables.

## Front matter

Abstract · Acknowledgements · Table of Contents · **List of Tables** · **List
of Figures** · then Chapter 1.

Each list carries a two-column header — `Table … Page`, `Figure … Page` — and
one entry per item with its page number. Front-matter folios are letters; the
body is numbered from 1 at the first page of Chapter 1.

## Figures and tables

- Numbered per chapter: `Figure 3-1`, `Table 3-1`, restarting each chapter.
- **Both figure and table captions go BELOW the object, centred.** Tables too —
  this differs from the Thai books, which put table captions above.
- The caption label is bold; use a real Word SEQ field so numbering and the
  lists stay correct when something is inserted.
- Body text refers to them as `(Figure 3-6)` and `Table 3-2`, with the hyphen.
- Use Case Description is a table per use case, captioned
  `Table 3-3 Use Case description: Sign up`.
- Data Dictionary is a table per entity, captioned
  `Table 3-6 Data dictionary: user`.

## Diagram style

The example diagrams are plain: black on white, no fill colours, one thin
stroke weight, one font, a square boundary box around a use case diagram. They
look like default draw.io output because that is what they are.

So: no pastel fills, no rounded boxes in a different colour each, no
bold-title-plus-grey-subtitle inside every box, no coloured callout boxes.
Anything a diagram cannot say in a label belongs in the caption or the body
text under it.

## Before calling a chapter done

1. Sections match the spine, and nothing required is missing.
2. Every figure and table is numbered, captioned below and centred, and listed
   in List of Figures or List of Tables.
3. Chapter 4 figures are code with line-range explanations; chapter 5 figures
   are screens and results.
4. Headings use Heading 1 / Heading 2 only; deeper numbering is body text.
5. Bibliography entries are all cited in the body, and vice versa.
