# CyberCase: จุดขายของตัวระบบเมื่อเทียบกับงานใกล้เคียงบน OpenReview

วันที่ตรวจ: 2026-10-01 | โค้ดที่ตรวจ: HEAD `7c57bd9` | ขอบเขต: เปรียบเทียบ contribution ของระบบ ไม่รันโมเดล ไม่แก้ application

## ข้อเสนอที่ได้จากการเปรียบเทียบ

**เสนอ CyberCase เป็นกระบวนการวิเคราะห์สำนวนที่ใช้ claim พร้อมที่มาและสถานะเป็นหน่วยกลาง แยกการสร้างรายการ claims ออกจากการสังเคราะห์ภาพรวม และให้ backend ตรวจการอ้างอิงก่อนเก็บผลไปใช้งานต่อ**

นี่เป็นข้อเสนอด้าน system design และการนำไปใช้กับงานสำนวน พร้อมผลเชิงประจักษ์สนับสนุน ไม่ใช่ข้อสรุปว่าเราเป็นคนแรกที่คิดการแยกขั้นหรือการตรวจ quote และยังไม่มีการทดลองเทียบกับวิธีในบทความด้านล่างโดยตรง

ของที่อยู่ในระบบจริงมีสามส่วน:

1. **Claim representation:** เก็บข้อความ, ประเภท reported/analytical_inference/unknown, สถานะความรู้ และ supporting/contradicting citations; parties, timeline และ impacts อ้าง claim IDs
2. **Reading/Judgement separation:** ขั้นอ่านสร้าง claims และโครงสร้างคดี; ขั้น judgement สร้าง summary, gaps และ optional technical interpretation โดย schema ไม่เปิดให้เขียนทับ claims/parties/timeline/impacts
3. **Backend provenance control:** binder ตรวจ source และข้อความอ้างอิง จัดตำแหน่งต้นทาง และลด `reported` ที่ไม่มี supporting citation ผ่านการตรวจเป็น `not_confirmed`; report สร้างจาก analysis snapshot ที่เก็บไว้

ประโยชน์ที่ออกแบบไว้คือให้ผู้ใช้ตรวจรายการข้อกล่าวอ้าง ที่มา และสิ่งที่ยังไม่ทราบได้แยกจากสรุปภาพรวม ส่วนประโยชน์ต่อความเร็ว/ความถูกต้องของผู้ใช้ต้องมีการศึกษาผู้ใช้ก่อนจึงจะอ้างผลได้

## งานที่พบและสิ่งที่แต่ละงานเสนอ

