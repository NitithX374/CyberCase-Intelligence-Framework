# CyberCase Framework — SDLC และคู่มือทำความเข้าใจ Frontend / Backend

วันที่จัดทำ: 10 กันยายน 2026  
ขอบเขต: โค้ดใน working tree ของ `F:\Cybercase Framework` บน branch `main` ณ วันที่ตรวจสอบ มีการแก้ไขที่ยังไม่ได้ commit จึงไม่เท่ากับ release ที่ deploy แล้ว  
ผู้อ่าน: เจ้าของระบบ นักพัฒนา และผู้ที่ต้องอธิบายระบบโดยเริ่มจากพื้นฐาน

## 1. เริ่มอ่านตรงไหน

ถ้ายังไม่รู้จักระบบ ให้อ่านบท 2–5 ก่อน เพื่อเข้าใจว่าผู้ใช้ทำอะไรและข้อมูลเดินทางอย่างไร จากนั้นอ่านบท 6–12 เพื่อเข้าใจโค้ดและข้อมูล ส่วนบท 13–18 อธิบายการทดสอบ การติดตั้ง การดูแล และวิธีพัฒนาต่อ

เอกสารนี้มีข้อมูลสองประเภท: **พฤติกรรมที่ตรวจพบในโค้ด** และ **กระบวนการ SDLC ที่เสนอให้ใช้** การมีหัวข้อ Planning, Testing หรือ Deployment ไม่ได้หมายความว่าโครงการได้ผ่านการอนุมัติทุกขั้นตอนอย่างเป็นทางการแล้ว ผลทดสอบเก่าจะระบุว่าเป็นหลักฐานย้อนหลัง และไม่มีการรับรองสถานะ production จากการอ่านโค้ดครั้งนี้

ชื่อ “Case” ที่แสดงในหน้าจอหมายถึงพื้นที่ทำงานของเรื่องหนึ่ง แต่ข้อมูลหลักใน backend ยังใช้ชื่อ `ChatThread` ไม่ได้มีตาราง Case แยกต่างหาก การเข้าใจจุดนี้ช่วยลดความสับสนเวลาไล่โค้ด

## 2. ระบบนี้ทำอะไร

CyberCase ช่วยรับเรื่องราวจากผู้ใช้ จัดทำผลวิเคราะห์ที่อ้างกลับไปยังข้อความต้นทาง ระบุข้อมูลที่ยังขาด และสร้างรายงานจากผลที่บันทึกไว้ ผู้ใช้ส่งเรื่องด้วยการพิมพ์เองหรืออ่านข้อความจากเอกสาร ตรวจทาน แล้วส่งข้อความนั้นเข้าสู่ระบบ

ตัวอย่าง: ผู้ใช้เขียนว่า “ผู้แจ้งพบว่าโทรศัพท์หายจากโต๊ะเวลา 14:00 น. ยังไม่ทราบว่าใครนำไป” ระบบควรสรุปว่าเป็นข้อมูลที่ผู้แจ้งรายงาน แยกสิ่งที่ยังไม่ทราบ และอาจถามข้อมูลเพิ่ม ระบบไม่ควรเปลี่ยนข้อความนี้เป็นข้อสรุปว่าบุคคลหนึ่งกระทำผิด

ผลจาก AI เป็นผลวิเคราะห์ ไม่ใช่การยืนยันความจริงของเหตุการณ์ การพบข้อความอ้างอิงในต้นทางพิสูจน์ได้เพียงว่าข้อความนั้นปรากฏในแหล่งข้อมูล ไม่ได้พิสูจน์โดยอัตโนมัติว่าข้อสรุปตีความถูกต้องทั้งหมด

### 2.1 งานหลักของผู้ใช้

1. สมัครสมาชิกหรือเข้าสู่ระบบ
2. เปิดพื้นที่ทำงานเดิมหรือสร้างเรื่องใหม่
3. เตรียมเรื่องราวและตรวจทานข้อความจากเอกสารถ้ามี
4. ส่งข้อมูลเพื่อวิเคราะห์
5. อ่าน Overview และตรวจแหล่งอ้างอิง
6. ตอบคำถามเพิ่มเติมเมื่อระบบต้องการข้อมูล หรือเพิ่มข้อมูลใหม่
7. ใช้ Ask เพื่อถามเกี่ยวกับข้อมูลเดิม
8. สร้างรายงาน อ่านประวัติรายงาน และดาวน์โหลด PDF

### 2.2 สิ่งที่ต้องแยกให้ออก

| สิ่งที่เห็น | ความหมายจริง |
|---|---|
| ข้อความผู้ใช้ที่ส่งเป็นข้อมูลเรื่อง | แหล่งข้อมูลหลักสำหรับการวิเคราะห์ |
| คำถาม Ask | คำถามของผู้วิเคราะห์ ไม่ใช่หลักฐานเพิ่มเติม |
| คำตอบของ AI | ผลสรุปหรือการตีความจากข้อมูลที่มี |
| MITRE ATT&CK | ความรู้ภายนอกสำหรับบริบททางไซเบอร์ เมื่อเข้าเงื่อนไข |
| ผล OCR | ข้อความที่อ่านจากเอกสาร ยังต้องตรวจทาน |
| รายงาน | ผลที่ประกอบจากข้อมูลและการวิเคราะห์ที่บันทึกไว้ในช่วงเวลาหนึ่ง |
| `validated` | ผ่านเงื่อนไขของตัวตรวจที่เกี่ยวข้อง ไม่ใช่รับรองข้อเท็จจริงทุกประโยค |

## 3. SDLC ของโครงการ

SDLC คือวงจรตั้งแต่กำหนดปัญหา ออกแบบ ลงมือพัฒนา ทดสอบ เปิดใช้งาน จนถึงดูแลระบบ จุดประสงค์คือทำให้การเปลี่ยนระบบมีเหตุผลและตรวจสอบได้

ตารางต่อไปนี้เป็นกระบวนการที่เสนอให้ใช้กับโค้ดปัจจุบัน ไม่ใช่ประวัติการดำเนินโครงการย้อนหลัง

| ขั้นตอน | คำถามที่ต้องตอบ | สิ่งส่งมอบ | เกณฑ์ผ่านที่เสนอ |
|---|---|---|---|
| Planning | ใครใช้ระบบ และแก้ปัญหาอะไร | ขอบเขตงาน ผู้ใช้เป้าหมาย ข้อจำกัด | เจ้าของระบบเห็นตรงกันว่าทำอะไรและไม่ทำอะไร |
| Requirements | ผู้ใช้ต้องทำอะไรได้ | Requirement และ acceptance criteria | แต่ละข้อมีวิธีทดสอบที่ชัดเจน |
| Analysis & Design | ข้อมูลผ่านส่วนใด ใครเป็นเจ้าของข้อมูล | API contract, data model, workflow, trust boundary | ไม่มีเส้นทางที่เปลี่ยนความเห็น AI เป็นหลักฐานโดยไม่ตั้งใจ |
| Implementation | แก้ที่โมดูลใด | โค้ด migration และเอกสารที่สัมพันธ์กัน | โค้ดแยกหน้าที่และรักษาสัญญาระหว่างระบบ |
| Testing | พฤติกรรมจริงตรงข้อกำหนดหรือไม่ | ผล unit, integration, browser และ provider tests | ครอบคลุมเส้นทางสำเร็จ ล้มเหลว และสิทธิ์ผู้ใช้ |
| Deployment | จะนำเวอร์ชันใดไปใช้ที่ไหน | Image, configuration, migration/rollback plan | ตรวจบริการและข้อมูลหลังเปิดใช้งาน |
| Maintenance | เมื่อผิดพลาดจะค้นหาและแก้อย่างไร | Logs, run IDs, incident record, regression tests | ระบุสาเหตุได้และป้องกันปัญหาเดิมซ้ำ |

### 3.1 ข้อกำหนดที่สะท้อนอยู่ในระบบ

