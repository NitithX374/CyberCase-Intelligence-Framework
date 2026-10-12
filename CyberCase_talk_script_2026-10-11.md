# สคริปต์พูดพร้อมจุดโค้ด · CyberCase (28 หน้า, 11 ต.ค. 2026)

แต่ละหน้ามี: **Highlight** (หน้านี้พูดเรื่องอะไร) · **บนสไลด์** (ชี้อะไรบนจอ) · **พูด** (script ภาษาอังกฤษ ตรงกับ speaker notes ในสไลด์ตอนนี้) · **ดูโค้ด / ดูไฟล์** · **ถ้าโดนถาม** · **ห้ามพูด**

- เลขหน้า = ลำดับใน editor ส่วน (วงกลม N) = เลขที่โชว์มุมขวาล่างของสไลด์
- โค้ดอ้างจาก repo `F:/Cybercase Framework` branch main commit 79f8b194 ตรวจเลขบรรทัดแล้ววันที่ 11 ต.ค. ถ้าดึงโค้ดใหม่ เลขบรรทัดอาจเลื่อน ให้ค้นชื่อฟังก์ชันแทน
- เวลาพูดคิดที่ 130 คำต่อนาที รวมทั้ง deck ประมาณ 23:00 นาที (2,991 คำ) หน้า setup ของ evaluation (21, 23, 25) ยาวที่สุด ถ้าเวลาไม่พอให้พูดแค่ส่วนแรกของ script หน้านั้น

## ภาพรวมทั้ง deck

| หน้า | (วงกลม) | Highlight | เวลา |
|---|---|---|---|
| 1 | – | แนะนำตัว และบอกขอบเขตงานของเรา: วิเคราะห์คดีแบบโต้ตอบ กับสร้างรายงาน | 0:17 |
| 2 | – | ปัญหาจริงจากนิติบัณฑิต: เอกสารเยอะ อ่านช้า ข้อเท็จจริงเปลี่ยน → เป้าหมายคือตอบ who / what / where / when จากเอกสารของคดีเอง และทุกประโยคตรวจย้อนได้ | 0:41 |
| 3 | – | ทุกประโยคในสรุปตามไปถึงคำจริงในเอกสารได้: model เขียนและเลือก ID ส่วน code ตรวจ ID และเติมคำจริง | 0:36 |
| 4 | – | งานแบ่งสองส่วน: Part 1 วิเคราะห์แล้วเก็บ 1 แถว ส่วน Part 2 สร้างรายงานจากแถวนั้นโดยไม่เรียก model | 0:36 |
| 5 | 1 | backend ตัวเดียวคุมทุกการเรียก บริการภายนอกมีแค่ Typhoon OCR, LLM ผ่าน OpenRouter และ RAG ที่เป็น downstream service (เรียกเฉพาะเมื่อจำเป็น) | 0:48 |
| 6 | – | เข้า Part 1: จาก source ไปจนได้ analysis ที่ตรวจแล้วและเก็บไว้ | 0:06 |
| 7 | 2 | ไฟล์ทุกชนิดกลายเป็นข้อความที่รู้ว่าแต่ละหน้าเริ่มตรงไหน และทั้งคดีต้องไม่เกิน 40,000 tokens | 0:52 |
| 8 | 3 | 7 ขั้นของการวิเคราะห์: สีกล่องบอกว่าใครทำ ข้าวหลามตัดแดง = code ตัดสิน → model เขียน ส่วน code ผูก ตรวจ และตัดสิน | 0:56 |
| 9 | 4 | ถามสิ่งที่ขาดก่อนวิเคราะห์: LLM หา gap ตามรายการ 5W1H แต่ code เป็นคนตัดสินว่าจะถามหรือไม่ | 0:52 |
| 10 | 5 | ค้น ATT&CK เฉพาะเมื่อ source บรรยายพฤติกรรมไซเบอร์ชัดเจน และ code ตรวจว่าข้อความที่ model ยกมามีอยู่จริงคำต่อคำ | 1:00 |
| 11 | 6 | Reader แค่ชี้ unit ID ส่วนคำที่โชว์ใน citation code เป็นคนคัดลอกจาก source เสมอ | 0:53 |
| 12 | 7 | 4 rules ใน code คัดว่าอะไรเข้า summary ได้ ส่วนคะแนน support จาก model บนเครื่องแค่เตือน ไม่กรอง | 0:59 |
| 13 | 8 | สรุปเขียนจาก claim ที่ผ่าน rules เท่านั้น ทุกประโยคลงท้ายด้วย claim ID และ code ตรวจทุก ID ถ้าผิดแม้ตัวเดียว ทั้ง analysis ล้ม | 0:54 |
| 14 | 9 | สิ่งที่ผู้สืบสวนเห็น: ทุกประโยคมีเลขยก กดแล้วไปยัง finding ที่ประโยคนั้นอิง | 0:18 |
| 15 | 10 | ปลายโซ่: เปิด finding แล้วเห็นหน้าเอกสารจริงพร้อม highlight คำที่อ้าง | 0:25 |
| 16 | 11 | แชทใช้หลักเดียวกัน: ทุกข้อความบอก basis และ code เก็บ citation เฉพาะที่ตรวจเจอจริง | 0:46 |
| 17 | – | เข้า Part 2: รายงานสร้างจาก JSON ที่ Part 1 เก็บไว้เท่านั้น | 0:15 |
| 18 | 12 | ไม่มี model ในรายงาน: 1 analysis = 1 report อ่านแถวที่เก็บไว้ แล้วเติม template เดียวทั้ง HTML และ PDF | 0:48 |
| 19 | 13 | แต่ละ section ของรายงานอ่านจาก field ในแถว JSON ไม่มีอะไรถูกเขียนตอนออกรายงาน | 0:38 |
| 20 | – | 3 การทดสอบ: ALCE (ตอบพร้อม citation), OCR error, usability 5 คน แต่ละอันมีหน้าวิธีทำกับหน้าผล | 0:23 |
| 21 | 14 | วิธีทดสอบ ALCE: LLM ตัวเดียวกัน 100 คำถาม เขียน 3 แบบ (A passages, B claims ทั้งหมด, C claims ที่ผ่าน check) เปลี่ยนแค่สิ่งที่มันอ่าน | 1:59 |
| 22 | 15 | เขียนจาก claim ไม่เสียอะไรที่วัดได้ (46.8 vs 47.8) และป้ายเตือนแม่นพอ ๆ กับ base rate (16.7% vs 15.0%) จึงใช้แค่เตือน | 1:16 |
| 23 | 16 | วิธีทดสอบ OCR: ทำ key fact ในข่าวไทย 100 ข่าวให้เสียแบบที่ Typhoon อ่านผิดจริง แล้วเทียบการวิเคราะห์ข้อความสะอาดกับข้อความเสีย | 1:44 |
| 24 | 17 | OCR อ่านผิด คำผิดกลายเป็นความจริงของคดี: ตัวเลขผิดถูกลอก 14/19 fact ที่ลบหายจาก summary 58/70 และไม่มีอันไหนถูกเตือน | 0:55 |
| 25 | 18 | วิธีทดสอบกับคน: 5 คน คดี phishing สมมติ 1 คดี 5 งาน วัดความง่ายต่องาน (SEQ) และ SUS ตอนจบ | 1:34 |
| 26 | 19 | ทุกคนทำครบ 5 งาน แต่ SUS 59.5 ต่ำกว่าค่าเฉลี่ย 68 สาเหตุหลักคือรอนาน (4 ใน 5 คน) | 0:36 |
| 27 | 20 | ข้อจำกัดที่ยอมรับ: พึ่งบริการภายนอก, ความฉลาดอยู่ที่ LLM, ไม่มีการตรวจความหมาย, OCR ผิดผ่านได้, ช้าและทดสอบเล็ก | 1:16 |
| 28 | – | สรุป 3 ข้อ: model เขียน code ผูกและตรวจ · rules คัด support แค่เตือน · report จาก JSON ไม่มี model และระบบไม่ตรวจข้อเท็จจริงนอกคดี ไม่ตัดสินคดี | 0:36 |

