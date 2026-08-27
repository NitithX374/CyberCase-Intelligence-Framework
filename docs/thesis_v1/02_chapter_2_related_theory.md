# บทที่ 2 ทฤษฎีและงานที่เกี่ยวข้อง

## 2.1 แบบจำลองภาษาขนาดใหญ่

แบบจำลองภาษาขนาดใหญ่ (Large Language Model: LLM) เป็นแบบจำลองเชิงสถิติที่เรียนรู้ความสัมพันธ์ของหน่วยภาษาและสร้างลำดับข้อความตามบริบท สถาปัตยกรรม Transformer ใช้กลไก attention เพื่อประมวลความสัมพันธ์ระหว่างตำแหน่งในลำดับและเป็นรากฐานของแบบจำลองภาษาสมัยใหม่จำนวนมาก [@vaswani2017attention] ในงานเชิงระบบ LLM สามารถรับ instruction, context และข้อกำหนดรูปแบบผลลัพธ์เพื่อสรุป จำแนก หรือสร้างข้อความได้

ข้อจำกัดสำคัญคือ LLM สร้างข้อความจากความน่าจะเป็น มิได้ทำการพิสูจน์ข้อเท็จจริงโดยธรรมชาติ ข้อความที่อ่านดีอาจมีรายละเอียดที่ไม่มีใน input หรือเพิ่มความแน่นอนเกินหลักฐาน CyberCase จึงไม่ใช้ prose เพียงอย่างเดียวเป็นสภาวะของการวิเคราะห์ แต่สร้าง structured trace ควบคู่กัน พร้อมตรวจความสอดคล้องของรหัสแหล่งที่มา การใช้ LLM ในระบบนี้เป็นการประยุกต์ใช้เพื่อช่วยจัดรูปและวิเคราะห์ข้อมูล ไม่ใช่ข้อเสนอ Transformer หรือ LLM architecture ใหม่

## 2.2 Prompt Engineering และ Structured Generation

Prompt engineering คือการกำหนดบทบาท ขอบเขตข้อมูล คำสั่ง และรูปแบบผลลัพธ์ให้โมเดล ในระบบที่ต้องการตรวจสอบย้อนกลับ prompt ต้องระบุทั้งสิ่งที่อนุญาตและสิ่งที่ห้าม เช่น ระบุว่า raw evidence เป็นข้อมูล authoritative เพียงแหล่งเดียว ห้ามใช้ external context เพื่อเติมข้อเท็จจริงของคดี และห้ามสรุปความผิดหรือผลทางกฎหมาย

Structured generation ทำให้ผลลัพธ์มี schema เช่น JSON ที่ตรวจด้วย Pydantic ได้ ข้อดีคือระบบสามารถตรวจ type, enumeration, cardinality และ cross-reference ก่อนบันทึก แต่ schema validity ไม่เท่ากับ factual validity ข้อมูลอาจมีรูปแบบถูกต้องแต่ชี้ source ID ที่ไม่สนับสนุน claim CyberCase จึงเพิ่ม semantic/provenance validation ได้แก่ การตรวจว่า source ID อยู่ใน evidence set, supporting กับ contradicting IDs ไม่ทับกัน, reported/inference claims ต้องมีแหล่งสนับสนุน และ inference ต้องมี reasoning summary

ระบบใช้แนวคิด fail-closed กับข้อผิดพลาดที่กระทบ trust boundary กล่าวคือไม่ยอมรับ trace ที่ provenance ผิด แม้ในบางกรณีที่โครงสร้างวิเคราะห์ไม่สมบูรณ์ ระบบอาจคง visible prose เพื่อไม่ทำให้ผู้ใช้สูญเสียคำตอบ พร้อมบันทึก failure metadata แยกต่างหาก การออกแบบนี้สะท้อนว่าความล้มเหลวเชิง presentation กับความล้มเหลวเชิงหลักฐานมีระดับความเสี่ยงต่างกัน