| งานบน OpenReview | Contribution ที่ระบุในงาน | ส่วนที่ทับกับ CyberCase และผลต่อจุดขาย | สถานะที่ยืนยันได้ |
|---|---|---|---|
| [Auditable Evidence Trails for Pedagogy-Grounded LLM Judging](https://openreview.net/pdf?id=CF3TqONsjF) | ระบบสร้าง rubric แล้วให้ agent อีกตัวให้คะแนนพร้อม evidence trail; orchestrator ตรวจ source presence และกฎการให้คะแนน | ใกล้ที่สุดในเชิงระบบ: แยกขั้น + trace + โค้ดตรวจมีอยู่แล้ว เราต้องระบุปัญหาและโครงสร้างเฉพาะงานสำนวนให้ชัด | Anonymous ACL submission; ยังยืนยัน acceptance ไม่ได้ |
| [FRONT: Learning Fine-Grained Grounded Citations for Attributed Large Language Models](https://openreview.net/pdf?id=7atXKldh-r) | ฝึกโมเดลเลือก quote ก่อนสร้างคำตอบ แล้วใช้ preference optimization จัดคำตอบให้สอดคล้องกับ quote | หลักเลือกหลักฐานก่อนเขียนคำตอบมี prior work; CyberCase ใช้ API และจัด case representation ไม่ได้เสนอ training recipe นี้ | [Findings ACL 2024](https://aclanthology.org/2024.findings-acl.838/) |
| [SelfCite: Self-Supervised Alignment for Context Attribution in Large Language Models](https://openreview.net/forum?id=rKi8eyJBoB) | ใช้ reward จากการเอาข้อความที่ cite ออก/เก็บเฉพาะข้อความนั้น เพื่อเลือกและฝึก citation | งานนี้เสนอวิธีสร้าง citation ที่ดีขึ้น เราตรวจ occurrence ของ citation ที่โมเดลเสนอ จึงไม่ใช่ verifier ความหมายหรือวิธีเดียวกัน | [ICML 2025 / PMLR 267](https://proceedings.mlr.press/v267/chuang25a.html) |
| [CogniBench: A Legal-inspired Framework and Dataset for Assessing Cognitive Faithfulness of Large Language Models](https://openreview.net/pdf/1ec0391d9c9fd60a5a47083851b7e95c445c5627.pdf) | แยก factual statements กับ cognitive statements และสร้างเกณฑ์/ชุดข้อมูลตรวจความสอดคล้องของข้ออนุมาน | สนับสนุนว่าการอ้างข้อเท็จจริงกับการอนุมานต้องประเมินต่างกัน; เรามีประเภท/สถานะ แต่ยังไม่ตรวจ cognitive faithfulness | [ACL 2025](https://aclanthology.org/2025.acl-long.1046/) |
| [NyayaMind: A Framework for Transparent Legal Reasoning and Judgment Prediction in the Indian Legal System](https://openreview.net/pdf/809df147b865f2b676b87aca5d6e327a3ac2b2ee.pdf) | Framework ที่รวม retrieval กฎหมาย/คดีเก่า กับโมเดล fine-tune สำหรับ issues, arguments, reasoning และ outcome | ใกล้ใน domain และการจัด reasoning เป็นโครงสร้าง แต่เป้าหมายหลักคือ legal outcome/explanation ไม่ใช่ coverage ของข้อมูลในสำนวน | Anonymous ACL submission + [arXiv 2604.09069](https://arxiv.org/abs/2604.09069); ยังยืนยัน acceptance ไม่ได้ |

### แหล่งที่อ่านและข้อจำกัดการเข้าถึง

- OpenReview forum/PDF บางหน้าแสดง browser challenge และ public API ตอบ HTTP 403 จึง **ไม่ได้อ่าน official reviews, rebuttals หรือคะแนนกรรมการของรายการเหล่านี้**
- Auditable Evidence Trails: อ่าน indexed excerpts จากต้นฉบับ OpenReview ได้แก่ abstract/บทนำและ limitations; ไม่ได้อ้างว่าอ่านทั้งฉบับ งานระบุเองว่าการตรวจ quote ตรวจเพียง source presence ไม่พิสูจน์ semantic support
- FRONT: อ่าน methodology 3.1–3.2, experimental settings และ human evaluation จาก [ต้นฉบับ arXiv](https://arxiv.org/html/2408.04568v1); ยืนยัน publication จาก ACL Anthology แยกจาก anonymous submission ชื่อขั้น alignment ใน revision ต่างกัน
- SelfCite: อ่านวิธี reward/context ablation และ discussion เรื่อง contributive/corroborative attribution จาก [ต้นฉบับ arXiv](https://arxiv.org/html/2502.09604v2); PMLR ยืนยันทั้ง publication และลิงก์ OpenReview
- CogniBench: อ่านนิยาม/annotation framework 2.1–2.2 และวิธีขยายข้อมูลจาก [ต้นฉบับ arXiv](https://arxiv.org/html/2505.20767v1); งานใช้แนวคิดกฎหมายเป็น analogy ไม่ใช่การทดลองวิเคราะห์สำนวนคดีจริง
- NyayaMind: อ่าน task description 3.1–3.4 และ dataset/methodology ที่เกี่ยวข้องจาก [ต้นฉบับ arXiv](https://arxiv.org/html/2604.09069v1); ไม่ยกผลของผู้เขียนมาเป็นผลที่เราตรวจซ้ำแล้ว

## งานนอก OpenReview ที่จำกัดการอ้าง novelty โดยตรง

[AI Assistance for Court Review of Default Judgments — Default Assistant](https://clp.law.stanford.edu/wp-content/uploads/2026/05/AI-Assistance-for-Court-Review-of-Default-Judgments.pdf), หน้า 3–4: ดึง quote/table จากเอกสารคดี หาตำแหน่งในต้นฉบับ เก็บเฉพาะส่วนที่หาเจอ แล้วให้โมเดลเขียนคำแนะนำพร้อม citation งานนี้ทำ source verification **ก่อน** final generation และมีการศึกษาผู้ใช้

จึงอ้างไม่ได้ว่าระบบอ่านสำนวน แยก extraction กับ judgement และตรวจ quote ด้วยโค้ดเพิ่งมีใน CyberCase ความแตกต่างที่เสนอได้ต้องเป็นรายละเอียดการจัดข้อมูล/งานเป้าหมาย และผลการประเมินของเรา ไม่ใช่การประกาศว่าการประกอบขั้นเหล่านี้ไม่เคยมีใครทำ

## Mapping กลับไปยังโค้ดจริง

| ส่วนของข้อเสนอ | หลักฐานใน repository |
|---|---|
| ประเภท claim และ epistemic status | [claims.py](../../backend/app/trace/claims.py) บรรทัด 15–25 |
| Quote/source citation contract | [claims.py](../../backend/app/trace/claims.py) บรรทัด 69–76 |
| Schema แยกเจ้าของ fields | [trace.py](../../backend/app/trace/trace.py) บรรทัด 137–153 |
| สอง model calls และ input ของ judgement | [write.py](../../backend/app/analysis/write.py) บรรทัด 24–40 |
| รวม trace โดยใช้ evidence fields จาก reading | [write.py](../../backend/app/analysis/write.py) บรรทัด 103–119 |
| Binder แก้ citations/status | [bind.py](../../backend/app/trace/bind.py) บรรทัด 191–220 |
| ค้น quote ใน source | [bind.py](../../backend/app/trace/bind.py) บรรทัด 232–247 |
| Report จาก stored analysis | [generate.py](../../backend/app/reports/generate.py) บรรทัด 54–64 |

## เส้นแบ่งระหว่างสิ่งที่ระบบทำกับสิ่งที่ผลทดลองพิสูจน์

- การไม่ให้ judgement เขียนทับ evidence fields เป็น property ของ schema/การรวม trace แต่ยังไม่ได้แยกผลเชิงสาเหตุของ property นี้จาก extra model call หรือ prompts
- Reading เองสร้างทั้ง reported claims และ qualified inferences ได้ จึงไม่ใช่การบังคับให้ขั้นแรกมีแต่ข้อเท็จจริง; ประเภท/สถานะที่โมเดลใส่มายังไม่ใช่ ground truth
- Judgement เห็น raw sources และ reading ที่ยังไม่ผ่าน binder; binder ทำงานหลังสอง calls ห้ามบรรยายว่า judgement รับแต่หลักฐานที่ตรวจแล้ว
- การคง claims ไม่ได้พิสูจน์ว่า summary เขียนถูกหรือไม่เติมข้ออนุมาน การตรวจ quote occurrence ก็ไม่พิสูจน์ว่า quote รองรับความหมายของ claim
- M4/M4b วัด overlap/lexical coverage กับ CASIE annotations ไม่ใช่ผลการตรวจความถูกต้องทางกฎหมายหรือ semantic entailment
- ผล two-call versus one-call ที่ควบคุม decoding สนับสนุน workflow comparison; ยังไม่ใช่การเทียบกับ FRONT, SelfCite, Default Assistant หรือ Auditable Evidence Trails
- Grammar/structured-output policy เป็นผลประกอบด้านการทำให้ workflow รันสำเร็จ ไม่ต้องเปลี่ยนให้เป็น contribution หลักของตัวระบบ

## ข้อเสนอสำหรับการเขียนเปเปอร์

เริ่มจากปัญหาของงานสำนวน: ผู้ตรวจต้องเห็นข้อกล่าวอ้าง ที่มา ประเภท และช่องว่างของข้อมูลแยกจากข้อความสรุป จากนั้นเสนอ claim representation + reading/judgement contracts + backend binding เป็นระบบที่แก้ปัญหานี้ แล้วใช้ผล traceability/annotated coverage ที่มีอยู่ประเมินระบบ

สิ่งที่ยังไม่ยืนยันคือความใหม่ของระบบเหนือ closest prior work และประโยชน์ต่อผู้ใช้จริง ถ้าจะอ้าง superiority ต้องมี baseline ตามวิธีงานนั้น; ถ้าจะอ้างความแม่นยำของข้อวิเคราะห์ต้องมี semantic/human evaluation เพิ่ม ข้อเสนอในบันทึกนี้ไม่ได้อนุมัติหรือเริ่มการทดลองเหล่านั้น