## ตัวเลขที่ต้องจำ

| เรื่อง | ตัวเลข |
|---|---|
| ขนาดคดีสูงสุด | 40,000 tokens ทุก source รวมกัน (เกิน → 413) · narrative ≤ 250,000 ตัวอักษร · PDF ≤ 50 หน้า |
| Follow-up | สูงสุด 3 รอบ × 3 คำถาม |
| Gate | แต่ละ source ≤ 4,000 ตัวอักษร รวม ≤ 20,000 |
| Support check | MPNet cosine ≥ 0.20 · mDeBERTa ≤ 512 tokens · LR ≥ 0.50 = supported |
| Judgement | ขอประโยคสูงสุด = claims ÷ 3 (2–8) เป็นการขอ ไม่บังคับ |
| ALCE | STR-EM 46.8 vs 47.8 · เตือน 16.7% vs base rate 15.0% · κ 0.52 |
| OCR | ตัวเลขผิดถูกลอก 14/19 (74%) · fact ที่ลบหาย 58/70 (83%) · ไม่มีอันไหนถูกเตือน |
| UAT | 5/5 ทำครบ · SUS 59.5 (SD 9.3, 95% CI 48.0–71.0) < 68 · 4/5 บอกว่าช้า |
| LLM | Gemma 4 26B (open-weight) ผ่าน OpenRouter |

---

## หน้า 1 · Cybercase Intelligence Framework

> **Highlight:** แนะนำตัว และบอกขอบเขตงานของเรา: วิเคราะห์คดีแบบโต้ตอบ กับสร้างรายงาน

**บนสไลด์:**
- ชื่อโปรเจกต์ อาจารย์ 3 ท่าน ชื่อและรหัสนักศึกษา
- ทักทายสั้น ๆ แล้วไปหน้าถัดไป ไม่ต้องอ่านชื่อทุกคนบนจอ

**พูด** (~0:17 นาที)

> Good morning. I'm Kritsakorn. My part of CyberCase is interactive case analysis and report generation: how we turn the files of a cybercrime case into a summary that an investigator can check, and into a report.

---

## หน้า 2 · Reading a case file is slow, and mistakes slip in

> **Highlight:** ปัญหาจริงจากนิติบัณฑิต: เอกสารเยอะ อ่านช้า ข้อเท็จจริงเปลี่ยน → เป้าหมายคือตอบ who / what / where / when จากเอกสารของคดีเอง และทุกประโยคตรวจย้อนได้

**บนสไลด์:**
- การ์ดแดง What goes wrong = ปัญหา 3 ข้อ
- การ์ดฟ้า What they want first = สิ่งที่อยากรู้ก่อน 3 ข้อ
- กล่องดำล่าง Our aim = เป้าหมายของระบบ

**พูด** (~0:41 นาที)

> Before the system, the problem. We asked a law graduate what goes wrong when reading a case file. Three things: with many documents everything blurs and mistakes slip in; long, complex files take a long time; and facts shift, so every statement needs a document behind it. We also asked what they want to know first from a case file: who is involved, what each one did, and where and when. That is our aim: answer these from the case's own documents, with every sentence traceable to its source.

**ดูโค้ด:**
- `backend/app/analysis/prompts.py:119` `CASE_CHECKLIST` รายการ who / what / when / where / why / how / how much ที่ระบบใช้หา gap ตรงกับการ์ดฟ้า

**ถ้าโดนถาม:**
- *คนที่สัมภาษณ์คือใคร* → นิติบัณฑิตหนึ่งคน ไม่เอ่ยชื่อ เป็นข้อมูลเพื่อกำหนดโจทย์ ไม่ใช่การวัดผล

---

## หน้า 3 · An AI wrote this case summary. Which sentence can you check?

> **Highlight:** ทุกประโยคในสรุปตามไปถึงคำจริงในเอกสารได้: model เขียนและเลือก ID ส่วน code ตรวจ ID และเติมคำจริง

**บนสไลด์:**
- การ์ดฟ้า The model: Summary sentence → Claim A-02 (ประโยคลงท้าย [A-02])
- ลูกศร unit ID ข้ามจากการ์ดฟ้าไปการ์ดแดง = จุดที่ model ส่งต่อให้ code
- การ์ดแดง Our code: Source unit (ID + ลายนิ้วมือ) → คำจริงพร้อมไฟล์และหน้า

**พูด** (~0:36 นาที)

> Imagine an AI has written the summary of a case file. Which of its sentences can you check? In our system, every one. Here is how we do it: each summary sentence ends with the claims it rests on, each claim points to a numbered unit of a source, and our code fills in the exact words from the page. In the next minutes I will show how we build that chain, step by step, and where it stops.

**ดูโค้ด:**
- `backend/app/sources/evidence.py:28` `evidence_revision` ลายนิ้วมือ 16 ตัวของข้อความทั้ง source
- `backend/app/sources/evidence.py:45` รูปแบบ ID เต็ม `SRC:U006-<revision>`
- `backend/app/trace/evidence_binding.py:42` `bind_citations` code ตรวจ ID แล้วคัดลอกคำจริง
- `backend/app/analysis/claim_gate.py:47` `check_judgement_references` ทุก [A-xx] ในสรุปต้องเป็น claim ที่ส่งให้จริง
- `backend/app/trace/summary.py:12` `scan_summary` ตัดสรุปเป็นประโยคตามวงเล็บ [A-xx]

**ถ้าโดนถาม:**
- *ทำไมไม่ให้ LLM ยกคำพูดเอง* → LLM อาจแก้คำนิดเดียวแล้วยังดูเหมือนคำจริง ส่วน ID ตรวจได้แน่นอนว่ามีจริงไหม และคำที่โชว์มาจาก source เสมอ

---

## หน้า 4 · We analyse the case, then build the report from it

> **Highlight:** งานแบ่งสองส่วน: Part 1 วิเคราะห์แล้วเก็บ 1 แถว ส่วน Part 2 สร้างรายงานจากแถวนั้นโดยไม่เรียก model

**บนสไลด์:**
- การ์ดแดง Part 1 → one stored analysis
- การ์ดฟ้า Part 2 → no model call
- สีแถบซ้ายของสไลด์บอกว่าอยู่ Part ไหน

**พูด** (~0:36 นาที)

> We split the work in two. In part one, interactive case analysis, the investigator adds sources, answers our follow-up questions and gets a checked analysis, which we store as one row. In part two, we build the report only from that stored row, with no model call. So the report can never say something the analysis did not store. Slides of part one carry a red bar on the left, slides of part two a blue one.

**ดูโค้ด:**
- `backend/app/analysis/pipeline.py:70` `advance_case` Part 1 ทั้งหมดอยู่ในฟังก์ชันเดียว
- `backend/app/reports/generate.py:38` `generate_report` จุดเริ่มของ Part 2

---

## หน้า 5 (วงกลม 1) · How the parts connect: one backend makes every call

> **Highlight:** backend ตัวเดียวคุมทุกการเรียก บริการภายนอกมีแค่ Typhoon OCR, LLM ผ่าน OpenRouter และ RAG ที่เป็น downstream service (เรียกเฉพาะเมื่อจำเป็น)

**บนสไลด์:**
- Users → Frontend (Next.js) → Backend (FastAPI, 6 ส่วน) → PostgreSQL
- แถวล่าง: Typhoon OCR, LLM, RAG (เส้นประจาง = downstream)

**พูด** (~0:48 นาที)

> Here is how the parts connect. The investigator works in a Next.js web app, which talks only to our FastAPI backend: a REST call goes in, and JSON with live progress steps comes back. Every feature lives in that backend: reading sources, follow-up and chat, the analysis pipeline, the support check with its local models, and the report. The backend is the only part that calls outside services: Typhoon OCR for page images, the LLM, Gemma 4 through OpenRouter, for JSON answers, and, only when needed, the RAG service, drawn faded because it is a downstream service. Everything the case owns is stored in PostgreSQL.