| ID | ข้อกำหนด | ส่วนที่รับผิดชอบ | เกณฑ์ยอมรับตัวอย่าง |
|---|---|---|---|
| FR-01 | ต้องมีบัญชีก่อนใช้พื้นที่ทำงาน | AccountGate และ auth dependencies | ผู้ไม่เข้าสู่ระบบเปิดข้อมูลเรื่องไม่ได้ทั้ง UI และ API |
| FR-02 | สมัครด้วยอีเมล/รหัสผ่าน | password_auth และ auth schema | ปฏิเสธรูปแบบอีเมลผิด อีเมลซ้ำ และรหัสผ่านไม่ผ่านเกณฑ์ |
| FR-03 | เข้าสู่ระบบผ่าน OAuth เมื่อกำหนดค่า | auth router และ oauth_clients | ตรวจ state และตัวตนจาก provider ก่อนออก session |
| FR-04 | ผู้ใช้เห็นเฉพาะเรื่องของตน | chat ownership | บัญชี B อ่านหรือแก้เรื่องของ A ไม่ได้ |
| FR-05 | เก็บข้อความและงานวิเคราะห์ | chat_messages, chat_runs | โหลดหน้าใหม่แล้วยังอ่านข้อความที่ server รับแล้วได้ |
| FR-06 | จำ draft และสถานะบางส่วนในเบราว์เซอร์ | account-storage และ draft hooks | สลับเรื่องแล้ว draft ไม่ปะปนกัน |
| FR-07 | อ่านเอกสารก่อนส่งวิเคราะห์ | document-ingestion และ Intake | preview ไม่สร้างหลักฐานหรือเริ่มวิเคราะห์เอง |
| FR-08 | อ้างอิงกลับไปยังข้อความต้นทาง | analysis trace และ citation modules | การอ้างอิงมี source ID และข้อความที่ตรวจสอบได้ |
| FR-09 | ถามข้อมูลเพิ่มอย่างมีขอบเขต | followup services | ไม่วนถามหัวข้อเดิมอย่างไม่จำกัด |
| FR-10 | แยก Ask กับเพิ่มข้อมูล | run creation และ raw_evidence | คำถาม Ask ไม่เข้า evidence snapshot |
| FR-11 | สร้างรายงานที่มีประวัติ | reports services | มี version, source snapshot และ idempotency key |

คุณสมบัติเช่น latency เป้าหมาย จำนวนผู้ใช้พร้อมกัน SLA ระยะเก็บข้อมูล และ recovery time ยังไม่ควรใส่ตัวเลขรับรองจนกว่าจะกำหนด requirement และทดสอบจริง

## 4. ภาพรวมสถาปัตยกรรม

ระบบแบ่งเป็น frontend, backend, PostgreSQL และบริการ GraphRAG พร้อมบริการโมเดลภายนอกตาม configuration

| ส่วน | หน้าที่ | เทคโนโลยีหลัก | ไม่ควรรับผิดชอบ |
|---|---|---|---|
| Frontend | รับการกระทำ แสดงข้อมูล จัด draft และติดตาม run | Next.js, React, TypeScript, Tailwind, TanStack Query | ตัดสินสิทธิ์ขั้นสุดท้ายหรือเก็บฐานข้อมูลหลัก |
| Backend | ตรวจสิทธิ์ รับข้อความ จัด workflow ตรวจ contract บันทึกผล | FastAPI, Pydantic, SQLAlchemy async | เชื่อค่าจาก UI โดยไม่ตรวจ |
| PostgreSQL | เก็บผู้ใช้ เรื่อง ข้อความ งาน และรายงาน | PostgreSQL, Alembic | เรียก AI หรือแสดงหน้าจอ |
| rag-service | ค้นความรู้และส่งบริบท/MITRE กลับ | LangGraph และ GraphRAG stack | เป็นเจ้าของข้อความคดีของผู้ใช้ใน backend |
| OCR provider | อ่านข้อความจากภาพ/หน้าที่ต้อง recognition | Typhoon หรือ Google Vision ที่เลือกไว้ | รับรองความถูกต้องของข้อมูลเรื่อง |
| LLM provider | สร้างผลวิเคราะห์หรือผลตาม schema | provider/model ที่ตั้งค่าไว้ | บังคับสิทธิ์ผู้ใช้หรือเขียนฐานข้อมูลโดยตรง |

เบราว์เซอร์เรียก backend API; backend ติดต่อฐานข้อมูลและบริการที่จำเป็น ผู้ใช้ไม่ได้เชื่อม PostgreSQL โดยตรง และการเรียกโมเดลหลักอยู่ฝั่ง server

ใน Compose ปัจจุบัน frontend ใช้พอร์ต 3000, backend 8000, rag-service 8001 และ PostgreSQL เปิดที่ `127.0.0.1:5433` บนเครื่อง host แต่ backend ภายใน Compose ติดต่อ `db:5432` ชื่อและพอร์ตภายใน container จึงไม่เหมือน URL ที่เบราว์เซอร์ใช้

## 5. เดินตามหนึ่งเหตุการณ์ตั้งแต่คลิกจนได้ผล

สมมติผู้ใช้ส่งเรื่องใหม่โดยไม่มีไฟล์

1. Frontend ตรวจ session ผ่าน auth hook และ AccountGate
2. ผู้ใช้พิมพ์เรื่องราว ขณะยังไม่ส่งข้อความเป็น draft ในฝั่งเบราว์เซอร์
3. ถ้ายังไม่มี thread ตัว submission hook ขอสร้าง thread ก่อน
4. Frontend สร้าง idempotency key แล้วส่งข้อความไป `POST /api/v1/chats/{thread_id}/messages`
5. Backend ตรวจ session และ ownership ของ thread
6. Backend lock thread ตรวจคำขอซ้ำ ตรวจว่าไม่มี run อื่นกำลังทำ และระบุชนิดข้อความ
7. ภายใน transaction เดียว backend บันทึก user message กับ queued run และเปลี่ยน thread เป็น `processing`
8. API ตอบ `202 Accepted` พร้อม message และ run: หมายถึงรับงานแล้ว ยังไม่ได้วิเคราะห์เสร็จ
9. FastAPI BackgroundTasks เรียก worker ให้ claim run แล้วเปลี่ยนเป็น `running`
10. Worker สร้าง evidence snapshot จากข้อความที่อนุญาต พร้อม source IDs และ SHA-256
11. สำหรับการวิเคราะห์ใหม่ worker เลือก pipeline และพิจารณาใช้ RAG ตามเงื่อนไข
12. โมดูลวิเคราะห์เรียกโมเดล ตรวจผล และประเมิน gap/follow-up
13. Worker บันทึก assistant message, metadata, optional RAG context และสถานะ run/thread ใน transaction จบงาน
14. Frontend อ่านสถานะซ้ำโดยมีช่วงรอประมาณหนึ่งวินาที เมื่อเสร็จนำข้อมูลที่บันทึกแล้วมาแสดง
15. ผู้ใช้เปิด Overview เพื่อตรวจผล หรือเห็นคำถามเพิ่มเติมหาก thread เป็น `awaiting_followup`

การปิดหน้าจอไม่ใช่คำสั่งยกเลิกงานบน server หลัง backend รับคำขอแล้ว แต่ BackgroundTasks ยังอยู่ใน process ของ backend หาก process หยุด งานอาจขาดตอน ต้องอาศัย recovery และ retry จึงไม่ใช่ durable queue แยกบริการแบบเต็มรูปแบบ

## 6. Frontend ทำงานอย่างไร

### 6.1 โครงสร้างและจุดเข้า

`frontend/src/app/layout.tsx` และ `providers.tsx` จัดโครงหน้าและ shared providers ส่วน `/chat` ใช้ workspace ร่วมกัน แยกการเลือกข้อมูล การส่งข้อความ และการจัด layout ออกจากกัน

| โมดูล | หน้าที่ |
|---|---|
| `components/ChatWorkspace.tsx` | เชื่อม route, query, session และ user actions |
| `components/ChatWorkspaceLayout.tsx` | จัด sidebar, เนื้อหาหลัก และแผงสนทนา |
| `features/chat/routing/chat-route.ts` | แปล URL เป็น thread/view และสร้าง URL |
| `hooks/use-chat-queries.ts` | query keys และ mutation ของรายการ thread |
| `features/chat/workspace/use-chat-thread-selection.ts` | ประสานการเลือกเรื่องและการโหลดข้อมูล |
| `features/chat/workspace/use-chat-draft.ts` | ข้อความ draft และข้อมูลคำขอที่กำลังส่ง/รอ retry |
| `features/chat/runs/use-chat-submission.ts` | ส่งข้อความ สร้าง key รับผล accepted และติดตามงาน |
| `features/chat/runs/chat-polling.ts` | วงจรอ่านข้อมูลจน run จบและจัดการ cancellation |