## 2.3 Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) ผสานการค้นคืนข้อมูลกับการสร้างข้อความ โดยนำเอกสารหรือข้อความที่ค้นได้มาเป็น context แก่ generator งานต้นแบบของ Lewis และคณะอธิบายการเชื่อม parametric memory ของแบบจำลองกับ non-parametric memory จากดัชนีภายนอก [@lewis2020rag] ส่วน Dense Passage Retrieval ใช้ dual encoders เพื่อฝังคำถามและ passage ในปริภูมิเดียวกันสำหรับค้นคืน [@karpukhin2020dpr]

RAG ช่วยให้ระบบเข้าถึงข้อมูลเฉพาะโดเมนที่ไม่ควรคาดหวังให้โมเดลจำจากการฝึก แต่ไม่รับประกันว่าข้อมูลที่ค้นได้เกี่ยวข้องหรือว่าคำตอบจะอ้างบริบทอย่างถูกต้อง จึงต้องแยกขั้น retrieval, evaluation, reasoning และ validation ใน CyberCase บริการ RAG ไม่ใช่แหล่งหลักฐานของคดี แต่เป็นแหล่งข้อมูลเทคนิคภายนอกสำหรับช่วยตีความพฤติกรรมไซเบอร์ Backend บันทึก retrieval context ที่คืนมาเพื่อให้ทราบว่าการวิเคราะห์รุ่นหนึ่งอาศัย snapshot ใด

## 2.4 Vector Search, Sparse Retrieval และ Rank Fusion

การค้นคืนแบบเวกเตอร์แทนข้อความด้วย embedding แล้ววัดความใกล้ เช่น cosine similarity ทำให้ค้นข้อความที่ใช้คำต่างกันแต่มีความหมายใกล้กันได้ BGE-M3 เป็น embedding model ที่รองรับหลายภาษาและหลายรูปแบบการค้นคืน ได้แก่ dense, sparse และ multi-vector [@chen2024bgem3] current RAG service กำหนด embedding dimension 1,024 และใช้ทั้ง dense กับ sparse retrieval ใน Qdrant

Dense retrieval เหมาะกับ semantic similarity ขณะที่ sparse retrieval ให้ความสำคัญกับ token หรือคำเฉพาะ เช่น technique IDs และชื่อเครื่องมือ การรวมอันดับด้วย Reciprocal Rank Fusion (RRF) ช่วยรวมผลจากตัวจัดอันดับหลายชุดโดยไม่ต้องทำให้คะแนนดิบอยู่ในสเกลเดียวกัน [@cormack2009rrf] หลังการรวม ระบบใช้ cross-encoder reranker เพื่อจัดลำดับ candidates อีกครั้ง การออกแบบหลายขั้นเพิ่มโอกาสได้ context ที่เกี่ยวข้อง แต่เพิ่ม latency และจุดที่ต้องประเมินแยกกัน

## 2.5 Knowledge Graph และ Graph-Based Retrieval

Knowledge graph แทน entity และความสัมพันธ์ด้วยโหนดและเส้นเชื่อม เหมาะกับข้อมูล MITRE ATT&CK ซึ่ง technique อาจเชื่อมกับ tactic, software, mitigation หรือ object อื่นใน STIX ข้อดีของ graph retrieval คือสามารถดึงบริบทที่มีความสัมพันธ์โดยตรงกับผล vector search แทนการพึ่งความคล้ายทางภาษาเท่านั้น

ใน current implementation ผลจาก Qdrant ถูกนำไปขยายเพื่อนบ้านขาเข้าและขาออกโดยตรงใน Neo4j แล้วรวมเป็น context หลัก ดังนั้นบทนี้อธิบายเส้นทางหลักว่าเป็น direct 1-hop expansion ไม่ใช่ 2-hop แม้เอกสารเก่าบางไฟล์กล่าวถึงการขยายสองชั้น และแม้ repository จะมี helper สำหรับ multi-hop path แยกต่างหาก ความแตกต่างระหว่าง documentation กับ code path นี้เป็นตัวอย่างของเหตุผลที่วิทยานิพนธ์ต้องยึด runtime path ปัจจุบัน

## 2.6 MITRE ATT&CK และ STIX 2.1