**ดูโค้ด:**
- `docker-compose.yml:39-40` model ที่ใช้จริง `google/gemma-4-26b-a4b-it` และ provider ที่ล็อกไว้ `nextbit/bf16,coreweave/bf16`
- `backend/app/llm/payload.py:60` ล็อก provider ตามลำดับด้วย `allow_fallbacks: False`
- `backend/app/llm/request.py:130` `request_stage` ทุกการเรียก LLM ผ่านฟังก์ชันนี้ retry รอ 2 วินาทีที่ `:36` และ `:81`
- `backend/app/analysis/stream.py:25` `announce(step)` และ `:50` `progress_response` ส่ง step สด (SSE) ไปหน้าจอ
- `backend/app/main.py:71-77` ไม่ยอมเปิดถ้ามีมากกว่า 1 worker เพราะ analysis รันอยู่ใน request
- `backend/app/sources/ingestion/recognition.py:48` `TyphoonRecognizerConfig` การเรียก Typhoon OCR
- `backend/app/analysis/technical_context/rag_client.py:20` `request_rag` จุดเดียวที่เรียก RAG service

**ถ้าโดนถาม:**
- *ทำไมส่งข้อมูลคดีขึ้น cloud* → Gemma เป็น open-weight ย้ายไปรันในเครือข่ายปิดได้ ต้นแบบนี้ใช้ OpenRouter และนับเป็นข้อจำกัด (หน้า 27)
- *RAG ทำอะไร* → คืนตาราง technique ของ ATT&CK เป็นงานของอีกคน เราเรียกใช้เป็น downstream service

---

## หน้า 6 · Interactive case analysis

> **Highlight:** เข้า Part 1: จาก source ไปจนได้ analysis ที่ตรวจแล้วและเก็บไว้

**พูด** (~0:06 นาที)

> Part one: how we go from the case sources to a stored, checked analysis.

---

## หน้า 7 (วงกลม 2) · How we turn every file into text with its pages

> **Highlight:** ไฟล์ทุกชนิดกลายเป็นข้อความที่รู้ว่าแต่ละหน้าเริ่มตรงไหน และทั้งคดีต้องไม่เกิน 40,000 tokens

**บนสไลด์:**
- ข้าวหลามตัด what kind? แยก PDF / photo / Word / typed
- PDF วาดทุกหน้าเป็นรูปแล้วส่ง Typhoon OCR แม้มี text layer
- photo หมุนตาม EXIF ก่อน
- ข้าวหลามตัด 40,000 tokens: เกิน = Refused และไม่เก็บอะไร

**พูด** (~0:52 นาที)

> First, how we turn files into text. The investigator adds a typed narrative or uploads a file, and we route it by its kind. A PDF we draw page by page and send every page to Typhoon OCR, even when it has a text layer, so every document takes the same path. A photo we turn upright first; a Word file we read directly; typed text we keep as typed. We keep a map of where each page starts, so every quote can later show its page. Before we store anything, we weigh the whole case: if all the sources together would pass forty thousand tokens, we refuse the file and store nothing.

**ดูโค้ด:**
- `backend/app/sources/ingestion/service.py:60` แยกเส้นทางตามชนิดไฟล์ `:89` `ingest_pdf` `:117` `ingest_image`
- `backend/app/sources/ingestion/files.py:83` `render_pdf_page` วาดหน้า PDF เป็นรูป `:103` `normalize_image` หมุนตาม EXIF
- `backend/app/sources/ingestion/provenance.py:5` `bind_exact_page_spans` แผนที่ว่าแต่ละหน้าเริ่มที่ตัวอักษรที่เท่าไร
- `backend/app/sources/service.py:156-158` ชั่งทั้งคดี เกินงบ → `source_too_large` (413)
- `backend/app/llm/settings.py:7-8` `SOURCE_TOKEN_BUDGET = 40_000` และ `SOURCE_OVERHEAD_TOKENS = 100`
- `backend/app/config.py:98` PDF ได้สูงสุด 50 หน้า

**ถ้าโดนถาม:**
- *ทำไม OCR ทุกหน้าแม้มี text layer* → ให้ทุกเอกสารผ่านทางเดียวกัน และ text layer ของ PDF ภาษาไทยมักเพี้ยน เช่น สระลอย ลำดับอักษรผิด
- *40,000 มาจากไหน* → งบที่ prompt ของ Reader รับได้พร้อมคำสั่งและคำตอบ เป็นเพดานที่ตั้งตอนออกแบบ

**ห้ามพูด:** อย่าบอกว่า OCR ถูกต้อง 100% เพราะหน้า 24 จะแสดงว่ามันพลาด

---

## หน้า 8 (วงกลม 3) · How we analyse a case: the model writes, code decides

> **Highlight:** 7 ขั้นของการวิเคราะห์: สีกล่องบอกว่าใครทำ ข้าวหลามตัดแดง = code ตัดสิน → model เขียน ส่วน code ผูก ตรวจ และตัดสิน

**บนสไลด์:**
- ฟ้าเทา = LLM, ครีม = code, ขาว = model บนเครื่อง, เส้นประ = downstream
- ขั้น 1 gap check: ถ้ามีเรื่องต้องถาม → ถามแล้วหยุด ไม่จ่ายค่าขั้นแพง
- ขั้น 2 gate, 3 Reading, 4–5 binding และ rules, 6 Judgement, 7 ตรวจและเก็บ

**พูด** (~0:56 นาที)

> This is how we analyse a case, in seven steps. The colours tell you who does the work: blue-grey boxes are LLM calls, cream boxes are our own code, white boxes are models on our own server, the dashed box is the downstream service, and every red diamond is a decision our code makes. Step one is a cheap gap check; if something worth asking is missing, we ask and stop there. Step two decides whether ATT&CK is needed. In step three the model reads and writes claims; in steps four and five our code links and filters them. Step six writes the summary, and step seven checks it and stores it. The model writes; our code links, checks and decides.

**ดูโค้ด:**
- `backend/app/analysis/pipeline.py:70-93` `advance_case` ทั้ง pipeline อ่านจากบนลงล่าง
- `backend/app/analysis/pipeline.py:116` `assess_gaps` (ขั้น 1) `:131` `retrieve_technical_context` (ขั้น 2) `:148` `write_analysis` (ขั้น 3–6) `:165` `bind_to_case` (ขั้น 7)
- `backend/app/analysis/write.py:47` `write_trace` Reading → binding → rules → Judgement, views และ support check พร้อมกัน

**ถ้าโดนถาม:**
- *ทำไมแยก Reading กับ Judgement* → Reader ผูกกับ source ทีละ unit ส่วนคนสรุปเห็นแค่ claim ที่ผ่านการตรวจ ทุกประโยคจึงอ้างย้อนได้

---

## หน้า 9 (วงกลม 4) · How we find what is missing, and ask first

> **Highlight:** ถามสิ่งที่ขาดก่อนวิเคราะห์: LLM หา gap ตามรายการ 5W1H แต่ code เป็นคนตัดสินว่าจะถามหรือไม่

**บนสไลด์:**
- LLM คืน gaps เป็น JSON (gap_key, priority, askable, question)
- ข้าวหลามตัด: high + askable + ยังไม่เคยถาม + ยังเหลือรอบ (3 รอบ × 3 คำถาม)
- คำตอบเก็บเป็น QA-01 ไม่ใช่ source
- ตอบครบรอบ → วิเคราะห์ใหม่ 1 ครั้ง

**พูด** (~0:52 นาที)

> Step one: how we find what is missing. We send the sources, and any answers we already have, to the LLM, which checks the case against a fixed list: who was affected, who did it, what, when, where, why, how, and how much. It returns the gaps as JSON. Our code, not the model, decides whether to ask: only a high-priority gap we have not asked before, one question at a time, at most three questions in a round and three rounds. The answer is stored as a chat message, QA-01, not as a new source. When the round is answered, we run the analysis once, so three questions cost one analysis.