### 6.2 หน้าจอและแหล่งข้อมูล

| หน้า/พื้นที่ | ผู้ใช้ทำอะไร | ข้อมูลมาจากไหน |
|---|---|---|
| `/login` | เข้าสู่ระบบ | auth API |
| `/register` | สมัครสมาชิก | form และ register API |
| `/chat` | เปิด workspace | รายการ thread ของบัญชี |
| `/chat/{id}/intake` | เตรียมเรื่องและตรวจข้อความจากเอกสาร | draft, extraction preview และข้อมูลต้นทาง |
| `/chat/{id}/overview` | อ่านสรุป findings/gaps และแหล่งอ้างอิง | persisted messages และ structured trace |
| `/chat/{id}/materials` | อ่านแหล่งข้อมูลที่มีอยู่ | projection จากข้อความและ provenance |
| `/chat/{id}/report` | สร้าง/อ่านรายงานและประวัติ | report API |
| `/chat/{id}/technical-context` | อ่านบริบทเทคนิคที่มีจริง | metadata และ RAG-related data |
| แผง Chat ภายใน workspace | ถาม ตอบ clarification และเพิ่มข้อมูล | messages/run state เดียวกับพื้นที่หลัก |

ตัวแปล route ปัจจุบันรู้จัก Intake, Materials, Report และ Technical Context อย่างชัดเจน ส่วน path ที่ไม่เข้ากลุ่มจะเลือก Overview แม้มีไฟล์ route ชื่อ chat อยู่ จึงไม่ควรอธิบายว่า URL ทุกชื่อมี workspace mode แยกกันเสมอ

Overview และ Materials เป็นการจัดมุมมองของข้อมูลที่บันทึกอยู่แล้ว ไม่ได้สร้างตารางใหม่ทุกครั้งที่เปิดหน้า ผล v3 อ่านจาก structured fields; ข้อมูล v2 เก่าต้องไม่ถูกแปลงให้ดูเหมือนผลวิเคราะห์ v3 ที่ตรวจใหม่แล้ว

### 6.3 State มีหลายชั้น

| ชั้น | ตัวอย่าง | อายุข้อมูล/ข้อจำกัด |
|---|---|---|
| React component state | เปิด modal, ขนาดแผง Chat, สถานะลากขอบ | โดยทั่วไปอยู่ตามอายุ component |
| Query cache | รายการ thread และ thread detail | ช่วยแสดงผล ไม่ใช่ฐานข้อมูลถาวร |
| localStorage | draft, action, เส้นทางล่าสุด, preview ที่รองรับ | อยู่ใน browser profile และ origin เดียวกัน จนถูกล้าง |
| Session cookie | token สำหรับให้ backend ตรวจบัญชี | มีอายุและนโยบาย cookie ของระบบ |
| PostgreSQL | ข้อความที่ส่งแล้ว งานวิเคราะห์ รายงาน | อยู่ฝั่ง server และไม่ขึ้นกับ browser cache |

localStorage ใช้ namespace เช่น `cybercase:<user-id>:<key>` เพื่อแยกบัญชี มี account marker สำหรับเลือก namespace การออกจากระบบเปลี่ยน session และล้าง query cache; การแจ้ง session เปลี่ยนข้ามแท็บช่วยให้แต่ละแท็บตรวจตัวตนใหม่

คำว่า “จำสถานะ” ในเวอร์ชันนี้หมายถึง state ที่ถูกเขียนลง storage โดยเฉพาะ ไม่ได้เก็บทุก click, scroll position หรือค่าความกว้างแผงทั้งหมด การล้าง browser data ทำให้ draft หายได้ และการย้ายเครื่องไม่ย้าย localStorage ไปด้วย แต่ข้อความที่ backend บันทึกแล้วโหลดคืนจากฐานข้อมูลได้

ไฟล์ต้นฉบับที่ผู้ใช้เลือกเป็น browser `File` ไม่สามารถคืนจากข้อความ JSON ใน localStorage ได้โดยตรง แม้ extraction preview บางส่วนยังอยู่ก็ตาม

### 6.4 การกันผลจากเรื่องเก่ามาทับเรื่องใหม่

การสลับ thread ใช้ selection identity และ AbortSignal คำตอบที่กลับมาช้าต้องตรวจว่ายังเป็น selection ปัจจุบันก่อนอัปเดตหน้าจอ การ abort HTTP ฝั่ง browser ไม่ได้แปลว่า server ยกเลิก run ที่รับแล้ว

Polling มีวงจรกลาง ใช้ thread detail เป็นหลัก และตรวจ run ID เมื่อมี ก่อนยอมรับว่าจบงาน หากอ่านผิดพลาดติดต่อกันเกินเกณฑ์จะรายงาน error แทนรอเงียบ ๆ ตลอดไป ช่วงรอ 1 วินาทีไม่ใช่การรับประกันว่าผลจะปรากฏภายใน 1 วินาที เพราะยังมีเวลา network และประมวลผล

## 7. Authentication และขอบเขตสิทธิ์

### 7.1 สมัครด้วยอีเมลและรหัสผ่าน

Backend ใช้ schema ตรวจรูปแบบอีเมลและปรับ normalization ตาม flow ตรวจอีเมลซ้ำ และ hash รหัสผ่านด้วย scrypt พร้อม salt การสมัครกำหนดรหัสผ่าน 12–128 ตัวอักษร เมื่อสำเร็จตอบ UserRead และตั้ง session cookie ให้ใช้งานต่อได้ทันที

**ปัจจุบันตรวจรูปแบบอีเมลเท่านั้น** ไม่ส่ง verification link ไม่ตรวจ mailbox ว่ามีอยู่จริง และไม่อ้างว่าผู้สมัครเป็นเจ้าของอีเมล ระบบ SMTP ไม่จำเป็นสำหรับ flow นี้ แม้ model/migration ยังมี nullable verification columns จากงานก่อนหน้า

### 7.2 Login และ session

การ login ตรวจบัญชีและ password hash แล้วออก JWT ให้ browser เก็บใน HTTP-only cookie Frontend อ่านข้อมูลผู้ใช้ผ่าน API ไม่อ่าน token จาก JavaScript โดยตรง อายุ JWT ตามค่า default ใน config คือ 7 วัน; deployment สามารถตั้งค่าต่างออกไปได้

Cookie ใช้ SameSite Lax และมีตัวเลือก Secure การตั้งค่า HTTPS จริงต้องสอดคล้องกับ frontend/backend domains และ CORS การ logout ล้าง cookie แต่ยังไม่มีระบบเพิกถอน JWT แต่ละใบฝั่ง server

### 7.3 OAuth

Frontend ขอรายชื่อ provider ที่ตั้งค่าพร้อมจาก backend เมื่อผู้ใช้เลือก provider จะเข้าสู่ redirect flow มี state สำหรับผูก callback กับคำขอเดิม Backend ตรวจข้อมูลตัวตนและอีเมลที่ provider ยืนยันก่อนสร้าง/ใช้บัญชี

Google/GitHub ต้องมี credentials และ callback URL ที่ตรง environment จึงใช้งานจริงได้ การมีโค้ด OAuth ไม่ได้แปลว่าปุ่มนั้นพร้อมใน runtime ทุกแห่ง หากอีเมลชนกับบัญชีจากช่องทางอื่น โค้ดไม่เชื่อมบัญชีให้อัตโนมัติ

### 7.4 ป้องกันทั้ง UI และ API

AccountGate ปล่อยหน้าสาธารณะเฉพาะ `/login` และ `/register` หน้าอื่นรอตรวจ session ก่อนแสดง children หากตรวจ session ล้มเหลวจะแสดงให้ลองใหม่ ไม่ตีความ network failure ว่า logout สำเร็จ

