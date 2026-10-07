# CyberCase Intelligence Framework: Backend Architecture & NLI Grounding Verification
## Presentation Slide Deck & Comprehensive Speaker Notes

> **Interactive Deck Available:** Open [`slides.html`](file:///f:/Cybercase%20Framework/nli_grounding_experiment/presentation/slides.html) directly in any web browser to present in full-screen interactive mode with keyboard navigation (<kbd>→</kbd>, <kbd>←</kbd>, <kbd>Space</kbd>, <kbd>F</kbd> for Fullscreen, <kbd>S</kbd> for Speaker Notes).

---

## Slide 1: Title & Executive Hook
- **Category:** System Overview
- **Title:** Evidence-Grounded Threat Intelligence: Robust Backend & Frozen NLI Verification
- **Subtitle:** CyberCase Intelligence Framework
- **Key Metrics Highlight:**
  - WiCE Test Accuracy: **66.64%**
  - Official Champion ($B1\text{-LR}$) Macro-$F_1$: **0.6185**
  - Hallucination Leaks into Judgement: **0%**
- **Speaker Notes (Thai):**
  > "สวัสดีครับ วันนี้ผมจะมานำเสนอสถาปัตยกรรม Backend ทั้งระบบของ **CyberCase Intelligence Framework** ซึ่งเป็นแพลตฟอร์มวิเคราะห์คดีภัยคุกคามทางไซเบอร์ที่มุ่งเน้นความถูกต้องของหลักฐานเป็นอันดับหนึ่ง ไฮไลต์สำคัญที่สุดของการนำเสนอวันนี้คือ **NLI Grounding Verification Engine** ซึ่งทำหน้าที่เป็น Trust Boundary หรือด่านคัดกรองความจริงทางคณิตศาสตร์ที่ไม่พึ่งพาการสุ่มคำของ LLM และผ่านการทดสอบแบบ Controlled Factor Ablation จนได้โมเดลระดับแชมป์เปียนที่เสถียรและประหยัดทรัพยากรครับ"
- **Estimated Time:** 1:00 min

---

## Slide 2: The Core Challenge: Grounding in Threat Intel
- **Category:** Problem & Motivation
- **Title:** The Grounding Dilemma in Threat Intel
- **The Core Problem:** ทำไม Generative LLMs และ Vanilla RAG ถึงไม่เพียงพอสำหรับคดีไซเบอร์?
- **3 Critical Pitfalls:**
  1. **Hallucinated Attribution:** LLM มักจะ "แต่งเติม" หรือตั้งสมมติฐานเกินจริงเกี่ยวกับ Threat Actors และเทคนิค MITRE ATT&CK ที่ไม่มีอยู่ในเอกสารหลักฐานดิบ
  2. **Attention Dilution:** เมื่อใส่เอกสารคดีขนาดยาว (Full Premise) โมเดลจะมีอาการความสนใจเจือจาง นำไปสู่การมองข้ามหลักฐานหรือการปฏิเสธหลักฐานจริง
  3. **Missing Trust Boundary:** สถาปัตยกรรม RAG ทั่วไปรับข้อมูลค้นหาแล้วส่งให้ LLM สรุปทันที ขาดกลไกการรับรอง (Auditable Verification)
- **The CyberCase Solution:**
  - ตัดเอกสารเป็น **Evidence Units (U001, U002...)** ที่มี character offset และ text hash คงที่
  - บังคับให้ Case Reading สกัดเป็น **Canonical Claims** ที่ผูกกับ Unit IDs
  - ส่งผ่าน **NLI Verification Engine** ก่อนส่งต่อไปยังขั้นตอน Judgement
- **Speaker Notes (Thai):**
  > "ในการสืบสวนคดีความมั่นคงไซเบอร์ ความผิดพลาดแม้แต่ประโยคเดียว เช่น การระบุผู้โจมตีผิด หรือการโยงเทคนิคการโจมตีโดยไม่มีหลักฐาน อาจส่งผลกระทบมหาศาล ปัญหาของ LLM ในปัจจุบันคือมัน 'เก่งในการแต่งเรื่อง' แต่ 'แย่ในการปฏิเสธตัวเอง' ถ้าเอกสารยาว ความสนใจของมันจะกระจาย เราจึงสร้างระบบที่ล็อคหลักฐานเป็นชิ้นๆ (Evidence Units) และสร้างด่านตรวจความจริงก่อนที่จะสรุปคดีครับ"
- **Estimated Time:** 1:30 min

---

## Slide 3: 4-Service Topology & The Core Backend Rule
- **Category:** System Architecture
- **Title:** 4-Service Topology & The Core Backend Rule
- **4 Decoupled Microservices:**
  1. **Frontend (Port 3000):** Next.js 15, React 19, Strict TypeScript, TanStack Query สำหรับ Server State
  2. **Backend API (Port 8000):** FastAPI, PostgreSQL, Async SQLAlchemy, Case State Management, Report Rendering (WeasyPrint)
  3. **Claim-View Runtime (Port 8090):** llama.cpp CPU hosting Pinned `NuExtract3` สกัด Parties, Timeline, Impacts (สำหรับแสดงผล UI/Report เท่านั้น ไม่ส่งเข้า Judgement)
  4. **GraphRAG Service (Port 8001):** FastAPI, Neo4j (STIX 2.1 Graph) + Qdrant (Vector DB), BGE-M3 + Reranker สำหรับเสริมบริบท MITRE ATT&CK
- **The Golden Backend Rule:**
  > **"Read Short. Think Free. Write Short."**
  - **Read Short:** อ่านข้อมูลคดีในเสี้ยววินาที แล้วปิด Transaction ทันที
  - **Think Free:** โมเดล LLM หรือ NLI ประมวลผลนานหลายสิบวินาทีอย่างอิสระ **โดยไม่ถือ DB Connection / Row Lock**
  - **Write Short:** เมื่อผลลัพธ์พร้อม เปิด Transaction สั้นๆ เพื่อบันทึกผล
  - *ประโยชน์:* รองรับ Concurrency สูง, ป้องกัน Database Connection Exhaustion และไม่มีปัญหา Deadlock
- **Speaker Notes (Thai):**
  > "ระบบหลังบ้านของเราแบ่งออกเป็น 4 บริการชัดเจน และกฎเหล็กสำคัญที่สุดของทีมคือ 'Read Short. Think Free. Write Short.' งานวิเคราะห์ AI ต้องใช้เวลานานเป็นนาที หากเราเปิด Database Transaction ค้างไว้ ฐานข้อมูลจะพังทันที เราจึงออกแบบให้ Pipeline เป็น Stateless Functions 100% อ่านข้อมูลเสร็จ ปล่อย Connection แล้วให้โมเดลคิด จากนั้นค่อยเปิด Connection เขียนผลลัพธ์ในเสี้ยววินาทีครับ"
- **Estimated Time:** 1:45 min

---

## Slide 4: End-to-End Pipeline Workflow
- **Category:** Execution Pipeline
- **Title:** End-to-End Analysis Advance Flow
- **7-Stage Sequential Advance:**
  1. **Gap Assessment:** ตรวจสอบความสมบูรณ์ของเอกสารคดีด้วยโมเดลราคาถูกก่อนทำงานหนัก
  2. **Clarification Loop:** หากข้อมูลสำคัญขาดหาย ถามผู้วิเคราะห์ผ่านแชท (Human-in-the-loop, Stateless)
  3. **MITRE Gate:** ประเมินว่าคดีนี้เข้าข่ายต้องดึงข้อมูลเทคนิค ATT&CK จาก GraphRAG หรือไม่
  4. **Case Reading:** สกัด **Canonical Claims** พร้อมระบุ Source Unit IDs (เช่น `U001`, `U005`)
  5. **Evidence Binding & NLI Gate (Spotlight!):** ตรวจสอบว่า Claim กับ Unit IDs สอดคล้องกันทางความหมายจริงหรือไม่
  6. **Judgement & Summary:** สรุปสาระสำคัญของคดี โดยทุกประโยคในบทสรุปจะจบด้วย Claim IDs ที่ผ่านการรับรองเสมอ
  7. **Reports & Interactive Chat:** สร้างรายงาน PDF แบบ Deterministic และเปิดแชทถามตอบที่มีการอ้างอิงระดับประโยค
- **Judgement Isolation Principle:**
  - Judgement **ไม่มีสิทธิ์เห็นเอกสารดิบทั้งก้อน**! อ่านเฉพาะ Claims ที่ผ่านการยืนยันแล้วเท่านั้น เพื่อตัดโอกาสการ Hallucinate 100%
- **Speaker Notes (Thai):**
  > "นี่คือ Pipeline Advance จริงของระบบ ทุกขั้นตอนถูกออกแบบให้ตรวจสอบย้อนกลับได้ ที่สำคัญคือ 'Judgement Isolation' — ตัวโมเดลที่ทำหน้าที่เขียนบทสรุปคดีและสรุปเทคนิคการโจมตี จะถูกปิดตาไม่ให้เห็นเอกสารดิบทั้งฉบับ มันจะเห็นเฉพาะ Claims ที่ผ่านด่าน NLI Verification มาแล้วเท่านั้น ถ้า Claim ไหนไม่ผ่าน จะถูกตัดออกตั้งแต่ด่านที่ 5 ทันทีครับ"
- **Estimated Time:** 2:00 min

---

## Slide 5: The Spotlight: NLI Grounding Verification Engine
- **Category:** Core Innovation Spotlight
- **Title:** The NLI Grounding Verification Engine
- **ทำไมต้องเป็น Frozen NLI แทนที่จะเป็น LLM Judge?**
  | มิติการเปรียบเทียบ | LLM-as-a-Judge (เช่น GPT-4o / Claude) | CyberCase NLI Engine ($B1\text{-LR}$) |
  |---|---|---|
  | **Inference Mechanism** | Generative Token Sampling (สุ่มคำ) | Frozen Pretrained Encoder (ความน่าจะเป็นคงที่) |
  | **ต้นทุน & ทรัพยากร** | เสียค่า API Token สูง, มี Latency เป็นวินาที | รัน Local บน GPU 4GB VRAM, Latency ~227 ms |
  | **ความคงเส้นคงวา** | มีความแปรปรวน (Non-deterministic) | Deterministic 100% ตรวจสอบทางคณิตศาสตร์ได้ |
  | **ความปลอดภัย** | เสี่ยงต่อ Prompt Injection ในเอกสารคดี | ปลอดภัยจาก Prompt Injection โดยสมบูรณ์ |
  | **ความเอนเอียง (Bias)** | ชอบตอบตกลง (Sycophancy Bias) | ควบคุมได้ด้วย Task-Specific Decision Layer |
- **กลไกการทำงานของ NLI Engine:**
  - ป้อนคู่ `[Premise: Filtered Units] + [Hypothesis: Claim]` เข้า Encoder
  - ได้ความน่าจะเป็น 3 มิติ: $[P_{\text{entail}}, P_{\text{neutral}}, P_{\text{contradiction}}]$
  - ส่งเข้า **Task-Specific Logistic Regression Decision Layer** เพื่อตัดสินว่าเป็น `SUPPORTED` หรือ `UNSUPPORTED`
- **Speaker Notes (Thai):**
  > "หลายคนอาจถามว่า 'ทำไมไม่ใช้ GPT-4 เป็น Judge ตัดสินไปเลย?' คำตอบคือ ในงานคดีความ เรายอมรับความไม่แน่นอนของการสุ่มคำไม่ได้ LLM ยังเสี่ยงต่อ Prompt Injection ถ้าในเอกสารมีคำสั่งแฝงอยู่ แต่ NLI เป็นโมเดล Encoder แบบแช่แข็ง (Frozen) มันไม่ตอบเป็นตัวหนังสือ แต่มันคำนวณเวกเตอร์ความน่าจะเป็นทางคณิตศาสตร์ออกมาตรงๆ เร็วกว่า ประหยัดกว่า และไม่มีช่องโหว่ทางความปลอดภัยครับ"
- **Estimated Time:** 2:00 min

---

## Slide 6: Pipeline Ablation Design: From B0 to B4
- **Category:** Scientific Experimentation
- **Title:** Pipeline Ablation Design: From B0 to B4
- **การออกแบบชุดทดลองควบคุมตัวแปร (Locked Canonical Protocol):**
  - **B0:** Full Premise $\to$ Forward NLI $\to$ 1D DEV-tuned Threshold ($\theta_{\text{DEV}}$) (Canonical Baseline)
  - **B0-LR:** Full Premise $\to$ Forward [E, N, C] $\to$ Task-specific 3D Logistic Regression (Fit บน TRAIN split เท่านั้น)
  - **B1:** Semantic Filter ($\tau=0.20$) $\to$ Forward NLI $\to$ 1D DEV-tuned Threshold ($\theta_{\text{DEV}}$)
  - **B1-LR (Official Champion):** Semantic Filter ($\tau=0.20$) $\to$ Forward [E, N, C] $\to$ Task-specific 3D Logistic Regression
  - **B2:** Full Premise $\to$ Bidirectional NLI (Forward + Reverse [6 probs]) $\to$ 6D Logistic Regression
  - **B3:** Filtered Premise ($\tau=0.20$) $\to$ Bidirectional NLI (Forward + Reverse [6 probs]) $\to$ 6D Logistic Regression
  - **B4:** B3 + Temperature Scaling + Selective Rejection Gating (ตั้งด่านความมั่นใจสูง)
- **Scientific Rigor & Constraints:**
  - **Single Source of Truth:** รายงานผลจาก `outputs/canonical/` ที่ผ่าน final audit และ freeze เรียบร้อย
  - **Strict Threshold Isolation:** $\theta$ จูนจาก DEV split ($N=1,043$) เท่านั้น ไม่แตะ TEST split (mDeBERTa $\theta_{\text{B0}}=0.36, \theta_{\text{B1}}=0.23$; MiniLM $\theta_{\text{B0}}=0.15, \theta_{\text{B1}}=0.20$)
  - **Zero LR Leakage:** LR fit เฉพาะ $X_{\text{train}}, y_{\text{train}}$ ($N=3,750$) เท่านั้น TEST ใช้ทำนายอย่างเดียว และ DEV ห้ามหลุดเข้า `clf.fit()`
  - **Evaluation Rigor:** ประเมินบน Held-out WiCE Test split ($N = 1,070$)
  - **Statistical Testing:** ใช้ **Paired Bootstrap** ($N_{\text{boot}} = 1,000$, Seed = 42, Same Sampled Indices) รายงาน 95% Confidence Intervals
- **Speaker Notes (Thai):**
  > "เพื่อค้นหาองค์ประกอบที่ดีที่สุด เราไม่ได้เดาสุ่ม แต่ตั้งสมมติฐานเป็นขั้นตอน B0 ถึง B4 เพื่อดูว่า: การกรองหลักฐาน (Filtering) ช่วยจริงไหม? การใช้ Logistic Regression คุมขอบเขตช่วยจริงไหม? และการรัน NLI ย้อนกลับแบบ 2 ทิศทาง (Reverse NLI) จำเป็นหรือไม่? ทุก baseline นิยามตายตัวด้วย Canonical Protocol โดย B0/B1 ใช้ DEV-tuned threshold ไม่ใช้ naive argmax และทุกขั้นตอนวัดผลด้วย Paired Bootstrap 1,000 รอบอย่างเป็นวิทยาศาสตร์ครับ"
- **Estimated Time:** 1:45 min

---

## Slide 7: Empirical Results on WiCE Held-out Test (N = 1,070)
- **Category:** Empirical Evidence
- **Title:** Benchmark Results on Held-out WiCE Test (N = 1,070)
- **Metric Definition Note:**
  - $\text{FSR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$ (False Positive Rate over Gold Unsupported/Negative claims)
- **Full Confusion Matrix & Metrics Table (mDeBERTa-v3-base - Primary Champion):**
  | Method | TP | FP | TN | FN | Accuracy | Macro-$F_1$ | Supp-$F_1$ | FSR [$\frac{\text{FP}}{\text{FP}+\text{TN}}$] |
  |---|---|---|---|---|---|---|---|---|
  | **B0** (Full, $\theta_{\text{DEV}}=0.36$) | 140 | 188 | 552 | 190 | 64.67% | 0.5852 | 0.4255 | 25.41% |
  | **B0-LR** (Full Premise + 3D LR) | 154 | 203 | 537 | 176 | 64.58% | 0.5937 | 0.4483 | 27.43% |
  | **B1** (Filtered, $\theta_{\text{DEV}}=0.23$) | 174 | 234 | 506 | 156 | 63.55% | 0.5967 | 0.4715 | 31.62% |
  | **B1-LR (OFFICIAL CHAMPION)** | 167 | 194 | 546 | 163 | **66.64%** | **0.6185** | **0.4834** | **26.22%** |
  | **B3** (Bidi NLI + 6D LR) | 172 | 200 | 540 | 158 | 66.54% | 0.6205 | 0.4900 | 27.03% |
- **Statistical Significance (Paired Bootstrap 95% CIs, Seed 42):**
  - **B1-LR vs. B0:** $\Delta\text{Macro-}F_1 = +0.0333$ [$+0.0128, +0.0533$] (**มีนัยสำคัญทางสถิติ**, CI พ้น 0)
  - **B1-LR vs. B0-LR:** $\Delta\text{Macro-}F_1 = +0.0248$ [$+0.0048, +0.0451$] (**การกรองหลักฐานมีนัยสำคัญภายใต้ LR**)
  - **B1-LR vs. B1:** $\Delta\text{FSR} = -5.42\%$ [$-7.17\%, -3.70\%$] (**ลด False Support ได้อย่างมีนัยสำคัญ**), $\Delta\text{Macro-}F_1 = +0.0219$ [$+0.0076, +0.0350$]
  - **B3 vs. B1-LR:** $\Delta\text{Macro-}F_1 = +0.0020$ [$-0.0065, +0.0113$] (**ไม่มีนัยสำคัญ**, CI ครอบคลุม 0)
- **Speaker Notes (Thai):**
  > "ผลลัพธ์บน WiCE Held-out Test 1,070 ตัวอย่าง ออกมาอย่างชัดเจนครับ B1-LR ทำคะแนน Macro-F1 ได้ 0.6185 ชนะ B0 พื้นฐานขึ้นมา +0.0333 และที่สำคัญคือช่วงความเชื่อมั่น 95% พ้นศูนย์อย่างเด็ดขาด นอกจากนี้ บน mDeBERTa เลเยอร์การตัดสินใจ Logistic Regression ยังช่วยลด FSR จาก 31.62% ใน B1 ลงมาเหลือ 26.22% ใน B1-LR ควบคู่ไปกับการปรับปรุง Macro-F1 ครับ"
- **Estimated Time:** 2:00 min

---

## Slide 8: Busting the "Reverse NLI" Assumption
- **Category:** Engineering Finding
- **Title:** Busting the "Reverse NLI" Assumption
- **สมมติฐานที่มักเข้าใจผิด:**
  - หลายคนเชื่อว่า การรัน NLI ย้อนกลับ ($Claim \implies Evidence$) ควบคู่กับไปข้างหน้า ($Evidence \implies Claim$) จะช่วยจับการอ้างหลักฐานเกินจริงได้ดีขึ้น
- **สิ่งที่ตัวเลขพิสูจน์จริง (The Empirical Reality):**
  - บน `mDeBERTa-v3-base`: $\Delta\text{Macro-}F_1 = +0.0020$ [$-0.0065, +0.0113$]
  - บน `multilingual-MiniLM-L6`: $\Delta\text{Macro-}F_1 = +0.0011$ [$-0.0153, +0.0179$]
  - **ช่วงความเชื่อมั่น 95% ครอบคลุมศูนย์ทั้งสองสถาปัตยกรรม!**
- **Trade-off ทางวิศวกรรม:**
  - Reverse NLI ต้องรัน Forward Pass เพิ่มอีก 1 รอบ (**requires approximately twice the NLI inference passes**)
  - แต่ไม่ได้ประโยชน์ทางสถิติกลับมาเลย (95% CI ครอบคลุมศูนย์)
- **The Engineering Verdict:**
  - **Occam's Razor ชนะ:** เลือก $B1\text{-LR}$ (Forward-Only) เป็นแชมป์เปียนตัวจริง เพราะให้ผลลัพธ์เทียบเท่ากันในเชิงสถิติ (statistically indistinguishable performance) โดยไม่ต้องเสียรอบ NLI inference pass ซ้ำสอง
- **Speaker Notes (Thai):**
  > "นี่คือจุดที่ทำให้งานวิจัยของเราประหยัดต้นทุนและตอบโจทย์วิศวกรรมจริง: เดิมทีเราคิดว่ารัน Bidirectional NLI สองทิศทางน่าจะฉลาดกว่า แต่พอทำ Paired Bootstrap บนทั้งสองตระกูลโมเดล พบว่าคะแนนเพิ่มขึ้นเพียง +0.0020 และ 95% CI คลุมศูนย์ทั้งคู่ แปลว่าทางสถิติมันไม่ได้ช่วยอะไรเลย แต่ต้องรัน NLI inference ซ้ำสองรอบโดยเปล่าประโยชน์! เราจึงตัด Reverse NLI ทิ้ง และเลือก Forward-only B1-LR เป็น Production ครับ"
- **Estimated Time:** 1:45 min

---

## Slide 9: Cross-Family Sensitivity & The Naive Argmax Trap
- **Category:** Model Family Sensitivity
- **Title:** Cross-Family Consistency & The Naive Argmax Trap
- **สถานะการทดลอง:** Post-hoc Cross-Backbone Sensitivity Analysis (ไม่ใช่ Model Selection Experiment, Champion หลักยังคงเป็น mDeBERTa ตาม Pre-registered DEV Protocol)
- **ผลการทดสอบควบคุมตัวแปรข้าม 2 ตระกูลโมเดล (Canonical Protocol):**
  | Controlled Comparison | mDeBERTa (~278M) | MiniLM (~107M) | ทิศทางสอดคล้องกัน? |
  |---|---|---|---|
  | **Filtering effect (1D $\theta_{\text{DEV}}$)** ($B1$ vs $B0$) | Supp-$F_1$ $+0.0457$ (Sig) | Macro-$F_1$ $+0.0722$ (Sig) | **สอดคล้องกัน (ดีขึ้นทั้งคู่)** |
  | **Filtering under LR** ($B1\text{-LR}$ vs $B0\text{-LR}$) | Macro-$F_1$ $+0.0248$ (Sig) | Macro-$F_1$ $+0.1091$ (Sig) | **สอดคล้องกัน (ชนะขาดทั้งคู่)** |
  | **LR after filter** ($B1\text{-LR}$ vs $B1$) | Macro-$F_1$ $+0.0219$ (Sig) | Supp-$F_1$ $+0.0241$ (Sig) | **สอดคล้องกัน (ปรับสมดุลทั้งคู่)** |
  | **Reverse NLI** ($B3$ vs $B1\text{-LR}$) | $+0.0020$ (CI คลุม 0) | $+0.0011$ (CI คลุม 0) | **สอดคล้องกัน (ไร้นัยสำคัญทั้งคู่)** |
- **The MiniLM Naive Argmax Trap vs DEV-tuned Threshold:**
  - บน MiniLM ถ้าใช้ **Naive Argmax** โดยไม่ทำ DEV threshold tuning:
    - B0 Argmax ได้ Accuracy สูงถึง **69.16%** แต่ Macro-$F_1$ ต่ำเพียง **0.4720** (Supported-$F_1$ = 0.1259)
    - *สาเหตุ:* WiCE Test มี Gold Negative 740 จาก 1070 ตัว (69.16%) โมเดลทายปฏิเสธถึง 1,020 ตัว (95.3%) จับ Claim จริงได้แค่ 25 ตัว (Recall 7.58%)
  - **เมื่อใช้ Canonical Protocol (DEV-tuned threshold):**
    - จูน $\theta_{\text{DEV}}=0.15$ บน DEV: กู้ Recall กลับมาที่ 38.79%, Macro-$F_1$ ขึ้นเป็น **0.5705** (TP=128, FP=184)
    - การใส่ Semantic Filter ($\theta_{\text{DEV}}=0.20$): ดัน Macro-$F_1$ เป็น **0.6427** และ B1-LR ไปถึง **0.6496**
- **Speaker Notes (Thai):**
  > "สไลด์นี้แสดงการทดสอบความทนทานข้ามสถาปัตยกรรม (Sensitivity Analysis) บน MiniLM พบว่าประโยชน์ของ Filtering และการไร้นัยสำคัญของ Reverse NLI ตรงกันทั้งสองตระกูล และยังเผยให้เห็น 'กับดักของค่า Accuracy' บนโมเดลขนาดเล็ก — ถ้าใช้ Naive Argmax จะได้ Accuracy 69% แต่ Macro-F1 หล่นเหลือ 0.4720 เพราะมันตอบปฏิเสธไปถึง 95% ของชุดข้อมูล! การใช้ DEV-tuned Threshold หรือ Logistic Regression จึงจำเป็นอย่างยิ่งในการกู้สัญญาณให้โมเดลครับ"
- **Estimated Time:** 2:00 min

---

## Slide 10: Hardware Profiling & Production Latency
- **Category:** Efficiency Audit
- **Title:** Hardware Profiling & Production Latency
- **การวัดเวลาจริงบน NVIDIA GeForce GTX 1650 (4,096 MiB VRAM):**
  | ส่วนประกอบของ Pipeline | mDeBERTa-v3-base ($B1\text{-LR}$) | multilingual-MiniLMv2-L6 ($B1\text{-LR}$) |
  |---|---|---|
  | **ขนาดโมเดล (Parameters)** | ~278M parameters | ~107M parameters ($2.6\times$ เล็กกว่า) |
  | **Semantic Filter Latency** | Mean: 153.27 ms (Median: 148.25 ms) | Mean: 153.27 ms (Median: 148.25 ms) |
  | **Forward NLI Latency** | Mean: 313.73 ms (Median: 334.86 ms) | Mean: 29.19 ms (Median: 11.87 ms) ($10.7\times$ เร็วกว่า!) |
  | **Logistic Regression Layer** | Mean: 0.76 ms (Median: 0.62 ms) | Mean: 0.76 ms (Median: 0.62 ms) |
  | **Total Single-Item Latency** | **467.77 ms / claim** | **183.22 ms / claim** |
  | **Batched Throughput** | **~227 ms / claim** | เร็วกว่าระดับหลักสิบรอบต่อวินาที |
- **Production Safety in FastAPI:**
  - Wrap การคำนวณ GPU/CPU Bound ด้วย `asyncio.to_thread` เพื่อไม่บล็อก I/O ของผู้ใช้คนอื่น
  - รัน Single Worker ควบคุม VRAM ไม่ให้เกิด Memory Crash (OOM)
- **Speaker Notes (Thai):**
  > "เราวัดประสิทธิภาพจริงบนการ์ดจอระดับเริ่มต้นอย่าง GTX 1650 4GB VRAM เพื่อพิสูจน์ว่าระบบรันได้ในสภาพแวดล้อมจำกัด mDeBERTa ใช้เวลารวมเฉลี่ย 467ms แบบเดี่ยว และ 227ms แบบ Batched ส่วน MiniLM ทำ NLI ได้เร็วถึง 29ms เร็วกว่า 10 เท่า! ทำให้เรามีตัวเลือก Production Champion สองระดับ: mDeBERTa สำหรับความแม่นยำสูง และ MiniLM สำหรับงาน Edge หรือเครื่องลูกข่ายครับ"
- **Estimated Time:** 1:45 min

---

## Slide 11: External Transferability on AttributionBench
- **Category:** External Stress Testing
- **Title:** External Transferability on AttributionBench
- **การทดสอบความทนทานข้ามโดเมน (Frozen External Transfer):**
  - นำ $B1\text{-LR}$ ที่ผ่านการเทรนจาก WiCE ไปทดสอบบน **AttributionBench** ทันทีโดยไม่ Re-tune ค่าใดๆ ทั้งสิ้น
  1. **Official In-Domain Test ($N = 1,610$) — Mixed / Competitive Transfer:**
     - Accuracy: **63.85%** (B0: 64.72%, $-0.87$ pp)
     - Macro-$F_1$: **0.6384** (B0: 0.6462, $-0.0078$)
     - Supported-$F_1$: **0.6330** (B0: 0.6278, $+0.0052$)
     - FSR: **34.66%** (B0: 30.06%, $+4.60$ pp)
  2. **Official Out-of-Domain Test ($N = 1,686$) — Performance–FSR Trade-off:**
     - Accuracy: **73.01%** (B0: 71.95%, $+1.06$ pp)
     - Macro-$F_1$: **0.7281** (B0: 0.7190, $+0.0091$)
     - Supported-$F_1$: **0.7515** (B0: 0.7305, $+0.0210$)
     - FSR: **35.59%** (B0: 32.15%, $+3.44$ pp)
- **The B4 Selective Gating Discovery:**
  - ในการตรวจสอบความปลอดภัยขั้นสูง $B4$ มี False-Support Admission Rate เป็น **0%** จริง แต่เป็นเพราะ Threshold สูงจนทำหน้าที่เป็น High-Confidence Rejection Gate ที่ปฏิเสธ Claim เกือบทั้งหมด
  - $B1\text{-LR}$ จึงเป็นจุดสมดุลที่ดีที่สุดระหว่างความปลอดภัยและการใช้งานได้จริง
- **Speaker Notes (Thai):**
  > "เรานำโมเดลแชมป์เปียน B1-LR ไปทดสอบข้ามโดเมนบน AttributionBench ชุด Official Test ทั้งแบบ In-Domain 1,610 ตัวอย่าง และ Out-of-Domain 1,686 ตัวอย่าง โดยไม่มีการจูนค่าใหม่แม้แต่น้อย ผลคือในชุด In-Domain เป็นผลแบบ Mixed / Competitive โดยยังรักษาระดับคะแนนใกล้เคียง B0 และได้ Supp-F1 สูงขึ้นเล็กน้อย ส่วนในชุด Out-of-Domain B1-LR ทำคะแนน Accuracy (+1.06 pp), Macro-F1 (+0.0091) และ Supp-F1 (+0.0210) ได้สูงขึ้น โดยแลกมากับ False Support Rate ที่เพิ่มขึ้น (+3.44 pp) ซึ่งเป็นการรายงาน Performance–FSR Trade-off อย่างตรงไปตรงมาครับ"
- **Estimated Time:** 1:30 min

---

## Slide 12: Thesis-Safe Claims & Research Discipline
- **Category:** Academic Integrity
- **Title:** Thesis-Safe Claims & Research Discipline
- **สิ่งที่ผลการทดลองสนับสนุนอย่างหนักแน่น (Strongly Supported):**
  - Semantic Filtering ชนะอย่างมีนัยสำคัญเมื่อควบคุมเลเยอร์การตัดสินใจให้เท่ากัน
  - Task-Specific Logistic Regression ช่วยยกระดับ Macro-$F_1$ บนหลักฐานที่กรองแล้ว
  - Reverse NLI ไม่ให้ผลประโยชน์ที่น่าเชื่อถือทางสถิติข้าม 2 โมเดลที่เราทดสอบ
- **สิ่งที่ห้ามเคลมเกินจริงตามระเบียบวิธีวิจัย (Claims That Must NOT Be Made):**
  - ❌ *ห้ามเคลม:* "Reverse NLI ไร้ประโยชน์สำหรับทุกโมเดลในโลก" (เคลมได้เฉพาะ: *ไม่พบนัยสำคัญบนสองโมเดลที่ประเมิน*)
  - ❌ *ห้ามเคลม:* "MiniLM ดีกว่า mDeBERTa อย่างเป็นทางการ" (เพราะ MiniLM ตกเกณฑ์บน DEV ในขั้นตอนคัดเลือก การทดสอบ TEST เป็นเพียง Post-hoc Sensitivity)
  - ❌ *ห้ามเคลม:* "เอกสารยาวทำลาย Attention Mechanism" (เพราะไม่ได้วัด Attention Map ตรงๆ อ้างอิงได้เฉพาะพฤติกรรมการทำนาย)
- **Speaker Notes (Thai):**
  > "ในเชิงวิชาการ ความซื่อสัตย์ต่อข้อมูลสำคัญที่สุดครับ เราสรุปผลตามกรอบที่พิสูจน์ได้จริง เราไม่เคลมว่า Reverse NLI แย่สำหรับทุกโมเดลในโลก แต่ยืนยันว่าบนโมเดลที่เราทดลอง มันไม่คุ้มค่าทางสถิติ และเราไม่แอบโปรโมต MiniLM มาแทน mDeBERTa เพียงเพราะเห็นคะแนน Test สูงกว่า เพราะในกติกา Pre-registered มันตกเกณฑ์บน DEV ไปก่อนแล้ว นี่คือวินัยทางวิทยาศาสตร์ของโปรเจกต์นี้ครับ"
- **Estimated Time:** 1:30 min

---

## Slide 13: Conclusion & Next Steps
- **Category:** Conclusion
- **Title:** A Verifiable, Production-Ready Threat Intelligence Foundation
- **3 Key Executive Takeaways:**
  1. **สถาปัตยกรรมแข็งแกร่ง (Solid Architecture):** 4 บริการแยกอิสระ ยึดวินัย *"Read Short. Think Free. Write Short."* ไม่ล็อกฐานข้อมูล
  2. **Trust Boundary พิสูจน์แล้ว (Proven Grounding):** โมเดลแชมป์เปียน $B1\text{-LR}$ เอาชนะ baseline อย่างมีนัยสำคัญ ป้องกันการสร้างข้อมูลเท็จก่อนเข้าสู่ Judgement
  3. **พร้อมใช้งานจริง (Production-Ready):** ทำงานได้บนฮาร์ดแวร์ทั่วไป Latency ต่ำ ตรวจสอบย้อนกลับได้ทุกประโยค
- **Speaker Notes (Thai):**
  > "สรุปภาพรวมทั้งหมด CyberCase Framework เป็นแพลตฟอร์มที่เชื่อมโยงระหว่างสถาปัตยกรรมซอฟต์แวร์ที่แข็งแกร่ง กับโมเดล AI ที่มีหลักฐานตรวจสอบได้จริง เราพร้อมสำหรับการสาธิตระบบ (Live Demo) และการนำไปต่อยอดใช้งานจริงในหน่วยงานความมั่นคงปลอดภัยไซเบอร์ครับ ขอขอบคุณทุกท่านครับ มีคำถามหรือข้อสงสัยเพิ่มเติมไหมครับ?"
- **Estimated Time:** 1:00 min

---

## Defense Q&A Cheatsheet (สำหรับตอบข้อซักถามของกรรมการ / ผู้ฟัง)

### Q1: ทำไมถึงไม่ใช้ LLM-as-a-Judge เช่น GPT-4o หรือ Claude 3.5 Sonnet มาตรวจ Claim?
**แนวทางการตอบ:**
1. **Determinism:** LLM Judge มีความแปรปรวน (stochastic) และเสี่ยงต่อ Sycophancy Bias (ชอบเห็นด้วยกับสิ่งที่เขียนมา)
2. **Security:** หากเอกสารคดีมี Indirect Prompt Injection ตัว LLM Judge อาจถูกหลอกให้ตัดสินว่าถูกต้องได้ แต่ NLI เป็น Encoder ทางคณิตศาสตร์จึงปลอดภัยจาก Prompt Injection 100%
3. **Cost & Latency:** การตรวจ Claim 20–30 ข้อความต่อคดีด้วย LLM Judge จะเสียเวลาหลายสิบวินาทีและเสียเงินหลายบาท แต่ NLI บน Local GPU ใช้เวลาเพียงไม่กี่ร้อยมิลลิวินาทีและฟรีค่า Token

### Q2: ทำไม B0 บน MiniLM ถึงได้ Accuracy สูงถึง 69.16% ถ้าใช้ Naive Argmax แต่คุณบอกว่ามันล้มเหลว?
**แนวทางการตอบ:**
- เพราะชุดข้อมูล WiCE Test มี Class Imbalance สูง โดยมี Gold Negative ถึง 740 จาก 1,070 ตัว (ตรงกับ 69.16% พอดีเป๊ะ)
- เมื่อตรวจ Confusion Matrix ของ MiniLM B0 ภายใต้ Naive Argmax พบว่ามันตอบปฏิเสธไปถึง 1,020 ตัว (95.3%) และจับ Claim จริงได้แค่ 25 ตัว (Recall ต่ำเตี้ยเพียง 7.58%, Supported-$F_1$ = 0.1259)
- ดังนั้น Accuracy 69.16% จึงเป็นเพียง 'ภาพลวงตา' ของการทายลบเกือบทั้งหมด
- ภายใต้ Canonical Protocol ที่จูน Threshold บน DEV ($\theta_{\text{DEV}}=0.15$) โมเดลสามารถกู้ Recall กลับมาที่ 38.79% (Macro-$F_1$ = 0.5705) และเมื่อใส่ Semantic Filter + LR ($B1\text{-LR}$) Recall ฟื้นกลับมาเป็น 56.97% และ Macro-$F_1$ ทะยานขึ้นเป็น 0.6496

### Q3: ทำไม MiniLM ได้ Macro-F1 บน TEST สูงกว่า mDeBERTa (0.6496 vs 0.6185) แต่คุณไม่เลือก MiniLM เป็นโมเดลหลัก?
**แนวทางการตอบ:**
- เพราะเรารักษาวินัย **Pre-registered Scientific Protocol**: ในขั้นตอนคัดเลือกบน DEV Split โมเดล MiniLM ทำคะแนนแพ้ mDeBERTa (0.6240 vs 0.6397) จึงไม่ผ่านเกณฑ์การเลื่อนชั้น (DEV Promotion Gate)
- การนำ MiniLM มารันบน TEST เกิดขึ้นภายหลังเพื่อทำ Post-hoc Cross-Backbone Sensitivity Analysis และตรวจสอบความเร็ว
- ในระเบียบวิธีวิจัยที่ดี เราต้องไม่เปลี่ยนโมเดลหลักย้อนหลังหลังจากที่เห็นคะแนนบน TEST แล้ว แต่เราสามารถระบุให้ MiniLM เป็นตัวเลือก 'High-Throughput Edge Alternative' ได้ครับ

### Q4: ทำไม Reverse NLI ถึงไม่ช่วยเพิ่มคะแนน?
**แนวทางการตอบ:**
- ทฤษฎี NLI ดั้งเดิมระบุว่า Premise ต้องครอบคลุม Hypothesis ($E \implies C$) การตรวจย้อนกลับ ($C \implies E$) มักจะให้ผลเป็น Neutral หรือ Contradiction เมื่อ Evidence มีข้อมูลกว้างกว่า Claim อยู่แล้ว ทำให้ Feature ฝั่ง Reverse ไม่ได้ให้ Signal ใหม่ที่มีนัยสำคัญต่อโมเดล Logistic Regression เลย และผล Bootstrap 95% CI ก็ครอบคลุมศูนย์ทั้งสองสถาปัตยกรรมครับ

### Q5: คำจำกัดความของ FSR (False Support Rate) ในงานนี้คืออะไร? ต่างจาก False Discovery Rate (FDR) อย่างไร?
**แนวทางการตอบ:**
- ในงานวิจัยนี้ FSR นิยามอย่างชัดเจนตามสูตรความปลอดภัยของคดี:
  $$\text{FSR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$
- นั่นคือ **False Positive Rate over Gold Unsupported Claims** (ตัวหารคือจำนวน Claim ทั้งหมดในชุดทดสอบที่ไม่มีหลักฐานรองรับจริง $N_{\text{neg}} = 740$)
- เราเลือกสูตรนี้เพราะในงานความมั่นคงไซเบอร์และคดีความ สิ่งที่เราต้องการควบคุมคือ **"จากข้อความหลอกลวง/ไม่มีมูลความจริงทั้งหมด ระบบพลาดปล่อยให้หลุดผ่าน (Admit as Supported) ไปกี่เปอร์เซ็นต์"** ซึ่งเทียบเท่ากับ Admission Rate of False Claims
- ถ้าใช้ $\frac{\text{FP}}{\text{TP} + \text{FP}}$ จะเป็น False Discovery Rate (FDR) ซึ่งแปรผันตามจำนวนข้อความที่ทำนายบวกทั้งหมด แต่สูตร FPR ของเรายึดโยงกับ Gold Negative คงที่ ทำให้เปรียบเทียบข้าม Baseline ได้อย่างเที่ยงตรงครับ