**ดูโค้ด:**
- `backend/app/analysis/prompts.py:119` `CASE_CHECKLIST` รายการ 5W1H
- `backend/app/analysis/pipeline.py:116` `assess_gaps` การเรียก LLM ราคาถูกที่หา gap
- `backend/app/trace/claims.py:262` field ของ gap (`gap_key`, status, priority, askable, คำถาม)
- `backend/app/followup/clarification.py:30` `eligible_gaps` เงื่อนไขที่จะถาม `:44` `rounds_are_spent` `:48` `decide_followup`
- `backend/app/config.py:85-86` `chat_followup_max_rounds = 3` และ `chat_followup_gaps_per_round = 3`
- `backend/app/chat/reply.py:181` `record_answer_and_ask_next` `:269` `next_question_of_round` (ไม่เรียก model) `:215` `analyse_after_round`

**ถ้าโดนถาม:**
- *ทำไมคำตอบไม่เป็น source* → เป็นคำพูดของผู้ใช้ในแชท ไม่ใช่เอกสารคดี จึงอ้างแยกเป็น QA และไม่ทำให้ analysis เก่าหมดอายุ
- *ถ้า model ถามเรื่องเดิมซ้ำ* → code กันไว้ด้วย gap_key ที่เคยถามแล้ว

---

## หน้า 10 (วงกลม 5) · How we decide when to look up ATT&CK

> **Highlight:** ค้น ATT&CK เฉพาะเมื่อ source บรรยายพฤติกรรมไซเบอร์ชัดเจน และ code ตรวจว่าข้อความที่ model ยกมามีอยู่จริงคำต่อคำ

**บนสไลด์:**
- ส่งแต่ละ source ไม่เกิน 4,000 ตัวอักษร (รวม 20,000)
- LLM ตอบ RETRIEVE หรือ SKIP พร้อม trigger_text
- ข้าวหลามตัด: trigger อยู่ใน source จริงไหม (NFKC) ไม่ผ่าน = SKIP
- query = trigger ทีละบรรทัด + คำถามคำตอบ follow-up → RAG → ตาราง technique
- แถวที่ RAG ผูกกับประโยคในคดี = MA-xx (candidate ไม่ตรวจเพิ่ม)

**พูด** (~1:00 นาที)

> Step two: how we decide when to look up ATT&CK. We send each source, up to four thousand characters, and the model answers RETRIEVE or SKIP. For RETRIEVE it must quote the exact spans that show cyber behaviour, such as running a command; a stolen phone or a bank transfer is not enough, and when unsure it must skip. Then our code checks that every quoted span really appears, word for word, in the source it cites. If not, it is a skip, and the analysis goes on without ATT&CK. If it passes, we build the query, the spans one per line plus the answered follow-ups, and ask the downstream RAG service for a technique table. We keep that table and reuse it while the case stays the same.

**ดูโค้ด:**
- `backend/app/analysis/technical_context/gate_llm.py:24-26` งบ 20,000 / 4,000 ตัวอักษร และ 1,024 tokens `:29` prompt `:84` `per_source_limit`
- `backend/app/analysis/technical_context/gate_llm.py:179-199` code ตรวจ trigger (`:188` normalize แบบ NFKC) ไม่ผ่าน = `mitre_applicability_invalid_grounding`
- `backend/app/analysis/technical_context/gate_llm.py:219` เรียกด้วย `temperature=0.0`
- `backend/app/analysis/technical_context/retrieve.py:35` `retrieval_query` ประกอบ query ทีละบรรทัด `:25` `technical_context_key` (ใช้ตารางเดิมซ้ำ) `:102` `gated_augmentation`
- `backend/app/trace/associations.py:35` `mapped_associations` แถวที่มี span `reread` (`:21`) กลายเป็น MA-xx สถานะ `candidate_only` (`:55`)

**ถ้าโดนถาม:**
- *ทำไมไม่ค้น ATT&CK ทุกคดี* → คดีส่วนใหญ่ไม่ได้เป็นไซเบอร์จริง เช่น ขโมยโทรศัพท์ หลอกโอนเงิน ถ้าค้นทุกคดีจะได้ technique ที่ไม่เกี่ยวมาปน
- *gate ผิดได้ไหม* → ได้ จึงออกแบบให้ผิดไปทาง SKIP

**ห้ามพูด:** gate เลือกประโยคจาก unit (ผิด: มันยกข้อความเอง แล้ว code ตรวจ) · Judgement จับคู่ ATT&CK (ผิด: association มาจาก RAG)

---

## หน้า 11 (วงกลม 6) · How we tie every claim to the exact source words

> **Highlight:** Reader แค่ชี้ unit ID ส่วนคำที่โชว์ใน citation code เป็นคนคัดลอกจาก source เสมอ

**บนสไลด์:**
- code ตัด source เป็น unit มีเลข (SaT)
- Reader เขียน claim และชี้ U006 ห้ามยกคำพูด
- Binding (code): ID มีจริง ข้อความไม่เปลี่ยน → คัดลอกคำ + offset + หน้า
- ID ไม่ resolve → claim ยังอยู่แต่มีป้าย และเข้า summary ไม่ได้

**พูด** (~0:53 นาที)

> Steps three and four: how we tie every claim to the exact source words. First our code cuts each source into numbered units, using a sentence model, SaT. The Reader, our LLM, reads those units and writes claims, but it never copies a quote: it only points to unit IDs, such as U006. Then binding, which is pure code: we check that U006 exists in that source and that its text has not changed, and we copy the exact words, with their character offsets and their page. If an ID does not resolve, the claim is kept but marked, and it cannot reach the summary. The model chooses; the words always come from our code.

**ดูโค้ด:**
- `backend/app/trace/sentences.py:34` `SaT("sat-3l-sm")` ตัดประโยค `:17` threshold 0.025 `:47` ใช้ crfcut แทนเมื่อ SaT โหลดไม่ได้
- `backend/app/sources/evidence.py:28` `evidence_revision` และ `:45` สร้าง ID เต็มของแต่ละ unit
- `backend/app/analysis/reading_sources.py:47` ID สั้น `U001` ที่ Reader เห็น `:52` `canonical_id` แปลงกลับเป็น ID เต็ม
- `backend/app/analysis/prompts.py:5` `CASE_READING_SYSTEM_PROMPT` prompt ของ Reader (ห้ามยกคำพูด)
- `backend/app/analysis/write.py:61` เรียก stage `case_reading` และ `:119` `checked_reading`
- `backend/app/trace/evidence_binding.py:42` `bind_citations` ตรวจ ID (`:55` `duplicate_id`) แล้วคัดลอกคำ offset และหน้า
- `backend/app/trace/bind.py:77` `bound_claims` ฟังก์ชันที่เรียกทั้งหมดนี้

**ถ้าโดนถาม:**
- *ถ้า Reader ชี้ unit ที่มีจริงแต่ไม่สนับสนุน claim* → binding จับไม่ได้ เพราะตรวจแค่ว่ามีจริง support check พยายามจับ แต่วัดแล้วแม่นพอ ๆ กับการสุ่ม จึงทำแค่เตือน
- *ทำไมต้องใช้ model ตัดประโยค* → ภาษาไทยไม่มีเครื่องหมายจบประโยค

---

## หน้า 12 (วงกลม 7) · How we decide what may enter the summary

> **Highlight:** 4 rules ใน code คัดว่าอะไรเข้า summary ได้ ส่วนคะแนน support จาก model บนเครื่องแค่เตือน ไม่กรอง

**บนสไลด์:**
- 4 rules: มี source ที่ resolve, ไม่มี ID เสีย, ไม่มี source ขัดแย้ง, status reported หรือ unknown
- ไม่ผ่าน = ยังโชว์เป็น finding แต่ไม่ส่งให้คนสรุป
- support check: MPNet เลือก unit → mDeBERTa → LR → ต่ำกว่า 0.5 = เตือน
- ตัวเลขบนสไลด์เป็นตัวอย่าง