MITRE ATT&CK เป็นฐานความรู้เกี่ยวกับ tactics และ techniques ของผู้โจมตีที่อาศัยข้อสังเกตจากโลกจริง [@mitreAttack] Tactic อธิบายวัตถุประสงค์เชิงยุทธวิธี ส่วน technique อธิบายวิธีที่ผู้โจมตีบรรลุวัตถุประสงค์ และ sub-technique ให้รายละเอียดเฉพาะยิ่งขึ้น ข้อมูล ATT&CK ใน repository อยู่ในรูป STIX 2.1 ซึ่งเป็นมาตรฐานการแทนและแลกเปลี่ยน cyber threat intelligence แบบ machine-readable [@oasisStix21]

ATT&CK มีประโยชน์ต่อการตั้งชื่อและอธิบายพฤติกรรมไซเบอร์ แต่ไม่ควรเป็น ontology กลางของคดีทุกประเภท และการที่คำบรรยายมีคำคล้าย technique ไม่ใช่หลักฐานยืนยันเทคนิคนั้น CyberCase จึงกำหนด MITRE association เป็น `candidate_only` และ `external_technical_context` เชื่อมกับ claim ที่ได้รับการตรวจแล้ว การตัดสินใจนี้คงประโยชน์ของมาตรฐานทางเทคนิคโดยไม่ย้าย authority จากสำนวนไปสู่ฐานความรู้

## 2.7 Evidence Grounding และ Source Provenance

Grounding หมายถึงการผูกข้อความที่ระบบสร้างกับข้อมูลที่อนุญาตให้ใช้สนับสนุน ส่วน provenance หมายถึงข้อมูลว่าข้อความนั้นมาจากแหล่งใด การประเมิน attributed information seeking เสนอให้แยกคุณภาพคำตอบออกจากคุณภาพ attribution เพราะคำตอบอาจถูกต้องแต่ไม่มีแหล่ง หรือมีแหล่งแต่แหล่งไม่รองรับข้อความ [@rashkin2023measuring] ALCE เสนอเกณฑ์ที่พิจารณาความถูกต้อง ความครบถ้วน และคุณภาพ citation ในระบบสร้างคำตอบพร้อมอ้างอิง [@gao2023alce]

CyberCase ใช้ message-level provenance โดยแต่ละ claim ระบุ supporting และ contradicting source message IDs ข้อดีคือรหัสอ้างอิงตรงกับหน่วย persistence ที่แน่นอนและตรวจได้ ข้อจำกัดคือข้อความหนึ่งอาจยาวและมีหลายข้อความจริง/เท็จ การชี้ทั้ง message จึงไม่ละเอียดเท่าระดับ page, paragraph หรือ span การพัฒนาระยะยาวควรรักษา document ID, page และ offsets แต่ต้องไม่สร้าง source locator ที่ไม่มีอยู่จริง

ค่า evidence SHA-256 ใช้ตรวจว่าผลวิเคราะห์ผูกกับ raw evidence snapshot ใด ค่าแฮชไม่รับรองความจริงของเนื้อหา แต่ช่วยตรวจ stale binding และการเปลี่ยน input แบบ deterministic เมื่อนำมาร่วมกับ retrieval-context ID ระบบสามารถบอกได้ว่าการวิเคราะห์หนึ่งอาศัยหลักฐานและบริบทภายนอกชุดใด

## 2.8 Epistemic Uncertainty ในผลลัพธ์ของ LLM

ความไม่แน่นอนทางญาณวิทยาเกี่ยวข้องกับสิ่งที่ระบบรู้จากหลักฐานและระดับที่ข้ออ้างได้รับการสนับสนุน ไม่ใช่เพียงค่า probability ภายในโมเดล งานด้าน calibration ชี้ว่าความเชื่อมั่นที่แบบจำลองแสดงอาจไม่สอดคล้องกับความถูกต้องจริง และวิธีถามหรือรูปแบบงานมีผลต่อ calibration [@jiang2021calibrating; @geng2024survey]

