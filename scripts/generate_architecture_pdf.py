"""Script to generate a comprehensive, highly-detailed PDF architecture document for CyberCase Intelligence Framework."""

import os
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Colors
_NAVY = colors.HexColor("#1A365D")
_BLUE = colors.HexColor("#2B6CB0")
_TEAL = colors.HexColor("#2C7A7B")
_DARK = colors.HexColor("#1A202C")
_TEXT = colors.HexColor("#2D3748")
_MUTED = colors.HexColor("#718096")
_LIGHT_BG = colors.HexColor("#F7FAFC")
_PANEL = colors.HexColor("#EDF2F7")
_BORDER = colors.HexColor("#E2E8F0")
_RULE = colors.HexColor("#CBD5E0")
_CODE_BG = colors.HexColor("#1E293B")
_ACCENT = colors.HexColor("#3182CE")
_BADGE_BG = colors.HexColor("#EBF8FF")
_BADGE_TEXT = colors.HexColor("#2B6CB0")
_SUCCESS_BG = colors.HexColor("#F0FFF4")
_SUCCESS_TEXT = colors.HexColor("#22543D")
_WARN_BG = colors.HexColor("#FFFAF0")
_WARN_TEXT = colors.HexColor("#7B341E")

PAGE_WIDTH, PAGE_HEIGHT = A4

def register_fonts():
    font_paths = [
        ("C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf", "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf"),
        ("/usr/share/fonts/truetype/tlwg/Garuda.ttf", "/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf"),
    ]
    for reg, bld in font_paths:
        if os.path.exists(reg) and os.path.exists(bld):
            try:
                pdfmetrics.registerFont(TTFont("CyberCaseFont", reg))
                pdfmetrics.registerFont(TTFont("CyberCaseFontBold", bld))
                return "CyberCaseFont", "CyberCaseFontBold"
            except Exception as e:
                print(f"Font registration failed for {reg}: {e}")
    return "Helvetica", "Helvetica-Bold"

def build_styles(reg, bold):
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontName=bold,
            fontSize=22,
            leading=26,
            textColor=_NAVY,
            alignment=TA_LEFT,
        ),
        "doc_subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontName=reg,
            fontSize=11,
            leading=16,
            textColor=_MUTED,
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Normal"],
            fontName=bold,
            fontSize=14,
            leading=18,
            textColor=_NAVY,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Normal"],
            fontName=bold,
            fontSize=11,
            leading=15,
            textColor=_BLUE,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Normal"],
            fontName=bold,
            fontSize=9.5,
            leading=13,
            textColor=_DARK,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName=reg,
            fontSize=8.5,
            leading=12.5,
            textColor=_TEXT,
            alignment=TA_JUSTIFY,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8.5,
            leading=12.5,
            textColor=_DARK,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName=reg,
            fontSize=8.5,
            leading=12.5,
            textColor=_TEXT,
            leftIndent=10,
            firstLineIndent=-6,
        ),
        "code_block": ParagraphStyle(
            "CodeBlock",
            parent=base["Normal"],
            fontName=reg,
            fontSize=7.5,
            leading=10.5,
            textColor=colors.HexColor("#E2E8F0"),
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName=reg,
            fontSize=8,
            leading=11,
            textColor=_TEXT,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=11,
            textColor=colors.white,
        ),
        "table_cell_code": ParagraphStyle(
            "TableCellCode",
            parent=base["Normal"],
            fontName=bold,
            fontSize=7.5,
            leading=10,
            textColor=_BLUE,
        ),
        "badge": ParagraphStyle(
            "Badge",
            parent=base["Normal"],
            fontName=bold,
            fontSize=8,
            leading=10,
            textColor=_BADGE_TEXT,
            alignment=TA_CENTER,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName=reg,
            fontSize=8.5,
            leading=12,
            textColor=_MUTED,
        ),
    }

def draw_header_footer(canvas, doc, reg, bold):
    canvas.saveState()
    canvas.setStrokeColor(_RULE)
    canvas.setLineWidth(0.5)
    
    # Top header line (except first page)
    if doc.page > 1:
        canvas.line(doc.leftMargin, PAGE_HEIGHT - 13 * mm, PAGE_WIDTH - doc.rightMargin, PAGE_HEIGHT - 13 * mm)
        canvas.setFont(bold, 7)
        canvas.setFillColor(_MUTED)
        canvas.drawString(doc.leftMargin, PAGE_HEIGHT - 10 * mm, "CYBERCASE INTELLIGENCE FRAMEWORK — ARCHITECTURE SPECIFICATION")
        canvas.drawRightString(PAGE_WIDTH - doc.rightMargin, PAGE_HEIGHT - 10 * mm, "BACKEND & FRONTEND DEEP DIVE")
    
    # Bottom footer line
    canvas.line(doc.leftMargin, 12 * mm, PAGE_WIDTH - doc.rightMargin, 12 * mm)
    canvas.setFont(reg, 7)
    canvas.setFillColor(_MUTED)
    canvas.drawString(doc.leftMargin, 8 * mm, "Confidential — System Architecture & Technical Implementation Document")
    canvas.drawRightString(PAGE_WIDTH - doc.rightMargin, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()

def create_code_panel(code_text, styles):
    p = Paragraph(code_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), styles["code_block"])
    t = Table([[p]], colWidths=[PAGE_WIDTH - 36 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _CODE_BG),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('CORNERPAD', (0,0), (-1,-1), 3),
    ]))
    return t