Backend ตรวจผู้ใช้ใน chat routes และตรวจเจ้าของก่อนเข้าถึงข้อความ run หรือ report การซ่อนปุ่มใน frontend เพียงอย่างเดียวไม่ใช่การป้องกันสิทธิ์ Thread เก่าที่ `user_id` เป็น null ไม่ได้ถูกยกให้บัญชีแรกโดยอัตโนมัติ

Request guard ปฏิเสธ unsafe requests ที่มี Origin นอก allowlist และตั้ง auth response เป็น no-store การไม่มี Origin ไม่ถูกปฏิเสธด้วยเงื่อนไขนี้เพียงอย่างเดียว จึงไม่ควรอธิบายว่าเป็นกลไก CSRF token แบบครบวงจร

ข้อจำกัดปัจจุบันที่ควรวางแผนต่อ: password reset, email ownership verification, account linking, server-side session revocation และการป้องกันความถี่ของ login ยังไม่ใช่คุณสมบัติที่เอกสารนี้รับรองว่าเสร็จแล้ว

## 8. Backend แบ่งหน้าที่อย่างไร

### 8.1 การเริ่มบริการ

`backend/app/main.py` สร้าง FastAPI ลงทะเบียน middleware/routes และจัด lifespan ตอนเริ่มตรวจฐานข้อมูลด้วย `SELECT 1` ทำ recovery ของ run ที่หมดเวลา และเริ่ม monitor เมื่อปิดบริการยกเลิก monitor และ dispose database engine

`database.py` สร้าง async engine/session ข้อมูลเชื่อมต่อจริงประกอบจากค่า PostgreSQL host/port/user/password/database ในโค้ดปัจจุบัน อย่าสรุปว่าเปลี่ยน `DATABASE_URL` อย่างเดียวแล้ว connection จะเปลี่ยน แม้ config จะมี property เกี่ยวกับ URL

### 8.2 ชั้นของโค้ด

| ชั้น | ตัวอย่าง | เหตุผลที่แยก |
|---|---|---|
| Router | `routers/chat.py` | จัด HTTP, dependencies และ response codes |
| Schema | `schemas/chat.py`, `schemas/reports.py` | ตรวจรูปแบบ input/output |
| Service | `services/chat/`, `services/reports/` | เก็บกฎการทำงานไม่ผูกกับหน้าจอ |
| Workflow | `services/workflow/` | ประสานหลายขั้นและจัดวงจร run |
| Model | `models/` | อธิบายตารางและความสัมพันธ์ |
| External client | `services/clients/`, `services/llm/` | แยก HTTP/provider errors จากกฎโดเมน |
| Migration | `alembic/` | เปลี่ยน schema อย่างมีลำดับ |

Pydantic ตรวจ shape/type/เงื่อนไขที่กำหนด SQLAlchemy จัด query และ transaction ส่วน PostgreSQL constraints ช่วยคุมความถูกต้องแม้มีหลายคำขอพร้อมกัน ทั้งสามอย่างมีหน้าที่ต่างกัน

### 8.3 State ของ thread และ run

| Thread status | ความหมาย |
|---|---|
| `idle` | ยังไม่มีงานที่เริ่มวิเคราะห์ |
| `processing` | มีงานรับแล้วหรือกำลังทำ |
| `awaiting_followup` | รอข้อมูลเพิ่มเติมจากผู้ใช้ |
| `answered` | มีผลตอบกลับพร้อมให้ทำงานต่อ |
| `failed` | งานล้มเหลวหรือขาดตอน ต้องตรวจ error/retry |

Run มี `queued`, `running`, `completed`, `failed` แยกจาก thread เพราะ thread เป็นภาพรวมเรื่องหนึ่ง ส่วน run เป็นความพยายามประมวลผลคำขอหนึ่งครั้ง ตัวอย่าง run completed สามารถทำให้ thread awaiting_followup ได้ เพราะงานรอบนั้นจบด้วยคำถามเพิ่มเติม

### 8.4 Idempotency, lock และ recovery

Idempotency key แทนการกระทำเชิงตรรกะหนึ่งครั้ง ถ้า network ขาดหลัง server รับแล้ว การส่งซ้ำด้วย key และเนื้อหาเดิมจะอ้างงานเดิม ไม่สร้าง user message ซ้ำตามปกติ ถ้า key เดิมแต่ payload เปลี่ยน backend ตอบ conflict

Request fingerprint รวม content, action และ document sources ที่เกี่ยวข้อง มี unique constraint ของ key ภายใน thread และ partial unique index ให้หนึ่ง thread มี active run ได้ไม่เกินหนึ่งงาน

Worker มี lease owner/expiry โดย lease ปัจจุบันยาว 6 นาทีและ heartbeat ต่ออายุทุก 30 วินาที การ complete ตรวจว่ายังเป็นเจ้าของ run ก่อนเขียนผล Monitor ตรวจงานขาดตอนทุก 30 วินาทีและตอน startup โดยเปลี่ยนงานหมดอายุเป็น failed พร้อม `chat_run_interrupted` ไม่ได้ทำให้ AI กลับมาทำขั้นเดิมต่อเองทันที

Retry งานขาดตอนต้องผ่านเงื่อนไขใน `chat_run_retry.py` เพื่อไม่ฟื้นงานเก่ามาทับงานใหม่ ความทนทานนี้ช่วย recover งาน แต่ไม่ใช่การรับประกัน exactly-once สำหรับค่าใช้จ่าย provider ทุกกรณี

## 9. ฐานข้อมูลเก็บอะไร

มี 6 ตารางโดเมนหลักตาม ORM ที่ตรวจสอบ ไม่รวมตาราง version ของ Alembic

| ตาราง | ข้อมูลสำคัญ | ความสัมพันธ์ |
|---|---|---|
| `users` | email, name, password_hash, OAuth identity, timestamps | ผู้ใช้หนึ่งคนมีหลาย threads |
| `chat_threads` | user_id, title, status, next_message_ordinal | เรื่องหนึ่งมีหลาย messages/runs/reports |
| `chat_messages` | role, content, ordinal, metadata_json, retrieval_context_id | อยู่ใน thread และเป็นต้นทางของ run/analysis |
| `chat_runs` | request_message_id, key, fingerprint, payload, status, lease, errors | ผูกคำขอและการประมวลผล |
| `rag_contexts` | context, mitre_table, retrieval_context_id | context ไม่เกินหนึ่งแถวต่อ run ที่สร้างมัน |
| `chat_reports` | version, snapshot, hash, analysis_message_id, structured_report, status | รายงานหลายเวอร์ชันต่อ thread |

`metadata_json` เป็น JSONB ใช้เก็บ evidence kind, provenance, analysis trace และ follow-up metadata จึงไม่จำเป็นต้องมีตาราง claim/gap แยกในเวอร์ชันนี้ แต่ schema ฝั่งแอปยังจำเป็นเพื่อไม่ให้ JSON กลายเป็นข้อมูลไร้สัญญา

Ordinal กำหนดลำดับข้อความภายใน thread มี unique `(thread_id, ordinal)` ไม่ควรใช้เวลาที่สร้างเพียงอย่างเดียวแทนลำดับ conversation

หลาย foreign keys ใช้ cascade เมื่อ thread ถูกลบ ข้อมูลลูกที่ผูกอยู่จะถูกลบตามการออกแบบ ดังนั้น Delete case มีผลต่อข้อมูลถาวร การมี Docker volume ช่วยให้ข้อมูลอยู่ข้าม container restart แต่ไม่เท่ากับมี backup

SHA-256 ใช้ระบุว่าข้อความ snapshot เปลี่ยนหรือไม่ ไม่ใช่การเข้ารหัสเนื้อหา และไม่ใช่ลายเซ็นพิสูจน์ผู้เขียน

## 10. หลักฐาน การวิเคราะห์ และคำถามเพิ่มเติม

### 10.1 ข้อความใดเข้าการวิเคราะห์

`services/chat/raw_evidence.py` เรียง user messages ตาม ordinal แล้วรวมข้อความเริ่มต้น คำตอบ clarification และ added case information ข้อความ assistant และ analyst question ไม่เข้าชุดหลักฐานนี้

