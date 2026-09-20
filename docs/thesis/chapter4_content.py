"""The text of Chapter 4. Code listings are sliced from the repository."""

from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH

from build_chapter4 import Chapter, commit, source_of

BACKEND = "backend/app/services"


def opening(ch: Chapter) -> None:
    heading = ch.document.add_heading("Chapter 4\nSystem Development", level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    ch.body(
        "This chapter describes how the CyberCase platform is built. Chapter 3 set out what the "
        "system is required to do and why; this chapter presents the code that does it, module by "
        "module, with the reasoning behind each design decision recorded alongside the listing. "
        "Every code figure is extracted directly from the repository when this chapter is "
        f"generated, at commit {commit()}, so the listing shown is the code that was executed for "
        "the experiments reported in Chapter 5."
    )
    ch.body(
        "One term is used consistently throughout. A case source is any material the case is "
        "analysed from: a narrative the investigator typed, the text extracted from an uploaded "
        "document, or an answer given to a follow-up question. The single word source covers all "
        "three, because the system treats them identically and giving them separate names in the "
        "code invited them to drift apart."
    )
    ch.body(
        "The chapter follows the path a case takes through the system. Sections 4.1 and 4.2 "
        "establish the environment and the service boundaries. Section 4.3 covers how material "
        "becomes a source. Sections 4.4 to 4.8 follow one analysis, from the pipeline that runs "
        "it to the report on how well it was grounded. Section 4.9 covers the follow-up question "
        "an analysis leaves behind, 4.10 the report compiler, 4.11 the web interface, and 4.12 "
        "the automated tests that hold the whole thing in place."
    )


def environment(ch: Chapter) -> None:
    ch.heading("4.1 Development Environment and Technology Stack")
    ch.body(
        "The platform is split across three services that run as separate processes and "
        "communicate over HTTP. Table 4-1 lists the technology in each. The split matters for the "
        "research and not only for deployment: the retrieval service is a separate scope of work, "
        "and keeping it behind an HTTP boundary is what allows the backend to be measured with "
        "that service switched off entirely."
    )
    ch.table(
        "Services and their technology",
        ["Service", "Path", "Port", "Technology", "Responsibility"],
        [
            [
                "Frontend",
                "frontend/",
                "3000",
                "Next.js 16, React 19, Tailwind CSS 4, TanStack Query",
                "The investigator workspace",
            ],
            [
                "Backend API",
                "backend/",
                "8000",
                "FastAPI, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL, Alembic",
                "Cases, sources, analysis, chat, reports",
            ],
            [
                "RAG service",
                "rag_service/",
                "8001",
                "FastAPI, LangGraph, Qdrant, Neo4j, BGE-M3",
                "MITRE ATT&CK retrieval, separate scope",
            ],
        ],
    )
    ch.plain(
        "Secrets are supplied by Doppler in deployed environments and by a local .env file during "
        "development. The three services are brought up together with Docker Compose. Neo4j and "
        "Qdrant are cloud-hosted and have no local container."
    )
    ch.document.add_paragraph()


def structure(ch: Chapter) -> None:
    ch.heading("4.2 Backend Structure and Service Boundaries")
    ch.body(
        "The backend is organised so that each layer reaches only the layer below it. Routers "
        "translate HTTP into service calls, and service errors back into status codes. Services "
        "hold the logic. Models describe the tables. No service imports a router, and no code in "
        "the analysis pipeline imports the database session."
    )
    ch.plain("backend/app/", bold=True)
    ch.bullets(
        [
            "routers/ - one file per resource; errors.py turns a service error into an HTTP response",
            "schemas/ - request and response contracts, all declared with extra=forbid",
            "models/ - the SQLAlchemy tables",
            "services/auth/ - sessions, password hashing, the guard every browser request passes",
            "services/document_ingestion/ - upload to text: format routing, parsers, OCR, provenance",
            "services/sources/ - documents, and the one bundle an analysis reads from",
            "services/case_analysis/ - the analysis itself: prompts, provider call, binding, and the gate",
            "services/technical_context/ - the MITRE retrieval a pipeline stage asks for",
            "services/case_workflow/ - running an analysis, and answering a question about one",
            "services/chat/ - the case conversation and the follow-up it carries",
            "services/reports/ - contracts, content, assembly, HTML and PDF rendering",
            "services/llm/ - provider routing and the model registry",
            "services/clients/ - the HTTP client for the RAG service",
        ]
    )
    ch.body(
        "The HTTP surface is small and entirely case-scoped. Table 4-2 lists it in full. An "
        "automated test asserts this exact set of routes, so a route added without being recorded "
        "here fails the suite."
    )
    ch.table(
        "The HTTP API, under the prefix /api/v1",
        ["Method and path", "Purpose"],
        [
            ["GET /health", "Backend and database health"],
            ["POST /auth/register, /auth/login, /auth/logout", "Cookie session lifecycle"],
            ["GET /auth/me, /auth/session", "The signed-in user, required and optional"],
            ["GET, POST /cases", "List and create cases"],
            ["GET, PATCH, DELETE /cases/{case_id}", "Read, rename and delete one case"],
            ["GET, POST /cases/{case_id}/documents", "Upload a document, list what was uploaded"],
            ["GET /cases/{case_id}/documents/{id}/content", "Read a document back"],
            ["GET, POST /cases/{case_id}/sources", "What the case is analysed from"],
            ["GET, POST /cases/{case_id}/analysis", "Read the latest analysis, or run one"],
            ["GET /cases/{case_id}/chat", "The Ask panel transcript"],
            ["POST /cases/{case_id}/chat/messages", "Send a message or answer a question"],
            ["POST, GET /cases/{case_id}/reports", "Generate and list report versions"],
            ["GET /cases/{case_id}/reports/{id}/pdf", "Export a stored report as PDF"],
            ["GET /cases/{case_id}/reports/{id}/html", "Render a stored report as HTML"],
        ],
    )
    ch.body(
        "Every case route is authenticated and ownership-scoped. There is no run resource and no "
        "queue: an analysis happens inside the request that asked for it, and the caller waits "
        "for it. This is a deliberate simplification. A background worker would require a run "
        "table, a polling endpoint, and a reconciliation path for runs that die mid-flight, and "
        "none of that machinery would change what the research measures."
    )


def sources(ch: Chapter) -> None:
    ch.heading("4.3 Case Sources: What an Analysis Reads")
    ch.body(
        "An analysis reads exactly one thing: a bundle of case sources, assembled in one short "
        "transaction and then handed to the pipeline. Material reaches that bundle by two routes. "
        "A narrative typed into the intake form becomes a source directly. An uploaded document is "
        "routed by format, its text extracted, and that text becomes a source."
    )
    ch.plain("4.3.1 Document ingestion and text extraction", bold=True)
    ch.body(
        "A PDF that already carries a text layer is parsed directly, which is both faster and "
        "exact. A scanned PDF has no text layer, so its pages are rendered to images and read by "
        "Typhoon OCR, a vision-language model specialised for Thai documents. Either route "
        "produces text together with provenance: which pages it came from, which extraction "
        "method produced it, and any warnings raised along the way."
    )
    ch.body(
        "That provenance is not documentation. It is what later allows a quotation in the "
        "analysis to be resolved to a page number in the original file, which is the mechanism "
        "described in Section 4.7."
    )
    ch.plain("4.3.2 The source bundle and its revision", bold=True)
    ch.body(
        "Each case carries a source_revision counter that increases whenever its sources change. "
        "The bundle records the revision it was read at, and the analysis result is written back "
        "only if the case is still at that revision. If the investigator uploaded a document "
        "while the analysis was running, the write is refused with a conflict rather than storing "
        "an analysis of material that no longer describes the case."
    )
    ch.code_figure(
        source_of(f"{BACKEND}/case_workflow/analysis.py", "run_case_analysis"),
        "Running one analysis, with the database connection closed while it thinks",
        [
            (("async def run_case_analysis", "continuing_followup: bool = False"), "The signature takes a stage tuple, defaulting to none. An experiment "
                           "passes its own stages here; production passes nothing and gets the "
                           "configured arm."),
            (("Analyse the case and store the result", "starts a chain of its own"), "The docstring records the two properties that matter: the pipeline "
                            "runs with no connection open, and a follow-up continuation inherits "
                            "the rounds already spent."),
            (("stages = stages or analysis_stages()",), "The arm is resolved here, at call time, so the setting in force when the "
                        "analysis runs is the arm that runs."),
            (("started = await read_case_for_analysis",), "One short transaction reads the case and its sources, then releases the "
                        "connection. Holding a connection across a model call that takes tens of "
                        "seconds would exhaust the pool under any real load."),
            (("artifacts = await run_pipeline", "            stages,"), "The pipeline runs. Only AnalysisInput crosses this boundary, which is "
                            "why the same call works over a dataset row."),
            (("except CaseAnalysisFailure", "raise CaseWorkflowError"), "A failure inside the pipeline becomes a workflow error carrying its "
                            "code, so the router can map it to a status without matching on text."),
            (("return await store_analysis",), "A second short transaction writes the result, subject to the revision "
                            "check described above."),
        ],
    )