def create_info_panel(title, content, styles, bg_color=_PANEL, border_color=_BORDER):
    t_title = Paragraph(f"<b>{title}</b>", styles["h3"])
    t_content = Paragraph(content, styles["body"])
    t = Table([[t_title], [Spacer(1, 2*mm)], [t_content]], colWidths=[PAGE_WIDTH - 36 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t

def generate_pdf(output_path: str):
    reg, bold = register_fonts()
    styles = build_styles(reg, bold)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
    )
    
    story = []
    
    # -------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------
    story.append(Paragraph("CYBERCASE INTELLIGENCE FRAMEWORK", ParagraphStyle(
        "Eyebrow", parent=styles["doc_subtitle"], fontName=bold, fontSize=8.5, textColor=_ACCENT, spaceAfter=2
    )))
    story.append(Paragraph("System Architecture Specification: Full-Stack Deep Dive", styles["doc_title"]))
    story.append(Paragraph(
        "เอกสารสรุปสถาปัตยกรรมระบบอย่างละเอียด: Frontend (Next.js 15), Backend (FastAPI), GraphRAG (LangGraph + Neo4j + Qdrant), Data Flow และ State Machine",
        styles["doc_subtitle"]
    ))
    story.append(Spacer(1, 4 * mm))
    
    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Version:</b> 1.0.0 (Production Architecture)", styles["cover_meta"]),
            Paragraph("<b>Generated Date:</b> August 2026", styles["cover_meta"]),
            Paragraph("<b>Classification:</b> System Architecture", styles["cover_meta"]),
        ],
        [
            Paragraph("<b>Core Stack:</b> Next.js 15, FastAPI, Neo4j, Qdrant", styles["cover_meta"]),
            Paragraph("<b>AI Engine:</b> LangGraph Agentic RAG + OpenRouter", styles["cover_meta"]),
            Paragraph("<b>Intelligence:</b> MITRE ATT&CK STIX 2.1", styles["cover_meta"]),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[(PAGE_WIDTH - 36*mm)/3]*3)
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), _LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, _BORDER),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=_NAVY))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY & ARCHITECTURAL FOUNDATION
    # -------------------------------------------------------------
    story.append(Paragraph("1. ภาพรวมระบบและหลักการออกแบบ (Executive Summary & Architecture Vision)", styles["h1"]))
    story.append(Paragraph(
        "<b>CyberCase Intelligence Framework</b> เป็นระบบ Full-Stack Agentic RAG ที่ออกแบบมาเพื่อการสืบสวนและวิเคราะห์เหตุการณ์ภัยคุกคามทางไซเบอร์ (Cybersecurity Incident Analysis) "
        "โดยทำการจับคู่พฤติกรรมการโจมตีเข้ากับฐานความรู้ <b>MITRE ATT&CK (STIX 2.1)</b> แบบ 2-Hop Graph Traversal ร่วมกับการสืบค้นเชิงความหมาย (Dense Vector Search) "
        "และมีระบบจัดเก็บประวัติการวิเคราะห์แบบ <b>Immutable Case State</b> เพื่อให้ทุกการวิเคราะห์สามารถตรวจสอบย้อนกลับ (Auditability) ได้อย่างสมบูรณ์",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))
    
    # Core Architecture Tenets
    tenets_data = [
        [
            Paragraph("<b>หลักการสถาปัตยกรรม</b>", styles["table_header"]),
            Paragraph("<b>รายละเอียดการนำไปใช้งาน (Implementation Details)</b>", styles["table_header"]),
        ],
        [
            Paragraph("<b>Single Source of Truth</b>", styles["table_cell_code"]),
            Paragraph("PostgreSQL เป็นแหล่งข้อมูลเดียวที่เป็น Authoritative State สำหรับแชท (Threads), ข้อความ (Messages), การประมวลผล (Runs), และประวัติสถานะเคส (CaseStateVersions) โดย Frontend จะไม่มี local state ที่ขัดแย้งกับฐานข้อมูล", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Decoupled GraphRAG</b>", styles["table_cell_code"]),
            Paragraph("`rag_service` ทำงานเป็น Microservice อิสระ ทำหน้าที่ประมวลผลการค้นหา กราฟ และ AI เท่านั้น โดย Backend เป็นผู้ดูแล Clarification State, Follow-up Gating และ Snapshot Management", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Immutable Case State DAG</b>", styles["table_cell_code"]),
            Paragraph("ทุกการสกัดข้อมูลและอัปเดตเคสจะสร้างเวอร์ชันใหม่ (`CaseStateVersion`) เสมอ มี parent lineage ชัดเจน ป้องกันการเขียนทับ (In-place Mutation) และรองรับการทำ Audit Trail", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Asynchronous Run Lease</b>", styles["table_cell_code"]),
            Paragraph("ระบบ Chat Ingestion ทำงานแบบ Asynchronous Job (HTTP 202 Accepted) ควบคุมผ่าน Worker Lease (`RUN_LEASE_DURATION` 60s) ป้องกัน Deadlock และ Concurrency Collision", styles["table_cell"]),
        ],
    ]
    t_tenets = Table(tenets_data, colWidths=[42*mm, PAGE_WIDTH - 36*mm - 42*mm])
    t_tenets.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_tenets)
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 2: HIGH-LEVEL TOPOLOGY & SERVICE ORCHESTRATION
    # -------------------------------------------------------------
    story.append(Paragraph("2. ผังโครงสร้างระดับสูง (High-Level System Topology & Services)", styles["h1"]))
    story.append(Paragraph(
        "โครงสร้างระบบแบ่งออกเป็น 3 เลเยอร์หลัก พร้อมฐานข้อมูลเฉพาะทาง 4 ชนิด เชื่อมโยงผ่าน Docker Compose:",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))

    topology_text = """
  +-----------------------------------------------------------------------------------+
  |                       FRONTEND LAYER (Next.js 15 App Router)                      |
  |  - React 19 + Tailwind CSS 4 + TypeScript                                         |
  |  - 3-Panel Workspace (Thread Sidebar | Chat Stream & Actions | Intelligence Tabs) |
  |  - Lease-Aware Polling (1s Interval) + Generation Guard (Race-Condition Safe)     |
  +-----------------------------------------+-----------------------------------------+
                                            | HTTP REST API (Port 8000)
                                            v
  +-----------------------------------------------------------------------------------+
  |                         BACKEND API LAYER (FastAPI Async)                         |
  |  - Endpoints: /chats, /messages, /runs, /reports, /health                        |
  |  - Run Worker Lease Manager (In-process Async Background Task with TTL Lease)     |
  |  - Baseline Extraction & Delta Mutation Engine (JSON Schema Validation)           |
  |  - Clarification & Gap Policy Engine (Priority Gating & Safe Token Tracing)       |
  |  - Deterministic PDF Report Generator (ReportLab Snapshot Renderer)               |
  +--------------------+--------------------+--------------------+--------------------+
                       |                    |                    |
                       | SQLAlchemy Async   | HTTP POST /query   | Docker Secrets
                       v                    v                    v
  +--------------------+-------+   +--------+-----------+   +----+--------------------+
  |    PERSISTENCE LAYER       |   |  STANDALONE RAG    |   | CONFIGURATION & SECRETS |
  |      (PostgreSQL 16)       |   |     SERVICE        |   | - Doppler Secret Vault  |
  | - chat_threads             |   | (FastAPI + LangGraph)| | - OpenRouter Multi-LLM  |
  | - chat_messages            |   +----+-----------+---+   |   (Luna/Sonnet/OSS/4o)  |
  | - chat_runs                |        |           |       +-------------------------+
  | - case_state_versions (DAG)|        | BGE-M3    | 2-Hop Cypher
  | - chat_reports & snapshots |        v           v
  +----------------------------+   +----+-----+   +-+--------+
                                   |  QDRANT  |   |  NEO4J   |
                                   | VectorDB |   | Graph DB |
                                   +----------+   +----------+
"""
    story.append(create_code_panel(topology_text, styles))
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 3: FRONTEND ARCHITECTURE DEEP DIVE
    # -------------------------------------------------------------
    story.append(Paragraph("3. สถาปัตยกรรมฝั่ง Frontend (Next.js 15 + React 19)", styles["h1"]))
    story.append(Paragraph(
        "Frontend ถูกสร้างบนสถาปัตยกรรม <b>Next.js 15 App Router</b> ร่วมกับ <b>React 19</b> และ <b>Tailwind CSS 4</b> "
        "โดยเน้นความเป็น Cognitive Forensic Workspace ที่สามารถประมวลผลและแสดงผลข้อมูลการสืบสวนที่มีความซับซ้อนสูงได้อย่างราบรื่น",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("3.1 โครงสร้างโฟลเดอร์และส่วนประกอบหลัก (Component Architecture)", styles["h2"]))
    
    fe_comp_data = [
        [
            Paragraph("<b>ไดเรกทอรี / โมดูล</b>", styles["table_header"]),
            Paragraph("<b>หน้าที่และความรับผิดชอบ (Role & Responsibilities)</b>", styles["table_header"]),
        ],
        [
            Paragraph("`src/app/chat/page.tsx`", styles["table_cell_code"]),
            Paragraph("Main Entrypoint ของหน้าแชทหลัก จัดการ Life cycle, การเลือก Thread, และทำ Data Fetching เริ่มต้น", styles["table_cell"]),
        ],
        [
            Paragraph("`src/components/ChatWorkspace.tsx`", styles["table_cell_code"]),
            Paragraph("ศูนย์กลางควบคุม Layout แบ่งเป็น 3 ส่วน: Sidebar, Conversation Feed, และ Intelligence Inspector Tabs พร้อมคุม Master State", styles["table_cell"]),
        ],
        [
            Paragraph("`src/components/conversation/`", styles["table_cell_code"]),
            Paragraph("โมดูลข้อความ: `MessageBubble`, `MessageList`, `Composer` (กล่องพิมพ์ข้อความที่ปรับตามสถานะ), `ActionSelector` (เลือกเจตนา: New Incident, Add Info, Ask), และ `FollowupBanner`", styles["table_cell"]),
        ],
        [
            Paragraph("`src/components/analysis/`", styles["table_cell_code"]),
            Paragraph("โมดูลวิเคราะห์เคส: `CaseOverview` (สรุปผลการวิเคราะห์), `MitreTechniqueList` (ตารางเทคนิค MITRE พร้อม Confidence Score), `ExtractedEntities` (Entity Badges), และ `RawEvidenceViewer`", styles["table_cell"]),
        ],
        [
            Paragraph("`src/components/timeline/` & `relationships/`", styles["table_cell_code"]),
            Paragraph("แสดงลำดับเหตุการณ์การโจมตี (Chronological Timeline Cards) และแผนผังกราฟความสัมพันธ์ระหว่าง Actor, Tool, และ Victim", styles["table_cell"]),
        ],
        [
            Paragraph("`src/components/report/`", styles["table_cell_code"]),
            Paragraph("โมดูลรายงาน: แสดงตัวอย่าง Markdown Report, ตัวเลือกดาวน์โหลด PDF (`/pdf`), และประวัติเวอร์ชันรายงาน", styles["table_cell"]),
        ],
        [
            Paragraph("`src/lib/api.ts`", styles["table_cell_code"]),
            Paragraph("Type-safe API Client เชื่อมต่อ Backend Endpoint พร้อมระบบจัดการ Error, AbortSignal และ Retry Mechanism", styles["table_cell"]),
        ],
    ]
    t_fe_comp = Table(fe_comp_data, colWidths=[48*mm, PAGE_WIDTH - 36*mm - 48*mm])
    t_fe_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_fe_comp)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.2 วงรอบการทำงานและการจัดการความสอดคล้องของ State (Polling & Concurrency Guard)", styles["h2"]))
    story.append(Paragraph(
        "เนื่องจาก Backend ประมวลผลแบบ Asynchronous Background Task ฝั่ง Frontend จึงมีกลไก Polling และ Concurrency Guard ที่รัดกุม:",
        styles["body"]
    ))
    story.append(Paragraph("• <b>Lease-Aware Polling (1s Interval):</b> หลังส่งข้อความและได้ `202 Accepted` Frontend จะเริ่ม Poll `GET /api/v1/chats/{thread_id}` ทุก 1 วินาที โดยตรวจสอบสถานะ `status` (`processing` $\to$ Poll ต่อ, `awaiting_followup` $\to$ เปิดกล่องถามคำถามชี้แจง, `idle`/`answered` $\to$ หยุด Poll และเรนเดอร์คำตอบ)", styles["bullet"]))
    story.append(Paragraph("• <b>Dual Concurrency Guard:</b> ป้องกันปัญหา Race Condition เมื่อผู้ใช้สลับ Thread อย่างรวดเร็ว โดยใช้: <br/>"
                           "  1. <i>AbortController:</i> ยกเลิก HTTP Request/Polling ของ Thread เดิมทันทีที่มีการสลับ Thread<br/>"
                           "  2. <i>selectionGenerationRef:</i> ตัวนับลำดับการเลือก (Generation Monotonic Counter) เพื่อปฏิเสธการตอบกลับที่มาช้ากว่า (Late Response) ไม่ให้เขียนทับ State ของ Thread ปัจจุบัน", styles["bullet"]))
    story.append(Paragraph("• <b>Idempotency Key Injection:</b> ทุกข้อความที่ส่งจะสร้าง UUID เฉพาะเป็น `idempotency_key` เพื่อป้องกันการส่งซ้ำกรณี Network Retry", styles["bullet"]))
    story.append(Spacer(1, 4 * mm))

    # -------------------------------------------------------------
    # SECTION 4: BACKEND ARCHITECTURE & PIPELINE DEEP DIVE
    # -------------------------------------------------------------
    story.append(Paragraph("4. สถาปัตยกรรมฝั่ง Backend (FastAPI + SQLAlchemy Async)", styles["h1"]))
    story.append(Paragraph(
        "Backend ทำหน้าที่เป็น Orchestrator กลางของทั้งระบบ ควบคุมตั้งแต่ Data Ingestion, Background Worker Lease, "
        "การสกัดข้อมูล Structured Case State, การเรียก GraphRAG, ตรวจสอบ Clarification Gating, จนถึงการบันทึกผลลัพธ์ลง PostgreSQL",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("4.1 โครงสร้างเลเยอร์ของ Services (Backend Modular Services)", styles["h2"]))
    
    be_svc_data = [
        [
            Paragraph("<b>โมดูล Service</b>", styles["table_header"]),
            Paragraph("<b>คำอธิบายการทำงานเชิงลึก (In-Depth Technical Role)</b>", styles["table_header"]),
        ],
        [
            Paragraph("`services/workflow/`", styles["table_cell_code"]),
            Paragraph("<b>Worker & Pipeline Core:</b> จัดการ Run Lease Lock (`worker.py`), รัน Execution Pipeline 5 ขั้นตอน (`pipeline.py`), และ Mapping ผลลัพธ์ (`outcome.py`)", styles["table_cell"]),
        ],
        [
            Paragraph("`services/case_state/`", styles["table_cell_code"]),
            Paragraph("<b>Case State & Mutation:</b> จัดการ Immutable DAG Versions, คำนวณ State Delta จากข้อความใหม่ (`mutator.py`), และแปลง Case State เป็นข้อความค้นหาที่กระชับสำหรับ RAG (`projector.py`)", styles["table_cell"]),
        ],
        [
            Paragraph("`services/extraction/`", styles["table_cell_code"]),
            Paragraph("<b>Structured Extraction:</b> ทำหน้าที่สกัด Entities, Evidence, Timeline, และ Relationships จากข้อความดิบของผู้ใช้ ด้วย JSON Schema Validation และ Entity Normalization", styles["table_cell"]),
        ],
        [
            Paragraph("`services/case_analysis/`", styles["table_cell_code"]),
            Paragraph("<b>Grounded Case Overview:</b> ทำงานร่วมกับ LLM เพื่อสร้างบทวิเคราะห์เชิงเทคนิคที่ Grounded บนข้อมูลจาก GraphRAG และ Case State พร้อมสร้าง Analysis Trace และ Claims", styles["table_cell"]),
        ],
        [
            Paragraph("`services/followup/`", styles["table_cell_code"]),
            Paragraph("<b>Gap Analysis & Clarification Gate:</b> วิเคราะห์ช่องว่างของข้อมูล (IOCs, Timestamps, Vectors) จัดลำดับความสำคัญ (Priority Queue) และตัดสินใจว่าจะถามคำถามเพิ่มเติมหรือจบเคส", styles["table_cell"]),
        ],
        [
            Paragraph("`services/reports/`", styles["table_cell_code"]),
            Paragraph("<b>Deterministic Report & PDF:</b> สร้างรายงาน Markdown และเรนเดอร์เอกสาร PDF ผ่าน ReportLab จาก Snapshot ที่ถูก Freeze ไว้ พร้อมตรวจสอบความถูกต้องของ SHA-256 Hash", styles["table_cell"]),
        ],
        [
            Paragraph("`services/clients/` & `llm/`", styles["table_cell_code"]),
            Paragraph("<b>HTTP Client & Model Registry:</b> จัดการการเชื่อมต่อ HTTP ไปยัง `rag_service` (`rag_client.py`) และระบบ Routing/Fallback ของ OpenRouter โมเดล LLM", styles["table_cell"]),
        ],
    ]
    t_be_svc = Table(be_svc_data, colWidths=[42*mm, PAGE_WIDTH - 36*mm - 42*mm])
    t_be_svc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_be_svc)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("4.2 ขั้นตอนการประมวลผล Background Pipeline (Execution Pipeline Lifecycle)", styles["h2"]))
    story.append(Paragraph(
        "เมื่อฟังก์ชัน `process_chat_run` ใน `services/workflow/pipeline.py` ทำงาน จะผ่านขั้นตอนลำดับดังนี้:",
        styles["body"]
    ))

    pipeline_steps = """
  [Step 1: Claim Lease]      ChatRunWorker ทำการ Claim Lease บน ChatRun ID พร้อมใส่ Worker ID และตั้ง TTL (60s)
           │
           ▼
  [Step 2: Action Branch]    แยก Flow ตาม Post-Answer Action:
           ├─► "initial_query": รัน Baseline Extraction -> สร้าง CaseStateVersion v1 -> ส่ง RAG Query
           ├─► "add_case_info": รัน Delta Extraction -> Apply Delta -> สร้าง CaseStateVersion vN -> ส่ง RAG Query
           └─► "ask": ข้าม Extraction และ RAG -> นำ Case State ปัจจุบัน + Analysis Context มาตอบคำถาม Q&A ทันที
           │
           ▼
  [Step 3: GraphRAG Query]   แปลง Case State เป็น Focused Query -> เรียก POST http://rag_service:8001/query
           │                 -> ได้ MITRE Techniques + Graph Context + Graph Reasoning
           ▼
  [Step 4: Case Overview]    เรียก Case Analysis LLM เพื่อสังเคราะห์ภาพรวมการโจมตี (Overview Narrative)
           │                 พร้อมจับคู่ Evidence และสร้าง Atomic Claims
           ▼
  [Step 5: Followup Gate]    ประเมิน Gap Analysis: มีข้อมูลสำคัญขาดหายหรือไม่?
           ├─► ขาดข้อมูลสำคัญ (Gap Found) -> เปลี่ยนสถานะเป็น "awaiting_followup" + สร้าง Assistant Question
           └─► ข้อมูลครบถ้วน (No Critical Gap) -> เปลี่ยนสถานะเป็น "idle" + คืนคำตอบสมบูรณ์ (Completed Answer)
           │
           ▼
  [Step 6: Persist Outcome]  บันทึก Assistant Message, อัปเดต Thread Status, บันทึก CaseStateVersion, ปลด Run Lease
"""
    story.append(create_code_panel(pipeline_steps, styles))
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 5: GRAPHRAG ARCHITECTURE & RETRIEVAL ENGINE
    # -------------------------------------------------------------
    story.append(Paragraph("5. สถาปัตยกรรม GraphRAG และ Hybrid Retrieval (`rag_service`)", styles["h1"]))
    story.append(Paragraph(
        "`rag_service` เป็นหัวใจสำคัญในการสืบค้นและจับคู่ข่าวกรองภัยคุกคาม โดยผสานพลังระหว่าง <b>Dense Vector Search</b> "
        "และ <b>Graph Knowledge Expansion</b> เข้าด้วยกันอย่างสมบูรณ์แบบ",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))

    rag_arch_data = [
        [
            Paragraph("<b>องค์ประกอบ RAG</b>", styles["table_header"]),
            Paragraph("<b>กลไกและเทคโนโลยีที่ใช้งาน (Technical Mechanism)</b>", styles["table_header"]),
        ],
        [
            Paragraph("<b>Dense Vector Search</b>", styles["table_cell_code"]),
            Paragraph("ใช้โมเดล <b>BAAI/bge-m3</b> (1024-dimensional embeddings, รองรับภาษาไทย-อังกฤษสมบูรณ์) จัดเก็บใน <b>Qdrant Vector Database</b> ทำการค้นหาเชิงความหมายด้วย Cosine Similarity", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Graph Traversal</b>", styles["table_cell_code"]),
            Paragraph("จัดเก็บโครงสร้าง <b>MITRE ATT&CK STIX 2.1</b> ใน <b>Neo4j Graph Database</b> ดึงความสัมพันธ์ระดับ 2-Hop Cypher Query เชื่อมโยง Tactics, Techniques, Sub-techniques, Mitigations, และ Threat Groups", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Reciprocal Rank Fusion</b>", styles["table_cell_code"]),
            Paragraph("ผสานผลลัพธ์จาก Vector Search และ Graph Centrality ด้วยอัลกอริทึม <b>RRF (k=60)</b> เพื่อคัดเลือกเทคนิคที่สอดคล้องกับพฤติกรรมของภัยคุกคามมากที่สุด", styles["table_cell"]),
        ],
        [
            Paragraph("<b>Cross-Encoder Reranker</b>", styles["table_cell_code"]),
            Paragraph("ปรับปรุงลำดับความแม่นยำด้วยโมเดล Reranker `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` ก่อนส่งเข้าสู่ Context Builder", styles["table_cell"]),
        ],
        [
            Paragraph("<b>LangGraph Agentic Loop</b>", styles["table_cell_code"]),
            Paragraph("ควบคุม Flow ด้วย State Machine: แปลงภาษา (Cross-Lingual Thai $\\leftrightarrow$ English), ตรวจสอบความเพียงพอของบริบท (Sufficiency Evaluator), และวนซ้ำขยายการค้นหา (Broaden Search Loop) สูงสุด 2 รอบ", styles["table_cell"]),
        ],
    ]
    t_rag_arch = Table(rag_arch_data, colWidths=[42*mm, PAGE_WIDTH - 36*mm - 42*mm])
    t_rag_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_rag_arch)
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 6: PERSISTENCE & DATABASE SCHEMA
    # -------------------------------------------------------------
    story.append(Paragraph("6. โครงสร้างฐานข้อมูลและการจัดเก็บสถานะ (PostgreSQL Persistence Schema)", styles["h1"]))
    story.append(Paragraph(
        "โครงสร้างตารางใน PostgreSQL ถูกออกแบบตามหลัก Relational Integrity พร้อม Foreign Key Constraints และ Cascading Deletes:",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))

    db_tables_data = [
        [
            Paragraph("<b>ชื่อตาราง (Table Name)</b>", styles["table_header"]),
            Paragraph("<b>Primary Key / Constraints</b>", styles["table_header"]),
            Paragraph("<b>หน้าที่และความหมายของข้อมูล (Description & Schema Role)</b>", styles["table_header"]),
        ],
        [
            Paragraph("`chat_threads`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>Check: status IN ('idle', 'processing', 'awaiting_followup', 'answered', 'failed')", styles["table_cell"]),
            Paragraph("เก็บบทสนทนาหลัก, ชื่อเคส (`title`), สถานะปัจจุบัน, `next_message_ordinal`, และ Foreign Key ชี้ไปยัง `current_case_state_version_id`", styles["table_cell"]),
        ],
        [
            Paragraph("`chat_messages`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>FK: `thread_id` (CASCADE)<br/>Unique: (`thread_id`, `ordinal`)", styles["table_cell"]),
            Paragraph("เก็บข้อความทั้งหมดเรียงตาม `ordinal` พร้อม `role` (`user`, `assistant`, `system`), `content`, และ `metadata_json` (เก็บ Extraction, Gaps, Traces)", styles["table_cell"]),
        ],
        [
            Paragraph("`chat_runs`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>FK: `thread_id` (CASCADE)<br/>Check: status IN ('queued', 'running', 'completed', 'failed')", styles["table_cell"]),
            Paragraph("จัดการงานประมวลผล Background Worker เก็บ `worker_id`, `lease_expires_at`, `operation`, `post_answer_action`, และ Error Details", styles["table_cell"]),
        ],
        [
            Paragraph("`case_state_versions`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>FK: `thread_id` (CASCADE)<br/>Unique: (`thread_id`, `version`)", styles["table_cell"]),
            Paragraph("บันทึกประวัติสถานะเคสแบบ <b>Immutable DAG</b> เก็บ `state_json` (Entities, Evidence, Timeline, Relations), `delta_json`, และ `parent_version_id`", styles["table_cell"]),
        ],
        [
            Paragraph("`chat_reports`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>FK: `thread_id` (CASCADE)<br/>Unique: (`thread_id`, `version_number`)", styles["table_cell"]),
            Paragraph("เก็บรายงานฉบับสมบูรณ์ (Report Snapshot) พร้อม `source_snapshot_hash` (SHA-256), `report_json` (Structured Claims), และ Markdown Content", styles["table_cell"]),
        ],
        [
            Paragraph("`rag_context_snapshots`", styles["table_cell_code"]),
            Paragraph("`id` (UUID)<br/>FK: `thread_id` (CASCADE)", styles["table_cell"]),
            Paragraph("จัดเก็บ Snapshot ของผลลัพธ์การสืบค้นจาก GraphRAG สำหรับการตรวจสอบความสอดคล้องและการทำ Audit", styles["table_cell"]),
        ],
    ]
    t_db = Table(db_tables_data, colWidths=[36*mm, 45*mm, PAGE_WIDTH - 36*mm - 81*mm])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 7: END-TO-END DATA FLOW & API CONTRACTS
    # -------------------------------------------------------------
    story.append(Paragraph("7. สรุป API Contracts และลำดับการส่งข้อมูล (End-to-End Workflow & REST Endpoints)", styles["h1"]))
    story.append(Paragraph(
        "Backend ให้บริการ RESTful API ภายใต้ Prefix `/api/v1/chats` ตามสัญญาข้อตกลง (API Contracts) ดังนี้:",
        styles["body"]
    ))
    story.append(Spacer(1, 3 * mm))

    api_data = [
        [
            Paragraph("<b>Method</b>", styles["table_header"]),
            Paragraph("<b>Endpoint Route</b>", styles["table_header"]),
            Paragraph("<b>Status Code</b>", styles["table_header"]),
            Paragraph("<b>คำอธิบายการทำงาน (Function & Behavior)</b>", styles["table_header"]),
        ],
        [
            Paragraph("`GET`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats`", styles["table_cell"]),
            Paragraph("`200 OK`", styles["table_cell"]),
            Paragraph("เรียกดูรายการ Thread ทั้งหมด เรียงลำดับตาม `updated_at` ล่าสุด", styles["table_cell"]),
        ],
        [
            Paragraph("`POST`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats`", styles["table_cell"]),
            Paragraph("`201 Created`", styles["table_cell"]),
            Paragraph("สร้าง Thread ใหม่ (กำหนดชื่อหรือใช้ค่าเริ่มต้น 'New chat')", styles["table_cell"]),
        ],
        [
            Paragraph("`GET`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}`", styles["table_cell"]),
            Paragraph("`200 OK`", styles["table_cell"]),
            Paragraph("ดึงข้อมูลรายละเอียด Thread, Messages ทั้งหมดตามลำดับ Ordinal, และ Current Case State", styles["table_cell"]),
        ],
        [
            Paragraph("`PATCH`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}`", styles["table_cell"]),
            Paragraph("`200 OK`", styles["table_cell"]),
            Paragraph("แก้ไขข้อมูล Thread เช่น การเปลี่ยนชื่อหัวข้อ (`title`)", styles["table_cell"]),
        ],
        [
            Paragraph("`DELETE`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}`", styles["table_cell"]),
            Paragraph("`204 No Content`", styles["table_cell"]),
            Paragraph("ลบ Thread ถาวร พร้อมลบ Messages, Runs, และ Case States ทั้งหมดด้วย Cascading Delete", styles["table_cell"]),
        ],
        [
            Paragraph("`POST`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}/messages`", styles["table_cell"]),
            Paragraph("`202 Accepted`", styles["table_cell"]),
            Paragraph("รับข้อความใหม่ สร้าง User Message + ChatRun (queued) และเริ่ม Background Processing", styles["table_cell"]),
        ],
        [
            Paragraph("`GET`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}/runs/{run_id}`", styles["table_cell"]),
            Paragraph("`200 OK`", styles["table_cell"]),
            Paragraph("ตรวจสอบสถานะการทำงานของ Run เฉพาะตัว (Polling Target สำหรับ Error Tracking)", styles["table_cell"]),
        ],
        [
            Paragraph("`POST`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}/reports`", styles["table_cell"]),
            Paragraph("`201 Created`", styles["table_cell"]),
            Paragraph("สร้าง Frozen Report Version จากประวัติแชทและ Case State ปัจจุบัน", styles["table_cell"]),
        ],
        [
            Paragraph("`GET`", styles["table_cell_code"]),
            Paragraph("`/api/v1/chats/{thread_id}/reports/{id}/pdf`", styles["table_cell"]),
            Paragraph("`200 OK`", styles["table_cell"]),
            Paragraph("ดาวน์โหลดเอกสารรายงานการสืบสวนรูปแบบ PDF ที่ถูกเรนเดอร์แบบ Deterministic", styles["table_cell"]),
        ],
    ]
    t_api = Table(api_data, colWidths=[18*mm, 52*mm, 24*mm, PAGE_WIDTH - 36*mm - 94*mm])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), _NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, _BORDER),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 5 * mm))

    # -------------------------------------------------------------
    # SECTION 8: DEPLOYMENT & PRODUCTION READINESS
    # -------------------------------------------------------------
    story.append(Paragraph("8. การติดตั้งและการปรับใช้ (Deployment, Configuration & Roadmap)", styles["h1"]))
    story.append(Paragraph(
        "ระบบรองรับการรันผ่าน Docker Compose โดยจัดการความลับ (Secrets) ผ่าน Doppler CLI:",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    
    story.append(Paragraph("• <b>Docker Infrastructure:</b> รันคอนเทนเนอร์ 4 ตัวพร้อมกัน ได้แก่ `postgres` (ฐานข้อมูลสัมพันธ์), `rag-service` (GraphRAG Microservice), `backend` (FastAPI Orchestrator), และ `frontend` (Next.js 15 Web Client)", styles["bullet"]))
    story.append(Paragraph("• <b>Secret Management:</b> ใช้ Doppler ในการควบคุม Environment Variables ทั้งหมด (`DOPPLER_TOKEN`, `OPENROUTER_API_KEY`, `NEO4J_URI`, `QDRANT_HOST`, `DATABASE_URL`)", styles["bullet"]))
    story.append(Paragraph("• <b>Production Roadmap:</b> การพัฒนาสู่ระดับองค์กรในอนาคตจะรวมถึง: การเพิ่ม User Authentication (JWT/OAuth2) และ Multi-tenant Row-level Security, การทำ Trash/Restore สำหรับ Chat Threads, และ Distributed Task Queue (เช่น Celery/Redis) สำหรับ Scale Worker ข้ามโฮสต์", styles["bullet"]))
    story.append(Spacer(1, 6 * mm))

    # Sign-off box
    sign_off = [
        [
            Paragraph("<b>CyberCase Intelligence Framework Technical Architecture Specification</b><br/>"
                      "Document compiled and verified against current active repository codebase.", styles["cover_meta"]),
            Paragraph("<b>Status:</b> STABLE<br/><b>Verified:</b> August 2026", styles["cover_meta"]),
        ]
    ]
    t_sign = Table(sign_off, colWidths=[PAGE_WIDTH - 36*mm - 40*mm, 40*mm])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), _LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, _BORDER),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sign)

    # Build PDF
    doc.build(
        story,
        onFirstPage=lambda c, d: draw_header_footer(c, d, reg, bold),
        onLaterPages=lambda c, d: draw_header_footer(c, d, reg, bold),
    )
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    output_dir = Path("deliverables")
    output_dir.mkdir(exist_ok=True)
    out_file = str(output_dir / "CyberCase_Architecture_Specification_Backend_Frontend.pdf")
    generate_pdf(out_file)