| Action/สถานการณ์ | evidence_kind | ผล |
|---|---|---|
| ส่งเรื่องครั้งแรก | `initial_case_narrative` | เริ่ม analysis ใหม่ |
| ตอบขณะ awaiting_followup | `clarification_answer` | เพิ่มข้อมูลและวิเคราะห์ใหม่ตาม chain |
| เลือกเพิ่มข้อมูล | `added_case_information` | เพิ่มหลักฐานและวิเคราะห์ใหม่ |
| เลือก Ask | `analyst_question` | ตอบคำถามจากบริบทเดิม ไม่ขยาย evidence |

หากผู้ใช้พิมพ์ข้อเท็จจริงใหม่ผ่าน Ask ข้อความนั้นจะไม่ถูกนับเป็นหลักฐานตามเจตนาของระบบ ผู้ใช้ต้องเลือกเพิ่มข้อมูลเพื่อให้ผลวิเคราะห์เรื่องและรายงานรุ่นต่อไปพิจารณาข้อมูลดังกล่าว

### 10.2 Pipeline ปกติ: raw_direct

Default ใน configuration คือ `raw_direct` งานวิเคราะห์ใหม่เตรียม raw evidence ตรวจ MITRE applicability แล้วเรียก Main Case Analysis ด้วยข้อมูลต้นทางและบริบทที่รับเข้าได้ ผลถูก parse เป็น contract ของระบบและผูกกับ evidence hash/source IDs

MITRE applicability มี `RETRIEVE` หรือ `SKIP` การเลือก RETRIEVE ต้องผ่านการตรวจ attribution; เมื่อผลไม่ชัดเจน ผิด schema หรือ provider ล้มเหลว จะไม่อนุมานว่าเกี่ยวข้องกับ MITRE โดยอัตโนมัติ

Analysis trace v3 เก็บผลแบบมีโครงสร้าง เช่น summary, grounded claims, citations, gaps และข้อมูลอ้างอิงที่รองรับ หน้าจอจึงไม่ต้องเดาข้อมูลทุกอย่างจากข้อความ Markdown ยาว ๆ แต่การตรวจโครงสร้างและ quote ไม่ได้แทน semantic verification

### 10.3 ทางเลือก opt-in: claim_anchored

เมื่อเลือก `CASE_ANALYSIS_PIPELINE=claim_anchored` เส้นทาง overview ใช้ attribute-first ตามลำดับหลัก:

1. สร้าง registry ของแหล่งข้อมูลและตรวจ evidence hash
2. เรียก extraction stage เพื่อเสนอ claims พร้อมแหล่งข้อความ
3. Binder ตรวจ literal spans และ binding ตาม contract
4. Selector เลือก claims ภายใต้ token budget และบันทึก omissions
5. เรียก generation stage จาก claims ที่เลือก
6. ประกอบ trace และบันทึก execution receipt

โหมดนี้มีจุดต่อ SemanticVerifier แต่การใช้งานที่ไม่มี verifier บันทึก `semantic_verification=not_performed` จึงไม่ควรเรียกว่าได้ทำ NLI แล้ว Phase 1 ปิด technical augmentation โดยตั้งใจ; ไม่ใช่ raw_direct ที่เพิ่มขั้นสกัดแต่ยังเรียก RAG แบบเดิมทั้งหมด

Prompt/pipeline version เช่น v1, trace schema v3 และ migration 0004 เป็นคนละระบบเลขเวอร์ชัน ไม่มีข้อกำหนดว่าต้องเลขเดียวกัน

### 10.4 Ask

`question_execution.py` ต้องมี analysis context ใช้ evidence และบริบทเดิม ตอบแบบ `question_answer` ไม่เรียก fresh RAG และไม่เดิน gap/follow-up pipeline ใหม่ ผลถามตอบเป็น response-scoped ไม่แทน canonical overview ของเรื่องโดยอัตโนมัติ

### 10.5 Gap และ follow-up

หลัง analysis overview ระบบประเมินข้อมูลที่ขาด แล้วเติม canonical gaps ใน trace ก่อนตัดสินใจว่าจะถามอะไรต่อ Operational metadata ยังช่วยจำ chain และหัวข้อที่เคยถาม

Stateful policy จำกัดการถามตรงหัวข้อ normalized เดิมต่อ chain และใช้ config จำกัดจำนวนรอบ โดย default `chat_followup_max_rounds=2` การตอบว่าไม่ทราบไม่ได้ทำให้ข้อเท็จจริงกลายเป็นทราบแล้ว: gap อาจยังอยู่แต่หมดโอกาสถามใน chain นั้น หรือ analysis ใหม่อาจพบหัวข้ออื่น

หากตัดสินใจถาม ผู้ใช้เห็น assistant content เป็นคำถาม แต่ metadata อาจมีผลวิเคราะห์ของรอบนั้นอยู่ด้วย จึงต้องอ่านชนิด metadata ไม่ใช่อ่านข้อความที่แสดงเพียงอย่างเดียวแล้วสรุปว่าไม่มี analysis

## 11. RAG และการอ่านเอกสารเป็นคนละระบบย่อย

### 11.1 RAG boundary

Backend เรียก `rag-service POST /query` ผ่าน `services/clients/rag_client.py` ส่ง query และ use_agent แล้วตรวจ response ด้วย Pydantic timeout ฝั่ง client ปัจจุบัน 300 วินาที

Response มี status, retrieval_context_id, context, mitre_table และ legal_reference ตาม schema ปัจจุบัน ข้อความคำตอบภายใน GraphRAG ถูกใช้เป็น relevance signal ภายใน rag-service แต่ไม่ใช่ assistant answer หลักที่ส่งให้ผู้ใช้จาก endpoint นี้

บริบทที่ใช้จริงถูกบันทึกใน PostgreSQL `rag_contexts` ผูก run เพื่อให้ backend ไม่ต้องพึ่ง cache ชั่วคราวใน rag-service ตลอดไป หาก RAG ล้มเหลวหรือไม่มีบริบทที่รับเข้าได้ การวิเคราะห์ทั่วไปสามารถทำต่อพร้อมสถานะ unavailable/no-applicable-context ได้

พบโค้ดเรียกบริการ legal reference เพิ่มใน rag-service และ field รับเข้าฝั่ง backend แต่การค้นการใช้งานใน backend/frontend ครั้งนี้พบเพียง schema ฝั่ง backend ไม่พบการนำ field นี้ต่อเข้า UI หรือ durable RagContext ดังนั้น **ไม่ควรอธิบายว่ามีระบบวิเคราะห์กฎหมายครบวงจรที่ใช้งานผ่านหน้าจอแล้ว**

Neo4j และ Qdrant เป็นแหล่งข้อมูลภายนอก Compose ชุดนี้ ต้องเตรียมและ ingest ความรู้ให้พร้อมต่างหาก การมี container rag-service ทำงานไม่ได้พิสูจน์ว่าข้อมูลค้นหาหรือโมเดลพร้อมตอบทุกคำขอ

### 11.2 Document ingestion

Endpoint `POST /api/v1/document-ingestion/preview` รับไฟล์ multipart และส่งผลอ่านข้อความกลับ รองรับ PDF, DOCX, PNG, JPEG โดยตรวจลักษณะ bytes ของไฟล์ ค่า default จำกัด 20 MiB, 50 หน้า และ 40 ล้าน image pixels; ค่า runtime อาจตั้งต่างได้

PDF พิจารณาข้อความ native หรือ recognition ระดับหน้า DOCX ใช้ parser ส่วนภาพ/หน้าที่ต้อง recognition ส่งผ่าน provider ที่เลือกไว้ ค่า default เป็น Typhoon; Google Vision เป็นทางเลือกที่ต้องกำหนด credentials

ลำดับใช้งานคือเลือกไฟล์ → preview → ผู้ใช้ตรวจ/แก้ข้อความ → ส่ง narrative พร้อม provenance ที่รับได้ การ preview เองไม่สร้าง thread evidence ไม่เรียก main analysis และไม่สร้าง report