CyberCase ไม่แสดงคะแนน confidence เชิงตัวเลข เพราะ repository ยังไม่มี calibration study ที่ทำให้ตัวเลขดังกล่าวมีความหมาย ระบบใช้สถานะแบบ categorical ได้แก่ `reported`, `suspected`, `contradicted`, `not_established`, `unknown` และ `not_confirmed` ร่วมกับประเภท claim `reported`, `analytical_inference` และ `unknown` การแยกสองมิตินี้ทำให้บอกได้ทั้งธรรมชาติของข้ออ้างและสถานะการสนับสนุน เช่น analytical inference อาจเป็น `suspected` และต้องมี reasoning summary โดยไม่ถูกนำเสนอเป็นข้อเท็จจริง

## 2.9 Gap Analysis และ Clarification Questions

การถาม clarification เป็นแนวทางจัดการ input ที่กำกวมหรือไม่เพียงพอ งาน ClarQ จัดชุดข้อมูลคำถามขอความชัดเจนขนาดใหญ่จากหลายโดเมน [@kumar2020clarq] และงาน CAmbigNQ แยกปัญหาเป็นการตรวจ ambiguity, สร้างคำถาม clarification และตอบหลังได้รับคำชี้แจง [@lee2023clarification] งานเหล่านี้ให้หลักการว่าการถามควรสัมพันธ์กับ ambiguity และ downstream task แต่ไม่ได้ออกแบบสำหรับสำนวนคดีโดยตรง

CyberCase ใช้ taxonomy สี่ค่า: `NOT_PROVIDED` สำหรับข้อมูลที่ยังไม่ให้, `EXPLICITLY_UNKNOWN` สำหรับข้อมูลที่ผู้ใช้ระบุว่าไม่ทราบหรือไม่มี, `AMBIGUOUS` สำหรับข้อมูลตีความได้หลายแบบ และ `CONFLICTING` สำหรับข้อมูลขัดแย้งกัน ความต่างที่สำคัญคือ `EXPLICITLY_UNKNOWN` ไม่ควรสร้างคำถามซ้ำ ระบบเลือกได้สูงสุดหนึ่ง gap ที่ถามได้และมี priority สูงหรือกลางในหนึ่ง decision พร้อมจำกัดจำนวนรอบปัจจุบันไว้สองรอบ

การออกแบบนี้เป็นการประยุกต์ workflow ไม่ใช่วิธีสร้างคำถามใหม่ทางวิจัย และผล pilot หนึ่งกรณีไม่เพียงพอจะบอกว่าคำถามดีขึ้นโดยทั่วไป การประเมินที่เหมาะสมในอนาคตควรวัด necessity, answerability, target-gap match, redundancy, downstream claim change และภาระคำถามร่วมกัน

## 2.10 OCR และ Document Understanding

Optical Character Recognition (OCR) แปลงภาพตัวอักษรพิมพ์เป็นข้อความ ส่วน Handwritten Text Recognition (HTR) มุ่งที่ลายมือ เอกสารจริงยังต้องผ่านการแบ่งหน้า การตรวจชนิดเอกสาร การจัดลำดับ และการรักษาตำแหน่งต้นทางก่อนเข้าสู่ analysis การใช้ OCR ไม่ได้ทำให้ข้อความเป็นหลักฐานที่เชื่อถือได้โดยอัตโนมัติ เพราะอาจอ่านผิด ลำดับข้อความผิด หรือสูญเสีย layout

working tree ปัจจุบันของ CyberCase มี preview pipeline สำหรับ PDF, DOCX, PNG และ JPEG ใช้ Typhoon OCR กับหน้าที่ถูก route และปิด HTR ไว้ ผลลัพธ์แสดงแก่ผู้ใช้เป็น untrusted preview และยังไม่ถูก persist หรือป้อนเข้า raw evidence การกล่าวถึง document understanding ในวิทยานิพนธ์จึงต้องจำกัดที่ต้นแบบ preview และแนวทางในอนาคต ไม่อ้างว่าระบบวิเคราะห์สำนวนเอกสารครบวงจรแล้ว

## 2.11 งานและระบบที่เกี่ยวข้อง