**พูด** (~0:59 นาที)

> Steps five and six: how we decide what may enter the summary. Every claim meets four rules in code: it has a resolved source, no broken unit ID, no source that contradicts it, and it is reported, not guessed. A claim that fails is still shown as a finding, with a mark, but it is never given to the summary writer. Beside that, we run a support check on our own server: MPNet picks the closest units, mDeBERTa scores whether they entail the claim, and a small classifier turns that into one score. Below 0.5 we show a warning. We use it only as a warning, never as a filter, and I will show the measurement behind that choice. The numbers on the slide are an example.

**ดูโค้ด:**
- `backend/app/trace/claim_validation.py:60` `assessment_blocker` 4 rules อยู่ในฟังก์ชันนี้ `:86` `usable_claims` `:199` `unverified_claims`
- `backend/app/analysis/claim_gate.py:43` `usable_reading` ชุด claim ที่ส่งให้ Judgement `:18` `checked_claim_support` (model ไม่มี = unassessed ไม่ล้ม)
- `backend/app/trace/b1_verifier.py:61` `verify` MPNet → ต่อ unit ด้วยขึ้นบรรทัดใหม่ → mDeBERTa → LR `:38` เลือก unit ที่ cosine ≥ 0.20 `:16` threshold
- `backend/app/trace/b1_lr.json` น้ำหนัก LR และ threshold ที่ fit บน WiCE
- `backend/app/trace/source_selector.py:17` `SourceSelector` (MPNet) และ `trace/nli_model.py:80` `predict` (mDeBERTa)

**ถ้าโดนถาม:**
- *ทำไมแค่เตือน* → หน้า 22: ป้ายเตือนแม่นพอ ๆ กับ base rate และถ้าตัดทิ้งคำตอบแค่สั้นลง
- *ทำไม claim ที่ลอกคำต่อคำยังโดนเตือน* → NLI ไม่เคยเห็นกรณี premise = hypothesis ตอนเทรน E ประมาณ 0.32 เป็นจุดบอดที่รู้แล้ว

---

## หน้า 13 (วงกลม 8) · How we write a summary that names its claims

> **Highlight:** สรุปเขียนจาก claim ที่ผ่าน rules เท่านั้น ทุกประโยคลงท้ายด้วย claim ID และ code ตรวจทุก ID ถ้าผิดแม้ตัวเดียว ทั้ง analysis ล้ม

**บนสไลด์:**
- input: ข้อความ claim, status, คำที่อ้าง (ไม่มี source และ ATT&CK)
- ข้าวหลามตัด: ทุก [A-xx] เป็น claim ที่ส่งให้จริงไหม ไม่ = fail (502) ไม่เก็บอะไร
- ผ่าน → ตัดเป็นประโยคพร้อมเลข finding
- พร้อมกัน: views (parties, timeline, impacts) แค่โชว์

**พูด** (~0:54 นาที)

> Steps six and seven: how we write the summary. The summary writer sees only the claims that passed the rules: their text, their status and the words they cite. It never sees the sources or ATT&CK. Every sentence it writes must end with the IDs of the claims it rests on. Then our code checks every ID: if the summary names a claim it was not given, we fail the whole analysis rather than store a sentence nobody can trace. If all IDs are valid, we cut the summary into sentences, each with its finding numbers. At the same time, another call lists parties, a timeline and impacts, for display only. Everything is stored as one analysis row.

**ดูโค้ด:**
- `backend/app/analysis/write.py:72` `judged = usable_reading(reading)` เฉพาะ claim ที่ผ่าน 4 rules
- `backend/app/analysis/write.py:86-102` สามงานพร้อมกัน: `verify_task` `:86`, `view_task` `:88`, `judge_task` `:90`, `gather` `:101`, ตรวจ ID `:102`
- `backend/app/analysis/write.py:194` `summary_sentence_limit` ขอจำนวนประโยคสูงสุด = claims ÷ 3 (2–8, ค่าคงที่ `:42-44`) `:201` `judgement_request`
- `backend/app/analysis/prompts.py:158` `CASE_JUDGEMENT_SYSTEM_PROMPT` และ `:192` กฎจำนวนประโยค
- `backend/app/analysis/claim_gate.py:47-62` `check_judgement_references` ID ไม่ตรง → `case_judgement_invalid_claim` (502)
- `backend/app/trace/summary.py:12` `scan_summary` ตัดสรุปเป็นประโยคตามวงเล็บ
- `backend/app/analysis/views.py:111` `derive_claim_views` ถ้าล้ม views ว่างพร้อมคำเตือน แต่ Judgement ไปต่อ

**ถ้าโดนถาม:**
- *ทำไมให้ล้มแทนตัดประโยคนั้น* → ID ปลอมแปลว่า model ไม่ทำตามสัญญา ถ้าเก็บต่อจะได้ trace ที่หลอกตา
- *สรุปยาวกว่า source* → ตอนนี้ request บอกจำนวนประโยคสูงสุด (claims ÷ 3, 2 ถึง 8) แต่เป็นการขอ ไม่ได้บังคับ
- *summary ยังผิดได้ไหม* → ได้ ประโยคอาจสรุป claim ผิด ระบบรับประกันแค่ว่าอ้างย้อนได้

---

## หน้า 14 (วงกลม 9) · How a reader checks a sentence

> **Highlight:** สิ่งที่ผู้สืบสวนเห็น: ทุกประโยคมีเลขยก กดแล้วไปยัง finding ที่ประโยคนั้นอิง

**บนสไลด์:**
- ภาพหน้าจอ summary พร้อมเลขยก
- parties, timeline, impact ด้านล่าง (จาก views แค่โชว์)

**พูด** (~0:18 นาที)

> This is what the investigator sees. Each sentence of the summary ends with raised numbers, and each number opens the finding that sentence rests on. Below are the parties, the timeline and the impact, listed from the same claims.

**ดูโค้ด:**
- `frontend/src/features/analysis/SummaryUnits.tsx` ประโยคพร้อมเลขยก
- `frontend/src/features/analysis/AnalysisSummary.tsx` ส่วน summary ทั้งหมด
- `backend/app/trace/bind.py:33` `item_support` ป้าย bound / mixed / unbound / no_claim (`trace/trace.py:20`)

**ถ้าโดนถาม:**
- *ป้าย mixed หรือ unbound หมายถึงอะไร* → สถานะการผูก citation ของ claim ไม่ได้บอกว่าจริงหรือเท็จ

---

## หน้า 15 (วงกลม 10) · How a finding opens its page

> **Highlight:** ปลายโซ่: เปิด finding แล้วเห็นหน้าเอกสารจริงพร้อม highlight คำที่อ้าง

**บนสไลด์:**
- finding เรื่องที่อยู่ผู้ส่ง highlight บนหน้า 1 ของ complaint letter
- finding 5 และ 6 มีป้ายเตือนจาก support check

**พูด** (~0:25 นาที)

> And this is the end of the chain. When the investigator opens a finding, we open its page of the original document and mark the exact words it cites. Here it is the finding about the sender's address, marked on page one of the complaint letter. Findings five and six carry the support check's warning.

**ดูโค้ด:**
- `frontend/src/features/analysis/AnalysisFindings.tsx` รายการ finding
- `frontend/src/features/citations/SourceDrawer.tsx` เปิดหน้าเอกสารและ highlight คำ
- `backend/app/trace/evidence_binding.py:42` offset และเลขหน้าที่ highlight มาจากตรงนี้

---

## หน้า 16 (วงกลม 11) · How we answer questions with their sources

> **Highlight:** แชทใช้หลักเดียวกัน: ทุกข้อความบอก basis และ code เก็บ citation เฉพาะที่ตรวจเจอจริง