ปัจจุบัน UI เน้นหนึ่ง reviewed document-derived narrative แม้ handoff contract จะรับ list เพื่อรองรับการขยาย ภาพรวมนี้ยังไม่ใช่การรับรอง workflow หลายเอกสารเต็มรูปแบบ

HTR ถูกปิดที่ production router ด้วย `htr_enabled=False` ไม่ควรบอกผู้ใช้ว่าระบบถอดลายมือไทยได้ ผล OCR ที่ไม่มี confidence ต้องคงความหมายว่าไม่มีค่าที่วัด ไม่เติมคะแนนสมมติ และ warning ไม่ได้แปลว่าอ่านข้อความล้มเหลวเสมอไป

Headers เช่น idempotency/case key ที่ endpoint รับอยู่ไม่ได้เป็นหลักฐานว่า preview มี deduplication หรือ persistence เพราะ handler ปัจจุบันไม่ได้ใช้ค่าเหล่านี้ใน service call

### 11.3 Citation และหน้าเอกสาร

การแสดงเลขหน้าต้องมี provenance ที่ตรวจได้: document identity, text hash, exact quote และช่วงข้อความที่ชี้หน้าได้ไม่กำกวม หากผู้ใช้แก้ narrative จน mapping ไม่รองรับ ระบบควรอ้าง reviewed narrative โดยไม่แต่งเลขหน้า

การเปิดข้อความอ้างอิงใน drawer คือการตรวจ extracted text ไม่ใช่การเปิด PDF ต้นฉบับพร้อมพิกัดบนภาพ การ persist original document และ original-page viewer ไม่ใช่ความสามารถที่รับรองใน flow นี้

## 12. รายงานสร้างอย่างไร

รายงานปัจจุบันเป็น deterministic/template-first: `report_generation.py` เรียก `build_template_report` และบันทึก provider=`deterministic`, model=`template` ไม่เรียก LLM เพิ่มเพื่อเขียนรายงานใหม่ทุกครั้ง แต่เนื้อหาวิเคราะห์ที่นำมาใช้ยังมาจากขั้น AI ก่อนหน้า

ลำดับหลัก:

1. ตรวจบัญชีและ ownership ของ thread
2. ตรวจเปิดใช้ report generation
3. โหลดข้อความและเลือก assistant message ที่เป็น `grounded_main_analysis`
4. ต้องมี user-authored evidence และ main analysis จึงสร้าง snapshot
5. ผูก RAG เฉพาะเมื่อ context ตรงกับ analysis; ไม่มี MITRE ก็สร้างรายงานได้
6. คำนวณ snapshot hash ตรวจ idempotency และกำหนด version ถัดไป
7. ประกอบ structured report จากแม่แบบ
8. บันทึก snapshot, report, status และ failure information ถ้ามี

รายงานเก่าเป็นประวัติของข้อมูลตอนสร้าง การเพิ่มข้อมูลใหม่ไม่ควรตีความว่า report เก่าถูกเขียนใหม่เอง ผู้ใช้สร้างเวอร์ชันใหม่เพื่อสะท้อนผลที่ต้องการ

**สร้างรายงานกับ export PDF มี gate ไม่เหมือนกัน:** ตอน generation ไม่ใช้ custom source/MITRE binding validator เป็น admission gate แต่ PDF ต้องเป็น completed report และเรียก `validate_structured_report` อีกครั้ง ดังนั้นสร้างรายงานได้แต่ export ไม่ได้เป็นสถานการณ์ที่เกิดได้ตามโค้ด ต้องดู error ของ export แยกต่างหาก

ข้อจำกัดที่พบจาก `report_snapshot.py`: snapshot รวบรวม evidence ปัจจุบันและเลือก main-analysis message ล่าสุดตามชนิด metadata ฟังก์ชันนี้ไม่ได้ตรวจให้ครบว่า hash ของ analysis นั้นตรงกับ evidence ปัจจุบัน หรือไม่มี run กำลังทำอยู่ จึงไม่ควรรับรองจากชื่อ snapshot ว่ามี freshness gate สมบูรณ์ ควรเพิ่ม acceptance test กรณีเพิ่มข้อมูลแล้วกดสร้างรายงานระหว่างวิเคราะห์ก่อนใช้ในงานจริงที่ต้องการความเข้มงวดนี้

## 13. API ที่ frontend ใช้

ทุก path ในตารางขึ้นต้นด้วย `/api/v1` ยกเว้นระบุเป็น interface ของ rag-service ในบทก่อน Placeholder `{id}` หมายถึง UUID ของ resource ไม่ใช่ข้อความชื่อเรื่อง

| Method | Path | หน้าที่ |
|---|---|---|
| GET | `/health` | สถานะ backend/ฐานข้อมูลตาม health handler |
| POST | `/auth/register` | สมัคร password account และตั้ง session |
| POST | `/auth/login` | ตรวจอีเมล/รหัสผ่าน |
| GET | `/auth/session` | อ่านผู้ใช้หรือ null สำหรับ session ที่ไม่มี |
| GET | `/auth/me` | อ่านผู้ใช้โดยต้อง authenticated |
| POST | `/auth/logout` | ล้าง session cookie |
| GET | `/auth/providers` | provider ที่พร้อมตาม configuration |
| GET | `/auth/login/{provider}` | เริ่ม OAuth redirect |
| GET | `/auth/callback/{provider}` | รับ OAuth callback |
| POST | `/auth/dev-login` | ทางเข้า development ที่ปิด default |
| GET / POST | `/chats` | อ่านรายการ / สร้าง thread |
| GET / PATCH / DELETE | `/chats/{thread_id}` | อ่าน / แก้ชื่อ / ลบ thread |
| POST | `/chats/{thread_id}/messages` | รับข้อความและสร้าง run; ตอบ 202 |
| GET | `/chats/{thread_id}/runs/{run_id}` | อ่านสถานะงาน |
| POST / GET | `/chats/{thread_id}/reports` | สร้าง / อ่านรายการ reports |
| GET | `/chats/{thread_id}/reports/{report_id}` | อ่าน report รุ่นที่เลือก |
| GET | `/chats/{thread_id}/reports/{report_id}/pdf` | export PDF |
| POST | `/document-ingestion/preview` | อ่านเอกสารแบบ preview; ต้อง authenticated |

Chat/report ownership ตรวจจาก backend ไม่รับ user_id จาก browser มาเชื่อว่าเป็นเจ้าของ มี typed request/response ใน `backend/app/schemas/` และ frontend API layer; FastAPI `/docs` เมื่อเปิดบริการช่วยตรวจ schema ที่ runtime ใช้จริง

ตัวอย่างเชิงแนวคิดของการส่งข้อมูลเพิ่มหลัง answered (ต้องใช้ thread จริงและ authenticated cookie):

```json
{
  "content": "พบข้อมูลเพิ่มเติมจากผู้แจ้งว่าเหตุเกิดเวลาประมาณ 14:00 น.",
  "idempotency_key": "a-new-key-for-this-logical-submission",
  "action": "add_case_info"
}
```

HTTP 201 หมายถึงสร้าง resource, 202 หมายถึงรับงาน, 401 เกี่ยวกับ authentication, 403 อาจเกิดจาก origin guard, 404 resource ไม่พบ/ไม่เปิดเผยให้บัญชีนี้, 409 คำขอขัดกับสถานะหรือ key, 413 ไฟล์เกินขนาด, 415 ชนิดไฟล์ไม่รองรับ และ 422 input ไม่ผ่าน contract รายละเอียดจริงขึ้นกับ handler ไม่ควรให้ UI เดาจาก status code อย่างเดียว

## 14. แผนทดสอบและเกณฑ์ก่อนยอมรับงาน

### 14.1 ระดับการทดสอบ