งานของ Scanlon และคณะสำรวจทั้งประโยชน์และความเสี่ยงของ ChatGPT ในงานนิติวิทยาศาสตร์ดิจิทัลหลายประเภท และเน้นว่าการใช้งานที่มีความเสี่ยงต้องอาศัยผู้มีความรู้เพื่อตรวจจับสมมติฐานและความผิดพลาด [@scanlon2023digitalforensics] ส่วนงานด้าน LLM เพื่อช่วยเขียนรายงานนิติวิทยาศาสตร์ดิจิทัลของ Michelet และ Breitinger ทดลองใช้ ChatGPT และ Llama 2 กับส่วนประกอบของรายงาน และสรุปว่า LLM อาจช่วยงานเขียนเมื่อมีการตรวจแก้อย่างรอบคอบ แต่ยังแทนผู้ปฏิบัติงานไม่ได้ [@michelet2024report] หลักการนี้สอดคล้องกับขอบเขตของ CyberCase ที่สร้างรายงาน provisional/structured และคง human review เป็นเงื่อนไข

เครื่องมือเอกสารทั่วไปที่ใช้ LLM มักเน้นถามตอบหรือสรุปเอกสาร แต่ขอบเขตของ CyberCase ต่างออกไปตรงการแยก raw evidence, analysis trace, external context, gap decision และ persisted report เป็น stages ที่ตรวจได้ การเปรียบเทียบนี้เป็นความต่างด้าน system design ไม่ใช่การกล่าวว่า CyberCase มีโมเดลที่เหนือกว่า

สำหรับระบบไซเบอร์ ATT&CK Navigator หรือเครื่องมือ threat intelligence เน้นการสำรวจและจัดทำ mapping ของ tactics/techniques ขณะที่ CyberCase นำ ATT&CK มาเป็นส่วนเสริมของ case review ระบบจึงต้องแสดงทั้งเหตุผลของ association และข้อจำกัดว่า association เป็น candidate ไม่ใช่ forensic finding

## 2.12 สรุปทฤษฎีและผลต่อการออกแบบ

### ตารางที่ 2-1 ความสัมพันธ์ระหว่างทฤษฎีกับการตัดสินใจออกแบบ

| ทฤษฎี/งานที่เกี่ยวข้อง | ความเสี่ยงหรือโอกาส | การตัดสินใจใน CyberCase |
|---|---|---|
| LLM/Transformer | สร้างข้อความได้ดีแต่ไม่พิสูจน์ข้อเท็จจริง | แยก prose กับ validated trace |
| Structured generation | ตรวจ schema ได้ แต่ข้อมูลอาจอ้าง source ผิด | เพิ่ม provenance validation ข้ามฟิลด์ |
| RAG | เพิ่มความรู้เฉพาะโดเมน แต่ retrieval อาจไม่ตรง | แยก external context จาก evidence |
| Dense+sparse retrieval และ RRF | ครอบคลุม semantic/lexical signals | ใช้ Qdrant hybrid retrieval และ reranker |
| Knowledge graph | เพิ่มความสัมพันธ์จาก candidate | ใช้ Neo4j direct-neighbor expansion |
| ATT&CK/STIX | มีภาษากลางทางไซเบอร์ | ใช้เฉพาะ technical enrichment |
| Factuality/attribution | ข้อความยาวมีทั้ง supported/unsupported claims | แยก atomic claims และ source IDs |
| Calibration | confidence ที่แสดงอาจไม่น่าเชื่อถือ | ใช้ categorical epistemic status; ไม่แสดงคะแนนที่ไม่ calibrate |
| Clarification research | คำถามช่วยแก้ ambiguity แต่เพิ่ม burden | gap taxonomy, one focused question, bounded rounds |
| OCR/document understanding | ขยายช่องทาง input แต่เพิ่ม extraction error | preview-only และ human review ก่อน authority |

จากทฤษฎีเหล่านี้ ระบบที่เหมาะกับโครงงานมิใช่ pipeline ที่นำเอกสารเข้า LLM แล้วพิมพ์รายงานทันที แต่เป็นระบบหลายชั้นที่คง identity ของข้อมูลต้นทาง ตรวจสัญญาผลลัพธ์ จำกัด authority ของ knowledge base และยอมรับอย่างชัดเจนว่าผลลัพธ์ทุกชิ้นยังต้องได้รับการตรวจจากมนุษย์