**บนสไลด์:**
- ข้อความเป็นคำตอบ follow-up? → เก็บเป็น QA
- ไม่ใช่ → LLM ตอบเป็น unit พร้อม basis 4 แบบ
- ข้าวหลามตัด: claim มีจริงและ quote เจอคำต่อคำ → แนบ citation + หน้า ไม่ผ่าน → ตัด citation ทิ้ง
- แชทไม่เรียก RAG

**พูด** (~0:46 นาที)

> The chat works the same way. When the investigator asks a question, we give the LLM the stored analysis, the sources and the earlier answers, and it replies in units, one statement each, with its basis: a case fact, an interpretation, technical, or general. A case fact must cite a claim or quote the source word for word. Our code checks every citation: if the claim exists and the quote is found in that source, we attach it with its page; if not, we drop the citation and show the statement without it. The chat never calls the RAG service.

**ดูโค้ด:**
- `backend/app/chat/reply.py:110` `post_case_message` แยกว่าเป็นคำตอบ follow-up หรือคำถาม
- `backend/app/chat/compose.py:23` `CHAT_PROMPT` (basis 4 แบบ) `:81` `generate_case_answer` `:115` `chat_request`
- `backend/app/chat/grounding.py:104` `drafted_unit` ตรวจ citation `:135` หา quote คำต่อคำใน source

**ถ้าโดนถาม:**
- *ทำไมไม่ลบข้อความที่ไม่มี citation* → บางข้อความเป็น general หรือ interpretation ที่ไม่ต้องมี citation

---

## หน้า 17 · Report generation

> **Highlight:** เข้า Part 2: รายงานสร้างจาก JSON ที่ Part 1 เก็บไว้เท่านั้น

**พูด** (~0:15 นาที)

> Part 2 starts here. The report is built only from what Part 1 stored: one JSON row per analysis. Every slide of this part has a blue bar on its left edge.

---

## หน้า 18 (วงกลม 12) · How we build the report without a model

> **Highlight:** ไม่มี model ในรายงาน: 1 analysis = 1 report อ่านแถวที่เก็บไว้ แล้วเติม template เดียวทั้ง HTML และ PDF

**บนสไลด์:**
- ข้าวหลามตัด 1: มี report แล้ว? → ส่งอันเดิม ไม่เขียนทับ
- อ่านแถว: analysis, sources_read, follow-up
- ข้าวหลามตัด 2: source ยังอยู่ครบ? ไม่ → ปฏิเสธ ต้องวิเคราะห์ใหม่
- snapshot → Jinja2 HTML → WeasyPrint PDF

**พูด** (~0:48 นาที)

> Part two: how we build the report, with no model at all. When the investigator presses Generate, we first check whether this analysis already has a report; if so, we return it, because we never rewrite a report. Otherwise we read the stored row: the analysis, the exact list of sources it read, and the follow-up answers it used. If one of those sources is gone, we refuse and ask for a new analysis. We build one snapshot, store it as a report version, and fill the same template for HTML and, through WeasyPrint, for PDF, so both always say the same thing.

**ดูโค้ด:**
- `backend/app/reports/generate.py:38` `generate_report` (มีแล้วส่งอันเดิม)
- `backend/app/reports/generate.py:224` `recorded_source_bundle` อ่านเฉพาะ sources_read `:237` `analysis_source_snapshot_invalid` `:242` `recorded_followup_history`
- `backend/app/reports/display.py:80` `build_case_report_content` สร้าง snapshot
- `backend/app/reports/render.py:78` HTML `:99` PDF (`:100` import WeasyPrint ในฟังก์ชัน) template อยู่ที่ `reports/templates/case_report.html.j2`

**ถ้าโดนถาม:**
- *ทำไมไม่ให้ LLM เขียนรายงาน* → รายงานต้องพูดตรงกับ analysis ที่เก็บไว้ทุกคำ การที่ template รักษา trace ได้เป็นจริงโดยการออกแบบ อย่าขายเป็นผลวิจัย
- *แก้รายงานได้ไหม* → ไม่ได้ อยากได้รายงานใหม่ต้องวิเคราะห์ใหม่

---

## หน้า 19 (วงกลม 13) · How each report section is filled from the row

> **Highlight:** แต่ละ section ของรายงานอ่านจาก field ในแถว JSON ไม่มีอะไรถูกเขียนตอนออกรายงาน

**บนสไลด์:**
- 1 สรุป ← summary_units + parties + timeline
- 2 ข้อเท็จจริง ← claims + citations + ป้ายเตือน
- 3–4 ATT&CK ← associations + ประโยคที่ RAG ผูก
- 5–6 ← gaps · 7 ข้อจำกัด ← สิ่งที่รันไม่ได้ · ภาคผนวก ← sources_read + follow-up

**พูด** (~0:38 นาที)

> This is how each section of the report is filled. Section one takes the summary sentences with their finding numbers, the parties and the timeline. Section two lists every finding with its quotes, page and warning. Sections three and four show the ATT&CK candidates and the case sentence behind each. Sections five and six come from the gaps. Section seven lists what could not run, and the appendix lists the sources read and the follow-up answers. Every line comes from the stored row.

**ดูโค้ด:**
- `backend/app/reports/display.py:80` `build_case_report_content` ประกอบทุก section `:179` `recommendation_items` (section 6) `:194` `source_register` (ภาคผนวก)
- `backend/app/reports/findings.py:65` `report_findings` (section 2)
- `backend/app/reports/technical.py:22` `report_techniques` (section 3–4)
- `backend/app/reports/limitations.py:23` `report_limitations` (section 7)

---

## หน้า 20 · How we tested it

> **Highlight:** 3 การทดสอบ: ALCE (ตอบพร้อม citation), OCR error, usability 5 คน แต่ละอันมีหน้าวิธีทำกับหน้าผล

**พูด** (~0:23 นาที)

> Now, how do we know it works, and where it stops? We ran three tests: a public benchmark for answers with citations, an experiment with OCR-style mistakes, and a usability test with five people. Each test has one slide on how we ran it and one on what we found.

---

## หน้า 21 (วงกลม 14) · We gave one LLM the same questions three ways

> **Highlight:** วิธีทดสอบ ALCE: LLM ตัวเดียวกัน 100 คำถาม เขียน 3 แบบ (A passages, B claims ทั้งหมด, C claims ที่ผ่าน check) เปลี่ยนแค่สิ่งที่มันอ่าน

**บนสไลด์:**
- Data · Model · A·B·C · Measure
- การ์ด STR-EM: คำตอบถูก 2 อย่าง เจอ 1 = 50%

**พูด** (~1:59 นาที)

> Here is how we tested the two design choices. The data is ALCE, a public benchmark for answers with citations, published at EMNLP 2023 by Gao and colleagues. We used its ASQA part: English questions that can be read in more than one way, so each has several correct short answers, and each comes with five Wikipedia passages found by a retriever. We took one hundred questions, numbers 51 to 150; the first fifty were used for a pilot. The model is Gemma 4 26B, the same model and settings as in our system. It wrote every answer three ways, and only what it read changed. A: it read the five passages, the usual ALCE setting. B: it read all the claims our Reader wrote from those passages, 2,399 claims in total. C: it read only the claims our support check passed. The first measure is STR-EM, ALCE's own measure for ASQA: for each question, the share of the correct short answers that appear in the answer. If a question has two correct answers and the answer names one of them, that question scores 50 percent; we average over the hundred questions. The second measure is about the warning. An independent checker, MiniCheck, read each claim against its passages and said supported or not. We compare how often a warned claim is unsupported with how often any claim is. Two more checkers, AttrScore and XLM-R, gave the same picture. Every difference has a 95 percent interval from a paired bootstrap: we resample the questions two thousand times.

**ดูไฟล์:**
- `F:/ALCE_runs/main100_q51_150/scores/summary.json` STR-EM ของ A, B, C
- `F:/ALCE_runs/main100_q51_150/scores/paired.json` ส่วนต่างแบบ paired bootstrap และแบบความยาวเท่ากัน
- `F:/cc-worktrees/alce-arms/research/alce_arms/` โค้ดการทดลอง (และ `research/verify_downstream/`)