| ระดับ | ตรวจอะไร | ตัวอย่างชุดที่มี |
|---|---|---|
| Unit/contract | กฎและ schema แบบแยกส่วน | `test_source_citations.py`, `test_gap_assembly.py`, `test_claim_anchored_binding.py` |
| Service/API | auth, ownership และเส้นทางคำขอ | `test_password_accounts.py`, `test_chat_ownership.py`, `test_route_surface.py` |
| PostgreSQL integration | constraint, transaction, recovery จริง | `test_run_recovery_postgres.py`, `test_claim_anchored_postgres.py` |
| Frontend | draft, projection, actions และ components | tests ภายใต้ `frontend/src/test/` |
| Build/static | TypeScript, bundling และ lint | frontend scripts, Ruff ตาม scope |
| Live provider | transport/credentials กับบริการจริง | ต้องทำแยกจาก mocked tests |
| Browser end-to-end | การเดินงานจริงตั้งแต่ login ถึง report | ต้องมี runtime และข้อมูลทดสอบที่กำหนด |

Mocked test ผ่านไม่ได้พิสูจน์ว่า OAuth callback domain, OCR credentials หรือ LLM provider จริงพร้อมใช้งาน ส่วน DB tests ที่ skipped ไม่ใช่ DB tests ที่ผ่าน

### 14.2 Acceptance scenarios ที่ควรใช้

1. สมัครด้วยอีเมลผิดรูปแบบถูกปฏิเสธ; อีเมลรูปแบบถูกสมัครได้โดยไม่รออีเมล
2. รหัสผ่านผิดไม่เข้า workspace; บัญชีถูกต้องเข้าได้
3. บัญชี B ใช้ URL ของ A แล้วอ่าน แก้ ลบ ส่งข้อความ หรือ export ไม่ได้
4. ส่งข้อความหนึ่งครั้งแล้ว refresh ยังพบข้อความเดิมและติดตาม run ได้
5. network ขาดหลัง accepted แล้ว retry ไม่เพิ่ม user message ซ้ำ
6. สลับ thread ระหว่าง polling แล้วผลเก่าไม่ทับเรื่องใหม่
7. เพิ่มข้อมูลเข้า evidence แต่ Ask ไม่เข้า evidence
8. OCR preview ไม่ persist เรื่องจนกว่าผู้ใช้ส่ง narrative
9. RAG ไม่เกี่ยวข้อง/ล่มยังแสดงผลทั่วไปโดยไม่แต่ง MITRE
10. citation ที่ระบุหน้าต้องชี้ exact source; edited text ไม่ได้เลขหน้าสมมติ
11. backend restart ระหว่าง run ทำให้ตรวจงานขาดตอนและ retry ได้
12. report มีประวัติและ key เดิมไม่สร้างเวอร์ชันซ้ำโดยไม่ตั้งใจ
13. PDF failure แสดงแยกจาก generation failure
14. ทดสอบ report freshness ขณะเพิ่มข้อมูลและระหว่าง processing ตามข้อจำกัดบท 12

### 14.3 หลักฐานที่มีและขอบเขตครั้งนี้

CONTINUITY บันทึกผลก่อนงานเอกสารนี้ของ format-only auth: backend 425 tests และ 2 subtests ผ่าน, 11 database tests skipped; frontend 162 tests พร้อม lint/build ผ่าน เป็นผลย้อนหลังวันที่ 10 กันยายน ไม่ใช่การ rerun สำหรับเอกสารฉบับนี้

การจัดทำเอกสารครั้งนี้ตรวจ source paths, routes, workflow และ persistence จากโค้ด ไม่ได้เปิดฐานข้อมูลจริง เรียก AI/OCR/OAuth จริง หรือยืนยัน deployment เอกสารไม่ควรใช้แทนผล acceptance test ของ release

## 15. Development และ Deployment

### 15.1 การพัฒนาในเครื่อง

เริ่มจากอ่าน `AGENTS.md`, `CONTINUITY.md`, git status และ configuration ของ environment ที่เลือก ห้ามนำ secret ไปใส่ frontend `NEXT_PUBLIC_*` เพราะค่ากลุ่มนี้ส่งถึง browser ได้

