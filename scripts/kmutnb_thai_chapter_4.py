import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from kmutnb_thai_helpers import (
    add_p, add_h1, add_h2, add_h3, add_h4,
    add_code_block,
    FONT_SIZE_BODY, FONT_SIZE_H1, FONT_SIZE_H2, FONT_SIZE_H3
)

def build_chapter_4(doc):
    add_h1(doc, "บทที่ 4", "การพัฒนาระบบ")
    
    add_p(doc, "ในบทนี้จะกล่าวถึงสภาพแวดล้อม ฮาร์ดแวร์ ซอฟต์แวร์ และเครื่องมือที่ใช้ในการพัฒนาระบบ ตลอดจนการพัฒนาซอฟต์แวร์ของโครงงานทั้งในส่วนระบบส่วนหลัง (Backend Application) และระบบส่วนหน้า (Frontend Web Workspace) โดยนำเสนอตัวอย่าง Source Code ที่สำคัญในแต่ละโมดูล พร้อมคำอธิบายการทำงานของตัวแปร ลำดับขั้นตอนการทำงาน และการตรวจจับข้อผิดพลาดอย่างละเอียด")
    
    add_h2(doc, "4.1 เครื่องมือและสภาพแวดล้อมที่ใช้ในการพัฒนาระบบ")
    add_h3(doc, "4.1.1 ซอฟต์แวร์และเครื่องมือที่ใช้ในการพัฒนา")
    add_p(doc, "• Python Version 3.10+: ภาษาหลักที่ใช้ในการพัฒนาระบบส่วนหลังและงานวิเคราะห์ข้อมูล", first_indent=0.75)
    add_p(doc, "• FastAPI Version 0.110+: เว็บเฟรมเวิร์กประสิทธิภาพสูงสำหรับการพัฒนา Asynchronous REST APIs", first_indent=0.75)
    add_p(doc, "• Pydantic Version 2.6+: ไลบรารีสำหรับตรวจสอบและบังคับใช้โครงสร้างข้อมูล (Data Validation & Schema)", first_indent=0.75)
    add_p(doc, "• PostgreSQL Version 16.0+: ระบบจัดการฐานข้อมูลเชิงสัมพันธ์ระดับองค์กร รองรับ JSONB และ UUID", first_indent=0.75)
    add_p(doc, "• SQLAlchemy Version 2.0+ (Asyncio): Object Relational Mapper สำหรับติดต่อฐานข้อมูลแบบ Asynchronous", first_indent=0.75)
    add_p(doc, "• ReportLab Version 4.1+: ไลบรารีสำหรับเรนเดอร์และสร้างเอกสาร PDF มาตรฐาน", first_indent=0.75)
    add_p(doc, "• Node.js Version 20.11+: สภาพแวดล้อมสำหรับการประมวลผล JavaScript/TypeScript ฝั่งเซิร์ฟเวอร์", first_indent=0.75)
    add_p(doc, "• Next.js Version 16.2.10 (App Router): ฟูลสแตกเว็บเฟรมเวิร์กสำหรับการพัฒนาส่วนติดต่อผู้ใช้", first_indent=0.75)
    add_p(doc, "• React Version 19.2.4: ไลบรารีสำหรับการสร้างส่วนต่อประสานผู้ใช้แบบตอบสนอง", first_indent=0.75)
    add_p(doc, "• TypeScript Version 5.3+: ภาษาที่ช่วยควบคุมประเภทข้อมูลสำหรับฝั่งลูกข่าย", first_indent=0.75)
    add_p(doc, "• Tailwind CSS Version 4.0+: ยูทิลิตี้เฟรมเวิร์กสำหรับการจัดรูปแบบและสไตล์ของหน้าเว็บ", first_indent=0.75)
    add_p(doc, "• TanStack Query (React Query) Version 5.24+: ไลบรารีจัดการแคชและการ Polling สถานะเซิร์ฟเวอร์", first_indent=0.75)
    add_p(doc, "• Pytest Version 8.0+ และ Vitest Version 1.3+: เครื่องมือทดสอบความถูกต้องของซอฟต์แวร์", first_indent=0.75)
    add_p(doc, "• Visual Studio Code: โปรแกรมแก้ไขโค้ดและสภาพแวดล้อมการพัฒนา", first_indent=0.75)
    add_p(doc, "• Git: ระบบควบคุมเวอร์ชันของซอฟต์แวร์ (Version Control System)", first_indent=0.75)

    add_h3(doc, "4.1.2 ระบบปฏิบัติการ")
    add_p(doc, "• Microsoft Windows 11 Pro 64-bit ร่วมกับ Windows Subsystem for Linux 2 (WSL2 Ubuntu 22.04 LTS)")

    add_h3(doc, "4.1.3 เครื่องคอมพิวเตอร์ที่ใช้ในการพัฒนาระบบ")
    add_p(doc, "• หน่วยประมวลผลกลาง (CPU): AMD Ryzen 7 5800H with Radeon Graphics (8 Cores, 16 Threads, 3.20 GHz Up to 4.40 GHz)")
    add_p(doc, "• หน่วยความจำหลัก (RAM): 32.00 GB DDR4 3200 MHz")
    add_p(doc, "• อุปกรณ์จัดเก็บข้อมูล (Storage): 1 TB M.2 NVMe PCIe 4.0 SSD")
    add_p(doc, "• หน่วยประมวลผลกราฟิก (GPU): NVIDIA GeForce RTX 3060 Laptop GPU (6 GB GDDR6)")

    add_h2(doc, "4.2 การพัฒนาระบบของโครงงานฝั่ง Backend")
    add_p(doc, "ระบบส่วนหลัง (Backend) ทำหน้าที่เป็นมันสมองในการประสานการทำงานทั้งหมด โดยมี Source code สำคัญที่พัฒนาขึ้นดังนี้:")

    # Code 4-1
    add_code_block(
        doc,
        title="ภาพที่ 4-1 Source code การสกัดและแปลงข้อความเอกสารสำนวนคดี (document_ingestion/preview.py)",
        code_text="""@router.post("/preview", response_model=DocumentPreviewResponse)
async def preview_document(
    file: UploadFile = File(...),
    ocr_service: OcrService = Depends(get_ocr_service)
) -> DocumentPreviewResponse:
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds 25MB limit")
        
    extracted_pages = []
    if file.filename.endswith(".pdf"):
        extracted_pages = await ocr_service.extract_pdf_pages(content)
    elif file.filename.endswith(".docx"):
        extracted_pages = await ocr_service.extract_docx_paragraphs(content)
    else:
        raise HTTPException(status_code=415, detail="Unsupported file format")
        
    full_text = "\\n\\n".join([p.text for p in extracted_pages])
    return DocumentPreviewResponse(
        filename=file.filename,
        page_count=len(extracted_pages),
        full_text=full_text,
        pages=extracted_pages,
        sha256=hashlib.sha256(content).hexdigest()
    )""",
        explanation_text="อธิบายภาพที่ 4-1 เป็น Source code ในส่วนของ API endpoint /api/v1/document-ingestion/preview โดยทำหน้าที่รับไฟล์เอกสารเข้ามาตรวจสอบขนาด (ไม่เกิน 25MB) และเรียกใช้งาน ocr_service ในการสกัดเนื้อหาตามชนิดไฟล์ (PDF หรือ DOCX) จากนั้นประกอบข้อความเป็น full_text พร้อมคำนวณค่าแฮช SHA-256 เพื่อส่งกลับไปให้ผู้ใช้ตรวจทานบนหน้าเว็บ โดยยังไม่มีการบันทึกข้อมูลลงในฐานข้อมูลจนกว่าผู้ใช้จะกดยืนยัน"
    )

    # Code 4-2
    add_code_block(
        doc,
        title="ภาพที่ 4-2 Source code ตัวคัดกรองความเกี่ยวข้องทางไซเบอร์ (mitre_applicability_gate.py)",
        code_text="""async def evaluate_mitre_applicability(evidence_text: str) -> ApplicabilityResult:
    prompt = MITRE_APPLICABILITY_PROMPT.format(evidence_text=evidence_text)
    try:
        response = await llm_client.generate_json(prompt, schema=ApplicabilitySchema)
        decision = response.get("decision", "SKIP")
        trigger_spans = response.get("trigger_spans", [])
        
        # Verify trigger spans exist verbatim in source text
        validated_spans = []
        if decision == "RETRIEVE":
            for span in trigger_spans:
                if span in evidence_text:
                    validated_spans.append(span)
            if not validated_spans:
                decision = "SKIP"  # Fail-safe degradation if spans are fabricated
                
        return ApplicabilityResult(decision=decision, trigger_spans=validated_spans)
    except Exception as exc:
        logger.warning(f"Applicability gate failed: {exc}, defaulting to SKIP")
        return ApplicabilityResult(decision="SKIP", trigger_spans=[])""",
        explanation_text="อธิบายภาพที่ 4-2 เป็นฟังก์ชัน evaluate_mitre_applicability ซึ่งทำหน้าที่เป็นตัวคัดกรองความเกี่ยวข้องทางไซเบอร์ก่อนการเรียก RAG โดยส่งข้อความพยานหลักฐานไปให้โมเดลจำแนก หากผลลัพธ์เป็น RETRIEVE ระบบจะนำข้อความกระตุ้น (trigger_spans) มาตรวจสอบว่าปรากฏอยู่จริงในเอกสารต้นฉบับหรือไม่ หากไม่พบข้อความตรงกัน ระบบจะปรับลดการตัดสินใจเป็น SKIP ทันที และหากเกิดข้อผิดพลาดใด ๆ ระบบจะคืนค่า SKIP เสมอเพื่อความปลอดภัย"
    )

    # Code 4-3
    add_code_block(
        doc,
        title="ภาพที่ 4-3 Source code โครงสร้าง Pydantic Trace V3 และ Claim Enums (contracts.py)",
        code_text="""class ClaimType(str, Enum):
    ALLEGATION = "allegation"
    PARTY_ROLE = "party_role"
    TIMELINE_EVENT = "timeline_event"
    EVIDENCE_EXHIBIT = "evidence_exhibit"
    PROCEDURAL_STEP = "procedural_step"

class EpistemicStatus(str, Enum):
    REPORTED = "reported"
    INFERENCE = "inference"
    UNRESOLVED = "unresolved"
    DISPUTED = "disputed"

class GroundedClaimV3(BaseModel):
    id: str = Field(regex=r"^A-(0[1-9]|[1-5][0-9]|6[0-4])$")  # A-01 to A-64
    statement: str
    claim_type: ClaimType
    epistemic_status: EpistemicStatus
    source_message_ids: list[UUID]
    exact_quotes: list[str]
    document_page: Optional[int] = None
    mitre_technique_id: Optional[str] = None""",
        explanation_text="อธิบายภาพที่ 4-3 เป็น Source code กำหนดโครงสร้างข้อมูลตามมาตรฐาน Pydantic โดยกำหนดประเภทของข้ออ้าง (ClaimType) และสถานะความเชื่อมั่นเชิงประจักษ์ (EpistemicStatus) อย่างเคร่งครัด โดยรหัสข้ออ้างถูกจำกัดให้อยู่ในรูปแบบ A-01 ถึง A-64 เพื่อป้องกันไม่ให้โมเดลสร้างรหัสที่สับสน และบังคับให้ทุกข้ออ้างต้องมีรายการ exact_quotes และ source_message_ids กำกับอยู่เสมอ"
    )

    # Code 4-4
    add_code_block(
        doc,
        title="ภาพที่ 4-4 Source code การถอดรหัสและการตรวจสอบโครงสร้าง Trace (response_decoder.py)",
        code_text="""def decode_analysis_response(raw_payload: dict, evidence_msg_id: UUID) -> AnalysisTraceV3:
    summary = raw_payload.get("case_summary", "")
    overview_5w1h = raw_payload.get("overview_5w1h", {})
    raw_claims = raw_payload.get("grounded_claims", [])
    
    validated_claims = []
    for rc in raw_claims:
        # Enforce source message identity binding
        rc["source_message_ids"] = [evidence_msg_id]
        try:
            claim = GroundedClaimV3(**rc)
            validated_claims.append(claim)
        except ValidationError as val_err:
            logger.error(f"Malformed claim payload skipped: {val_err}")
            continue
            
    return AnalysisTraceV3(
        summary=summary,
        overview_5w1h=overview_5w1h,
        claims=validated_claims,
        chronology=raw_payload.get("chronology", [])
    )""",
        explanation_text="อธิบายภาพที่ 4-4 เป็น Source code ฟังก์ชัน decode_analysis_response ทำหน้าที่แปลงข้อมูล JSON ที่ได้รับจากโมเดลให้อยู่ในรูป AnalysisTraceV3 โดยมีการบังคับผูกรหัสข้อความหลักฐานจริง (evidence_msg_id) เข้ากับทุกข้ออ้างโดยตรง เพื่อตัดปัญหาโมเดลสร้างรหัสแหล่งที่มาปลอม และหากข้ออ้างใดมีโครงสร้างไม่ถูกต้อง ระบบจะบันทึกข้อผิดพลาดและตัดทิ้งโดยไม่ทำให้ระบบหยุดทำงาน"
    )

    # Code 4-5
    add_code_block(
        doc,
        title="ภาพที่ 4-5 Source code อัลกอริทึมการตรวจสอบข้อความอ้างอิงตรง (source_citations.py)",
        code_text="""def validate_claim_citations(claim: GroundedClaimV3, source_text: str, doc_pages: list[Page]) -> GroundedClaimV3:
    verified_quotes = []
    for quote in claim.exact_quotes:
        clean_q = quote.strip()
        if clean_q and clean_q in source_text:
            verified_quotes.append(clean_q)
            
    claim.exact_quotes = verified_quotes
    if not verified_quotes:
        claim.document_page = None  # Remove page coordinate if quote is invalid
        return claim
        
    # Verify page location
    matched_pages = [p.page_number for p in doc_pages if verified_quotes[0] in p.text]
    if len(matched_pages) == 1:
        claim.document_page = matched_pages[0]
    else:
        claim.document_page = None  # Conservative degradation on page ambiguity
        
    return claim""",
        explanation_text="อธิบายภาพที่ 4-5 เป็นอัลกอริทึมการตรวจสอบข้อความอ้างอิงตรง validate_claim_citations โดยค้นหาข้อความ clean_q ใน source_text แบบตัวอักษรต่อตัวอักษร หากไม่พบจะตัดออกทันที และทำการค้นหาว่าข้อความดังกล่าวอยู่ในหน้าใด หากพบตรงกันในหน้าเดียวอย่างชัดเจน จึงจะบันทึกเลขหน้านั้น แต่หากข้อความดังกล่าวปรากฏในหลายหน้าหรือคาบเกี่ยวกัน ระบบจะปรับลดระดับเป็นไม่ระบุเลขหน้าเพื่อป้องกันการชี้นำหน้าที่ผิดพลาด"
    )

    # Code 4-6
    add_code_block(
        doc,
        title="ภาพที่ 4-6 Source code นโยบายการคัดเลือกประเด็นคำถามและการตัดลูป (followup/decision.py)",
        code_text="""def select_next_clarification_gap(gaps: list[AnalysisGapV3], exhausted_topics: set[str]) -> Optional[AnalysisGapV3]:
    eligible = []
    for g in gaps:
        norm_key = normalize_topic_key(g.topic)
        if g.askability == "ASKABLE" and norm_key not in exhausted_topics:
            eligible.append(g)
            
    if not eligible:
        return None  # Triggers PROCEED
        
    # Sort priority: HIGH before MEDIUM, linked claims preferred
    def rank_gap(gap: AnalysisGapV3):
        p_val = 0 if gap.priority == "HIGH" else 1
        link_val = 0 if len(gap.affected_claim_ids) > 0 else 1
        return (p_val, link_val)
        
    eligible.sort(key=rank_gap)
    return eligible[0]""",
        explanation_text="อธิบายภาพที่ 4-6 เป็น Source code ฟังก์ชัน select_next_clarification_gap ในการคัดเลือกประเด็นคำถามขอความกระจ่าง โดยระบบจะกรองหัวข้อที่เคยถามแล้ว (exhausted_topics) ออกไปทั้งหมด จากนั้นเรียงลำดับความสำคัญโดยให้ประเด็นระดับ HIGH และมีข้อกล่าวหาที่ได้รับผลกระทบขึ้นมาก่อน หากไม่เหลือประเด็นที่ถามได้ ระบบจะคืนค่า None ซึ่งส่งผลให้เวิร์กโฟลว์เปลี่ยนสถานะเป็น PROCEED และเสร็จสิ้นการวิเคราะห์ทันที"
    )

    # Code 4-7
    add_code_block(
        doc,
        title="ภาพที่ 4-7 Source code การจัดการสัญญาเช่า Worker และการกู้คืนงานขัดข้อง (workflow/chat_run_locks.py)",
        code_text="""async def acquire_run_lease(db: AsyncSession, run_id: UUID, worker_id: str) -> bool:
    now = datetime.now(timezone.utc)
    lease_until = now + timedelta(minutes=6)
    stmt = (
        update(ChatRun)
        .where(ChatRun.id == run_id)
        .where(or_(ChatRun.lease_owner.is_(None), ChatRun.lease_expires_at < now))
        .values(lease_owner=worker_id, lease_expires_at=lease_until, status="running")
    )
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount > 0""",
        explanation_text="อธิบายภาพที่ 4-7 เป็น Source code ฟังก์ชัน acquire_run_lease ซึ่งทำหน้าที่เคลมสิทธิ์ในการรันงานของ Worker โดยตรวจสอบว่างานนั้นยังไม่มีผู้ถือครองหรือสัญญาเช่าเดิมหมดอายุแล้ว โดยกำหนดระยะเวลาสัญญาเช่าไว้ที่ 6 นาที หาก Worker เดิมค้างหรือดับไป Worker ตัวใหม่จะสามารถเข้ามาถือครองสิทธิ์และดำเนินการต่อได้โดยไม่มีการประมวลผลซ้อนทับกัน"
    )

    # Code 4-8
    add_code_block(
        doc,
        title="ภาพที่ 4-8 Source code ตัวแปลงมุมมองรายงานและการเรนเดอร์ PDF (reports/report_builder.py)",
        code_text="""def build_template_report(snapshot: ReportSnapshot) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    story = []
    
    # Section 1: Executive Summary
    story.append(Paragraph("รายงานสรุปข้อเท็จจริงสำนวนคดีอาญา", style_title))
    story.append(Paragraph(snapshot.executive_summary, style_body))
    
    # Section 4: Grounded Findings Table
    table_data = [["รหัส", "ข้อกล่าวหา / พฤติการณ์", "สถานะ", "หน้า"]]
    for c in snapshot.claims:
        table_data.append([c.id, c.statement, c.epistemic_status.value, str(c.document_page or "-")])
    story.append(Table(table_data, colWidths=[40, 320, 80, 40], style=table_style))
    
    doc.build(story)
    return buffer.getvalue()""",
        explanation_text="อธิบายภาพที่ 4-8 เป็น Source code การประกอบและเรนเดอร์รายงาน PDF ด้วย ReportLab ผ่านฟังก์ชัน build_template_report โดยนำข้อมูลจาก ReportSnapshot ที่จัดเก็บไว้มาแปลงเป็นองค์ประกอบหน้ากระดาษ (Paragraph, Table) ตามรูปแบบแม่แบบมาตรฐาน โดยไม่มีการเรียกใช้โมเดลภาษา จึงรับประกันว่ารายงานที่ได้จะตรงกับข้อเท็จจริงในระบบ 100%"
    )

    add_h2(doc, "4.3 การพัฒนาระบบของโครงงานฝั่ง Frontend")
    add_p(doc, "ระบบส่วนหน้า (Frontend) พัฒนาด้วย Next.js 16 และ React 19 โดยมี Source code สำคัญที่พัฒนาขึ้นดังนี้:")

    # Code 4-9
    add_code_block(
        doc,
        title="ภาพที่ 4-9 Source code การจัดการแคชและการ Polling แบบวงรอบเดียว (features/chat/runs/chat-polling.ts)",
        code_text="""export function useChatPolling(threadId: string, activeRunId: string | null) {
  const queryClient = useQueryClient();
  
  return useQuery({
    queryKey: ["chat-thread", threadId],
    queryFn: () => fetchThreadDetail(threadId),
    enabled: Boolean(threadId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "processing" || Boolean(activeRunId)) {
        return 1500; // Poll every 1.5s during active processing
      }
      return false; // Stop polling when idle or awaiting user
    },
  });
}""",
        explanation_text="อธิบายภาพที่ 4-9 เป็น React Hook useChatPolling ที่ใช้ TanStack Query ในการตรวจสอบสถานะของสำนวนคดี โดยกำหนดเงื่อนไข refetchInterval อัตโนมัติ หากสถานะเป็น processing ระบบจะ Polling ทุก 1.5 วินาที และจะหยุด Polling ทันทีเมื่อสถานะเข้าสู่ idle หรือ awaiting_followup เพื่อประหยัดทรัพยากรเครือข่าย"
    )

    # Code 4-10
    add_code_block(
        doc,
        title="ภาพที่ 4-10 Source code การแยกสถานะแบบร่างและการส่งข้อความซ้ำ (features/chat/workspace/use-chat-submission.ts)",
        code_text="""export function useChatSubmission(threadId: string) {
  const [draft, setDraft] = useState("");
  const [pendingRetryRunId, setPendingRetryRunId] = useState<string | null>(null);
  
  const submitMessage = useMutation({
    mutationFn: (content: string) => postMessage(threadId, { content }),
    onSuccess: () => {
      setDraft(""); // Clear draft only upon confirmed submission
    },
    onError: (err) => {
      // Retain draft content on error so user input is never lost
      console.error("Submission failed, draft retained:", err);
    }
  });
  
  return { draft, setDraft, submitMessage, pendingRetryRunId, setPendingRetryRunId };
}""",
        explanation_text="อธิบายภาพที่ 4-10 เป็น Hook จัดการการส่งข้อความ useChatSubmission โดยแยกสถานะข้อความแบบร่าง (draft) ออกจากแคชของเซิร์ฟเวอร์ และมีเงื่อนไขว่าข้อความแบบร่างจะถูกล้างค่าก็ต่อเมื่อการส่งสำเร็จสมบูรณ์เท่านั้น หากเกิดข้อผิดพลาดทางเครือข่าย ข้อความจะยังคงอยู่บนหน้าจอเพื่อให้ผู้ใช้กดส่งใหม่ได้ทันทีโดยไม่ต้องพิมพ์ซ้ำ"
    )

    # Code 4-11
    add_code_block(
        doc,
        title="ภาพที่ 4-11 Source code คอมโพเนนต์แสดงภาพรวมและข้ออ้างเชิงประจักษ์ (CaseFindingsSection.tsx)",
        code_text="""export function CaseFindingsSection({ claims, onSelectCitation }: Props) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-900">รายการข้อกล่าวหาและพฤติการณ์คดี</h3>
      <div className="grid gap-3">
        {claims.map((claim) => (
          <div key={claim.id} className="p-4 rounded-lg border bg-white shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-xs font-bold text-blue-600">{claim.id}</span>
              <EpistemicBadge status={claim.epistemic_status} />
            </div>
            <p className="text-slate-800 text-sm mb-3">{claim.statement}</p>
            <div className="flex flex-wrap gap-2">
              {claim.exact_quotes.map((quote, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectCitation(claim.source_message_ids[0], quote, claim.document_page)}
                  className="px-2 py-1 text-xs bg-slate-100 hover:bg-amber-100 text-slate-700 rounded border"
                >
                  {claim.document_page ? `[หน้า ${claim.document_page}]` : "[เอกสารแนบ]"} "{quote.slice(0, 30)}..."
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}""",
        explanation_text="อธิบายภาพที่ 4-11 เป็นคอมโพเนนต์ CaseFindingsSection สำหรับแสดงรายการข้ออ้างทางคดี โดยแสดงป้ายสถานะความเชื่อมั่น (EpistemicBadge) และสร้างปุ่มชิปสำหรับการอ้างอิงแหล่งที่มา เมื่อผู้ใช้กดคลิกที่ปุ่มอ้างอิง ระบบจะเรียกฟังก์ชัน onSelectCitation เพื่อเปิดลิ้นชักเอกสารและทำไฮไลต์ข้อความอ้างอิงทันที"
    )

    # Code 4-12
    add_code_block(
        doc,
        title="ภาพที่ 4-12 Source code คอมโพเนนต์ลิ้นชักตรวจสอบเอกสารและการเน้นข้อความ (CitationDrawer.tsx)",
        code_text="""export function CitationDrawer({ isOpen, onClose, documentText, targetQuote, page }: Props) {
  if (!isOpen) return null;
  
  const highlightedContent = useMemo(() => {
    if (!targetQuote || !documentText.includes(targetQuote)) {
      return documentText;
    }
    const parts = documentText.split(targetQuote);
    return (
      <>
        {parts[0]}
        <mark className="bg-amber-200 text-slate-900 font-medium px-1 rounded">{targetQuote}</mark>
        {parts[1]}
      </>
    );
  }, [documentText, targetQuote]);
  
  return (
    <Drawer open={isOpen} onClose={onClose} title={`ตรวจสอบพยานหลักฐานต้นทาง ${page ? `(หน้า ${page})` : ""}`}>
      <div className="p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap">
        {highlightedContent}
      </div>
    </Drawer>
  );
}""",
        explanation_text="อธิบายภาพที่ 4-12 เป็นคอมโพเนนต์ CitationDrawer ทำหน้าที่เปิดหน้าต่างลิ้นชักจากด้านข้างเพื่อแสดงเอกสารสำนวนคดีต้นฉบับ โดยใช้ useMemo ในการค้นหา targetQuote และแท็ก <mark> สีเหลืองเพื่อเน้นข้อความอ้างอิงตรง ช่วยให้อัยการสามารถตรวจสอบบริบทแวดล้อมของข้อความนั้นได้อย่างชัดเจน"
    )

    doc.add_page_break()

print("Chapter 4 ready.")