**ถ้าโดนถาม:**
- *ทำไมข้อ 51–150* → 50 ข้อแรกใช้ทำ pilot
- *ทำไมไม่ทดสอบภาษาไทย* → ไม่มี benchmark ไทยที่มี label citation ให้ใช้ ถือเป็นข้อจำกัด

---

## หน้า 22 (วงกลม 15) · Claims lose nothing; a warning is no better than chance

> **Highlight:** เขียนจาก claim ไม่เสียอะไรที่วัดได้ (46.8 vs 47.8) และป้ายเตือนแม่นพอ ๆ กับ base rate (16.7% vs 15.0%) จึงใช้แค่เตือน

**บนสไลด์:**
- ซ้าย: A passages 46.8 vs B claims 47.8
- ขวา: claim ที่โดนเตือนไม่มีหลักฐาน 16.7% vs claim ทั้งหมด 15.0%

**พูด** (~1:16 นาที)

> How do we know these choices hold? We tested them on ALCE, a public benchmark for answers with citations, with one hundred English questions. On the left: the same LLM wrote each answer either from the original passages or from our claims, and got 46.8 against 47.8 percent of the short answers. Writing from claims loses nothing we can measure. On the right: an independent checker, MiniCheck, found 15 percent of all claims unsupported, and 16.7 percent of the claims our check warned about. About the same, so we keep the check as a warning, not a filter. If asked: the difference on the left is +1.0 point, 95 percent interval -1.6 to +3.5, which includes zero. Removing warned claims made answers 2.7 points worse, only because they became shorter; at equal length it was +0.9. AttrScore and XLM-R give the same picture, and the four judges agree moderately, Fleiss kappa 0.52. It is an English benchmark; no Thai benchmark with citation labels was available.

**ดูไฟล์:**
- `F:/ALCE_runs/main100_q51_150/scores/summary.json` STR-EM
- `F:/ALCE_runs/main100_q51_150/scores/paired.json` B−A +1.0 [−1.6, +3.5] และ C−B แบบความยาวเท่ากัน
- `F:/ALCE_runs/main100_q51_150/scores/judges_kappa_2026-10-11.json` Fleiss κ 0.52
- `F:/ALCE_runs/verify_downstream/checks/summary.json` `flag_precision` เทียบ `base_rate` ราย judge
- `F:/Thesis/book_2026-10-08/slides/charts_alce/alce_charts.py` สคริปต์กราฟ
- `research/attribution_benchmark/B1_RESULTS_2026-10-07.md` ผล benchmark ของตัวตรวจ (ใน repo)

**ถ้าโดนถาม:**
- *+1.0 แปลว่าดีกว่าไหม* → ไม่ ช่วง 95% คร่อม 0 แปลว่าวัดความต่างไม่ได้
- *ถ้าตัด claim ที่โดนเตือนทิ้ง* → คะแนนลด 2.7 เพราะคำตอบสั้นลง ถ้าคุมความยาวเท่ากันเหลือ +0.9

**ห้ามพูด:** claims ดีกว่า passages

---

## หน้า 23 (วงกลม 16) · We fed the analysis texts with OCR-style mistakes

> **Highlight:** วิธีทดสอบ OCR: ทำ key fact ในข่าวไทย 100 ข่าวให้เสียแบบที่ Typhoon อ่านผิดจริง แล้วเทียบการวิเคราะห์ข้อความสะอาดกับข้อความเสีย

**บนสไลด์:**
- Data · Damage · Run · Measure
- การ์ดตัวอย่าง (แต่งขึ้น): 48,500 → OCR 43,500 → summary 43,500 = copied wrong

**พูด** (~1:44 นาที)

> Here is how we tested what OCR mistakes do to the analysis. This experiment was asked for by our advisor. The data is ThaiSum, a public set of Thai news articles; we took one hundred crime articles and picked the key facts in each, such as numbers, places and names. We damaged those facts in two ways. First, character swaps: we used the swaps that Typhoon OCR really made when it read the printed Thai pages of ThaiOCRBench, so a digit or a letter changes the way the real OCR changes it. Second, deletion: the whole fact is removed, a harder version of the text Typhoon OCR drops. Then we ran the full CyberCase analysis, with Gemma 4 26B, once on the clean text and once on the damaged text, and compared them. We only counted facts that the clean analysis did state: 134 of the 179. For each damaged fact we asked one question: in the analysis of the damaged text, was the wrong form copied, was the right form restored, was it only mentioned with doubt, or was it left out. The example on the right is made up, only to show what copied wrong means: the source says 48,500, OCR reads 43,500, and the summary repeats 43,500. The limits: these are news articles, not case files, one model, and one run per text.

**ดูไฟล์:**
- `evaluation/ocr_downstream/thaisum_ocr/README.md` ใน repo: Protocol `:7` Inputs `:27` Key facts `:46` Arms `:66` Pipeline `:104` Outcomes `:122` Limits `:172`
- `F:/Thesis/book_2026-10-08/appendix.md:5-7` วิธีทดลองฉบับในเล่ม

**ถ้าโดนถาม:**
- *134 จาก 179 คืออะไร* → นับเฉพาะ fact ที่การวิเคราะห์ข้อความสะอาดพูดถึง
- *ใช้ระบบเวอร์ชันไหน* → วัดบนเวอร์ชันก่อนหน้า ที่ Reader ยังคัดลอก quote เอง (ตามเล่ม appendix บรรทัด 5) ข้อจำกัดที่เห็นใช้กับระบบปัจจุบันด้วย เพราะคำผิดอยู่ใน source จริง

---

## หน้า 24 (วงกลม 17) · A misread OCR word becomes the source of truth

> **Highlight:** OCR อ่านผิด คำผิดกลายเป็นความจริงของคดี: ตัวเลขผิดถูกลอก 14/19 fact ที่ลบหายจาก summary 58/70 และไม่มีอันไหนถูกเตือน

**บนสไลด์:**
- แท่งบน: OCR misread 19 numbers ส่วนแดง 14 copied the wrong number (74%)
- แท่งกลาง: We deleted 70 facts ส่วนแดง 58 left out of the summary (83%)
- บรรทัดล่าง: Marked as doubtful 0

**พูด** (~0:55 นาที)

> Here is what we found. Each bar is one kind of damage, and the red part is how often it went wrong. Top bar: OCR misread 19 numbers, changed the way Typhoon OCR really misreads Thai digits. In 14 of the 19, the analysis copied the wrong number; the other 5 were fixed, dropped, or written in both forms. Middle bar: we deleted 70 facts from the text. In 58 of the 70, the summary left them out; 12 were still there. Bottom line: not one misread fact was marked as doubtful. That is expected. The system checks what it wrote against the text it received, not that text against the paper. So the original documents stay the authority.

**ดูไฟล์:**
- `evaluation/ocr_downstream/thaisum_ocr/README.md:220` Result (2026-10-02)
- `F:/Thesis/book_2026-10-08/appendix.md:11-16` ตารางผล และบรรทัด 20 คำอธิบาย
- `F:/Thesis/book_2026-10-08/slides/charts_ocr/ocr_clear.py` สคริปต์กราฟหน้านี้

**ถ้าโดนถาม:**
- *ส่วนเทาคืออะไร* → ตัวเลข 5 ตัว = แก้คืนถูก 1, หายไป 2, เขียนทั้งค่าผิดและค่าถูก 2 · fact ที่ลบ 12 ตัว = ยังอยู่ 10, อยู่ในประโยคที่บอกว่าไม่แน่ใจ 2
- *ชื่อสถานที่กับคำทั่วไป* → ไม่อยู่บนสไลด์: ชื่อสถานที่ผิด 11 ตัว ถูกลอกแค่ 9% ส่วนคำทั่วไป 34 ตัว ถูกแก้คืน 68%

---

## หน้า 25 (วงกลม 18) · Five people ran one case from start to report