Frontend ใช้คำสั่งในโฟลเดอร์ frontend:

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
```

Backend ใช้ Python environment ที่ติดตั้ง requirements ของโครงการ ทำ migration ต่อฐานข้อมูลเป้าหมายที่ตรวจแล้ว และรัน Uvicorn จาก backend เช่น:

```powershell
python -m alembic upgrade head
doppler run -- uvicorn app.main:app --reload
```

คำสั่ง migration ต้องได้รับ connection configuration ของ environment ที่ถูกต้องด้วย หากใช้ Doppler เป็นแหล่งค่า ให้รัน migration ภายใต้ Doppler ที่เลือกเช่นกัน ไม่ใช่ใช้ connection จาก shell โดยไม่ตรวจ

### 15.2 Compose ปัจจุบัน

```powershell
doppler run -- docker compose up --build
```

Compose ชุดปัจจุบันเน้น development: backend ใช้ reload และ bind mount, frontend ใช้ dev target/webpack dev server, database ใช้ named volume ต้องเตรียม Neo4j/Qdrant และ provider settings ตามบริการที่ใช้ โดย rag-service มี GPU reservation ในไฟล์นี้

Backend startup command ใน Compose ทำ `alembic upgrade head` ก่อน Uvicorn และ depends_on ของ rag-service เป็น started ไม่ใช่ readiness ของโมเดล การเปิด container สำเร็จจึงยังต้องตรวจ readiness แยก

`JWT_COOKIE_SECURE` และ `CORS_ORIGINS` มีการรองรับใน settings แต่ไม่ได้ถูกส่งผ่านรายการ environment ของ Compose ที่ตรวจ ต้องปรับ wiring ให้ตรง deployment หากต้องใช้ค่าต่างจาก default

### 15.3 Configuration สำคัญ

| กลุ่ม | ตัวอย่าง | ใครใช้ |
|---|---|---|
| Database | PostgreSQL host/port/user/password/db | backend และ migration |
| Authentication | JWT secret, cookie settings, frontend base URL | backend |
| OAuth | Google/GitHub client credentials และ callback | backend/provider |
| Browser API | `NEXT_PUBLIC_API_URL` | frontend build/runtime ตามรูปแบบ deploy |
| Main analysis | `CORE_LLM_PROVIDER`, `CASE_ANALYSIS_PIPELINE`, model/budgets | backend |
| Optional retrieval | `RAG_SERVICE_URL` | backend |
| OCR | recognizer, Typhoon settings หรือ Google credentials | backend |
| Knowledge stores | Neo4j/Qdrant settings | rag-service |

ตารางนี้ระบุหมวด ไม่ใช่ไฟล์ secret template ฉบับครบ ต้องตรวจชื่อและค่าใน `config.py` และ Compose ของเวอร์ชันที่จะ deploy จริง

### 15.4 CI/CD ที่พบ

`.github/workflows/deploy.yml` มี build/push images สำหรับ backend, frontend และ rag-service เมื่อ push main หรือ workflow_dispatch ส่วน trigger Railway ของ backend/frontend มีเงื่อนไขเฉพาะ manual dispatch พร้อม input ที่เปิดไว้

Workflow นี้ไม่ได้ประกอบด้วย quality gate ที่รัน test suites ทั้งหมดก่อน build/push จึงไม่ควรตีความว่ามี image ใหม่เท่ากับผ่าน acceptance tests เอกสารฉบับนี้ไม่ได้ตรวจผล workflow หรือสถานะ Railway สด

### 15.5 Release gate ที่เสนอ

ก่อนใช้งานจริงควรระบุ commit/image digest, สำรองฐานข้อมูลและทดสอบ restore, ตรวจ migration, domain/CORS/cookie, provider readiness แล้วทำ smoke test ด้วยข้อมูลทดสอบตั้งแต่สมัครจน export PDF บันทึกผลและวิธี rollback โดยแยก rollback image ออกจาก rollback schema ซึ่งอาจมีผลต่อข้อมูล

## 16. การบำรุงรักษาและค้นหาปัญหา

| อาการ | จุดตรวจแรก | สิ่งที่ยังสรุปไม่ได้จากอาการอย่างเดียว |
|---|---|---|
| เข้า workspace ไม่ได้ | session API, cookie, Origin/CORS | ไม่ได้แปลว่ารหัสผ่านผิดเสมอ |
| กดส่งแล้วรอนาน | run ID/status และ backend logs | HTTP 202 ไม่ใช่ผลวิเคราะห์สำเร็จ |
| processing ค้างหลัง restart | lease expiry/recovery monitor | browser refresh ไม่ได้ restart worker |
| ข้อความดูหายหลังสลับบัญชี | บัญชีปัจจุบัน ownership และ API result | ไม่ควรย้าย thread ให้คนอื่นเพื่อแก้อาการ |
| draft หาย | account namespace, origin และ browser storage | ไม่ได้แปลว่า DB messages ถูกลบ |
| ไม่มี MITRE | applicability และ rag status | เรื่องทั่วไปอาจไม่ควรมี MITRE |
| มีข้อความแต่ไม่มี Overview ที่ใช้ได้ | analysis kind, trace schema/validation | assistant content ทุกอันไม่ใช่ canonical analysis |
| OCR มี warning | page route, provider result และคุณภาพข้อความ | warning ไม่เท่ากับ recognition failure |
| สร้าง report ได้แต่ PDF ไม่ได้ | export validator และ persisted snapshot | เป็นคนละ gate กับ generation |
| local ใช้ได้ production ไม่ได้ | image/version, env wiring, migrations, cookie domain | โค้ดบน disk อาจไม่ใช่โค้ดที่ container ใช้ |

ในการวิเคราะห์ปัญหาให้จด thread ID, run ID หรือ report ID พร้อมเวลาและ error code ก่อนเปลี่ยนโค้ด ไม่บันทึกรหัสผ่าน token หรือข้อความคดีเต็มลง log โดยไม่จำเป็น

## 17. จะเปลี่ยนระบบต่ออย่างไรโดยไม่หลงทาง

| อยากเปลี่ยนอะไร | เริ่มดูที่ไหน | ต้องตรวจผลกระทบต่อ |
|---|---|---|
| รูปแบบหน้า Overview | frontend overview components และ projection | trace schema, citation และ uncertainty |
| ความหมายของ Ask/เพิ่มข้อมูล | chat_run_creation และ raw_evidence | UI action, evidence snapshot และ reports |
| Login/registration | password_auth, auth services, AccountForm | session, ownership และ browser state |
| ข้อมูลที่ persist | models, schemas และ Alembic | API/generated types และ migration tests |
| Prompt/analysis stages | case_analysis และ pipeline_config | parser, traces, token budgets และ receipts |
| ถาม follow-up | followup และ clarification_chain | canonical gaps, topic attempts และ retries |
| Report/PDF | reports services/template/validation | snapshot/version, UI และ export gates |
| OCR provider | document_ingestion recognition/router | preview contract, confidence และ provenance |
| RAG contract | backend schemas/client และ rag-service schema/router | strict response validation ทั้งสองฝั่ง |

แนวทางพัฒนาที่เหมาะกับ repository นี้คือเปลี่ยนให้เล็กและตรวจปลายทางครบ รักษา entrypoint ที่เรียกใช้อยู่ แยกโมดูลตามหน้าที่ และรักษาข้อกำหนด code file ไม่เกิน 300 บรรทัดของโครงการ เอกสารยาวได้ แต่ไม่ควรใช้ข้อจำกัด LOC เป็นเหตุให้ซ่อน logic ไว้ในไฟล์ที่ไม่มีขอบเขตชัดเจน

## 18. คำศัพท์ที่ต้องรู้

| คำ | ความหมายในโครงการ |
|---|---|
| Frontend | โปรแกรมหน้าจอที่ผู้ใช้โต้ตอบ |
| Backend | โปรแกรม server ที่บังคับกฎและประสานงาน |
| API | สัญญารับส่งข้อมูลระหว่างโปรแกรม |
| Schema | รูปร่างและเงื่อนไขของข้อมูล |
| ORM | ตัวช่วยเขียน query/จัด model ให้สัมพันธ์กับตาราง |
| Transaction | กลุ่มการเปลี่ยนฐานข้อมูลที่ commit/rollback ร่วมกัน |
| Migration | ลำดับการเปลี่ยนโครงสร้างฐานข้อมูล |
| Thread | พื้นที่เรื่องหนึ่งพร้อมประวัติข้อความ |
| Run | งานประมวลผลคำขอหนึ่งงาน |
| Polling | อ่านสถานะซ้ำเป็นระยะ |
| Idempotency | ส่งการกระทำเดิมซ้ำโดยไม่สร้างผลซ้ำตาม contract |
| Lease/heartbeat | สิทธิ์ทำงานชั่วคราวและสัญญาณต่ออายุ |
| Evidence snapshot | ชุดข้อความที่ถือเป็นข้อมูลต้นทางในรอบนั้น |
| Claim | ข้อความเชิงข้อกล่าว/ข้อสังเกตในผลวิเคราะห์ ไม่ใช่คำรับรองความจริง |
| Provenance | ข้อมูลว่าผลหรือข้อความมาจากแหล่งใด |
| Projection | แปลงข้อมูลที่มีอยู่เป็นมุมมอง โดยไม่สร้างข้อเท็จจริงใหม่ |
| RAG | ค้นความรู้มาเป็นบริบทให้การสร้างคำตอบ |
| OCR / HTR | อ่านตัวพิมพ์จากภาพ / อ่านลายมือ ซึ่ง HTR ปัจจุบันปิดอยู่ |
| Canonical trace | ผลวิเคราะห์แบบมีโครงสร้างที่ระบบเลือกใช้เป็นสถานะหลัก |

## 19. แผนที่อ่าน source code

ทุก path ด้านล่างอ้างจาก root `F:\Cybercase Framework` เป็นแหล่งตรวจพฤติกรรมในเอกสาร ไม่ใช่รายการไฟล์ทั้งหมด

| ลำดับแนะนำ | แหล่งโค้ด |
|---|---|
| 1 — เปิดหน้าจอ | `frontend/src/components/ChatWorkspace.tsx`, `frontend/src/components/ChatWorkspaceLayout.tsx` |
| 2 — บัญชี | `frontend/src/components/auth/AccountGate.tsx`, `frontend/src/hooks/use-auth.ts`, `backend/app/routers/password_auth.py`, `backend/app/routers/auth.py` |
| 3 — State | `frontend/src/lib/account-storage.ts`, `frontend/src/features/chat/workspace/use-chat-draft.ts`, `frontend/src/hooks/use-chat-queries.ts` |
| 4 — ส่งข้อความ | `frontend/src/features/chat/runs/use-chat-submission.ts`, `backend/app/routers/chat.py`, `backend/app/services/chat/chat_run_creation.py` |
| 5 — Evidence | `backend/app/services/chat/raw_evidence.py`, `backend/app/services/chat/document_provenance.py` |
| 6 — Worker | `backend/app/services/workflow/pipeline_execution.py`, `backend/app/services/workflow/chat_run_completion.py`, `backend/app/services/workflow/run_recovery.py` |
| 7 — Analysis | `backend/app/services/case_analysis/pipeline_config.py`, `backend/app/services/case_analysis/claim_anchored/service.py`, `backend/app/services/workflow/analysis_pipeline_context.py` |
| 8 — Retrieval | `backend/app/services/clients/rag_client.py`, `backend/app/services/workflow/rag_routing.py`, `rag_service/app/routers/rag.py` |
| 9 — เอกสาร | `backend/app/routers/document_ingestion.py`, `backend/app/services/document_ingestion/detection.py` |
| 10 — รายงาน | `backend/app/services/reports/report_snapshot.py`, `backend/app/services/reports/report_generation.py`, `backend/app/services/reports/report_persistence.py` |
| 11 — Persistence | `backend/app/models/chat.py`, `backend/app/models/user.py`, `backend/app/models/rag_context.py`, `backend/app/models/report.py` |
| 12 — Runtime | `backend/app/main.py`, `backend/app/database.py`, `backend/app/config.py`, `docker-compose.yml`, `.github/workflows/deploy.yml` |

เอกสารประกอบเฉพาะบัญชี: `docs/product/ACCOUNT_ACCESS.md` ส่วนเอกสารสถาปัตยกรรมเก่าที่กล่าวว่าไม่มี authentication, เป็น single-user หรือจำเป็นต้องเรียก RAG ทุก analysis ต้องอ่านเป็น snapshot ของอดีตและตรวจ source ปัจจุบันก่อนใช้อ้างอิง