> **Highlight:** วิธีทดสอบกับคน: 5 คน คดี phishing สมมติ 1 คดี 5 งาน วัดความง่ายต่องาน (SEQ) และ SUS ตอนจบ

**บนสไลด์:**
- Who · Tasks · Measure
- การ์ด SUS: 10 ข้อ คะแนน 0–100 ค่าเฉลี่ยทั่วไป 68 ไม่ใช่เปอร์เซ็นต์

**พูด** (~1:34 นาที)

> And here is how we tested it with people. Five participants, mostly students, used the same version of the web app on the same day, with one fictional phishing case. They did five tasks in order: create a case; attach a file; run the analysis and read the result, including which ATT&CK technique the system found and why; answer a follow-up question; and create the report. After each task a short form asked whether they finished, whether it was difficult, and how easy it was on a scale from one to seven. This is the Single Ease Question. At the end they filled in the System Usability Scale, SUS: ten statements, each rated from one to five. For odd statements we take the answer minus one, for even statements five minus the answer, add them up and multiply by 2.5. That gives a score from zero to one hundred. It is a score, not a percentage, and about sixty-eight is the usual average across many studies. Three open questions closed the form: the most confusing part, what to change first, and whether they would trust a report written with an LLM. With five people we describe the group; we do not test for significance.

**ดูไฟล์:**
- `F:/Thesis/book_2026-10-08/chapter5.md:187` หัวข้อ 5.5 งาน 5 ข้อ ตาราง SEQ, SUS และ feedback

**ถ้าโดนถาม:**
- *SUS คิดยังไง* → ข้อคี่ (คะแนน − 1), ข้อคู่ (5 − คะแนน) รวมแล้วคูณ 2.5

---

## หน้า 26 (วงกลม 19) · Five of five finished; usability scored below average

> **Highlight:** ทุกคนทำครบ 5 งาน แต่ SUS 59.5 ต่ำกว่าค่าเฉลี่ย 68 สาเหตุหลักคือรอนาน (4 ใน 5 คน)

**บนสไลด์:**
- 5/5 ทำครบ
- SUS 45, 57.5, 62.5, 62.5, 70 → เฉลี่ย 59.5 (SD 9.3, 95% CI 48.0–71.0)
- 4/5 บอกว่ารอนาน

**พูด** (~0:36 นาที)

> We also tested it with five users on one fictional phishing case. All five finished all five tasks: creating a case, adding a file, running and reading the analysis, answering a follow-up, and creating the report. The usability score was 59.5, below the usual average of 68. Four of the five named the same reason: waiting for the analysis. That is the first thing to improve. With five people this describes the group; it is not a significance test.

**ดูไฟล์:**
- `F:/Thesis/book_2026-10-08/chapter5.md:187` หัวข้อ 5.5

**ถ้าโดนถาม:**
- *ผู้ใช้เชื่อถือรายงานไหม* → ไม่มีใครตอบว่าเชื่อเลย ทุกคนบอกว่าต้องตรวจก่อน การทดสอบนี้ไม่ได้วัดว่าเขาตรวจจริงไหม

**ห้ามพูด:** 59.5% (SUS ไม่ใช่เปอร์เซ็นต์) · ผู้ใช้เชื่อถือระบบ

---

## หน้า 27 (วงกลม 20) · The system still relies on the LLM and outside services

> **Highlight:** ข้อจำกัดที่ยอมรับ: พึ่งบริการภายนอก, ความฉลาดอยู่ที่ LLM, ไม่มีการตรวจความหมาย, OCR ผิดผ่านได้, ช้าและทดสอบเล็ก

**บนสไลด์:**
- การ์ด 5 ใบตามลำดับ First ถึง Fifth ใน script

**พูด** (~1:16 นาที)

> Before I close, the limits we acknowledge. First, the system depends on outside services: every LLM call goes through OpenRouter, OCR goes to Typhoon, and ATT&CK to the RAG service, which uses cloud databases. So the case text leaves our server, and without the internet there is no analysis. Gemma is an open-weight model, so it could run inside a closed network, but we have not done that yet. Second, the intelligence is in the LLM: it finds the gaps, decides on ATT&CK, writes the claims, the summary and the chat answers. Our code checks IDs and structure, not meaning. Third, we have no reliable check of meaning: the support check is about as good as chance, so it only warns, and a summary sentence can cite the right claim and still state it wrongly. Fourth, OCR mistakes pass straight through. Fifth, an analysis takes minutes, and our tests are small: an English benchmark, Thai news rather than case files, five users and one model.

**ดูโค้ด:**
- `docker-compose.yml:39-40` LLM ผ่าน OpenRouter (`backend/app/llm/payload.py:60` ล็อก provider)
- `backend/app/sources/ingestion/recognition.py:48` Typhoon OCR
- `backend/app/analysis/technical_context/rag_client.py:20` RAG service
- `backend/app/trace/claim_validation.py:60` code ตรวจแค่ ID และโครงสร้าง ไม่ใช่ความหมาย
- `backend/app/analysis/claim_gate.py:18` ผลตรวจ support เป็นแค่ป้ายเตือน

---

## หน้า 28 · Every summary sentence leads back to the source

> **Highlight:** สรุป 3 ข้อ: model เขียน code ผูกและตรวจ · rules คัด support แค่เตือน · report จาก JSON ไม่มี model และระบบไม่ตรวจข้อเท็จจริงนอกคดี ไม่ตัดสินคดี

**บนสไลด์:**
- 3 ข้อ แล้ว THANK YOU

**พูด** (~0:36 นาที)

> To sum up how we do it. First, the model writes, but our code binds every claim to its source and checks every ID. Second, rules in code decide what reaches the summary; the support score only warns. Third, the report is filled from the stored analysis, with no model. And what it does not do: it does not check facts outside the case, and it does not decide the case. Thank you. I am happy to take questions.

**ดูโค้ด:**
- `backend/app/trace/evidence_binding.py:42` ข้อ 1
- `backend/app/trace/claim_validation.py:60` ข้อ 2
- `backend/app/reports/generate.py:38` ข้อ 3

---

## คำถามรวมที่น่าจะโดน

| คำถาม | คำตอบสั้น |
|---|---|
| ระบบกัน hallucination ได้ไหม | กันได้แค่ว่าทุกประโยคต้องอ้าง claim ที่มีจริง และคำที่อ้างเป็นคำจริงจาก source ประโยคยังสรุปผิดได้ ระบบทำให้ตรวจได้ ไม่ได้รับประกันว่าถูก |
| ถ้า LLM ตอบ JSON เพี้ยน | ตรวจด้วย Pydantic ถ้าเสียขอใหม่ได้ 1 ครั้ง เน็ตหลุดหรือ 429/5xx retry 1 ครั้งหลัง 2 วินาที ยังไม่ได้ = analysis ล้มพร้อม error code |
| ภาษาไทยทำยังไง | ถ้า source มีอักษรไทยแม้ตัวเดียว เขียนผลเป็นไทย (`backend/app/analysis/language.py:14`) ตัดประโยคด้วย SaT หรือ crfcut ไม่แปลอะไรเลย |
| ทำไม Gemma | open-weight ย้ายไปรันในเครือข่ายปิดได้ ต้นแบบเรียกผ่าน OpenRouter โดยล็อก provider |
| งานของคุณกับเพื่อนแบ่งยังไง | ผมทำ web, backend, analysis pipeline, follow-up, report และ usability test ส่วน RAG เป็นของอีกคน ผมเรียกเป็น downstream service |
| ช้าเพราะอะไร | เรียก LLM หลายรอบต่อเนื่อง Judgement ครั้งเดียวประมาณ 2–3 นาที ระหว่างรอมี step ขึ้นให้เห็น |
| ถ้าเพิ่ม source หลังวิเคราะห์ | analysis เก่าถูกมองว่าไม่เป็นปัจจุบัน รายงานเก่ายังอ้าง sources_read เดิม ต้องกด Analyze ใหม่ |
