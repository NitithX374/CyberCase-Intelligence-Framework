# CyberCase File and Function Index

Generated `2026-08-31T05:20:19+00:00` from branch `main` at commit `58f2302`; working tree dirty: `yes`.

This is the exhaustive first-party source inventory for the checkout. Descriptions generated from code names are navigation aids; runtime truth is determined by imports, route registration, and the handover guide.
Coverage: **436 source files** and **2305 named symbols**.


## Database Migration Layer

### [`backend/alembic/baseline_versions/0001_raw_evidence_chat.py`](../../backend/alembic/baseline_versions/0001_raw_evidence_chat.py)

Purpose: Create the raw-evidence chat schema.

- L19 `def upgrade() -> None` — Implements upgrade.
- L138 `def downgrade() -> None` — Implements downgrade.

### [`backend/alembic/env.py`](../../backend/alembic/env.py)

Purpose: Owns env behavior for the database migration layer.

- L26 `def run_migrations_offline() -> None` — Run migrations in 'offline' mode.
- L41 `def do_run_migrations(connection) -> None` — Implements do run migrations.
- L48 `async def run_migrations_online() -> None` — Run migrations in 'online' mode.

## Backend Runtime

### [`backend/app/__init__.py`](../../backend/app/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/config.py`](../../backend/app/config.py)

Purpose: Application configuration — loaded from environment / .env file.

- L12 `class Settings(BaseSettings)` — All configuration values are read from environment variables.
- L35 `def async_database_url(self) -> str` — Ensures the URL uses postgresql+asyncpg:// for SQLAlchemy async engine.
- L65 `def cors_origins_list(self) -> list[str]` — Implements cors origins list.

### [`backend/app/database.py`](../../backend/app/database.py)

Purpose: Owns database behavior for the backend runtime.

- L34 `class Base(DeclarativeBase)` — Encapsulates base.
- L39 `async def get_db()` — Yield an async DB session for FastAPI dependency injection.

### [`backend/app/main.py`](../../backend/app/main.py)

Purpose: FastAPI application for chat APIs and document ingestion preview.

- L14 `async def lifespan(app: FastAPI)` — Startup / shutdown lifecycle.

### [`backend/app/models/__init__.py`](../../backend/app/models/__init__.py)

Purpose: Register the raw-evidence chat, retrieval, and report ORM models.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/models/chat.py`](../../backend/app/models/chat.py)

Purpose: Persistent chat threads, messages, and background processing runs.

- L33 `class ChatThread(Base)` — Encapsulates chatthread.
- L101 `class ChatMessage(Base)` — Encapsulates chatmessage.
- L166 `class ChatRun(Base)` — Encapsulates chatrun.

### [`backend/app/models/rag_context.py`](../../backend/app/models/rag_context.py)

Purpose: Durable retrieval context bound one-to-one to the chat run that produced it.

- L24 `class RagContext(Base)` — Encapsulates ragcontext.

### [`backend/app/models/report.py`](../../backend/app/models/report.py)

Purpose: Immutable report history scoped to a persisted chat thread.

- L29 `class ChatReport(Base)` — Encapsulates chatreport.

### [`backend/app/routers/__init__.py`](../../backend/app/routers/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/routers/chat.py`](../../backend/app/routers/chat.py)

Purpose: Chat thread, message, and report HTTP endpoints.

- L40 `async def list_chat_threads(db: AsyncSession=Depends(get_db))` — Lists chat threads.
- L52 `async def get_chat_thread(thread_id: UUID, db: AsyncSession=Depends(get_db))` — Retrieves chat thread.
- L65 `async def create_chat_thread(request: ChatThreadCreate, db: AsyncSession=Depends(get_db))` — Creates chat thread.
- L78 `async def update_chat_thread(thread_id: UUID, request: ChatThreadUpdate, db: AsyncSession=Depends(get_db))` — Updates chat thread.
- L91 `async def delete_chat_thread(thread_id: UUID, db: AsyncSession=Depends(get_db)) -> Response` — Removes chat thread.
- L108 `async def create_chat_message(thread_id: UUID, request: ChatMessageCreate, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db))` — Creates chat message.
- L128 `async def get_chat_run(thread_id: UUID, run_id: UUID, db: AsyncSession=Depends(get_db))` — Retrieves chat run.
- L140 `def _report_http_exception(error: ReportGenerationError) -> HTTPException` — Implements report http exception.
- L157 `async def generate_chat_report(thread_id: UUID, request: ChatReportCreate, db: AsyncSession=Depends(get_db))` — Generates chat report.
- L174 `async def list_chat_reports(thread_id: UUID, db: AsyncSession=Depends(get_db))` — Lists chat reports.
- L190 `async def get_chat_report(thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db))` — Retrieves chat report.
- L207 `async def download_chat_report_pdf(thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db))` — Implements download chat report pdf.

### [`backend/app/routers/document_ingestion.py`](../../backend/app/routers/document_ingestion.py)

Purpose: Owns document ingestion behavior for the backend runtime.

- L24 `def _build_recognizer() -> DocumentRecognizer` — Builds recognizer.
- L40 `def _build_region_pipeline(recognizer) -> RegionRecognitionPipeline` — Builds region pipeline.
- L53 `def _build_service() -> DocumentIngestionService` — Builds service.
- L68 `async def _read_limited(upload: UploadFile, max_bytes: int) -> bytes` — Retrieves limited.
- L90 `async def preview_document_ingestion(file: UploadFile=File(...), mode: IngestionMode=Query(default=IngestionMode.UNIFIED), segmentation: bool | None=Query(default=None)) -> IngestedDocument` — Implements preview document ingestion.

### [`backend/app/routers/health.py`](../../backend/app/routers/health.py)

Purpose: Health-check router.

- L14 `async def health_check(db: AsyncSession=Depends(get_db))` — Returns service health and database connectivity status.

### [`backend/app/schemas/__init__.py`](../../backend/app/schemas/__init__.py)

Purpose: Pydantic request and response schemas for all API domains.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/schemas/chat.py`](../../backend/app/schemas/chat.py)

Purpose: Chat Thread, Message, and Run API schemas.

- L28 `class ChatThreadCreate(BaseModel)` — Encapsulates chatthreadcreate.
- L36 `class ChatThreadUpdate(BaseModel)` — Encapsulates chatthreadupdate.
- L43 `class ChatMessageCreate(BaseModel)` — Encapsulates chatmessagecreate.
- L52 `class ChatThreadRead(BaseModel)` — Encapsulates chatthreadread.
- L62 `class ChatMessageRead(BaseModel)` — Encapsulates chatmessageread.
- L75 `class ChatThreadDetail(ChatThreadRead)` — Encapsulates chatthreaddetail.
- L79 `class ChatRunRead(BaseModel)` — Encapsulates chatrunread.
- L92 `class ChatMessageAccepted(BaseModel)` — Encapsulates chatmessageaccepted.

### [`backend/app/schemas/rag.py`](../../backend/app/schemas/rag.py)

Purpose: Owns rag behavior for the backend runtime.

- L8 `class RagQueryRequest(BaseModel)` — Encapsulates ragqueryrequest.
- L15 `class QueryRequest(RagQueryRequest)` — Encapsulates queryrequest.
- L19 `class MitreTableRow(BaseModel)` — One entry of the MITRE mapping table produced by the RAG service.
- L35 `class QueryResponse(BaseModel)` — Encapsulates queryresponse.
- L45 `def normalize_empty_retrieval_context_id(cls, value: Any) -> Any` — Treat the RAG service's empty-string sentinel as no frozen context.

### [`backend/app/schemas/reports.py`](../../backend/app/schemas/reports.py)

Purpose: Typed report output and chat-report API contracts.

- L63 `class ReportClaim(BaseModel)` — Encapsulates reportclaim.
- L74 `class ReportSection(BaseModel)` — Encapsulates reportsection.
- L83 `class StructuredReport(BaseModel)` — Encapsulates structuredreport.
- L94 `class ChatReportCreate(BaseModel)` — Encapsulates chatreportcreate.
- L101 `def normalize_idempotency_key(cls, value: str | None) -> str | None` — Normalizes idempotency key.
- L108 `class ChatReportRead(BaseModel)` — Encapsulates chatreportread.

### [`backend/app/services/__init__.py`](../../backend/app/services/__init__.py)

Purpose: Backend domain services.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/case_analysis/__init__.py`](../../backend/app/services/case_analysis/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/case_analysis/case_analysis_executor.py`](../../backend/app/services/case_analysis/case_analysis_executor.py)

Purpose: Owns case analysis executor behavior for the backend runtime.

- L33 `class MainCaseAnalysisService` — Run internal analysis without retrieval, persistence, or state mutation.
- L36 `def __init__(self, *, client: httpx.AsyncClient | None=None) -> None` — Implements init.
- L39 `async def analyze(self, *, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object) -> CaseAnalysisResult` — Analyze defensive snapshots of Case Narrative and retrieval context.
- L131 `async def _post(client: httpx.AsyncClient, messages_url: str, headers: dict[str, str], request_payload: dict[str, object]) -> httpx.Response` — Implements post.
- L155 `async def request_case_analysis(*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object, client: httpx.AsyncClient | None=None) -> CaseAnalysisResult` — Implements request case analysis.

### [`backend/app/services/case_analysis/case_analysis_prompt_builder.py`](../../backend/app/services/case_analysis/case_analysis_prompt_builder.py)

Purpose: Owns case analysis prompt builder behavior for the backend runtime.

- L18 `def build_case_analysis_prompt(*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, response_language: ResponseLanguage) -> str` — Builds case analysis prompt.
- L54 `def _validate_analysis_request(mode: object, question: object) -> tuple[AnalysisMode, str | None]` — Validates analysis request.
- L78 `def _bounded_json(payload: dict[str, object], maximum: int) -> str` — Implements bounded json.
- L113 `def _separate_analysis_context(analysis_context: dict[str, object] | None) -> tuple[list[str], dict[str, object] | None]` — Implements separate analysis context.
- L146 `def _dump(value: object) -> str` — Implements dump.

### [`backend/app/services/case_analysis/case_analysis_prompt_config.py`](../../backend/app/services/case_analysis/case_analysis_prompt_config.py)

Purpose: Owns case analysis prompt config behavior for the backend runtime.

- L61 `class CaseAnalysisFailure(Exception)` — Encapsulates caseanalysisfailure.
- L62 `def __init__(self, code: str, message: str) -> None` — Implements init.

### [`backend/app/services/case_analysis/case_analysis_response_parser.py`](../../backend/app/services/case_analysis/case_analysis_response_parser.py)

Purpose: Owns case analysis response parser behavior for the backend runtime.

- L39 `def _normalize_raw_analysis_ids(raw_analysis: dict[str, object]) -> None` — Normalizes raw analysis ids.
- L109 `def parse_case_analysis_response(response: httpx.Response, *, source_message_ids: set[str], analysis_context: Mapping[str, object], analysis_mode: AnalysisMode, evidence_sha256: str) -> CaseAnalysisResult` — Parses case analysis response.
- L204 `def _validated_response_payload(response: httpx.Response) -> dict[str, object]` — Implements validated response payload.
- L247 `def _retrieval_context_id(analysis_context: Mapping[str, object]) -> str | None` — Implements retrieval context id.

### [`backend/app/services/case_analysis/case_analysis_response_utils.py`](../../backend/app/services/case_analysis/case_analysis_response_utils.py)

Purpose: Owns case analysis response utils behavior for the backend runtime.

- L10 `def _extract_visible_text(payload: Mapping[str, object]) -> str` — Extract visible assistant text across supported provider response shapes.
- L36 `def _extract_text_value(value: object) -> str` — Extracts text value.
- L65 `def _log_response_shape(status_code: int, payload: Mapping[str, object]) -> None` — Log provider shape metadata without logging prompts or answer text.

### [`backend/app/services/case_analysis/compatibility.py`](../../backend/app/services/case_analysis/compatibility.py)

Purpose: Owns compatibility behavior for the backend runtime.

- L16 `def read_analysis_trace(payload: object) -> ReadableAnalysisTrace` — Retrieves analysis trace.

### [`backend/app/services/case_analysis/contracts.py`](../../backend/app/services/case_analysis/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L32 `class AnalysisClaim(BaseModel)` — Encapsulates analysisclaim.
- L43 `def normalize_text(cls, value: str) -> str` — Normalizes text.
- L48 `def unique_source_ids(cls, value: list[str]) -> list[str]` — Implements unique source ids.
- L57 `class MitreAssociation(BaseModel)` — Encapsulates mitreassociation.
- L68 `class AnalysisClaimV3(BaseModel)` — Encapsulates analysisclaimv3.
- L85 `def normalize_optional_text(cls, value: str | None) -> str | None` — Normalizes optional text.
- L97 `def unique_evidence_source_ids(cls, value: list[str]) -> list[str]` — Implements unique evidence source ids.
- L106 `class AnalysisGapV3(BaseModel)` — Encapsulates analysisgapv3.
- L120 `def normalize_gap_text(cls, value: str) -> str` — Normalizes gap text.
- L128 `def unique_affected_claim_ids(cls, value: list[str]) -> list[str]` — Implements unique affected claim ids.
- L137 `class AnalysisTraceV3(BaseModel)` — Encapsulates analysistracev3.
- L154 `def normalize_summary(cls, value: str) -> str` — Normalizes summary.
- L161 `class ProviderAnalysisClaimV3(AnalysisClaimV3)` — Encapsulates provideranalysisclaimv3.
- L165 `class ProviderMitreAssociation(MitreAssociation)` — Encapsulates providermitreassociation.
- L169 `class ProviderCaseAnalysisV3(BaseModel)` — Encapsulates providercaseanalysisv3.
- L182 `class ProviderCaseAnalysis(BaseModel)` — Encapsulates providercaseanalysis.
- L191 `class AnalysisTraceDraft(BaseModel)` — Encapsulates analysistracedraft.
- L201 `class AnalysisTrace(AnalysisTraceDraft)` — Encapsulates analysistrace.
- L206 `class AnalysisTraceFailureMetadata(BaseModel)` — Encapsulates analysistracefailuremetadata.
- L214 `class AnalysisTraceV3FailureMetadata(BaseModel)` — Encapsulates analysistracev3failuremetadata.
- L227 `class CaseAnalysisResult` — Encapsulates caseanalysisresult.

### [`backend/app/services/case_analysis/gap_assembly.py`](../../backend/app/services/case_analysis/gap_assembly.py)

Purpose: Owns gap assembly behavior for the backend runtime.

- L46 `def assemble_claim_linked_gaps(trace: AnalysisTraceV3, gap_analysis: GapAnalysis, *, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3` — Builds claim linked gaps.
- L79 `def enrich_case_analysis_result(result: CaseAnalysisResult, gap_analysis: GapAnalysis | None, *, source_message_ids: set[str], mitre_table: object=None) -> CaseAnalysisResult` — Implements enrich case analysis result.
- L115 `def _affected_claim_ids(gap: GapItem, claims: list[AnalysisClaimV3]) -> list[str]` — Implements affected claim ids.
- L134 `def _claim_linking_text(claim: AnalysisClaimV3) -> str` — Implements claim linking text.
- L141 `def _text_matches(gap_text: str, gap_tokens: set[str], claim_text: str) -> bool` — Implements text matches.
- L153 `def _normalized_text(value: str) -> str` — Implements normalized text.
- L158 `def _tokens(value: str) -> set[str]` — Implements tokens.
- L166 `def _validate_unchanged_trace_bindings(original: AnalysisTraceV3, enriched: AnalysisTraceV3) -> None` — Validates unchanged trace bindings.

### [`backend/app/services/case_analysis/mitre_applicability_contracts.py`](../../backend/app/services/case_analysis/mitre_applicability_contracts.py)

Purpose: Owns mitre applicability contracts behavior for the backend runtime.

- L12 `class ProviderMitreApplicability(BaseModel)` — Encapsulates providermitreapplicability.
- L21 `def normalize_source_ids(cls, value: list[str]) -> list[str]` — Normalizes source ids.
- L31 `def normalize_trigger_text(cls, value: list[str]) -> list[str]` — Normalizes trigger text.
- L40 `class MitreApplicabilityRecord(BaseModel)` — Encapsulates mitreapplicabilityrecord.
- L50 `def validate_routing_record(self) -> 'MitreApplicabilityRecord'` — Validates routing record.
- L60 `def skipped_mitre_applicability(failure_code: str | None=None) -> MitreApplicabilityRecord` — Implements skipped mitre applicability.

### [`backend/app/services/case_analysis/mitre_applicability_gate.py`](../../backend/app/services/case_analysis/mitre_applicability_gate.py)

Purpose: Owns mitre applicability gate behavior for the backend runtime.

- L38 `class MitreApplicabilityFailure(Exception)` — Encapsulates mitreapplicabilityfailure.
- L39 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L44 `class MitreApplicabilityGate` — Encapsulates mitreapplicabilitygate.
- L45 `def __init__(self, *, client: httpx.AsyncClient | None=None) -> None` — Implements init.
- L48 `async def evaluate(self, evidence_sources: Sequence[RawEvidenceSource]) -> MitreApplicabilityRecord` — Implements evaluate.
- L101 `async def _post(client: httpx.AsyncClient, url: str, headers: dict[str, str], payload: dict[str, object]) -> httpx.Response` — Implements post.
- L121 `async def evaluate_mitre_applicability(*, source_run_id: UUID, evidence_sources: Sequence[RawEvidenceSource], gate: MitreApplicabilityGate | None=None) -> MitreApplicabilityRecord` — Implements evaluate mitre applicability.
- L152 `def _parse_provider_response(response: httpx.Response) -> dict[str, object]` — Parses provider response.

### [`backend/app/services/case_analysis/mitre_applicability_prompt.py`](../../backend/app/services/case_analysis/mitre_applicability_prompt.py)

Purpose: Owns mitre applicability prompt behavior for the backend runtime.

- L63 `def build_mitre_applicability_prompt(evidence_sources: Sequence[RawEvidenceSource]) -> str` — Builds mitre applicability prompt.

### [`backend/app/services/case_analysis/mitre_applicability_validation.py`](../../backend/app/services/case_analysis/mitre_applicability_validation.py)

Purpose: Owns mitre applicability validation behavior for the backend runtime.

- L16 `def validate_mitre_applicability(payload: object, evidence_sources: Sequence[RawEvidenceSource]) -> MitreApplicabilityRecord` — Validates mitre applicability.
- L57 `def _normalize(value: str) -> str` — Normalizes normalize.

### [`backend/app/services/case_analysis/personalization.py`](../../backend/app/services/case_analysis/personalization.py)

Purpose: Owns personalization behavior for the backend runtime.

- L8 `def validate_response_language(value: object) -> ResponseLanguage` — Validates response language.
- L16 `def resolve_response_language(user_message: object) -> ResponseLanguage` — Implements resolve response language.

### [`backend/app/services/case_analysis/state_selector.py`](../../backend/app/services/case_analysis/state_selector.py)

Purpose: Owns state selector behavior for the backend runtime.

- L19 `class CanonicalCaseAnalysisState` — Encapsulates canonicalcaseanalysisstate.
- L24 `def validate_canonical_case_overview_trace(trace: AnalysisTraceV3, *, evidence_sha256: str, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3 | None` — Validates canonical case overview trace.
- L45 `def select_latest_canonical_case_overview(messages: Sequence[ChatMessage], *, evidence_sha256: str, source_message_ids: set[str]) -> CanonicalCaseAnalysisState | None` — Extracts latest canonical case overview.

### [`backend/app/services/case_analysis/validation.py`](../../backend/app/services/case_analysis/validation.py)

Purpose: Owns validation behavior for the backend runtime.

- L13 `class AnalysisTraceStructureError(ValueError)` — Encapsulates analysistracestructureerror.
- L14 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L19 `class AnalysisTraceProvenanceError(ValueError)` — Encapsulates analysistraceprovenanceerror.
- L20 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L25 `def validate_analysis_trace(analysis: ProviderCaseAnalysis, *, source_message_ids: set[str], mitre_table: object, analysis_mode: AnalysisMode) -> AnalysisTraceDraft` — Validates analysis trace.
- L68 `def validate_analysis_trace_v3(analysis: AnalysisTraceV3, *, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3` — Validates analysis trace v3.
- L154 `def detect_forbidden_provenance(raw_payload: object) -> None` — Implements detect forbidden provenance.
- L169 `def _admitted_technique_ids(value: object) -> set[str]` — Implements admitted technique ids.
- L183 `def _contains_key(value: object, forbidden: set[str]) -> bool` — Implements contains key.

### [`backend/app/services/chat/__init__.py`](../../backend/app/services/chat/__init__.py)

Purpose: Chat Thread and Message Domain Services.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/chat/chat_management.py`](../../backend/app/services/chat/chat_management.py)

Purpose: Owns chat management behavior for the backend runtime.

- L10 `class ChatService` — Encapsulates chatservice.
- L11 `def __init__(self, db: AsyncSession)` — Implements init.
- L14 `async def create_thread(self, request: ChatThreadCreate) -> ChatThread` — Creates thread.
- L26 `async def update_thread(self, thread_id: UUID, request: ChatThreadUpdate) -> ChatThread` — Updates thread.
- L44 `async def delete_thread(self, thread_id: UUID) -> None` — Removes thread.
- L60 `async def list_threads(self) -> list[ChatThread]` — Lists threads.
- L67 `async def get_thread(self, thread_id: UUID) -> ChatThread` — Retrieves thread.

### [`backend/app/services/chat/chat_message.py`](../../backend/app/services/chat/chat_message.py)

Purpose: Owns chat message behavior for the backend runtime.

- L16 `class ChatMessageService` — Encapsulates chatmessageservice.
- L17 `def __init__(self, db: AsyncSession)` — Implements init.
- L20 `async def create_message_and_run(self, thread_id: UUID, request: ChatMessageCreate) -> tuple[ChatMessage, ChatRun]` — Creates message and run.
- L27 `async def get_run(self, thread_id: UUID, run_id: UUID) -> ChatRun` — Retrieves run.
- L44 `async def list_messages(self, thread_id: UUID) -> list[ChatMessageRead]` — Lists messages.

### [`backend/app/services/chat/chat_run_creation.py`](../../backend/app/services/chat/chat_run_creation.py)

Purpose: Owns chat run creation behavior for the backend runtime.

- L16 `async def create_message_and_run(db: AsyncSession, thread_id: UUID, request: ChatMessageCreate) -> tuple[ChatMessage, ChatRun]` — Creates message and run.
- L67 `def _fingerprint(request: ChatMessageCreate) -> str` — Implements fingerprint.
- L72 `async def _locked_thread(db: AsyncSession, thread_id: UUID) -> ChatThread` — Implements locked thread.
- L82 `async def _existing_run(db: AsyncSession, thread_id: UUID, request: ChatMessageCreate, fingerprint: str) -> tuple[ChatMessage, ChatRun] | None` — Implements existing run.
- L108 `async def _ensure_no_active_run(db: AsyncSession, thread_id: UUID) -> None` — Implements ensure no active run.
- L122 `def _resolve_action(thread: ChatThread, requested_action: str | None) -> tuple[str, str]` — Implements resolve action.
- L150 `async def _followup_position(db: AsyncSession, thread: ChatThread, pending_answer: str, ordinal: int) -> tuple[int, int, dict[str, str] | None]` — Implements followup position.

### [`backend/app/services/chat/clarification_chain.py`](../../backend/app/services/chat/clarification_chain.py)

Purpose: Owns clarification chain behavior for the backend runtime.

- L9 `class ClarificationChain` — Encapsulates clarificationchain.
- L17 `def _followup_root_ordinal(message: ChatMessage) -> int | None` — Implements followup root ordinal.
- L34 `def _is_clarification_message(message: ChatMessage) -> bool` — Determines clarification message.
- L42 `def _is_terminal_assistant_message(message: ChatMessage) -> bool` — Determines terminal assistant message.
- L53 `def _followup_context(message: ChatMessage) -> dict[str, str]` — Implements followup context.
- L66 `def _answer_context(message: ChatMessage | None) -> dict[str, str]` — Implements answer context.
- L86 `def _exchange(question: ChatMessage, answer: str, answer_message: ChatMessage | None) -> ClarificationExchange` — Implements exchange.
- L109 `def reconstruct_clarification_chain(messages: Sequence[ChatMessage], *, root_ordinal: int | None=None, pending_answer: str | None=None) -> ClarificationChain | None` — Implements reconstruct clarification chain.

### [`backend/app/services/chat/raw_evidence.py`](../../backend/app/services/chat/raw_evidence.py)

Purpose: Owns raw evidence behavior for the backend runtime.

- L14 `class RawEvidenceSource` — Encapsulates rawevidencesource.
- L20 `class RawEvidenceSnapshot` — Encapsulates rawevidencesnapshot.
- L26 `def source_message_ids(self) -> tuple[UUID, ...]` — Implements source message ids.
- L30 `def build_raw_evidence_snapshot(messages: list[ChatMessage]) -> RawEvidenceSnapshot` — Builds raw evidence snapshot.
- L64 `async def load_raw_evidence_snapshot(db: AsyncSession, *, thread_id: UUID, through_ordinal: int | None=None) -> RawEvidenceSnapshot` — Retrieves raw evidence snapshot.

### [`backend/app/services/clients/__init__.py`](../../backend/app/services/clients/__init__.py)

Purpose: External Service Clients.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/clients/rag_client.py`](../../backend/app/services/clients/rag_client.py)

Purpose: Typed HTTP boundary for chat requests to the RAG service.

- L15 `class RagCallFailure(Exception)` — A safe, stable failure that may be persisted on a chat run.
- L18 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L24 `async def request_rag(content: str, *, client: httpx.AsyncClient | None=None) -> QueryResponse` — Call only the current completed-response RAG query boundary.
- L40 `async def _post_and_validate(client: httpx.AsyncClient, url: str, payload: dict[str, object]) -> QueryResponse` — Implements post and validate.

### [`backend/app/services/document_ingestion/__init__.py`](../../backend/app/services/document_ingestion/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/contracts.py`](../../backend/app/services/document_ingestion/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L6 `class IngestionMode(StrEnum)` — Encapsulates ingestionmode.
- L11 `class ExtractionMethod(StrEnum)` — Encapsulates extractionmethod.
- L18 `class SourceType(StrEnum)` — Encapsulates sourcetype.
- L26 `class RegionType(StrEnum)` — Encapsulates regiontype.
- L36 `class RecognitionMethod(StrEnum)` — Encapsulates recognitionmethod.
- L44 `class VerificationStatus(StrEnum)` — Encapsulates verificationstatus.
- L52 `class ContentRole(StrEnum)` — Encapsulates contentrole.
- L58 `class BoundingBox(BaseModel)` — Encapsulates boundingbox.
- L65 `class DocumentBlock(BaseModel)` — Encapsulates documentblock.
- L73 `class RecognizedContent(BaseModel)` — Encapsulates recognizedcontent.
- L79 `class RecognitionCandidate(BaseModel)` — Encapsulates recognitioncandidate.
- L88 `class DocumentRegion(BaseModel)` — Encapsulates documentregion.
- L106 `class RoutingSummary(BaseModel)` — Encapsulates routingsummary.
- L115 `class DocumentPage(BaseModel)` — Encapsulates documentpage.
- L125 `class IngestedDocument(BaseModel)` — Encapsulates ingesteddocument.

### [`backend/app/services/document_ingestion/detection.py`](../../backend/app/services/document_ingestion/detection.py)

Purpose: Owns detection behavior for the backend runtime.

- L9 `class DocumentKind(StrEnum)` — Encapsulates documentkind.
- L17 `class DetectedDocument` — Encapsulates detecteddocument.
- L22 `def _is_docx(content: bytes) -> bool` — Determines docx.
- L30 `def detect_document(content: bytes) -> DetectedDocument` — Implements detect document.

### [`backend/app/services/document_ingestion/errors.py`](../../backend/app/services/document_ingestion/errors.py)

Purpose: Owns errors behavior for the backend runtime.

- L1 `class DocumentIngestionError(Exception)` — Encapsulates documentingestionerror.
- L2 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L8 `class UnsupportedDocumentError(DocumentIngestionError)` — Encapsulates unsupporteddocumenterror.
- L9 `def __init__(self, message: str) -> None` — Implements init.
- L13 `class DocumentLimitError(DocumentIngestionError)` — Encapsulates documentlimiterror.
- L14 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L18 `class InvalidDocumentError(DocumentIngestionError)` — Encapsulates invaliddocumenterror.
- L19 `def __init__(self, message: str) -> None` — Implements init.
- L23 `class DocumentRecognitionError(Exception)` — Encapsulates documentrecognitionerror.
- L27 `class RecognitionConfigurationError(DocumentRecognitionError)` — Encapsulates recognitionconfigurationerror.
- L31 `class RecognitionTimeoutError(DocumentRecognitionError)` — Encapsulates recognitiontimeouterror.
- L35 `class RecognitionProviderError(DocumentRecognitionError)` — Encapsulates recognitionprovidererror.
- L39 `class RecognitionResponseError(DocumentRecognitionError)` — Encapsulates recognitionresponseerror.
- L43 `class DocumentSegmentationError(Exception)` — Encapsulates documentsegmentationerror.
- L47 `class SegmentationConfigurationError(DocumentSegmentationError)` — Encapsulates segmentationconfigurationerror.
- L51 `class SegmentationTimeoutError(DocumentSegmentationError)` — Encapsulates segmentationtimeouterror.
- L55 `class SegmentationProviderError(DocumentSegmentationError)` — Encapsulates segmentationprovidererror.
- L59 `class SegmentationResponseError(DocumentSegmentationError)` — Encapsulates segmentationresponseerror.

### [`backend/app/services/document_ingestion/evaluation/__init__.py`](../../backend/app/services/document_ingestion/evaluation/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/evaluation/metrics.py`](../../backend/app/services/document_ingestion/evaluation/metrics.py)

Purpose: Owns metrics behavior for the backend runtime.

- L16 `def _edit_distance(reference: list[str], prediction: list[str]) -> int` — Implements edit distance.
- L33 `def character_error_rate(ground_truth: str, prediction: str) -> float` — Implements character error rate.
- L39 `def word_error_rate(ground_truth: str, prediction: str) -> float` — Implements word error rate.
- L47 `def _expanded_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]` — Implements expanded samples.
- L59 `def _critical_field_scores(sample: dict[str, Any]) -> dict[str, float]` — Implements critical field scores.
- L71 `def _score_sample(sample: dict[str, Any]) -> dict[str, Any]` — Implements score sample.
- L95 `def _average(rows: list[dict[str, Any]]) -> dict[str, Any]` — Implements average.
- L129 `def evaluate(samples: list[dict[str, Any]]) -> dict[str, Any]` — Implements evaluate.

### [`backend/app/services/document_ingestion/merge/__init__.py`](../../backend/app/services/document_ingestion/merge/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/merge/reading_order.py`](../../backend/app/services/document_ingestion/merge/reading_order.py)

Purpose: Owns reading order behavior for the backend runtime.

- L4 `def order_regions(regions: list[DocumentRegion]) -> list[DocumentRegion]` — Implements order regions.
- L15 `def merge_region_text(regions: list[DocumentRegion]) -> str` — Implements merge region text.

### [`backend/app/services/document_ingestion/parsers/__init__.py`](../../backend/app/services/document_ingestion/parsers/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/parsers/docx_parser.py`](../../backend/app/services/document_ingestion/parsers/docx_parser.py)

Purpose: Owns docx parser behavior for the backend runtime.

- L22 `def _iter_document_blocks(document: DocumentObject)` — Implements iter document blocks.
- L30 `def _table_text(table: Table) -> str` — Implements table text.
- L39 `def parse_docx(content: bytes, document_id: str) -> tuple[list[DocumentPage], list[str]]` — Parses docx.

### [`backend/app/services/document_ingestion/parsers/pdf_text_parser.py`](../../backend/app/services/document_ingestion/parsers/pdf_text_parser.py)

Purpose: Owns pdf text parser behavior for the backend runtime.

- L15 `class NativeTextPolicy` — Encapsulates nativetextpolicy.
- L24 `class PdfPageInspection` — Encapsulates pdfpageinspection.
- L32 `class PdfInspection` — Encapsulates pdfinspection.
- L37 `def _normalize_text(text: str) -> str` — Normalizes text.
- L42 `def split_native_blocks(text: str) -> list[str]` — Implements split native blocks.
- L46 `def _is_printable(character: str) -> bool` — Determines printable.
- L50 `def _is_meaningful(character: str) -> bool` — Determines meaningful.
- L55 `def _has_usable_text(text: str, width: float, height: float, policy: NativeTextPolicy) -> bool` — Determines usable text.
- L80 `def inspect_pdf(content: bytes, policy: NativeTextPolicy, max_pages: int) -> PdfInspection` — Implements inspect pdf.

### [`backend/app/services/document_ingestion/provenance.py`](../../backend/app/services/document_ingestion/provenance.py)

Purpose: Owns provenance behavior for the backend runtime.

- L14 `def build_document_id(content: bytes) -> str` — Builds document id.
- L19 `def build_block_id(document_id: str, page_number: int, block_number: int) -> str` — Builds block id.
- L23 `def build_region_id(document_id: str, page_number: int, region_number: int) -> str` — Builds region id.
- L27 `def build_blocks(document_id: str, page_number: int, texts: list[str], source_type: SourceType) -> list[DocumentBlock]` — Builds blocks.
- L44 `def build_native_regions(document_id: str, page_number: int, texts: list[str]) -> list[DocumentRegion]` — Builds native regions.

### [`backend/app/services/document_ingestion/recognition/__init__.py`](../../backend/app/services/document_ingestion/recognition/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/recognition/base.py`](../../backend/app/services/document_ingestion/recognition/base.py)

Purpose: Owns base behavior for the backend runtime.

- L14 `class RenderedPage` — Encapsulates renderedpage.
- L22 `class RecognizedPage` — Encapsulates recognizedpage.
- L34 `class RenderedRegion` — Encapsulates renderedregion.
- L43 `class RecognitionResult` — Encapsulates recognitionresult.
- L55 `class DocumentRecognizer(Protocol)` — Encapsulates documentrecognizer.
- L56 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page.
- L59 `class OCRRecognizer(Protocol)` — Encapsulates ocrrecognizer.
- L60 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize.
- L63 `class HTRRecognizer(Protocol)` — Encapsulates htrrecognizer.
- L64 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize.

### [`backend/app/services/document_ingestion/recognition/content_filter.py`](../../backend/app/services/document_ingestion/recognition/content_filter.py)

Purpose: Owns content filter behavior for the backend runtime.

- L9 `def separate_generated_visual_descriptions(text: str) -> tuple[str, list[str]]` — Implements separate generated visual descriptions.

### [`backend/app/services/document_ingestion/recognition/htr.py`](../../backend/app/services/document_ingestion/recognition/htr.py)

Purpose: Owns htr behavior for the backend runtime.

- L11 `class ReviewRequiredHTRRecognizer` — Encapsulates reviewrequiredhtrrecognizer.
- L12 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize.

### [`backend/app/services/document_ingestion/recognition/typhoon.py`](../../backend/app/services/document_ingestion/recognition/typhoon.py)

Purpose: Owns typhoon behavior for the backend runtime.

- L31 `class TyphoonRecognizerConfig` — Encapsulates typhoonrecognizerconfig.
- L39 `def _prepare_messages(image_bytes: bytes, target_image_dimension: int)` — Implements prepare messages.
- L62 `class TyphoonDocumentRecognizer` — Encapsulates typhoondocumentrecognizer.
- L63 `def __init__(self, config: TyphoonRecognizerConfig) -> None` — Implements init.
- L66 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page.
- L76 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize.
- L87 `async def _request(self, image_bytes: bytes) -> tuple[str, list[str], Any]` — Implements request.
- L117 `async def _post(self, messages: list[dict[str, Any]]) -> Any` — Implements post.

### [`backend/app/services/document_ingestion/region_pipeline.py`](../../backend/app/services/document_ingestion/region_pipeline.py)

Purpose: Owns region pipeline behavior for the backend runtime.

- L33 `class RegionRecognitionPipeline` — Encapsulates regionrecognitionpipeline.
- L34 `def __init__(self, segmenter: DocumentRegionSegmenter, router: RegionRouter, ocr_recognizer: OCRRecognizer, htr_recognizer: HTRRecognizer) -> None` — Implements init.
- L46 `async def process(self, page: RenderedPage) -> tuple[DocumentPage, list[str]]` — Executes process.
- L75 `async def _recognize_region(self, page: RenderedPage, segmented_region: SegmentedRegion, route: RegionRoute) -> DocumentRegion` — Implements recognize region.
- L115 `def _result_region(segmented_region: SegmentedRegion, result: RecognitionResult) -> DocumentRegion` — Implements result region.
- L154 `def _empty_region(segmented_region: SegmentedRegion, route: RegionRoute, warning: str | None=None) -> DocumentRegion` — Implements empty region.
- L175 `def _count_route(summary: RoutingSummary, region: SegmentedRegion, route: RegionRoute) -> None` — Implements count route.
- L189 `def _build_blocks(page: RenderedPage, regions: list[DocumentRegion]) -> list[DocumentBlock]` — Builds blocks.

### [`backend/app/services/document_ingestion/rendering.py`](../../backend/app/services/document_ingestion/rendering.py)

Purpose: Owns rendering behavior for the backend runtime.

- L11 `def _encode_png(image: Image.Image) -> bytes` — Serializes png.
- L17 `def render_pdf_page(content: bytes, page_number: int, longest_edge: int) -> bytes` — Renders pdf page.
- L38 `def normalize_image(content: bytes, longest_edge: int, max_pixels: int) -> bytes` — Normalizes image.
- L56 `def image_dimensions(content: bytes) -> tuple[int, int]` — Implements image dimensions.
- L64 `def crop_image_region(content: bytes, bbox: BoundingBox) -> bytes` — Implements crop image region.

### [`backend/app/services/document_ingestion/routing/__init__.py`](../../backend/app/services/document_ingestion/routing/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/routing/region_router.py`](../../backend/app/services/document_ingestion/routing/region_router.py)

Purpose: Owns region router behavior for the backend runtime.

- L13 `class RegionRoute` — Encapsulates regionroute.
- L20 `class RegionRouter` — Encapsulates regionrouter.
- L21 `def __init__(self, mixed_policy: str, unknown_policy: str, htr_enabled: bool=False) -> None` — Implements init.
- L31 `def route(self, region: SegmentedRegion) -> RegionRoute` — Implements route.
- L53 `def _machine_route(method: RecognitionMethod) -> RegionRoute` — Implements machine route.
- L61 `def _review_route(method: RecognitionMethod) -> RegionRoute` — Implements review route.
- L69 `def _fallback(policy: str) -> RegionRoute` — Implements fallback.
- L75 `def _disabled_htr_route() -> RegionRoute` — Implements disabled htr route.

### [`backend/app/services/document_ingestion/segmentation/__init__.py`](../../backend/app/services/document_ingestion/segmentation/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/segmentation/base.py`](../../backend/app/services/document_ingestion/segmentation/base.py)

Purpose: Owns base behavior for the backend runtime.

- L9 `class SegmentedRegion` — Encapsulates segmentedregion.
- L19 `class SegmentedPage` — Encapsulates segmentedpage.
- L24 `class DocumentRegionSegmenter(Protocol)` — Encapsulates documentregionsegmenter.
- L25 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page.

### [`backend/app/services/document_ingestion/segmentation/whole_page.py`](../../backend/app/services/document_ingestion/segmentation/whole_page.py)

Purpose: Owns whole page behavior for the backend runtime.

- L11 `class WholePageRegionSegmenter` — Encapsulates wholepageregionsegmenter.
- L12 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page.

### [`backend/app/services/document_ingestion/service.py`](../../backend/app/services/document_ingestion/service.py)

Purpose: Owns service behavior for the backend runtime.

- L49 `class DocumentIngestionLimits` — Encapsulates documentingestionlimits.
- L56 `class DocumentIngestionService` — Encapsulates documentingestionservice.
- L57 `def __init__(self, recognizer: DocumentRecognizer, limits: DocumentIngestionLimits, native_text_policy: NativeTextPolicy | None=None, region_pipeline: RegionRecognitionPipeline | None=None) -> None` — Implements init.
- L69 `async def ingest(self, content: bytes, filename: str, mode: IngestionMode=IngestionMode.UNIFIED) -> IngestedDocument` — Implements ingest.
- L101 `def _validate_content(self, content: bytes) -> None` — Validates content.
- L110 `async def _ingest_pdf(self, content: bytes, document_id: str, mode: IngestionMode) -> tuple[list[DocumentPage], list[str], ExtractionMethod]` — Implements ingest pdf.
- L163 `async def _ingest_image(self, content: bytes, document_id: str, mode: IngestionMode) -> tuple[list[DocumentPage], list[str]]` — Implements ingest image.
- L179 `async def _process_rendered_page(self, rendered_page: RenderedPage, mode: IngestionMode) -> tuple[DocumentPage, list[str]]` — Executes rendered page.
- L193 `async def _recognize_page(self, rendered_page: RenderedPage) -> tuple[DocumentPage, str | None]` — Implements recognize page.
- L235 `def _unified_region(self, page: RenderedPage, recognized) -> DocumentRegion` — Implements unified region.
- L270 `def _native_page(document_id: str, page_number: int, texts: list[str]) -> DocumentPage` — Implements native page.
- L288 `def _safe_filename(filename: str) -> str` — Implements safe filename.

### [`backend/app/services/followup/__init__.py`](../../backend/app/services/followup/__init__.py)

Purpose: Gap Analysis and Follow-Up / Clarification Policy Package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/followup/claim_transport.py`](../../backend/app/services/followup/claim_transport.py)

Purpose: Owns claim transport behavior for the backend runtime.

- L13 `class GapAnalysisClaim(BaseModel)` — Encapsulates gapanalysisclaim.
- L29 `def build_gap_analysis_claim_transport(claims: Sequence[Mapping[str, object]]) -> list[dict[str, object]]` — Builds gap analysis claim transport.

### [`backend/app/services/followup/compatibility.py`](../../backend/app/services/followup/compatibility.py)

Purpose: Owns compatibility behavior for the backend runtime.

- L14 `async def resolve_followup_outcome(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], followup_root_ordinal: int, source_run_id: UUID, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None) -> AssistantOutcome | None` — Compatibility wrapper returning only the pending assistant outcome.

### [`backend/app/services/followup/context.py`](../../backend/app/services/followup/context.py)

Purpose: Owns context behavior for the backend runtime.

- L10 `def build_bounded_context(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, gap_analysis: GapAnalysis | Mapping[str, object] | None=None) -> dict[str, object]` — Builds bounded context.
- L48 `def content_size() -> int` — Implements content size.
- L138 `def _bounded(value: str, limit: int) -> str` — Implements bounded.
- L142 `def _bounded_mapping(value: Mapping[str, object], limit: int) -> dict[str, object]` — Implements bounded mapping.

### [`backend/app/services/followup/contracts.py`](../../backend/app/services/followup/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L14 `class FollowUpResolution` — The gate result and the audit record carried into the final message.
- L70 `def _answer_indicates_unavailable(answer: str) -> bool` — Implements answer indicates unavailable.

### [`backend/app/services/followup/decision.py`](../../backend/app/services/followup/decision.py)

Purpose: Owns decision behavior for the backend runtime.

- L39 `async def evaluate_followup_outcome(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], followup_root_ordinal: int, source_run_id: UUID, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, canonical_trace: AnalysisTraceV3 | None=None, precomputed_gap_stage: GapStageResult | None=None, evidence_sha256: str | None=None, canonical_state_required: bool=False) -> FollowUpResolution` — Implements evaluate followup outcome.
- L61 `def proceed_resolution(*, reason_code: str, stop_reason: str, **metadata_kwargs: Any) -> FollowUpResolution` — Implements proceed resolution.
- L84 `def ask_resolution(*, selected_gap, question: str, reason_code: str, stop_reason: str, decision_source: str, policy_decision: str, **metadata_kwargs: Any) -> FollowUpResolution` — Implements ask resolution.

### [`backend/app/services/followup/gap_analysis.py`](../../backend/app/services/followup/gap_analysis.py)

Purpose: Provider-backed detection of incident-specific analytical gaps.

- L32 `class AnthropicGapAnalysis` — Run the bounded Gap Analysis stage through the configured core LLM.
- L35 `async def analyze(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, client: httpx.AsyncClient | None=None) -> GapAnalysisResult` — Implements analyze.
- L114 `async def _post(client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]) -> tuple[dict[str, object], int | None, int | None]` — Implements post.
- L154 `def _nonnegative_int(value: object) -> int | None` — Implements nonnegative int.

### [`backend/app/services/followup/gap_stage.py`](../../backend/app/services/followup/gap_stage.py)

Purpose: Owns gap stage behavior for the backend runtime.

- L33 `class GapStageResult` — Encapsulates gapstageresult.
- L41 `async def run_gap_analysis_stage(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], policy: FollowUpPolicy | None, gap_analyzer: GapAnalyzer | None, raw_evidence: str | None, analysis_answer: str | None, analysis_context: Mapping[str, object] | None, analysis_claims: Sequence[Mapping[str, object]] | None, source_run_id: UUID) -> GapStageResult` — Executes gap analysis stage.

### [`backend/app/services/followup/gate.py`](../../backend/app/services/followup/gate.py)

Purpose: Owns gate behavior for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/followup/helpers.py`](../../backend/app/services/followup/helpers.py)

Purpose: Owns helpers behavior for the backend runtime.

- L20 `def _extract_llm_text(payload: Mapping[str, object] | object) -> str` — Extract raw text across supported provider response shapes (Anthropic, OpenRouter, etc.).
- L50 `def _extract_text_value(value: object) -> str` — Extracts text value.
- L84 `def _extract_llm_json(raw: str) -> dict[str, object]` — Parse JSON object from LLM response text, handling markdown fences and whitespace.
- L132 `async def _invoke_policy_method(method: Any, kwargs: dict[str, object]) -> object` — Call old test/custom policies without dropping new completeness context.
- L151 `def _coerce_gap_analysis_result(raw_result: object, *, elapsed_ms: float) -> GapAnalysisResult` — Implements coerce gap analysis result.
- L179 `def _normalize_gap_analysis_semantics(analysis: GapAnalysis) -> GapAnalysis` — Normalizes gap analysis semantics.
- L195 `def _required_material_gap(analysis: GapAnalysis) -> GapItem | None` — Implements required material gap.
- L208 `def _required_gap_question(original_user_content: str, gap: GapItem) -> str` — Implements required gap question.
- L215 `def _selected_askable_gap(analysis: GapAnalysis, selected_gap: str | None, *, compatibility: bool) -> GapItem | None` — Implements selected askable gap.
- L261 `def _gap_reason_code(gap: GapItem) -> str` — Implements gap reason code.
- L270 `def _coerce_policy_result(raw_result: object, *, elapsed_ms: float) -> FollowUpPolicyResult` — Implements coerce policy result.
- L294 `def _safe_token_count(value: object) -> int | None` — Implements safe token count.
- L300 `def _followup_failure_code(error: Exception) -> str` — Implements followup failure code.
- L308 `def _normalized_question(question: str) -> str` — Implements normalized question.

### [`backend/app/services/followup/metadata.py`](../../backend/app/services/followup/metadata.py)

Purpose: Owns metadata behavior for the backend runtime.

- L22 `def empty_gap_analysis_trace(*, status: str='not_run', latency_ms: float | None=None, failure_code: str | None=None) -> dict[str, Any]` — Implements empty gap analysis trace.
- L42 `def gap_analysis_trace(result: GapAnalysisResult) -> dict[str, Any]` — Implements gap analysis trace.
- L57 `def followup_metadata(*, source_run_id: UUID, followup_root_ordinal: int, round_number: int, prior_exchange_count: int, action: str, question: str, reason_code: str, stop_reason: str, latency_ms: float | None=None, input_tokens: int | None=None, output_tokens: int | None=None, provider: str | None=None, model: str | None=None, failure_code: str | None=None, decision: str | None=None, decision_source: str | None=None, policy_decision: str | None=None, selected_gap: str | None=None, selected_gap_detail: dict[str, Any] | None=None, requested_selected_gap: str | None=None, followup_context: dict[str, str] | None=None, gap_analysis: dict[str, Any] | None=None, rag_skipped: bool=True, rag_invoked: bool=False) -> dict[str, Any]` — Implements followup metadata.
- L120 `def mark_followup_rag_invoked(outcome: AssistantOutcome, metadata_json: dict[str, Any]) -> AssistantOutcome` — Implements mark followup rag invoked.
- L132 `def mark_followup_rag_invoked_metadata(metadata_json: dict[str, Any]) -> dict[str, Any]` — Implements mark followup rag invoked metadata.

### [`backend/app/services/followup/policy.py`](../../backend/app/services/followup/policy.py)

Purpose: Select one user follow-up from a previously computed Gap Analysis.

- L33 `def build_clarified_query(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]) -> str` — Build one bounded legacy `/query` request containing untrusted case data.
- L64 `def render() -> str` — Renders render.
- L105 `class AnthropicFollowUpPolicy` — Run the second, decision-only stage against Gap Analysis output.
- L108 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None) -> FollowUpDecision` — Implements decide.
- L130 `async def decide_with_metadata(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None) -> FollowUpPolicyResult` — Implements decide with metadata.
- L209 `async def _post(client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]) -> FollowUpPolicyResult` — Implements post.
- L249 `def _normalize_gap_analysis(value: GapAnalysis | Mapping[str, object] | None) -> GapAnalysis` — Normalizes gap analysis.
- L259 `def _bounded(value: str, limit: int) -> str` — Implements bounded.
- L263 `def _nonnegative_int(value: object) -> int | None` — Implements nonnegative int.

### [`backend/app/services/followup/prompts.py`](../../backend/app/services/followup/prompts.py)

Purpose: Prompts and bounded provider payloads for the two follow-up stages.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/followup/schemas.py`](../../backend/app/services/followup/schemas.py)

Purpose: Strict contracts shared by gap analysis and follow-up policy.

- L37 `class GapItem(BaseModel)` — One incident-specific information gap found in the current analysis.
- L52 `def normalize_status(cls, value: object) -> object` — Normalizes status.
- L74 `def normalize_priority(cls, value: object) -> object` — Normalizes priority.
- L90 `def validate_text(cls, value: str) -> str` — Validates text.
- L99 `def explicitly_unknown_is_not_askable(self) -> 'GapItem'` — Implements explicitly unknown is not askable.
- L105 `class GapAnalysis(BaseModel)` — All relevant gaps detected for one completed Main Case Analysis.
- L114 `class GapAnalysisResult` — Gap output plus provider telemetry; never an evidence mutation.
- L125 `class FollowUpDecision(BaseModel)` — One bounded decision made from an already-computed Gap Analysis.
- L139 `def normalize_decision_mode(cls, value: object) -> object` — Normalizes decision mode.
- L151 `def accept_legacy_action_shape(cls, value: object) -> object` — Implements accept legacy action shape.
- L169 `def validate_selected_gap(cls, value: object) -> str | None` — Validates selected gap.
- L182 `def validate_decision(self) -> 'FollowUpDecision'` — Validates decision.
- L212 `def action(self) -> Literal['ask_followup', 'proceed']` — Legacy name retained for existing in-process callers.
- L219 `class FollowUpPolicyResult` — Decision plus safe provider metrics when the adapter supplies them.
- L231 `class ClarificationExchange` — Encapsulates clarificationexchange.
- L242 `class GapAnalyzer(Protocol)` — Encapsulates gapanalyzer.
- L243 `async def analyze(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None) -> GapAnalysisResult` — Implements analyze.
- L255 `class FollowUpPolicy(Protocol)` — Encapsulates followuppolicy.
- L256 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None) -> FollowUpDecision` — Implements decide.

### [`backend/app/services/followup/stateful.py`](../../backend/app/services/followup/stateful.py)

Purpose: Owns stateful behavior for the backend runtime.

- L48 `def normalize_gap_key(topic: str) -> str` — Normalizes gap key.
- L67 `def apply_clarification_history(analysis: GapAnalysis, exchanges: Sequence[ClarificationExchange]) -> GapAnalysis` — Implements apply clarification history.
- L87 `def exhausted_gap_keys(exchanges: Sequence[ClarificationExchange]) -> set[str]` — Implements exhausted gap keys.
- L99 `def unavailable_gap_keys(exchanges: Sequence[ClarificationExchange]) -> set[str]` — Implements unavailable gap keys.
- L111 `def select_next_gap(gaps: Sequence[AnalysisGapV3 | GapItem], exchanges: Sequence[ClarificationExchange]) -> AnalysisGapV3 | GapItem | None` — Extracts next gap.
- L136 `def policy_gap(gap: AnalysisGapV3 | GapItem) -> GapItem` — Implements policy gap.
- L150 `def relevant_claim_context(trace: AnalysisTraceV3, gap: AnalysisGapV3) -> dict[str, object]` — Implements relevant claim context.
- L168 `def followup_context(gap: AnalysisGapV3 | GapItem, *, evidence_sha256: str | None) -> dict[str, str]` — Implements followup context.
- L185 `def clarification_answer_context(question_message_id: str, context: Mapping[str, object]) -> dict[str, str]` — Implements clarification answer context.
- L203 `def _exchange_gap_key(exchange: ClarificationExchange) -> str | None` — Implements exchange gap key.
- L211 `def _has_claim_links(gap: AnalysisGapV3 | GapItem) -> bool` — Determines claim links.

### [`backend/app/services/llm/__init__.py`](../../backend/app/services/llm/__init__.py)

Purpose: Core LLM Provider & Structured Output Infrastructure.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/llm/core_llm.py`](../../backend/app/services/llm/core_llm.py)

Purpose: Resolve the single production chat LLM provider without fallback.

- L15 `class CoreLlmConfigurationError(RuntimeError)` — The selected production provider is missing required configuration.
- L18 `def __init__(self, provider: CoreLlmProvider, key_env_name: str) -> None` — Implements init.
- L28 `class CoreLlmTarget` — Encapsulates corellmtarget.
- L37 `def resolve_core_llm_target(feature_anthropic_model: str, *, require_key: bool=True, configured_settings: Settings | None=None) -> CoreLlmTarget` — Return the exact selected target for an Anthropic-format feature call.

### [`backend/app/services/llm/model_registry.py`](../../backend/app/services/llm/model_registry.py)

Purpose: Central OpenRouter model registry, curated presets, and alias resolver for Backend services.

- L12 `class ModelPreset` — Encapsulates modelpreset.
- L72 `def resolve_openrouter_model(model_name_or_alias: str | None) -> str` — Resolve an alias or model name to its canonical OpenRouter model string.
- L92 `def list_available_models() -> list[dict[str, object]]` — Return catalog list of all curated ready-selection models with their metadata.
- L110 `def format_model_table() -> str` — Render formatted ASCII comparison table of curated ready-selection models.

### [`backend/app/services/llm/structured_output.py`](../../backend/app/services/llm/structured_output.py)

Purpose: Provider-facing JSON Schema helpers for structured model output.

- L45 `def anthropic_json_schema(model: type[BaseModel]) -> dict[str, Any]` — Build an Anthropic-compatible schema without weakening local validation.
- L59 `def _normalize_schema(value: object) -> object` — Normalizes schema.

### [`backend/app/services/llm/structured_output_request_router.py`](../../backend/app/services/llm/structured_output_request_router.py)

Purpose: Provider-aware request options for structured-output LLM calls.

- L28 `def structured_output_request_options(*, provider: CoreLlmProvider, feature: StructuredOutputFeature, configured_max_tokens: int, temperature: float | None=None) -> dict[str, object]` — Return only the provider-specific structured-output request options.

### [`backend/app/services/llm/structured_output_router.py`](../../backend/app/services/llm/structured_output_router.py)

Purpose: Route structured-output schemas to the selected core LLM provider.

- L14 `def structured_output_schema(model: type[BaseModel], *, provider: CoreLlmProvider) -> dict[str, Any]` — Build the provider-specific structured-output schema for ``model``.
- L30 `def _require_all_object_properties(value: object) -> None` — Implements require all object properties.

### [`backend/app/services/reports/__init__.py`](../../backend/app/services/reports/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/reports/pdf_chrome.py`](../../backend/app/services/reports/pdf_chrome.py)

Purpose: Owns pdf chrome behavior for the backend runtime.

- L20 `def header_meta_table(view_model: ReportViewModel, *, styles: dict[str, object], width: float) -> Table` — Implements header meta table.
- L53 `def table_style() -> TableStyle` — Implements table style.
- L69 `def draw_page_chrome(canvas, document, *, font_names: tuple[str, str], report_id: str, view_model: ReportViewModel) -> None` — Implements draw page chrome.

### [`backend/app/services/reports/pdf_design.py`](../../backend/app/services/reports/pdf_design.py)

Purpose: Owns pdf design behavior for the backend runtime.

- L22 `def register_report_fonts() -> tuple[str, str]` — Implements register report fonts.
- L54 `def find_report_font(environment_name: str, candidates: tuple[str, ...]) -> str | None` — Implements find report font.
- L68 `def build_report_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]` — Builds report styles.
- L95 `def formatted_text(value: object) -> str` — Format markdown text (bold, italic, code, line breaks) into safe ReportLab HTML.
- L113 `def paragraph_text(value: object) -> str` — Implements paragraph text.
- L117 `def plain_text(value: object) -> str` — Implements plain text.

### [`backend/app/services/reports/report_contracts.py`](../../backend/app/services/reports/report_contracts.py)

Purpose: Owns report contracts behavior for the backend runtime.

- L13 `class ReportSourceMessage(BaseModel)` — Encapsulates reportsourcemessage.
- L26 `class AdmittedMitreRow(BaseModel)` — Encapsulates admittedmitrerow.
- L36 `class ReportInputSnapshot(BaseModel)` — Encapsulates reportinputsnapshot.
- L52 `class ReportServiceError(Exception)` — Encapsulates reportserviceerror.
- L53 `def __init__(self, code: str, message: str) -> None` — Implements init.
- L59 `class ReportGenerationConflict(ReportServiceError)` — Encapsulates reportgenerationconflict.
- L63 `class ReportNotFound(ReportServiceError)` — Encapsulates reportnotfound.
- L67 `class ReportValidationError(ValueError)` — Encapsulates reportvalidationerror.
- L72 `class ReportRunResult` — Encapsulates reportrunresult.

### [`backend/app/services/reports/report_generation.py`](../../backend/app/services/reports/report_generation.py)

Purpose: Owns report generation behavior for the backend runtime.

- L16 `async def run_report_generation(snapshot: ReportInputSnapshot) -> ReportRunResult` — Executes report generation.

### [`backend/app/services/reports/report_html.py`](../../backend/app/services/reports/report_html.py)

Purpose: Deterministic Jinja2 HTML rendering for CyberCase incident analysis reports.

- L26 `def get_report_css() -> str` — Return the embedded CSS stylesheet for HTML/PDF rendering.
- L33 `def render_chat_report_html_from_view_model(view_model: ReportViewModel) -> str` — Render HTML string deterministically from a ReportViewModel.
- L43 `def render_chat_report_html(report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th') -> str` — Build the view model and render formal report HTML in Thai or English.

### [`backend/app/services/reports/report_pdf.py`](../../backend/app/services/reports/report_pdf.py)

Purpose: Owns report pdf behavior for the backend runtime.

- L21 `def render_chat_report_pdf(report: ChatReportRead, *, thread_title: str, language: ReportLanguage='th') -> bytes` — Renders chat report pdf.

### [`backend/app/services/reports/report_pdf_story.py`](../../backend/app/services/reports/report_pdf_story.py)

Purpose: Owns report pdf story behavior for the backend runtime.

- L19 `def build_formal_report_story(view_model: ReportViewModel, *, report: ChatReportRead, styles: dict[str, ParagraphStyle]) -> list[object]` — Builds formal report story.
- L47 `def _summary_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements summary story.
- L65 `def _timeline_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements timeline story.
- L102 `def _evidence_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle], content_width: float) -> list[object]` — Implements evidence story.
- L169 `def _mitre_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle], content_width: float) -> list[object]` — Implements mitre story.
- L219 `def _gap_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements gap story.
- L240 `def _next_steps_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements next steps story.
- L261 `def build_provenance_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Builds provenance story.

### [`backend/app/services/reports/report_persistence.py`](../../backend/app/services/reports/report_persistence.py)

Purpose: Owns report persistence behavior for the backend runtime.

- L30 `def serialize_chat_report(report: ChatReport) -> ChatReportRead` — Serializes chat report.
- L64 `class ChatReportService` — Encapsulates chatreportservice.
- L65 `def __init__(self, db: AsyncSession) -> None` — Implements init.
- L68 `async def generate_report(self, thread_id: UUID, request: ChatReportCreate) -> ChatReportRead` — Generates report.
- L124 `async def list_reports(self, thread_id: UUID) -> list[ChatReportRead]` — Lists reports.
- L133 `async def get_report(self, thread_id: UUID, report_id: UUID) -> ChatReportRead` — Retrieves report.
- L137 `async def get_report_pdf(self, thread_id: UUID, report_id: UUID) -> tuple[bytes, str]` — Retrieves report pdf.
- L163 `async def _thread_with_messages(self, thread_id: UUID, *, lock: bool) -> ChatThread` — Implements thread with messages.
- L175 `async def _latest_rag_context(self, thread_id: UUID) -> RagContext` — Implements latest rag context.
- L191 `async def _existing_report(self, thread_id: UUID, key: str) -> ChatReport | None` — Implements existing report.
- L200 `async def _next_version(self, thread_id: UUID) -> int` — Implements next version.
- L206 `async def _ensure_thread(self, thread_id: UUID) -> None` — Implements ensure thread.
- L209 `async def _report(self, thread_id: UUID, report_id: UUID, *, load_thread: bool=False) -> ChatReport` — Implements report.

### [`backend/app/services/reports/report_snapshot.py`](../../backend/app/services/reports/report_snapshot.py)

Purpose: Owns report snapshot behavior for the backend runtime.

- L16 `def build_current_report_snapshot(thread: ChatThread, *, rag_context: RagContext) -> ReportInputSnapshot` — Builds current report snapshot.
- L71 `def _analysis_message(messages: list[ChatMessage], retrieval_context_id: str) -> ChatMessage | None` — Implements analysis message.
- L85 `def _mitre_rows(value: object) -> list[AdmittedMitreRow]` — Implements mitre rows.
- L107 `def _unresolved_issues(metadata: dict[str, object]) -> list[str]` — Implements unresolved issues.

### [`backend/app/services/reports/report_template.py`](../../backend/app/services/reports/report_template.py)

Purpose: Owns report template behavior for the backend runtime.

- L12 `def _extract_summary_paragraphs(analysis_answer: str) -> list[str]` — Extracts summary paragraphs.
- L31 `def _extract_progression_claims(snapshot: ReportInputSnapshot) -> list[ReportClaim]` — Extracts progression claims.
- L104 `def build_template_report(snapshot: ReportInputSnapshot) -> StructuredReport` — Builds template report.

### [`backend/app/services/reports/report_validation.py`](../../backend/app/services/reports/report_validation.py)

Purpose: Owns report validation behavior for the backend runtime.

- L13 `def validate_structured_report(report: StructuredReport, *, source_message_ids: set[str], mitre_ids: set[str]) -> None` — Validates structured report.
- L33 `def source_snapshot_hash(snapshot: ReportInputSnapshot | dict[str, object]) -> str` — Implements source snapshot hash.

### [`backend/app/services/reports/report_view_model_builder.py`](../../backend/app/services/reports/report_view_model_builder.py)

Purpose: Owns report view model builder behavior for the backend runtime.

- L21 `def _clean_markdown_text(text: str) -> str` — Normalizes markdown text.
- L30 `def build_report_view_model(report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th') -> ReportViewModel` — Deterministically transform persisted ChatReportRead into ReportViewModel.
- L77 `def _format_source_label(source_ids: list[str]) -> str` — Implements format source label.

### [`backend/app/services/reports/report_view_model_contracts.py`](../../backend/app/services/reports/report_view_model_contracts.py)

Purpose: Owns report view model contracts behavior for the backend runtime.

- L9 `class TimelineViewRow` — Encapsulates timelineviewrow.
- L19 `class EvidenceViewRow` — Encapsulates evidenceviewrow.
- L29 `class IndicatorViewRow` — Encapsulates indicatorviewrow.
- L36 `class MitreMappingViewRow` — Encapsulates mitremappingviewrow.
- L48 `class UnresolvedIssueViewRow` — Encapsulates unresolvedissueviewrow.
- L55 `class VerificationActionViewRow` — Encapsulates verificationactionviewrow.
- L61 `class ProvenanceViewRow` — Encapsulates provenanceviewrow.
- L67 `class ReportViewModel` — Encapsulates reportviewmodel.

### [`backend/app/services/reports/report_view_model_items.py`](../../backend/app/services/reports/report_view_model_items.py)

Purpose: Owns report view model items behavior for the backend runtime.

- L15 `class ParsedReportItems` — Encapsulates parsedreportitems.
- L22 `def _extract_timeline_from_text(text: str, *, language: ReportLanguage) -> list[TimelineViewRow]` — Extracts timeline from text.
- L81 `def parse_report_items(sections_by_id: dict[str, ReportSection], *, language: ReportLanguage) -> ParsedReportItems` — Parses report items.

### [`backend/app/services/reports/report_view_model_text.py`](../../backend/app/services/reports/report_view_model_text.py)

Purpose: Owns report view model text behavior for the backend runtime.

- L205 `def _format_datetime(dt: datetime | None) -> str` — Implements format datetime.
- L213 `def _extract_indicators_from_text(text: str, note: str, seen: set[str]) -> list[IndicatorViewRow]` — Extracts indicators from text.

### [`backend/app/services/workflow/__init__.py`](../../backend/app/services/workflow/__init__.py)

Purpose: Chat Run Workflow and Execution Pipeline Package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/workflow/chat_run_claim.py`](../../backend/app/services/workflow/chat_run_claim.py)

Purpose: Owns chat run claim behavior for the backend runtime.

- L21 `async def claim_run(db: AsyncSession, run_id: UUID, worker_id: str) -> ClaimedChatRun | None` — Implements claim run.
- L110 `async def _analysis_context_for_state(db: AsyncSession, current_run: ChatRun, state: CanonicalCaseAnalysisState | None) -> dict[str, object] | None` — Implements analysis context for state.
- L134 `async def _latest_legacy_analysis_context(db: AsyncSession, current_run: ChatRun) -> dict[str, object] | None` — Implements latest legacy analysis context.
- L171 `async def _fail_missing_request(run: ChatRun, now: datetime) -> None` — Implements fail missing request.
- L177 `async def _fail_missing_evidence(run: ChatRun, now: datetime) -> None` — Implements fail missing evidence.
- L183 `async def _fail_missing_context(run: ChatRun, now: datetime) -> None` — Implements fail missing context.
- L192 `async def _mark_claim_failure(run: ChatRun, now: datetime, code: str, message: str) -> None` — Implements mark claim failure.

### [`backend/app/services/workflow/chat_run_completion.py`](../../backend/app/services/workflow/chat_run_completion.py)

Purpose: Owns chat run completion behavior for the backend runtime.

- L17 `async def complete_run(db: AsyncSession, run_id: UUID, worker_id: str, outcome: AssistantOutcome, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None) -> bool` — Implements complete run.
- L81 `def _serialize_analysis_trace(outcome: AssistantOutcome) -> dict[str, object] | None` — Serializes analysis trace.

### [`backend/app/services/workflow/chat_run_contracts.py`](../../backend/app/services/workflow/chat_run_contracts.py)

Purpose: Owns chat run contracts behavior for the backend runtime.

- L15 `class ClaimedChatRun` — Encapsulates claimedchatrun.

### [`backend/app/services/workflow/chat_run_failure.py`](../../backend/app/services/workflow/chat_run_failure.py)

Purpose: Owns chat run failure behavior for the backend runtime.

- L13 `async def fail_run(db: AsyncSession, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None) -> bool` — Persist a safe failure without exposing upstream response content.

### [`backend/app/services/workflow/chat_run_locks.py`](../../backend/app/services/workflow/chat_run_locks.py)

Purpose: Owns chat run locks behavior for the backend runtime.

- L10 `async def lock_run_thread(db: AsyncSession, run_id: UUID) -> ChatThread | None` — Lock the parent thread before the run to match message creation order.
- L30 `async def lock_owned_running_run(db: AsyncSession, run_id: UUID, worker_id: str) -> ChatRun | None` — Implements lock owned running run.

### [`backend/app/services/workflow/chat_run_store.py`](../../backend/app/services/workflow/chat_run_store.py)

Purpose: Owns chat run store behavior for the backend runtime.

- L16 `class ChatRunWorker` — Encapsulates chatrunworker.
- L17 `def __init__(self, db: AsyncSession)` — Implements init.
- L20 `async def claim_run(self, run_id: UUID, worker_id: str) -> ClaimedChatRun | None` — Implements claim run.
- L27 `async def complete_run(self, run_id: UUID, worker_id: str, outcome: Any) -> bool` — Implements complete run.
- L42 `async def fail_run(self, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None) -> bool` — Implements fail run.
- L61 `async def _lock_run_thread(self, run_id: UUID) -> ChatThread | None` — Implements lock run thread.
- L64 `async def _lock_owned_running_run(self, run_id: UUID, worker_id: str) -> ChatRun | None` — Implements lock owned running run.

### [`backend/app/services/workflow/outcome.py`](../../backend/app/services/workflow/outcome.py)

Purpose: Owns outcome behavior for the backend runtime.

- L20 `class RagContextPayload` — Encapsulates ragcontextpayload.
- L25 `def to_analysis_context(self) -> dict[str, object]` — Transforms analysis context.
- L34 `class AssistantOutcome` — Encapsulates assistantoutcome.
- L46 `def map_rag_response(response: QueryResponse) -> dict[str, object]` — Transforms rag response.
- L55 `def validated_rag_context_payload(response: QueryResponse) -> RagContextPayload` — Implements validated rag context payload.
- L79 `def fresh_analysis_outcome(answer: str, *, action: str, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], followup_metadata: dict[str, object], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements fresh analysis outcome.
- L127 `def question_outcome(answer: str, *, analysis_context: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements question outcome.
- L172 `def bind_followup_question(outcome: AssistantOutcome, *, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements bind followup question.
- L209 `def _retrieval_context_id(rag_context: RagContextPayload | None) -> str | None` — Implements retrieval context id.
- L213 `def _mitre_table(rag_context: RagContextPayload | None) -> list[dict[str, object]]` — Implements mitre table.
- L217 `def _rag_attempt_metadata(status: RagAttemptStatus, failure_code: str | None) -> dict[str, object]` — Implements rag attempt metadata.

### [`backend/app/services/workflow/pipeline.py`](../../backend/app/services/workflow/pipeline.py)

Purpose: Owns pipeline behavior for the backend runtime.

- L17 `def build_dependencies() -> PipelineDependencies` — Builds dependencies.
- L27 `async def process_chat_run(run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None) -> None` — Executes chat run.

### [`backend/app/services/workflow/pipeline_dependencies.py`](../../backend/app/services/workflow/pipeline_dependencies.py)

Purpose: Owns pipeline dependencies behavior for the backend runtime.

- L8 `class PipelineDependencies` — Encapsulates pipelinedependencies.

### [`backend/app/services/workflow/pipeline_execution.py`](../../backend/app/services/workflow/pipeline_execution.py)

Purpose: Owns pipeline execution behavior for the backend runtime.

- L42 `async def process_chat_run(run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None, applicability_call: Callable[..., Awaitable[MitreApplicabilityRecord]] | None=None, dependencies: PipelineDependencies) -> None` — Executes chat run.
- L90 `async def _run_fresh_analysis(claimed, *, rag_request, analysis_request, followup_evaluator, policy, gap_analyzer, applicability_gate) -> AssistantOutcome` — Executes fresh analysis.
- L219 `async def _run_question(claimed, analysis_request) -> AssistantOutcome` — Executes question.
- L246 `def _coerce_analysis_result(value: object) -> CaseAnalysisResult` — Implements coerce analysis result.

### [`backend/app/services/workflow/pipeline_failure.py`](../../backend/app/services/workflow/pipeline_failure.py)

Purpose: Owns pipeline failure behavior for the backend runtime.

- L9 `async def record_failure(dependencies: PipelineDependencies, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None) -> None` — Persists failure.

### [`backend/app/services/workflow/rag_routing.py`](../../backend/app/services/workflow/rag_routing.py)

Purpose: Owns rag routing behavior for the backend runtime.

- L23 `class RagAttempt` — Encapsulates ragattempt.
- L29 `async def attempt_mitre_applicability(claimed, applicability_gate) -> MitreApplicabilityRecord` — Implements attempt mitre applicability.
- L51 `async def attempt_optional_rag(claimed, rag_request) -> RagAttempt` — Implements attempt optional rag.

### [`backend/app/services/workflow/worker.py`](../../backend/app/services/workflow/worker.py)

Purpose: Owns worker behavior for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

## Repository Tooling

### [`backend/manual_smoke.py`](../../backend/manual_smoke.py)

Purpose: Bounded smoke test for a running chat-only backend.

- L19 `def _require_success(response: httpx.Response) -> dict[str, object]` — Implements require success.
- L27 `def main() -> None` — Implements main.

### [`backend/tools/__init__.py`](../../backend/tools/__init__.py)

Purpose: Defines the public package surface for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/tools/document_ingestion_eval.py`](../../backend/tools/document_ingestion_eval.py)

Purpose: Owns document ingestion eval behavior for the repository tooling.

- L15 `def _load_samples(path: Path) -> list[dict[str, Any]]` — Retrieves samples.
- L30 `def main() -> None` — Implements main.

### [`docs/developer-handover/extract_typescript_symbols.mjs`](../../docs/developer-handover/extract_typescript_symbols.mjs)

Purpose: Owns extract typescript symbols behavior for the repository tooling.

- L9 `function clean(text)` — Normalizes clean.
- L13 `function lineOf(sourceFile, node)` — Implements lineof.
- L17 `function declarationName(node, fallback)` — Implements declarationname.
- L23 `function parameters(node, sourceFile)` — Implements parameters.
- L28 `function returnType(node, sourceFile)` — Implements returntype.
- L32 `function addSymbol(symbols, sourceFile, node, kind, name, signature, parent = "")` — Implements addsymbol.
- L42 `function walk(sourceFile)` — Implements walk.
- L45 `function visit(node, parentName = "")` — Implements visit.

### [`docs/developer-handover/generate_symbol_index.py`](../../docs/developer-handover/generate_symbol_index.py)

Purpose: Owns generate symbol index behavior for the repository tooling.

- L15 `def run(command: list[str]) -> str` — Executes run.
- L26 `def source_files() -> list[Path]` — Implements source files.
- L40 `def first_sentence(text: str | None) -> str | None` — Implements first sentence.
- L50 `def words(name: str) -> str` — Implements words.
- L64 `def area_for(relative: str) -> str` — Implements area for.
- L84 `def file_purpose(relative: str, module_doc: str | None=None) -> str` — Implements file purpose.
- L103 `def describe(name: str, kind: str) -> str` — Implements describe.
- L144 `def python_signature(node: ast.AST) -> str` — Implements python signature.
- L153 `def python_symbols(path: Path) -> tuple[str | None, list[dict[str, object]]]` — Implements python symbols.
- L157 `class SymbolVisitor(ast.NodeVisitor)` — Encapsulates symbolvisitor.
- L158 `def __init__(self) -> None` — Implements init.
- L161 `def qualified(self, name: str) -> str` — Implements qualified.
- L165 `def visit_ClassDef(self, node: ast.ClassDef) -> None` — Implements visit classdef.
- L172 `def record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None` — Persists function.
- L180 `def visit_FunctionDef(self, node: ast.FunctionDef) -> None` — Implements visit functiondef.
- L183 `def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None` — Implements visit asyncfunctiondef.
- L190 `def typescript_symbols(paths: list[Path]) -> dict[str, list[dict[str, object]]]` — Implements typescript symbols.
- L206 `def section_for(relative: str) -> str` — Implements section for.
- L210 `def generate() -> str` — Generates generate.

### [`docs/thesis_v1/_work/build_thesis_docx.py`](../../docs/thesis_v1/_work/build_thesis_docx.py)

Purpose: Owns build thesis docx behavior for the repository tooling.

- L30 `def set_font(run, name=FONT, size=None, bold=None, italic=None, color=None)` — Updates font.
- L45 `def shade(element, fill)` — Implements shade.
- L54 `def set_cell_margins(cell, top=100, start=120, bottom=100, end=120)` — Updates cell margins.
- L69 `def set_table_geometry(table, widths)` — Updates table geometry.
- L98 `def add_field(paragraph, instruction, display='')` — Implements add field.
- L115 `def configure_styles(doc)` — Implements configure styles.
- L167 `def add_inline(paragraph, text, citation_numbers)` — Implements add inline.
- L192 `def table_widths(rows, total=9360)` — Implements table widths.
- L201 `def add_table(doc, rows, citation_numbers)` — Implements add table.
- L222 `def add_markdown(doc, text, citation_numbers, skip_h1=False)` — Implements add markdown.
- L288 `def bib_entries(text)` — Implements bib entries.
- L301 `def format_reference(fields)` — Implements format reference.
- L311 `def add_cover(doc)` — Implements add cover.
- L337 `def add_toc(doc)` — Implements add toc.
- L352 `def build()` — Builds build.

### [`frontend/eslint.config.mjs`](../../frontend/eslint.config.mjs)

Purpose: Owns eslint config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/next.config.ts`](../../frontend/next.config.ts)

Purpose: Owns next config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/postcss.config.mjs`](../../frontend/postcss.config.mjs)

Purpose: Owns postcss config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/tailwind.config.ts`](../../frontend/tailwind.config.ts)

Purpose: Owns tailwind config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/vitest.config.ts`](../../frontend/vitest.config.ts)

Purpose: Owns vitest config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`install_deps.py`](../../install_deps.py)

Purpose: Owns install deps behavior for the repository tooling.

- L7 `def install_requirements(directory)` — Install requirements from a requirements.txt file in the specified directory.
- L26 `def main()` — Implements main.

### [`rag_service/docs/_build_pdf.py`](../../rag_service/docs/_build_pdf.py)

Purpose: Build an HTML (mermaid-rendering, Thai-font) file from RAG_Module.md.

- L24 `def _stash_mermaid(m)` — Implements stash mermaid.
- L35 `def gh_slugify(value, separator='-')` — Implements gh slugify.
- L51 `def _restore_mermaid(m)` — Implements restore mermaid.

### [`rag_service/finetune/compare/run_comparison.py`](../../rag_service/finetune/compare/run_comparison.py)

Purpose: A/B Comparison — base qwen2.5:7b vs fine-tuned mitre-qwen:7b ============================================================= Runs the EXISTING generation evaluation (evaluation/eval_runner.py) once per model, switching models purely via the LOCAL_LLM_MODEL env var — no pipeline or eval code is modified.

- L49 `def run_eval(model: str, dataset: str, max_samples: int, out_md: Path) -> None` — Executes eval.
- L72 `def parse_metrics(md_path: Path) -> dict[str, float]` — Extract 'Metric -> value' pairs from the generation eval report.
- L90 `def render(base_model, ft_model, base_m, ft_m) -> str` — Renders render.
- L124 `def main()` — Implements main.

### [`rag_service/finetune/data/build_dataset.py`](../../rag_service/finetune/data/build_dataset.py)

Purpose: Dataset Builder — MITRE ATT&CK STIX → SFT instruction pairs =========================================================== Reuses the existing ``StixParser`` (ingestion/stix_parser.py) to turn the MITRE ATT&CK STIX bundles into chat-format training examples for fine-tuning the local generation model into a MITRE specialist.

- L46 `def _latest_bundle(folder: Path) -> Path | None` — Return the newest versioned STIX json in a folder (e.g.
- L52 `def version_key(p: Path)` — Implements version key.
- L59 `def load_parser(domains: list[str], all_versions: bool) -> StixParser` — Retrieves parser.
- L85 `def load_heldout_ids() -> set[str]` — Retrieves heldout ids.
- L105 `def build_indices(parser: StixParser)` — Builds indices.
- L119 `def label(stix_id)` — Implements label.
- L153 `def _record(system, user, assistant, category, subject_id, style, lang='en')` — Persists record.
- L167 `def generate_examples(parser, by_id, idx, held, rng, grounded_ratio, abstention_ratio=0.45, holdout=False)` — Generates examples.
- L173 `def add_grounded(category, sid, label, name, aid, desc, relation, neighbors, lead, q)` — Grounded twin of a list/relationship example — now ALWAYS emitted so grounded is the majority (the v4 model over-fit the closed-book template).
- L189 `def add_abstention(sid, label, name, aid, desc, present_rel, present_names, present_phrase, question, missing)` — Emit a grounded example whose question asks about something NOT in the context → the model must say so instead of guessing (the v4 model could not abstain; this category did not exist before).
- L202 `def ok(stix_id)` — Implements ok.
- L382 `def dedup(records)` — Implements dedup.
- L393 `def cap_per_category(records, max_per_cat, rng)` — Implements cap per category.
- L406 `def write_jsonl(path: Path, records)` — Implements write jsonl.
- L414 `def main()` — Implements main.

### [`rag_service/finetune/data/templates.py`](../../rag_service/finetune/data/templates.py)

Purpose: Q&A Templates — STIX → instruction pairs ======================================== Pure formatting helpers that turn parsed MITRE ATT&CK entities/relationships into (question, answer) pairs.

- L33 `def clean_text(text: str, max_chars: int | None=None) -> str` — Strip MITRE markdown noise (citations, links) and collapse whitespace.
- L61 `def first_sentence(text: str, max_chars: int=300) -> str` — First COMPLETE sentence of a description — used for per-mitigation blurbs so list answers never contain a sentence chopped mid-way.
- L73 `def _pick(rng: random.Random | None, options: list[str]) -> str` — Extracts pick.
- L77 `def _join_list(items: list[str], max_items: int) -> str` — Implements join list.
- L87 `def _ensure_period(s: str) -> str` — Implements ensure period.
- L91 `def technique_lookup(name, attack_id, desc, rng=None)` — Implements technique lookup.
- L105 `def mitigation_lookup(name, attack_id, desc, mitigations, rng=None)` — mitigations: list of (m_name, m_id, m_desc_short).
- L135 `def technique_profile(name, attack_id, desc, mitigations, groups, tactics, rng=None)` — Compound 'full overview' answer — description + tactic(s) + mitigations + groups in one reply.
- L167 `def technique_groups(name, attack_id, groups, rng=None)` — groups: list of (g_name, g_id).
- L183 `def technique_detection(name, attack_id, components, rng=None)` — components: list of data source/component name strings.
- L197 `def tactic_techniques(tactic_name, tactic_id, techniques, rng=None)` — techniques: list of (t_name, t_id).
- L218 `def group_techniques(group_name, group_id, techniques, rng=None)` — Implements group techniques.
- L233 `def group_software(group_name, group_id, software, rng=None)` — Implements group software.
- L253 `def software_techniques(sw_name, sw_id, sw_type, techniques, rng=None)` — Implements software techniques.
- L271 `def software_type_query(sw_name, sw_id, sw_type, desc, rng=None)` — Implements software type query.
- L287 `def campaign_attribution(camp_name, camp_id, groups, rng=None)` — Implements campaign attribution.
- L305 `def build_entity_context(entity_type, node_label, name, attack_id, desc)` — Format one entity like context_builder.build_context's semantic block.
- L323 `def build_relation_context(center_label, center_name, center_id, center_desc, relation_display, neighbor_names, rel_score=0.95)` — Context block for a LIST/relationship answer — mirrors the real pipeline's output: a semantic block PLUS a graph block (context_builder.build_context + SubgraphResult.to_text).
- L349 `def grounded_list_answer(center_name, center_id, lead, names, rng=None)` — Grounded list answer.
- L363 `def abstention_answer(name, attack_id, missing, present_phrase, rng=None)` — Answer for an abstention example: the question asks about something NOT in the context, so the model must say so plainly instead of guessing from memory.
- L376 `def grounded_user_prompt(context: str, question: str) -> str` — User turn for a grounded example (context + question).

### [`rag_service/finetune/export/merge_and_gguf.py`](../../rag_service/finetune/export/merge_and_gguf.py)

Purpose: Merge LoRA → GGUF (fallback / non-Unsloth path) =============================================== Use this when you trained the adapter elsewhere, or want the explicit transformers + llama.cpp route instead of Unsloth's ``save_pretrained_gguf``.

- L32 `def merge(base_model: str, adapter_dir: str, merged_dir: Path)` — Implements merge.
- L54 `def to_gguf(merged_dir: Path, llama_cpp: Path, quant: str)` — Transforms gguf.
- L80 `def main()` — Implements main.

### [`rag_service/finetune/ft_config.py`](../../rag_service/finetune/ft_config.py)

Purpose: Fine-tune Module — Central Configuration ========================================= All knobs for turning the local generation model (``qwen2.5:7b``) into a MITRE ATT&CK specialist, while keeping the original model intact for A/B comparison.

- L155 `def add_rag_to_path() -> None` — Put ``rag_service/app/RAG`` on sys.path so ``import GraphRAG.*`` works.

### [`rag_service/finetune/train/train_unsloth.py`](../../rag_service/finetune/train/train_unsloth.py)

Purpose: LoRA Trainer — Qwen → MITRE ATT&CK specialist ============================================= Run this on a Cloud GPU (Kaggle / Colab T4/P100 16 GB or better).

- L38 `def main()` — Implements main.
- L125 `def to_text(ex)` — Transforms text.

### [`scripts/generate_architecture_pdf.py`](../../scripts/generate_architecture_pdf.py)

Purpose: Script to generate a comprehensive, highly-detailed PDF architecture document for CyberCase Intelligence Framework.

- L48 `def register_fonts()` — Implements register fonts.
- L65 `def build_styles(reg, bold)` — Builds styles.
- L197 `def draw_header_footer(canvas, doc, reg, bold)` — Implements draw header footer.
- L218 `def create_code_panel(code_text, styles)` — Creates code panel.
- L232 `def create_info_panel(title, content, styles, bg_color=_PANEL, border_color=_BORDER)` — Creates info panel.
- L245 `def generate_pdf(output_path: str)` — Generates pdf.

## Backend Regression Suite

### [`backend/tests/test_analysis_trace.py`](../../backend/tests/test_analysis_trace.py)

Purpose: Verifies analysis trace behavior in the backend regression suite.

- L10 `def analysis(source_ids: list[str], technique_id: str='T1190') -> ProviderCaseAnalysis` — Implements analysis.
- L38 `def test_trace_binds_reported_claims_to_messages_and_mitre_to_retrieval() -> None` — Implements test trace binds reported claims to messages and mitre to retrieval.
- L49 `def test_reported_claim_cannot_cite_a_non_evidence_message() -> None` — Implements test reported claim cannot cite a non evidence message.
- L59 `def test_mitre_association_cannot_escape_bound_context() -> None` — Implements test mitre association cannot escape bound context.

### [`backend/tests/test_analysis_trace_cross_domain.py`](../../backend/tests/test_analysis_trace_cross_domain.py)

Purpose: Verifies analysis trace cross domain behavior in the backend regression suite.

- L17 `def test_v3_contract_is_domain_neutral(domain: str, claim_text: str) -> None` — Implements test v3 contract is domain neutral.

### [`backend/tests/test_analysis_trace_v3.py`](../../backend/tests/test_analysis_trace_v3.py)

Purpose: Verifies analysis trace v3 behavior in the backend regression suite.

- L13 `def build_trace(*, claims: list[dict[str, object]] | None=None, gaps: list[dict[str, object]] | None=None, retrieval_context_id: str | None=None) -> AnalysisTraceV3` — Builds trace.
- L46 `def reported_claim(*, claim_id: str='A-01', supporting: list[str] | None=None, contradicting: list[str] | None=None) -> dict[str, object]` — Implements reported claim.
- L63 `def analysis_gap(*, gap_id: str='G-01', status: str='NOT_PROVIDED', affected_claim_ids: list[str] | None=None, askable: bool=True) -> dict[str, object]` — Implements analysis gap.
- L82 `def test_valid_reported_claim() -> None` — Implements test valid reported claim.
- L88 `def test_reported_claim_without_support_is_rejected() -> None` — Implements test reported claim without support is rejected.
- L95 `def test_valid_analytical_inference() -> None` — Implements test valid analytical inference.
- L113 `def test_valid_unknown_not_established_claim() -> None` — Implements test valid unknown not established claim.
- L141 `def test_claim_source_outside_evidence_snapshot_is_rejected(field_name: str, expected_code: str) -> None` — Implements test claim source outside evidence snapshot is rejected.
- L153 `def test_same_source_cannot_support_and_contradict_claim() -> None` — Implements test same source cannot support and contradict claim.
- L167 `def test_inference_without_reasoning_summary_is_rejected() -> None` — Implements test inference without reasoning summary is rejected.
- L186 `def test_duplicate_claim_id_is_rejected() -> None` — Implements test duplicate claim id is rejected.
- L201 `def test_duplicate_gap_id_is_rejected() -> None` — Implements test duplicate gap id is rejected.
- L209 `def test_gap_referencing_nonexistent_claim_is_rejected() -> None` — Implements test gap referencing nonexistent claim is rejected.
- L218 `def test_duplicate_affected_claim_id_is_rejected() -> None` — Implements test duplicate affected claim id is rejected.
- L223 `def test_explicitly_unknown_case_level_gap_parses_correctly() -> None` — Implements test explicitly unknown case level gap parses correctly.
- L230 `def test_explicitly_unknown_gap_cannot_be_askable() -> None` — Implements test explicitly unknown gap cannot be askable.
- L237 `def test_reported_claim_can_preserve_conflicting_evidence() -> None` — Implements test reported claim can preserve conflicting evidence.
- L253 `def test_v2_trace_remains_readable_without_v3_reinterpretation() -> None` — Implements test v2 trace remains readable without v3 reinterpretation.
- L279 `def test_v3_trace_with_null_retrieval_context_is_valid() -> None` — Implements test v3 trace with null retrieval context is valid.
- L285 `def test_v3_case_overview_requires_evidence_hash() -> None` — Implements test v3 case overview requires evidence hash.

### [`backend/tests/test_canonical_analysis_state.py`](../../backend/tests/test_canonical_analysis_state.py)

Purpose: Verifies canonical analysis state behavior in the backend regression suite.

- L12 `def claim(claim_id: str, text: str) -> dict[str, object]` — Implements claim.
- L24 `def trace_payload(mode: str, *, summary: str, gaps: list[dict[str, object]]) -> dict[str, object]` — Implements trace payload.
- L43 `def gap_payload() -> dict[str, object]` — Implements gap payload.
- L56 `def message(ordinal: int, trace: dict[str, object]) -> ChatMessage` — Implements message.
- L67 `def test_qa_trace_cannot_replace_canonical_case_overview() -> None` — Implements test qa trace cannot replace canonical case overview.
- L94 `def test_invalid_main_trace_with_gap_metadata_is_not_canonical_state() -> None` — Implements test invalid main trace with gap metadata is not canonical state.
- L120 `def test_invalid_later_main_trace_cannot_replace_valid_canonical_gaps() -> None` — Implements test invalid later main trace cannot replace valid canonical gaps.
- L156 `def test_question_answer_is_response_scoped_and_runs_main_analysis_once() -> None` — Implements test question answer is response scoped and runs main analysis once.
- L171 `async def analysis_request(**kwargs)` — Implements analysis request.

### [`backend/tests/test_chat_delete.py`](../../backend/tests/test_chat_delete.py)

Purpose: Verifies chat delete behavior in the backend regression suite.

- L11 `class ChatDeleteServiceTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates chatdeleteservicetests.
- L12 `async def test_delete_thread_locks_and_deletes_parent(self) -> None` — Implements test delete thread locks and deletes parent.
- L28 `async def test_delete_missing_thread_returns_404(self) -> None` — Implements test delete missing thread returns 404.

### [`backend/tests/test_chat_followup_policy.py`](../../backend/tests/test_chat_followup_policy.py)

Purpose: Verifies chat followup policy behavior in the backend regression suite.

- L13 `class Analyzer` — Encapsulates analyzer.
- L14 `async def analyze(self, **kwargs)` — Implements analyze.
- L33 `class Policy` — Encapsulates policy.
- L34 `async def decide(self, **kwargs)` — Implements decide.
- L43 `def test_followup_consumes_raw_evidence_without_case_state() -> None` — Implements test followup consumes raw evidence without case state.
- L75 `def test_gap_analysis_contract_uses_free_text_affects_and_preserves_unknown() -> None` — Implements test gap analysis contract uses free text affects and preserves unknown.
- L99 `def test_extract_llm_json_markdown_fences() -> None` — Implements test extract llm json markdown fences.
- L112 `def test_extract_llm_json_surrounding_text() -> None` — Implements test extract llm json surrounding text.
- L120 `def test_extract_llm_text_and_thinking_blocks() -> None` — Implements test extract llm text and thinking blocks.
- L146 `def test_followup_schemas_lenient_coercion() -> None` — Implements test followup schemas lenient coercion.
- L178 `def test_reconstruct_clarification_chain_with_bound_metadata() -> None` — Implements test reconstruct clarification chain with bound metadata.
- L226 `def test_answer_indicates_unavailable_thai_and_english() -> None` — Implements test answer indicates unavailable thai and english.
- L246 `def test_evaluate_followup_proceeds_when_only_gap_is_explicitly_unknown() -> None` — Implements test evaluate followup proceeds when only gap is explicitly unknown.
- L249 `class UnknownAnalyzer` — Encapsulates unknownanalyzer.
- L250 `async def analyze(self, **kwargs)` — Implements analyze.

### [`backend/tests/test_chat_rag_client.py`](../../backend/tests/test_chat_rag_client.py)

Purpose: Verifies chat rag client behavior in the backend regression suite.

- L11 `class ChatRagClientTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates chatragclienttests.
- L12 `async def test_query_payload_and_completed_mapping(self) -> None` — Implements test query payload and completed mapping.
- L15 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.
- L47 `async def test_answer_fields_are_rejected(self) -> None` — Implements test answer fields are rejected.
- L50 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.
- L69 `async def test_non_completed_response_is_rejected(self) -> None` — Implements test non completed response is rejected.
- L70 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.
- L94 `class ChatRagResponseMappingTests(unittest.TestCase)` — Encapsulates chatragresponsemappingtests.
- L95 `def test_completed_mitre_rows_are_json_safe_and_preserve_fields(self) -> None` — Implements test completed mitre rows are json safe and preserve fields.
- L123 `def test_empty_no_hit_context_and_empty_id_sentinel_are_valid(self) -> None` — Implements test empty no hit context and empty id sentinel are valid.

### [`backend/tests/test_chat_raw_pipeline.py`](../../backend/tests/test_chat_raw_pipeline.py)

Purpose: Verifies chat raw pipeline behavior in the backend regression suite.

- L30 `def claimed(action: str)` — Implements claimed.
- L51 `async def retrieve_gate(**kwargs)` — Implements retrieve gate.
- L61 `def test_initial_and_added_information_run_fresh_rag_on_raw_evidence(action: str) -> None` — Implements test initial and added information run fresh rag on raw evidence.
- L67 `async def rag_request(query: str)` — Implements rag request.
- L81 `async def analysis_request(**kwargs)` — Implements analysis request.
- L88 `async def followup_evaluator(**kwargs)` — Implements followup evaluator.
- L108 `def test_ask_reuses_context_and_does_not_create_rag_payload() -> None` — Implements test ask reuses context and does not create rag payload.
- L111 `async def analysis_request(**kwargs)` — Implements analysis request.
- L122 `def test_v3_trace_persists_without_a_retrieval_context() -> None` — Implements test v3 trace persists without a retrieval context.
- L156 `def test_v2_trace_persistence_remains_backward_compatible() -> None` — Implements test v2 trace persistence remains backward compatible.
- L178 `def test_fresh_pipeline_uses_one_analysis_and_one_gap_result_for_both_surfaces() -> None` — Implements test fresh pipeline uses one analysis and one gap result for both surfaces.
- L185 `async def rag_request(query: str)` — Implements rag request.
- L193 `async def analysis_request(**kwargs)` — Implements analysis request.
- L223 `class CountingGapAnalyzer` — Encapsulates countinggapanalyzer.
- L224 `async def analyze(self, **kwargs)` — Implements analyze.
- L244 `class AskPolicy` — Encapsulates askpolicy.
- L245 `async def decide(self, **kwargs)` — Implements decide.

### [`backend/tests/test_chat_report.py`](../../backend/tests/test_chat_report.py)

Purpose: Verifies chat report behavior in the backend regression suite.

- L11 `def report_snapshot()` — Implements report snapshot.
- L60 `def test_report_snapshot_uses_raw_messages_analysis_and_run_context() -> None` — Implements test report snapshot uses raw messages analysis and run context.
- L69 `def test_deterministic_report_validates_against_source_and_mitre_bindings() -> None` — Implements test deterministic report validates against source and mitre bindings.

### [`backend/tests/test_core_llm_provider.py`](../../backend/tests/test_core_llm_provider.py)

Purpose: Verifies core llm provider behavior in the backend regression suite.

- L12 `class CoreLlmProviderTests(unittest.TestCase)` — Encapsulates corellmprovidertests.
- L14 `def _settings(*, provider: str='openrouter', openrouter_key: str='', anthropic_key: str='') -> Settings` — Implements settings.
- L27 `def test_default_provider_is_openrouter(self) -> None` — Implements test default provider is openrouter.
- L33 `def test_openrouter_target_uses_dedicated_secret_and_bearer_auth(self) -> None` — Implements test openrouter target uses dedicated secret and bearer auth.
- L45 `def test_openrouter_target_resolves_aliases(self) -> None` — Implements test openrouter target resolves aliases.
- L52 `def test_anthropic_target_preserves_feature_model_and_native_auth(self) -> None` — Implements test anthropic target preserves feature model and native auth.
- L67 `def test_invalid_provider_is_rejected_by_settings(self) -> None` — Implements test invalid provider is rejected by settings.
- L71 `def test_selected_provider_missing_key_has_no_fallback(self) -> None` — Implements test selected provider missing key has no fallback.
- L87 `def test_openrouter_api_key_cannot_satisfy_production_target(self) -> None` — Implements test openrouter api key cannot satisfy production target.

### [`backend/tests/test_cors.py`](../../backend/tests/test_cors.py)

Purpose: Verifies cors behavior in the backend regression suite.

- L6 `def test_localhost_frontend_cors_preflight_is_allowed() -> None` — Implements test localhost frontend cors preflight is allowed.

### [`backend/tests/test_database_schema.py`](../../backend/tests/test_database_schema.py)

Purpose: Verifies database schema behavior in the backend regression suite.

- L5 `def test_schema_contains_only_product_runtime_tables() -> None` — Implements test schema contains only product runtime tables.
- L15 `def test_case_state_columns_and_tables_are_absent() -> None` — Implements test case state columns and tables are absent.
- L22 `def test_rag_context_is_bound_one_to_one_to_chat_run() -> None` — Implements test rag context is bound one to one to chat run.
- L34 `def test_report_uses_analysis_and_retrieval_bindings() -> None` — Implements test report uses analysis and retrieval bindings.

### [`backend/tests/test_document_ingestion.py`](../../backend/tests/test_document_ingestion.py)

Purpose: Verifies document ingestion behavior in the backend regression suite.

- L25 `class RecordingRecognizer` — Encapsulates recordingrecognizer.
- L26 `def __init__(self, text: str='recognized Thai document text') -> None` — Implements init.
- L30 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page.
- L35 `class FailingRecognizer` — Encapsulates failingrecognizer.
- L36 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page.
- L40 `def _service(recognizer) -> DocumentIngestionService` — Implements service.
- L52 `def _docx_bytes(*paragraphs: str) -> bytes` — Implements docx bytes.
- L61 `def _pdf_bytes(page_texts: list[str | None]) -> bytes` — Implements pdf bytes.
- L75 `def _png_bytes() -> bytes` — Implements png bytes.
- L81 `def test_docx_uses_native_extraction() -> None` — Implements test docx uses native extraction.
- L99 `def test_text_pdf_does_not_trigger_recognition() -> None` — Implements test text pdf does not trigger recognition.
- L113 `def test_scanned_pdf_page_is_routed_to_recognizer() -> None` — Implements test scanned pdf page is routed to recognizer.
- L122 `def test_pdf_with_tiny_text_layer_is_still_routed_to_recognizer() -> None` — Implements test pdf with tiny text layer is still routed to recognizer.
- L132 `def test_mixed_pdf_routes_pages_independently_and_preserves_page_numbers() -> None` — Implements test mixed pdf routes pages independently and preserves page numbers.
- L150 `def test_block_ids_are_deterministic() -> None` — Implements test block ids are deterministic.
- L163 `def test_unsupported_file_type_fails_cleanly() -> None` — Implements test unsupported file type fails cleanly.
- L170 `def test_recognizer_failure_is_returned_as_controlled_warning() -> None` — Implements test recognizer failure is returned as controlled warning.
- L177 `def test_prompt_injection_like_document_text_remains_inert_data() -> None` — Implements test prompt injection like document text remains inert data.
- L187 `def test_ingestion_does_not_call_rag_or_case_analysis(monkeypatch) -> None` — Implements test ingestion does not call rag or case analysis.
- L190 `async def forbidden_rag(*args, **kwargs)` — Implements forbidden rag.
- L193 `async def forbidden_analysis(*args, **kwargs)` — Implements forbidden analysis.
- L210 `def test_ingestion_does_not_create_persisted_chat_or_case(monkeypatch) -> None` — Implements test ingestion does not create persisted chat or case.
- L213 `async def forbidden_create(*args, **kwargs)` — Implements forbidden create.

### [`backend/tests/test_document_ingestion_api.py`](../../backend/tests/test_document_ingestion_api.py)

Purpose: Verifies document ingestion api behavior in the backend regression suite.

- L13 `def _docx_bytes(text: str) -> bytes` — Implements docx bytes.
- L21 `def _png_bytes() -> bytes` — Implements png bytes.
- L27 `class StaticPageRecognizer` — Encapsulates staticpagerecognizer.
- L28 `async def recognize_page(self, page) -> RecognizedPage` — Implements recognize page.
- L36 `def test_preview_endpoint_is_independent_and_returns_structured_document() -> None` — Implements test preview endpoint is independent and returns structured document.
- L56 `def test_preview_endpoint_supports_unified_mode_and_segmentation_alias() -> None` — Implements test preview endpoint supports unified mode and segmentation alias.
- L77 `def test_preview_endpoint_rejects_unsupported_content() -> None` — Implements test preview endpoint rejects unsupported content.
- L88 `def test_default_image_preview_does_not_require_google_configuration(monkeypatch) -> None` — Implements test default image preview does not require google configuration.

### [`backend/tests/test_document_ingestion_eval.py`](../../backend/tests/test_document_ingestion_eval.py)

Purpose: Verifies document ingestion eval behavior in the backend regression suite.

- L10 `def test_cer_and_wer_use_edit_distance() -> None` — Implements test cer and wer use edit distance.
- L15 `def test_evaluation_compares_unified_and_routed_predictions() -> None` — Implements test evaluation compares unified and routed predictions.
- L34 `def test_evaluation_reports_region_and_critical_field_metrics() -> None` — Implements test evaluation reports region and critical field metrics.

### [`backend/tests/test_document_ingestion_routing.py`](../../backend/tests/test_document_ingestion_routing.py)

Purpose: Verifies document ingestion routing behavior in the backend regression suite.

- L38 `def _png_bytes() -> bytes` — Implements png bytes.
- L44 `def _region(region_id: str, region_type: RegionType, bbox: tuple[int, int, int, int], contains_handwriting: bool | None=None, page_number: int=3) -> SegmentedRegion` — Implements region.
- L61 `class StaticSegmenter` — Encapsulates staticsegmenter.
- L62 `def __init__(self, regions: list[SegmentedRegion]) -> None` — Implements init.
- L65 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page.
- L69 `class RecordingOCR` — Encapsulates recordingocr.
- L70 `def __init__(self, generated: bool=False) -> None` — Implements init.
- L74 `async def recognize(self, region) -> RecognitionResult` — Implements recognize.
- L87 `class RecordingHTR` — Encapsulates recordinghtr.
- L88 `def __init__(self) -> None` — Implements init.
- L91 `async def recognize(self, region) -> RecognitionResult` — Implements recognize.
- L101 `class FailingRecognizer` — Encapsulates failingrecognizer.
- L102 `async def recognize(self, region) -> RecognitionResult` — Implements recognize.
- L106 `class UnifiedRecognizer` — Encapsulates unifiedrecognizer.
- L107 `def __init__(self) -> None` — Implements init.
- L110 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page.
- L115 `def _pipeline(regions: list[SegmentedRegion], ocr=None, htr=None, mixed_policy: str='unified', htr_enabled: bool=False) -> RegionRecognitionPipeline` — Implements pipeline.
- L130 `def test_router_selects_ocr_htr_and_mixed_fallback() -> None` — Implements test router selects ocr htr and mixed fallback.
- L149 `def test_router_does_not_transcribe_figures_or_signatures() -> None` — Implements test router does not transcribe figures or signatures.
- L158 `def test_figure_region_stays_non_authoritative_without_recognizer_call() -> None` — Implements test figure region stays non authoritative without recognizer call.
- L174 `def test_routed_pipeline_preserves_reading_order_bbox_and_page_number() -> None` — Implements test routed pipeline preserves reading order bbox and page number.
- L206 `def test_ocr_and_htr_failures_are_controlled_per_region() -> None` — Implements test ocr and htr failures are controlled per region.
- L224 `def test_disabled_htr_preserves_handwriting_without_calling_provider() -> None` — Implements test disabled htr preserves handwriting without calling provider.
- L243 `def test_unavailable_enabled_htr_does_not_interrupt_printed_region() -> None` — Implements test unavailable enabled htr does not interrupt printed region.
- L263 `def test_unified_and_routed_modes_share_the_ingestion_service() -> None` — Implements test unified and routed modes share the ingestion service.
- L284 `def test_figure_tags_are_separated_from_literal_transcription() -> None` — Implements test figure tags are separated from literal transcription.

### [`backend/tests/test_document_ingestion_segmentation.py`](../../backend/tests/test_document_ingestion_segmentation.py)

Purpose: Verifies document ingestion segmentation behavior in the backend regression suite.

- L13 `def _png_bytes() -> bytes` — Implements png bytes.
- L19 `def test_whole_page_segmentation_assigns_deterministic_region_ids() -> None` — Implements test whole page segmentation assigns deterministic region ids.

### [`backend/tests/test_gap_assembly.py`](../../backend/tests/test_gap_assembly.py)

Purpose: Verifies gap assembly behavior in the backend regression suite.

- L12 `def claim(claim_id: str, text: str) -> dict[str, object]` — Implements claim.
- L24 `def trace(*, claims: list[dict[str, object]] | None=None, with_mitre: bool=False) -> AnalysisTraceV3` — Implements trace.
- L56 `def gap(*, topic: str='Property identity', status: str='NOT_PROVIDED', affects: str='A-01 — suspect possession of the missing property', priority: str='medium', askable: bool=True) -> GapItem` — Implements gap.
- L77 `def assemble(value: AnalysisTraceV3, gaps: list[GapItem]) -> AnalysisTraceV3` — Builds assemble.
- L86 `def test_gap_links_to_one_claim_by_stable_id() -> None` — Implements test gap links to one claim by stable id.
- L92 `def test_one_gap_can_affect_multiple_claims() -> None` — Implements test one gap can affect multiple claims.
- L103 `def test_free_text_affects_is_linked_conservatively() -> None` — Implements test free text affects is linked conservatively.
- L117 `def test_case_level_gap_may_have_no_claim_link() -> None` — Implements test case level gap may have no claim link.
- L131 `def test_gap_status_is_preserved(status: str, askable: bool) -> None` — Implements test gap status is preserved.
- L137 `def test_priority_order_controls_stable_gap_ids() -> None` — Implements test priority order controls stable gap ids.
- L153 `def test_gap_assembly_preserves_analysis_and_provenance_bindings() -> None` — Implements test gap assembly preserves analysis and provenance bindings.
- L162 `def test_unknown_direct_claim_reference_fails_without_persisting_empty_gaps() -> None` — Implements test unknown direct claim reference fails without persisting empty gaps.
- L178 `def test_missing_gap_analysis_marks_v3_trace_unavailable() -> None` — Implements test missing gap analysis marks v3 trace unavailable.
- L201 `def test_general_case_without_rag_or_mitre_validates(case_claim: str) -> None` — Implements test general case without rag or mitre validates.
- L208 `def test_cyber_case_with_mitre_still_validates() -> None` — Implements test cyber case with mitre still validates.

### [`backend/tests/test_gap_claim_transport.py`](../../backend/tests/test_gap_claim_transport.py)

Purpose: Verifies gap claim transport behavior in the backend regression suite.

- L27 `def claim_payload(index: int) -> dict[str, object]` — Implements claim payload.
- L39 `def trace_with_64_claims() -> AnalysisTraceV3` — Implements trace with 64 claims.
- L62 `def test_dedicated_transport_preserves_all_64_claims_in_order() -> None` — Implements test dedicated transport preserves all 64 claims in order.
- L75 `def test_gap_provider_payload_bypasses_generic_32_item_limiter(monkeypatch) -> None` — Implements test gap provider payload bypasses generic 32 item limiter.
- L78 `async def fake_post(client, messages_url, request_payload, headers)` — Implements fake post.
- L113 `def test_transport_bounds_text_without_dropping_claims() -> None` — Implements test transport bounds text without dropping claims.
- L121 `def test_transport_rejects_claim_count_above_v3_contract() -> None` — Implements test transport rejects claim count above v3 contract.
- L128 `def test_a64_exact_link_survives_gap_stage_assembly_and_serialization() -> None` — Implements test a64 exact link survives gap stage assembly and serialization.
- L132 `class Analyzer` — Encapsulates analyzer.
- L133 `async def analyze(self, **kwargs)` — Implements analyze.
- L153 `class Policy` — Encapsulates policy.
- L154 `async def decide(self, **kwargs)` — Implements decide.
- L195 `def test_gap_failure_log_includes_source_run_id(caplog) -> None` — Implements test gap failure log includes source run id.
- L198 `class FailingAnalyzer` — Encapsulates failinganalyzer.
- L199 `async def analyze(self, **kwargs)` — Implements analyze.

### [`backend/tests/test_general_case_analysis.py`](../../backend/tests/test_general_case_analysis.py)

Purpose: Verifies general case analysis behavior in the backend regression suite.

- L25 `def reported_claim(text: str, *, supporting: list[str] | None=None, contradicting: list[str] | None=None, status: str='reported') -> dict[str, object]` — Implements reported claim.
- L43 `def provider_payload(claims: list[dict[str, object]], *, answer: str='Grounded case answer.', associations: list[dict[str, object]] | None=None) -> dict[str, object]` — Implements provider payload.
- L58 `def response_for(payload: dict[str, object]) -> httpx.Response` — Implements response for.
- L65 `def parse(payload: dict[str, object], *, sources: set[str] | None=None, context: dict[str, object] | None=None, mode: str='case_overview')` — Parses parse.
- L82 `def test_same_runtime_contract_handles_five_case_domains_without_required_mitre(domain: str, claim_text: str) -> None` — Implements test same runtime contract handles five case domains without required mitre.
- L96 `def test_property_case_preserves_conflicting_reported_sources() -> None` — Implements test property case preserves conflicting reported sources.
- L110 `def test_analytical_inference_retains_sources_and_visible_reasoning() -> None` — Implements test analytical inference retains sources and visible reasoning.
- L127 `def test_analytical_inference_without_authoritative_support_is_rejected() -> None` — Implements test analytical inference without authoritative support is rejected.
- L142 `def test_missing_information_remains_not_established() -> None` — Implements test missing information remains not established.
- L159 `def test_non_authoritative_sources_are_rejected(invalid_source: str) -> None` — Implements test non authoritative sources are rejected.
- L176 `def test_cyber_case_accepts_bound_optional_mitre_context() -> None` — Implements test cyber case accepts bound optional mitre context.
- L200 `def mitre_association() -> dict[str, object]` — Implements mitre association.
- L211 `def test_mitre_association_is_removed_without_admitted_rag() -> None` — Implements test mitre association is removed without admitted rag.
- L225 `def test_mitre_association_outside_admitted_context_is_rejected() -> None` — Implements test mitre association outside admitted context is rejected.
- L241 `def test_question_answer_mode_returns_direct_answer_with_v3_trace() -> None` — Implements test question answer mode returns direct answer with v3 trace.
- L254 `def test_invalid_provider_structure_uses_safe_trace_failure() -> None` — Implements test invalid provider structure uses safe trace failure.
- L265 `def test_service_requests_v3_schema_with_optional_external_context(monkeypatch) -> None` — Implements test service requests v3 schema with optional external context.
- L268 `class Client` — Encapsulates client.
- L269 `async def post(self, url, *, headers, json)` — Implements post.
- L304 `def test_claim_id_normalization_handles_variants() -> None` — Implements test claim id normalization handles variants.

### [`backend/tests/test_main_case_analysis.py`](../../backend/tests/test_main_case_analysis.py)

Purpose: Verifies main case analysis behavior in the backend regression suite.

- L18 `def payload_from_prompt(prompt: str) -> dict[str, object]` — Implements payload from prompt.
- L23 `def test_analysis_prompt_uses_raw_evidence_and_separates_external_context() -> None` — Implements test analysis prompt uses raw evidence and separates external context.
- L43 `def test_analysis_prompt_accepts_no_external_context() -> None` — Implements test analysis prompt accepts no external context.
- L56 `def test_general_prompt_removes_forced_cyber_analysis_sections() -> None` — Implements test general prompt removes forced cyber analysis sections.
- L68 `def test_prompt_preserves_epistemic_and_legal_boundaries() -> None` — Implements test prompt preserves epistemic and legal boundaries.
- L81 `def test_question_answer_prompt_requires_a_direct_proportionate_answer() -> None` — Implements test question answer prompt requires a direct proportionate answer.
- L87 `def test_question_mode_requires_a_question() -> None` — Implements test question mode requires a question.
- L92 `def test_overview_rejects_a_question() -> None` — Implements test overview rejects a question.

### [`backend/tests/test_migration_chat_only_cleanup.py`](../../backend/tests/test_migration_chat_only_cleanup.py)

Purpose: Verifies migration chat only cleanup behavior in the backend regression suite.

- L8 `def test_migration_chain_is_one_clean_demo_baseline() -> None` — Implements test migration chain is one clean demo baseline.
- L16 `def test_baseline_declares_only_surviving_tables() -> None` — Implements test baseline declares only surviving tables.

### [`backend/tests/test_mitre_applicability_pipeline.py`](../../backend/tests/test_mitre_applicability_pipeline.py)

Purpose: Verifies mitre applicability pipeline behavior in the backend regression suite.

- L17 `def claimed(content: str, *, action: str='initial_analysis')` — Implements claimed.
- L38 `async def run_fresh(value, gate, rag_request)` — Executes fresh.
- L41 `async def analysis_request(**kwargs)` — Implements analysis request.
- L45 `async def followup_evaluator(**kwargs)` — Implements followup evaluator.
- L61 `def test_skip_avoids_rag_and_main_analysis_continues() -> None` — Implements test skip avoids rag and main analysis continues.
- L65 `async def gate(**kwargs)` — Implements gate.
- L68 `async def rag_request(query: str)` — Implements rag request.
- L81 `def test_retrieve_invokes_rag_once_before_main_analysis() -> None` — Implements test retrieve invokes rag once before main analysis.
- L85 `async def gate(**kwargs)` — Implements gate.
- L93 `async def rag_request(query: str)` — Implements rag request.
- L110 `def test_gate_failure_fails_closed_without_blocking_analysis() -> None` — Implements test gate failure fails closed without blocking analysis.
- L114 `async def gate(**kwargs)` — Implements gate.
- L117 `async def rag_request(query: str)` — Implements rag request.
- L129 `def test_rag_failure_after_retrieve_does_not_block_analysis() -> None` — Implements test rag failure after retrieve does not block analysis.
- L132 `async def gate(**kwargs)` — Implements gate.
- L140 `async def rag_request(query: str)` — Implements rag request.
- L152 `def test_ask_does_not_rerun_gate_or_rag() -> None` — Implements test ask does not rerun gate or rag.
- L156 `async def analysis_request(**kwargs)` — Implements analysis request.
- L167 `def test_new_evidence_reevaluates_gate() -> None` — Implements test new evidence reevaluates gate.
- L170 `async def gate(**kwargs)` — Implements gate.
- L175 `async def rag_request(query: str)` — Implements rag request.
- L178 `async def scenario()` — Implements scenario.

### [`backend/tests/test_mitre_applicability_provider.py`](../../backend/tests/test_mitre_applicability_provider.py)

Purpose: Verifies mitre applicability provider behavior in the backend regression suite.

- L21 `def target() -> CoreLlmTarget` — Implements target.
- L32 `def test_gate_uses_fixed_prompt_strict_schema_and_deterministic_options(monkeypatch) -> None` — Implements test gate uses fixed prompt strict schema and deterministic options.
- L41 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.
- L73 `def test_malformed_provider_output_fails_closed(monkeypatch) -> None` — Implements test malformed provider output fails closed.
- L76 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.
- L97 `def test_provider_error_fails_closed(monkeypatch) -> None` — Implements test provider error fails closed.
- L100 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler.

### [`backend/tests/test_mitre_applicability_validation.py`](../../backend/tests/test_mitre_applicability_validation.py)

Purpose: Verifies mitre applicability validation behavior in the backend regression suite.

- L81 `def test_semantic_fixture_contract(case_name: str, content: str, decision: str, trigger: str | None) -> None` — Implements test semantic fixture contract.
- L98 `def test_mixed_sources_cite_only_the_cyber_source() -> None` — Implements test mixed sources cite only the cyber source.
- L116 `def test_multi_message_behavior_can_cite_each_authoritative_source() -> None` — Implements test multi message behavior can cite each authoritative source.
- L183 `def test_invalid_or_unattributable_output_fails_closed(payload: object) -> None` — Implements test invalid or unattributable output fails closed.
- L192 `def test_trigger_must_be_an_exact_source_span() -> None` — Implements test trigger must be an exact source span.

### [`backend/tests/test_model_registry.py`](../../backend/tests/test_model_registry.py)

Purpose: Unit tests for the OpenRouter model registry and alias resolver.

- L13 `def test_default_model()` — Implements test default model.
- L42 `def test_curated_aliases_resolution(alias: str, expected_canonical_id: str)` — Implements test curated aliases resolution.
- L48 `def test_custom_model_passthrough()` — Implements test custom model passthrough.
- L54 `def test_list_and_table_formatting()` — Implements test list and table formatting.

### [`backend/tests/test_optional_rag_pipeline.py`](../../backend/tests/test_optional_rag_pipeline.py)

Purpose: Verifies optional rag pipeline behavior in the backend regression suite.

- L25 `def claimed(case_text: str)` — Implements claimed.
- L41 `def result_for(value, *, retrieval_context_id=None, cyber=False)` — Implements result for.
- L82 `async def run_overview(value, rag_request, *, cyber=False)` — Executes overview.
- L85 `async def analysis_request(**kwargs)` — Implements analysis request.
- L96 `class Analyzer` — Encapsulates analyzer.
- L97 `async def analyze(self, **kwargs)` — Implements analyze.
- L102 `class Policy` — Encapsulates policy.
- L103 `async def decide(self, **kwargs)` — Implements decide.
- L106 `async def applicability_gate(**kwargs)` — Implements applicability gate.
- L126 `def test_theft_analysis_completes_when_rag_is_unavailable() -> None` — Implements test theft analysis completes when rag is unavailable.
- L129 `async def rag_request(query: str)` — Implements rag request.
- L150 `def test_fraud_analysis_completes_when_rag_has_no_usable_context() -> None` — Implements test fraud analysis completes when rag has no usable context.
- L153 `async def rag_request(query: str)` — Implements rag request.
- L168 `def test_cyber_analysis_preserves_successful_rag_and_mitre_binding() -> None` — Implements test cyber analysis preserves successful rag and mitre binding.
- L171 `async def rag_request(query: str)` — Implements rag request.
- L194 `class Transaction` — Encapsulates transaction.
- L195 `async def __aenter__(self)` — Implements aenter.
- L198 `async def __aexit__(self, exc_type, exc, traceback)` — Implements aexit.
- L202 `class CompletionDb` — Encapsulates completiondb.
- L203 `def __init__(self)` — Implements init.
- L206 `def begin(self)` — Implements begin.
- L209 `def add(self, value)` — Implements add.
- L212 `async def flush(self)` — Implements flush.
- L216 `def test_rag_failure_does_not_persist_a_fake_rag_context() -> None` — Implements test rag failure does not persist a fake rag context.
- L219 `async def rag_request(query: str)` — Implements rag request.
- L227 `async def lock_thread(run_id)` — Implements lock thread.
- L230 `async def lock_run(run_id, worker_id)` — Implements lock run.

### [`backend/tests/test_raw_evidence_workflow.py`](../../backend/tests/test_raw_evidence_workflow.py)

Purpose: Verifies raw evidence workflow behavior in the backend regression suite.

- L10 `def message(ordinal: int, content: str, evidence_kind: str) -> ChatMessage` — Implements message.
- L21 `def test_raw_evidence_is_chronological_and_excludes_questions() -> None` — Implements test raw evidence is chronological and excludes questions.
- L40 `def test_first_message_and_post_answer_actions_have_explicit_evidence_kinds() -> None` — Implements test first message and post answer actions have explicit evidence kinds.
- L55 `def test_answered_thread_requires_an_explicit_action() -> None` — Implements test answered thread requires an explicit action.
- L62 `def test_clarification_answer_is_evidence() -> None` — Implements test clarification answer is evidence.

### [`backend/tests/test_report_view_model_and_pdf.py`](../../backend/tests/test_report_view_model_and_pdf.py)

Purpose: Verifies report view model and pdf behavior in the backend regression suite.

- L14 `def make_realistic_report_read() -> tuple[ChatReportRead, str]` — Implements make realistic report read.
- L114 `def test_view_model_extracts_timeline_and_gaps_without_contradictions()` — Implements test view model extracts timeline and gaps without contradictions.
- L154 `def test_report_view_model_timeline_provenance_multi_source_and_fallback()` — Implements test report view model timeline provenance multi source and fallback.
- L225 `def test_pdf_generation_produces_valid_pdf_bytes()` — Implements test pdf generation produces valid pdf bytes.
- L232 `def test_html_rendering_contains_standalone_sections()` — Implements test html rendering contains standalone sections.

### [`backend/tests/test_route_surface.py`](../../backend/tests/test_route_surface.py)

Purpose: Verifies route surface behavior in the backend regression suite.

- L9 `def _fastapi_app() -> FastAPI` — Implements fastapi app.
- L16 `def test_health_chat_and_nested_report_api_routes_are_registered() -> None` — Implements test health chat and nested report api routes are registered.
- L43 `def test_legacy_route_prefixes_return_not_found_without_startup() -> None` — Implements test legacy route prefixes return not found without startup.
- L55 `def test_startup_tolerates_database_unavailability_without_live_database(monkeypatch) -> None` — Implements test startup tolerates database unavailability without live database.
- L58 `class _FailingConnection` — Encapsulates failingconnection.
- L59 `async def __aenter__(self)` — Implements aenter.
- L62 `async def __aexit__(self, exc_type, exc, traceback)` — Implements aexit.
- L65 `class _FakeEngine` — Encapsulates fakeengine.
- L66 `def __init__(self) -> None` — Implements init.
- L69 `def connect(self) -> _FailingConnection` — Implements connect.
- L72 `async def dispose(self) -> None` — Implements dispose.
- L78 `async def exercise_lifespan() -> None` — Implements exercise lifespan.

### [`backend/tests/test_stateful_clarification.py`](../../backend/tests/test_stateful_clarification.py)

Purpose: Verifies stateful clarification behavior in the backend regression suite.

- L25 `def item(topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, affects: str='A-01') -> GapItem` — Implements item.
- L44 `def canonical_gap(gap_id: str, topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, claims: list[str] | None=None) -> AnalysisGapV3` — Implements canonical gap.
- L65 `def exchange(topic: str, answer: str, *, gap_id: str='G-01') -> ClarificationExchange` — Implements exchange.
- L93 `def test_gap_key_normalization_is_bounded_and_cross_revision(left: str, right: str) -> None` — Implements test gap key normalization is bounded and cross revision.
- L100 `def test_priority_claim_link_and_stable_order_select_next_gap() -> None` — Implements test priority claim link and stable order select next gap.
- L114 `def test_no_gaps_unknown_low_or_unaskable_proceed_without_candidate() -> None` — Implements test no gaps unknown low or unaskable proceed without candidate.
- L133 `def test_answered_gap_key_survives_gap_and_claim_ordinal_changes() -> None` — Implements test answered gap key survives gap and claim ordinal changes.
- L150 `def test_unavailable_answer_transitions_missing_topic_to_explicit_unknown(answer: str) -> None` — Implements test unavailable answer transitions missing topic to explicit unknown.
- L163 `def test_exhausted_ambiguous_or_conflicting_gap_preserves_status(status: str) -> None` — Implements test exhausted ambiguous or conflicting gap preserves status.
- L173 `def test_gap_stage_applies_short_answer_topic_context_once() -> None` — Implements test gap stage applies short answer topic context once.
- L176 `class Analyzer` — Encapsulates analyzer.
- L177 `async def analyze(self, **kwargs)` — Implements analyze.
- L202 `def test_followup_round_limit_prevents_question_generation(monkeypatch) -> None` — Implements test followup round limit prevents question generation.
- L205 `class Analyzer` — Encapsulates analyzer.
- L206 `async def analyze(self, **kwargs)` — Implements analyze.
- L211 `class Policy` — Encapsulates policy.
- L212 `async def decide(self, **kwargs)` — Implements decide.
- L238 `def test_one_question_contract_rejects_compound_questions() -> None` — Implements test one question contract rejects compound questions.

### [`backend/tests/test_stateful_clarification_characterization.py`](../../backend/tests/test_stateful_clarification_characterization.py)

Purpose: Verifies stateful clarification characterization behavior in the backend regression suite.

- L16 `def gap(topic: str, *, priority: str='high', status: str='NOT_PROVIDED') -> GapItem` — Implements gap.
- L33 `class StaticAnalyzer` — Encapsulates staticanalyzer.
- L34 `def __init__(self, gaps: list[GapItem])` — Implements init.
- L37 `async def analyze(self, **kwargs)` — Implements analyze.
- L41 `class StaticPolicy` — Encapsulates staticpolicy.
- L42 `def __init__(self, topic: str, question: str)` — Implements init.
- L46 `async def decide(self, **kwargs)` — Implements decide.
- L54 `def test_unavailable_answer_exhausts_only_its_topic() -> None` — Implements test unavailable answer exhausts only its topic.
- L88 `def test_same_topic_is_not_reasked_with_different_wording() -> None` — Implements test same topic is not reasked with different wording.
- L114 `def test_clarification_chain_retains_structural_gap_context() -> None` — Implements test clarification chain retains structural gap context.
- L170 `def test_asked_question_metadata_carries_gap_identity() -> None` — Implements test asked question metadata carries gap identity.

### [`backend/tests/test_stateful_clarification_decisions.py`](../../backend/tests/test_stateful_clarification_decisions.py)

Purpose: Verifies stateful clarification decisions behavior in the backend regression suite.

- L16 `class Analyzer` — Encapsulates analyzer.
- L17 `def __init__(self, gaps: list[GapItem])` — Implements init.
- L20 `async def analyze(self, **kwargs)` — Implements analyze.
- L24 `class Policy` — Encapsulates policy.
- L25 `def __init__(self, topic: str, question: str)` — Implements init.
- L30 `async def decide(self, **kwargs)` — Implements decide.
- L39 `def gap(topic: str, status: str) -> GapItem` — Implements gap.
- L51 `def test_no_gaps_proceeds_without_question_generation() -> None` — Implements test no gaps proceeds without question generation.
- L86 `def test_ambiguous_and_conflicting_gaps_allow_one_neutral_question(status: str, question: str, reason_code: str) -> None` — Implements test ambiguous and conflicting gaps allow one neutral question.
- L109 `def test_resolved_gap_disappearance_does_not_keep_old_task_active() -> None` — Implements test resolved gap disappearance does not keep old task active.

### [`backend/tests/test_stateful_clarification_domains.py`](../../backend/tests/test_stateful_clarification_domains.py)

Purpose: Verifies stateful clarification domains behavior in the backend regression suite.

- L24 `def case_value(content: str)` — Implements case value.
- L41 `def analysis(value, retrieval_id: str | None=None) -> CaseAnalysisResult` — Implements analysis.
- L64 `class Analyzer` — Encapsulates analyzer.
- L65 `def __init__(self, topic: str)` — Implements init.
- L69 `async def analyze(self, **kwargs)` — Implements analyze.
- L88 `class Policy` — Encapsulates policy.
- L89 `def __init__(self, topic: str)` — Implements init.
- L93 `async def decide(self, **kwargs)` — Implements decide.
- L102 `async def skip_gate(**kwargs)` — Implements skip gate.
- L116 `def test_general_case_domains_select_canonical_gap_without_mitre(case_text: str, topic: str) -> None` — Implements test general case domains select canonical gap without mitre.
- L124 `async def analysis_request(**kwargs)` — Implements analysis request.
- L128 `async def no_rag(query: str)` — Implements no rag.
- L149 `def test_cyber_followup_does_not_depend_on_rag_availability(rag_mode: str) -> None` — Implements test cyber followup does not depend on rag availability.
- L154 `async def retrieve_gate(**kwargs)` — Implements retrieve gate.
- L162 `async def rag_request(query: str)` — Implements rag request.
- L172 `async def analysis_request(**kwargs)` — Implements analysis request.

### [`backend/tests/test_stateful_clarification_metadata.py`](../../backend/tests/test_stateful_clarification_metadata.py)

Purpose: Verifies stateful clarification metadata behavior in the backend regression suite.

- L12 `def test_raw_evidence_hash_ignores_workflow_context_and_assistant_question() -> None` — Implements test raw evidence hash ignores workflow context and assistant question.
- L64 `def test_followup_position_copies_question_context_to_answer_metadata() -> None` — Implements test followup position copies question context to answer metadata.
- L97 `class Scalars` — Encapsulates scalars.
- L98 `def all(self)` — Implements all.
- L101 `class Result` — Encapsulates result.
- L102 `def scalars(self)` — Implements scalars.
- L105 `class Database` — Encapsulates database.
- L106 `async def execute(self, statement)` — Executes execute.
- L129 `def test_short_answer_context_is_structural_and_does_not_rewrite_user_content() -> None` — Implements test short answer context is structural and does not rewrite user content.
- L153 `def test_mismatched_answer_context_cannot_override_asked_gap_topic() -> None` — Implements test mismatched answer context cannot override asked gap topic.

### [`backend/tests/test_stateful_clarification_pipeline.py`](../../backend/tests/test_stateful_clarification_pipeline.py)

Purpose: Verifies stateful clarification pipeline behavior in the backend regression suite.

- L22 `def claimed(content: str, *, exchanges: tuple[ClarificationExchange, ...]=())` — Implements claimed.
- L46 `def analysis(value, retrieval_context_id: str | None=None) -> CaseAnalysisResult` — Implements analysis.
- L71 `def gap(topic: str, *, priority: str='high') -> GapItem` — Implements gap.
- L83 `async def skip_gate(**kwargs)` — Implements skip gate.
- L87 `class Analyzer` — Encapsulates analyzer.
- L88 `def __init__(self, gaps: list[GapItem])` — Implements init.
- L92 `async def analyze(self, **kwargs)` — Implements analyze.
- L97 `class Policy` — Encapsulates policy.
- L98 `def __init__(self, topic: str, question: str)` — Implements init.
- L103 `async def decide(self, **kwargs)` — Implements decide.
- L114 `def test_valid_v3_pipeline_uses_one_gap_call_and_one_question_call() -> None` — Implements test valid v3 pipeline uses one gap call and one question call.
- L123 `async def analysis_request(**kwargs)` — Implements analysis request.
- L128 `async def no_rag(query: str)` — Implements no rag.
- L158 `def test_invalid_main_trace_never_runs_gap_or_followup_provider() -> None` — Implements test invalid main trace never runs gap or followup provider.
- L163 `async def analysis_request(**kwargs)` — Implements analysis request.
- L188 `def test_short_unknown_reruns_analysis_and_gap_once_then_selects_next_topic() -> None` — Implements test short unknown reruns analysis and gap once then selects next topic.
- L206 `async def analysis_request(**kwargs)` — Implements analysis request.

### [`backend/tests/test_structured_output.py`](../../backend/tests/test_structured_output.py)

Purpose: Verifies structured output behavior in the backend regression suite.

- L10 `def test_report_schema_is_provider_compatible() -> None` — Implements test report schema is provider compatible.
- L17 `def test_analysis_trace_v2_schema_exposes_source_message_references() -> None` — Implements test analysis trace v2 schema exposes source message references.
- L24 `def test_analysis_trace_v3_provider_schema_exposes_grounded_claim_roles() -> None` — Implements test analysis trace v3 provider schema exposes grounded claim roles.

## Research And Evaluation Workspace

### [`deliverables/cybercase-report-followup-gap-study/scripts/validate_cases.py`](../../deliverables/cybercase-report-followup-gap-study/scripts/validate_cases.py)

Purpose: Validate CyberCase evaluation JSON files against schema and semantic invariants.

- L26 `def _json_path(parts: Iterable[Any]) -> str` — Implements json path.
- L33 `def _duplicates(values: Iterable[str]) -> set[str]` — Implements duplicates.
- L38 `def _state_map(claim: dict[str, Any]) -> tuple[dict[str, str], set[str]]` — Implements state map.
- L51 `def schema_errors(document: Any, schema: dict[str, Any]) -> list[str]` — Implements schema errors.
- L54 `def leaf_errors(error: Any) -> Iterable[Any]` — Implements leaf errors.
- L73 `def semantic_errors(document: Any) -> list[str]` — Return cross-field errors that JSON Schema cannot express.
- L178 `def check_refs(values: Any, allowed: set[str], path: str, ref_name: str) -> None` — Validates refs.
- L524 `def validate_document(document: Any, schema: dict[str, Any]) -> list[str]` — Validate one already-loaded document; useful for tests and mutation checks.
- L530 `def _expand_paths(arguments: list[str]) -> list[Path]` — Implements expand paths.
- L538 `def _set_claim_state(document: dict[str, Any], claim_id: str, variant: str, state: str) -> None` — Updates claim state.
- L551 `def run_self_test(schema: dict[str, Any]) -> int` — Run permanent valid-fixture and negative-mutation checks.
- L663 `def main(argv: list[str] | None=None) -> int` — Implements main.

### [`evaluation/analysis_pilot/__init__.py`](../../evaluation/analysis_pilot/__init__.py)

Purpose: Analysis-isolation evaluation pilot package: RAW_DIRECT vs EXTRACTED_STATE.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`evaluation/analysis_pilot/config.py`](../../evaluation/analysis_pilot/config.py)

Purpose: Configuration for the analysis-isolation evaluation pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`evaluation/analysis_pilot/dataset.py`](../../evaluation/analysis_pilot/dataset.py)

Purpose: Dataset loader and deterministic stratified sampling for the pilot.

- L12 `def load_all_cases(path: Path=DATASET_PATH) -> list[dict[str, Any]]` — Load all cases from the semantic verification JSONL file.
- L26 `def select_stratified_pilot_cases(cases: list[dict[str, Any]] | None=None, count: int=10) -> list[dict[str, Any]]` — Select stratified cases across scenarios and languages deterministically.

### [`evaluation/analysis_pilot/generator.py`](../../evaluation/analysis_pilot/generator.py)

Purpose: Analysis generator for RAW_DIRECT and EXTRACTED_STATE conditions.

- L43 `async def generate_analysis(*, case_info_text: str, condition: str, case: dict[str, Any], model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE, max_output_tokens: int=ANALYSIS_MAX_OUTPUT_TOKENS) -> GenerationRecord` — Run the analysis generation LLM call with strict structured output.
- L201 `async def run_raw_direct_condition(case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE) -> GenerationRecord` — Condition A: RAW_DIRECT.
- L218 `async def run_extracted_state_condition(case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE) -> tuple[GenerationRecord, ExtractionLogRecord]` — Condition B: EXTRACTED_STATE.

### [`evaluation/analysis_pilot/judge.py`](../../evaluation/analysis_pilot/judge.py)

Purpose: Single-probe binary LLM judge for evaluation probes.

- L31 `async def judge_single_probe(*, analysis_output: CaseAnalysisOutput | None, probe: dict[str, Any], case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE) -> ProbeJudgmentRecord` — Evaluate whether a generated case analysis semantically asserts/entails a single probe claim.
- L168 `async def judge_all_case_probes(*, analysis_output: CaseAnalysisOutput | None, case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE, concurrency: int=4) -> list[ProbeJudgmentRecord]` — Evaluate all verification pair probes for a single case under a given condition.
- L181 `async def _eval_one(probe: dict[str, Any]) -> ProbeJudgmentRecord` — Implements eval one.

### [`evaluation/analysis_pilot/metrics.py`](../../evaluation/analysis_pilot/metrics.py)

Purpose: Metric computations for Supported Probe Coverage, Epistemic Violations, and Factual Errors.

- L13 `def compute_case_metrics(judgments: list[ProbeJudgmentRecord]) -> dict[str, Any]` — Compute supported probe coverage, epistemic violation rates, and factual error rates for a single case.
- L81 `def compute_aggregate_metrics(case_metrics_list: list[dict[str, Any]]) -> dict[str, Any]` — Compute macro-averages and breakdown across all cases for a condition.

### [`evaluation/analysis_pilot/prompts.py`](../../evaluation/analysis_pilot/prompts.py)

Purpose: Unified prompts for analysis generation and single-probe binary judging.

- L46 `def get_prompt_hash(system_prompt: str, user_content: str) -> str` — Return SHA-256 hash of the full prompt content for provenance tracking.

### [`evaluation/analysis_pilot/runner.py`](../../evaluation/analysis_pilot/runner.py)

Purpose: Main evaluation pilot orchestrator and CLI entrypoint.

- L58 `def write_jsonl(path: Path, records: list[Any]) -> None` — Write list of Pydantic models or dicts to JSONL file.
- L70 `def generate_summary_markdown(raw_agg: dict[str, Any], ext_agg: dict[str, Any], case_results: list[dict[str, Any]], model_name: str, judge_model: str, selected_cases: list[dict[str, Any]]) -> str` — Format markdown summary table and per-case results.
- L107 `def _fmt_ep(ep_dict: dict[str, Any], key: str) -> str` — Implements fmt ep.
- L167 `async def run_single_case(case: dict[str, Any], *, model: str, judge_model: str, output_dir: Path) -> dict[str, Any]` — Execute both conditions and evaluate probes for a single case.
- L236 `async def run_pipeline(*, sanity_check: bool=False, model: str=DEFAULT_ANALYSIS_MODEL, judge_model: str=DEFAULT_JUDGE_MODEL, case_count: int=10, output_dir: Path=DEFAULT_OUTPUT_DIR) -> None` — Main pipeline execution orchestrator.
- L390 `def main() -> None` — Implements main.

### [`evaluation/analysis_pilot/schemas.py`](../../evaluation/analysis_pilot/schemas.py)

Purpose: Data schemas for analysis outputs, extraction logs, probe evaluations, and metrics.

- L18 `class Finding(BaseModel)` — A distinct analytical finding with an associated epistemic status.
- L36 `class CaseAnalysisOutput(BaseModel)` — Structured evaluation output schema for case analysis generation.
- L51 `class JudgeResponse(BaseModel)` — Structured output schema for the binary probe judge.
- L65 `class GenerationRecord(BaseModel)` — Full machine-readable log of an analysis generation call.
- L87 `class ExtractionLogRecord(BaseModel)` — Machine-readable record of production extraction step.
- L105 `class ProbeJudgmentRecord(BaseModel)` — Machine-readable log of an individual probe evaluation.

### [`experiments/__init__.py`](../../experiments/__init__.py)

Purpose: Isolated research experiments for CyberCase.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/context_refinement/__init__.py`](../../experiments/context_refinement/__init__.py)

Purpose: Isolated paired context-refinement experiment.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/context_refinement/__main__.py`](../../experiments/context_refinement/__main__.py)

Purpose: Owns main behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/context_refinement/cli.py`](../../experiments/context_refinement/cli.py)

Purpose: Owns cli behavior for the research and evaluation workspace.

- L14 `def _common_data_arguments(parser: argparse.ArgumentParser) -> None` — Implements common data arguments.
- L20 `def build_parser() -> argparse.ArgumentParser` — Builds parser.
- L44 `def main(argv: list[str] | None=None) -> None` — Implements main.

### [`experiments/context_refinement/compressor.py`](../../experiments/context_refinement/compressor.py)

Purpose: Owns compressor behavior for the research and evaluation workspace.

- L12 `class CompressorFailure(RuntimeError)` — Encapsulates compressorfailure.
- L16 `class LLMLingua2Refiner` — Encapsulates llmlingua2refiner.
- L19 `def __init__(self, model_name: str=DEFAULT_COMPRESSOR_MODEL, compression_rate: float=DEFAULT_COMPRESSION_RATE, device_map: str='cpu') -> None` — Implements init.
- L53 `def refine(self, context: str) -> RefinedContext` — Implements refine.
- L77 `def _as_int(value: Any) -> int | None` — Implements as int.

### [`experiments/context_refinement/contracts.py`](../../experiments/context_refinement/contracts.py)

Purpose: Owns contracts behavior for the research and evaluation workspace.

- L8 `class RefinedContext` — Encapsulates refinedcontext.
- L15 `class ContextRefiner(Protocol)` — Encapsulates contextrefiner.
- L19 `def refine(self, context: str) -> RefinedContext` — Implements refine.

### [`experiments/context_refinement/dataset.py`](../../experiments/context_refinement/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

- L23 `def sha256_file(path: Path) -> str` — Implements sha256 file.
- L31 `def _selection_ids(path: Path) -> list[str]` — Implements selection ids.
- L39 `def _row_language(row: dict[str, Any]) -> str` — Implements row language.
- L43 `def load_reused_subset(benchmark_path: Path, selection_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]` — Retrieves reused subset.
- L85 `def gold_text(row: dict[str, Any]) -> str` — Implements gold text.

### [`experiments/context_refinement/evaluation.py`](../../experiments/context_refinement/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

- L10 `def _ratio(numerator: int, denominator: int) -> float` — Implements ratio.
- L14 `def evaluate_pairs(rows: list[dict[str, Any]], raw_contexts: dict[str, dict[str, Any]], refined_contexts: dict[str, dict[str, Any]], predictions: dict[tuple[str, str], dict[str, Any]], sbert_model: Any) -> list[dict[str, Any]]` — Implements evaluate pairs.

### [`experiments/context_refinement/llm_client.py`](../../experiments/context_refinement/llm_client.py)

Purpose: Owns llm client behavior for the research and evaluation workspace.

- L17 `class OpenRouterPilotClient` — Encapsulates openrouterpilotclient.
- L22 `def __init__(self, api_key_env: str='OPENROUTER_API_KEY', base_url: str=DEFAULT_BASE_URL, timeout: float=120.0, max_attempts: int=5, backoff_base: float=1.0) -> None` — Implements init.
- L42 `def __enter__(self) -> 'OpenRouterPilotClient'` — Implements enter.
- L56 `def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None` — Implements exit.
- L61 `def predict(self, prompt: str, sample_id: str, condition: str) -> dict[str, Any]` — Implements predict.

### [`experiments/context_refinement/metrics.py`](../../experiments/context_refinement/metrics.py)

Purpose: Owns metrics behavior for the research and evaluation workspace.

- L6 `def load_sbert_model(model_name: str, device: str) -> Any` — Retrieves sbert model.
- L14 `def score_condition(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], condition: str, sbert_model: Any) -> dict[str, dict[str, float]]` — Implements score condition.

### [`experiments/context_refinement/prompting.py`](../../experiments/context_refinement/prompting.py)

Purpose: Owns prompting behavior for the research and evaluation workspace.

- L8 `def build_condition_prompt(row: dict[str, Any], context: str) -> str` — Builds condition prompt.
- L14 `def prompt_template_parts(row: dict[str, Any], raw_context: str, refined_context: str) -> tuple[str, str, str, str]` — Implements prompt template parts.
- L26 `def validate_context_only_prompt_change(row: dict[str, Any], raw_context: str, refined_context: str) -> None` — Validates context only prompt change.

### [`experiments/context_refinement/protected_spans.py`](../../experiments/context_refinement/protected_spans.py)

Purpose: Owns protected spans behavior for the research and evaluation workspace.

- L27 `def extract_protected_spans(text: str) -> list[dict[str, Any]]` — Extracts protected spans.
- L41 `def compare_protected_spans(raw_context: str, refined_context: str) -> dict[str, Any]` — Implements compare protected spans.

### [`experiments/context_refinement/reporting.py`](../../experiments/context_refinement/reporting.py)

Purpose: Owns reporting behavior for the research and evaluation workspace.

- L9 `def _percentile(values: list[float], percentile: float) -> float` — Implements percentile.
- L20 `def _metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements metric stats.
- L30 `def _group_metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements group metric stats.
- L37 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary.
- L85 `def _sum_span_types(records: list[dict[str, Any]], field: str) -> dict[str, int]` — Implements sum span types.
- L93 `def _ranked_examples(deltas: list[dict[str, Any]], group: str) -> list[dict[str, Any]]` — Implements ranked examples.
- L104 `def render_markdown(summary: dict[str, Any]) -> str` — Renders markdown.

### [`experiments/context_refinement/reproducibility.py`](../../experiments/context_refinement/reproducibility.py)

Purpose: Owns reproducibility behavior for the research and evaluation workspace.

- L11 `def set_deterministic_seed(seed: int) -> dict[str, Any]` — Updates deterministic seed.
- L30 `def runtime_device_report() -> dict[str, Any]` — Implements runtime device report.

### [`experiments/context_refinement/runner.py`](../../experiments/context_refinement/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L29 `def _raw_context_record(row: dict[str, Any]) -> dict[str, Any]` — Implements raw context record.
- L42 `def _refined_context_record(row: dict[str, Any], result: Any, refiner_config: dict[str, Any]) -> dict[str, Any]` — Implements refined context record.
- L62 `def _ensure_raw_contexts(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]` — Implements ensure raw contexts.
- L76 `def _ensure_refined_contexts(rows: list[dict[str, Any]], path: Path, refiner: LLMLingua2Refiner) -> dict[str, dict[str, Any]]` — Implements ensure refined contexts.
- L98 `def _prediction_record(row: dict[str, Any], condition: str, context: str, prompt: str, response: dict[str, Any]) -> dict[str, Any]` — Implements prediction record.
- L119 `def _ensure_predictions(rows: list[dict[str, Any]], condition: str, contexts: dict[str, dict[str, Any]], prediction_path: Path, client: OpenRouterPilotClient, existing: dict[tuple[str, str], dict[str, Any]]) -> None` — Implements ensure predictions.
- L145 `def _run_config(args: Any, dataset_manifest: dict[str, Any], runtime: dict[str, Any], seed_report: dict[str, Any]) -> dict[str, Any]` — Executes config.
- L188 `def _write_report(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], sbert_model_name: str, sbert_device: str) -> None` — Implements write report.
- L203 `def run_experiment(args: Any) -> None` — Executes experiment.
- L243 `def report_existing(args: Any) -> None` — Implements report existing.

### [`experiments/context_refinement/storage.py`](../../experiments/context_refinement/storage.py)

Purpose: Owns storage behavior for the research and evaluation workspace.

- L9 `def read_jsonl(path: Path) -> list[dict[str, Any]]` — Retrieves jsonl.
- L24 `def index_records(path: Path, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]` — Implements index records.
- L34 `def append_jsonl(path: Path, record: dict[str, Any]) -> None` — Implements append jsonl.
- L42 `def write_json(path: Path, value: Any) -> None` — Implements write json.
- L47 `def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None` — Implements write jsonl.
- L58 `def write_or_validate_json(path: Path, value: Any) -> None` — Implements write or validate json.

### [`experiments/context_refinement/tests/__init__.py`](../../experiments/context_refinement/tests/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/context_refinement/tests/test_dataset_and_storage.py`](../../experiments/context_refinement/tests/test_dataset_and_storage.py)

Purpose: Verifies dataset and storage behavior in the research and evaluation workspace.

- L11 `class DatasetAndStorageTests(unittest.TestCase)` — Encapsulates datasetandstoragetests.
- L12 `def test_existing_selection_is_reused_then_filtered(self) -> None` — Implements test existing selection is reused then filtered.
- L41 `def test_jsonl_index_rejects_duplicate_keys(self) -> None` — Implements test jsonl index rejects duplicate keys.

### [`experiments/context_refinement/tests/test_prompt_and_spans.py`](../../experiments/context_refinement/tests/test_prompt_and_spans.py)

Purpose: Verifies prompt and spans behavior in the research and evaluation workspace.

- L12 `class PromptAndSpanTests(unittest.TestCase)` — Encapsulates promptandspantests.
- L13 `def test_prompt_changes_only_context(self) -> None` — Implements test prompt changes only context.
- L28 `def test_protected_span_diagnostics_are_explicit(self) -> None` — Implements test protected span diagnostics are explicit.

### [`experiments/ctinexus_extraction_benchmark/__init__.py`](../../experiments/ctinexus_extraction_benchmark/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/__main__.py`](../../experiments/ctinexus_extraction_benchmark/__main__.py)

Purpose: Owns main behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/cache.py`](../../experiments/ctinexus_extraction_benchmark/cache.py)

Purpose: Owns cache behavior for the research and evaluation workspace.

- L11 `def load_jsonl_cache(path: Path) -> dict[str, ExtractorPrediction]` — Retrieves jsonl cache.
- L26 `def cache_matches(record: ExtractorPrediction, *, condition: str, doc_id: str, narrative_sha256: str, contract: dict[str, Any]) -> bool` — Implements cache matches.
- L46 `def append_jsonl(path: Path, record: ExtractorPrediction) -> None` — Implements append jsonl.
- L55 `def write_json(path: Path, payload: Any) -> None` — Implements write json.

### [`experiments/ctinexus_extraction_benchmark/constants.py`](../../experiments/ctinexus_extraction_benchmark/constants.py)

Purpose: Owns constants behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/dataset.py`](../../experiments/ctinexus_extraction_benchmark/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

- L18 `class GoldEntity` — Encapsulates goldentity.
- L24 `class GoldRelation` — Encapsulates goldrelation.
- L31 `class CTINexusCase` — Encapsulates ctinexuscase.
- L38 `def sha256_text(value: str) -> str` — Implements sha256 text.
- L42 `def _raw_entities(raw: dict[str, Any]) -> list[GoldEntity]` — Implements raw entities.
- L54 `def _raw_relations(raw: dict[str, Any]) -> list[GoldRelation]` — Implements raw relations.
- L70 `def _load_raw_document(path: Path) -> dict[str, Any]` — Retrieves raw document.
- L77 `def load_ctinexus_cases(dataset_dir: str | Path) -> list[CTINexusCase]` — Retrieves ctinexus cases.
- L94 `def dataset_manifest(cases: list[CTINexusCase], dataset_dir: str | Path) -> dict[str, Any]` — Implements dataset manifest.

### [`experiments/ctinexus_extraction_benchmark/evaluation.py`](../../experiments/ctinexus_extraction_benchmark/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

- L16 `def _stats(values: list[float]) -> dict[str, float | int | None]` — Implements stats.
- L31 `def _coverage(predictions: Iterable[ExtractorPrediction]) -> dict[str, object]` — Implements coverage.
- L48 `def _latency(predictions: Iterable[ExtractorPrediction], condition: str) -> dict[str, object]` — Implements latency.
- L71 `def _example(doc_id: str, category: str, values: object) -> dict[str, object]` — Implements example.
- L75 `def _error_examples(cases: list[CTINexusCase], evaluations: dict[str, DocumentEvaluation], predictions: dict[str, ExtractorPrediction]) -> dict[str, list[dict[str, object]]]` — Implements error examples.
- L128 `def evaluate_condition(cases: list[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str) -> tuple[dict[str, object], list[dict[str, object]]]` — Implements evaluate condition.
- L148 `def combined_error_examples(cases: list[CTINexusCase], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], e1_predictions: dict[str, ExtractorPrediction], e2_predictions: dict[str, ExtractorPrediction]) -> dict[str, list[dict[str, object]]]` — Implements combined error examples.

### [`experiments/ctinexus_extraction_benchmark/gliner.py`](../../experiments/ctinexus_extraction_benchmark/gliner.py)

Purpose: Owns gliner behavior for the research and evaluation workspace.

- L19 `def resolve_device(requested: str) -> str` — Implements resolve device.
- L27 `def _confidence_values(items: list[TypedEntityPrediction], relations: list[TypedRelationPrediction]) -> list[float]` — Implements confidence values.
- L33 `def _distribution(values: list[float]) -> dict[str, float | int | None]` — Implements distribution.
- L48 `def _field_value(value: Any) -> Any` — Implements field value.
- L54 `class CtinexusGlinerExtractor` — Encapsulates ctinexusglinerextractor.
- L55 `def __init__(self, *, model_name: str=GLINER_MODEL, device: str='auto', threshold: float=GLINER_THRESHOLD) -> None` — Implements init.
- L72 `def _ground(self, source: str, value: Any) -> dict[str, Any] | None` — Implements ground.
- L75 `def _extract_entities(self, source: str) -> tuple[list[TypedEntityPrediction], list[dict[str, Any]]]` — Extracts entities.
- L113 `def _extract_relations(self, source: str) -> tuple[list[TypedRelationPrediction], list[dict[str, Any]]]` — Extracts relations.
- L152 `def extract(self, case: CTINexusCase)` — Extracts extract.

### [`experiments/ctinexus_extraction_benchmark/production.py`](../../experiments/ctinexus_extraction_benchmark/production.py)

Purpose: Owns production behavior for the research and evaluation workspace.

- L23 `def _api_call_count(result: Any, serialized_input_length: int) -> int` — Implements api call count.
- L36 `async def extract_production(case: CTINexusCase, model: str=PRODUCTION_MODEL)` — Extracts production.

### [`experiments/ctinexus_extraction_benchmark/projection.py`](../../experiments/ctinexus_extraction_benchmark/projection.py)

Purpose: Owns projection behavior for the research and evaluation workspace.

- L16 `def _dedupe(values: Iterable[str]) -> list[str]` — Implements dedupe.
- L20 `def _prediction(*, condition: str, case: CTINexusCase, model: str, graph: PredictedGraph, typed_entities: list[TypedEntityPrediction], typed_relations: list[TypedRelationPrediction], diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements prediction.
- L45 `def production_prediction(case: CTINexusCase, extraction: Any, *, model: str, status: str, failure_code: str | None, failure_message: str | None, latency_ms: float, input_tokens: int | None, output_tokens: int | None, diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements production prediction.
- L115 `def gliner_prediction(case: CTINexusCase, *, model: str, entities: list[TypedEntityPrediction], relations: list[TypedRelationPrediction], latency_ms: float, diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements gliner prediction.
- L144 `def _dedupe_triplets(relations: list[TypedRelationPrediction]) -> list[tuple[str, str, str]]` — Implements dedupe triplets.
- L148 `def _dedupe_edges(relations: list[TypedRelationPrediction]) -> list[tuple[str, str]]` — Implements dedupe edges.

### [`experiments/ctinexus_extraction_benchmark/report.py`](../../experiments/ctinexus_extraction_benchmark/report.py)

Purpose: Owns report behavior for the research and evaluation workspace.

- L10 `def _metric(summary: dict[str, Any], block: str, field: str) -> float` — Implements metric.
- L14 `def _comparison_rows(e1: dict[str, Any], e2: dict[str, Any]) -> list[tuple[str, str, str, str]]` — Implements comparison rows.
- L34 `def _markdown_table(headers: list[str], rows: list[list[str]]) -> str` — Implements markdown table.
- L41 `def _category_table(condition: str, rows: list[dict[str, Any]], key: str) -> str` — Implements category table.
- L50 `def _summary_payload(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> dict[str, Any]` — Implements summary payload.
- L68 `def _markdown(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> str` — Implements markdown.
- L152 `def write_report(output_dir: Path, manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], errors: dict[str, Any]) -> dict[str, Any]` — Implements write report.

### [`experiments/ctinexus_extraction_benchmark/runner.py`](../../experiments/ctinexus_extraction_benchmark/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L38 `def _contracts(config: dict[str, Any]) -> dict[str, dict[str, Any]]` — Implements contracts.
- L54 `def _config(output_dir: Path, dataset_dir: Path, gliner_device: str) -> dict[str, Any]` — Implements config.
- L84 `def _verify_config(output_dir: Path, config: dict[str, Any]) -> None` — Validates config.
- L100 `def _offline_e1(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction` — Implements offline e1.
- L116 `def _offline_e2(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction` — Implements offline e2.
- L133 `async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]` — Executes benchmark.
- L190 `def _confidence_summary(predictions: dict[str, ExtractorPrediction]) -> dict[str, object]` — Implements confidence summary.
- L197 `def parse_args() -> argparse.Namespace` — Parses args.
- L206 `def main() -> None` — Implements main.

### [`experiments/ctinexus_extraction_benchmark/runtime.py`](../../experiments/ctinexus_extraction_benchmark/runtime.py)

Purpose: Owns runtime behavior for the research and evaluation workspace.

- L12 `def prepare_runtime() -> None` — Implements prepare runtime.

### [`experiments/ctinexus_extraction_benchmark/schemas.py`](../../experiments/ctinexus_extraction_benchmark/schemas.py)

Purpose: Owns schemas behavior for the research and evaluation workspace.

- L10 `class TypedEntityPrediction(BaseModel)` — Encapsulates typedentityprediction.
- L20 `class TypedRelationPrediction(BaseModel)` — Encapsulates typedrelationprediction.
- L35 `class ExtractorPrediction(BaseModel)` — Encapsulates extractorprediction.

### [`experiments/ctinexus_extraction_benchmark/type_mapping.py`](../../experiments/ctinexus_extraction_benchmark/type_mapping.py)

Purpose: Owns type mapping behavior for the research and evaluation workspace.

- L33 `def _key(value: str) -> str` — Implements key.
- L37 `def map_production_entity_type(value: str) -> str | None` — Transforms production entity type.

### [`experiments/ctinexus_extraction_benchmark/typed_metrics.py`](../../experiments/ctinexus_extraction_benchmark/typed_metrics.py)

Purpose: Owns typed metrics behavior for the research and evaluation workspace.

- L15 `def _mapped_type(condition: str, value: str) -> str | None` — Implements mapped type.
- L21 `def _sets_for_entity_type(case: CTINexusCase, prediction: ExtractorPrediction, condition: str)` — Implements sets for entity type.
- L36 `def entity_type_metrics(cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str) -> tuple[list[dict[str, object]], dict[str, int]]` — Implements entity type metrics.
- L69 `def relation_type_metrics(cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction]) -> list[dict[str, object]]` — Implements relation type metrics.

### [`experiments/followup_pilot/__init__.py`](../../experiments/followup_pilot/__init__.py)

Purpose: One-case pilot comparing no follow-up with adaptive clarification.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/followup_pilot/evaluator.py`](../../experiments/followup_pilot/evaluator.py)

Purpose: Blind, interactive manual evaluator for two pilot result files.

- L43 `class ShuffleLike(Protocol)` — Encapsulates shufflelike.
- L44 `def shuffle(self, values: list[ExperimentResult]) -> None` — Implements shuffle.
- L47 `def utc_now() -> datetime` — Implements utc now.
- L51 `def load_result(path: Path) -> ExperimentResult` — Retrieves result.
- L55 `def exact_duplicate_question_count(result: ExperimentResult) -> int` — Implements exact duplicate question count.
- L60 `def recovered_hidden_fields(result: ExperimentResult) -> set[str]` — Implements recovered hidden fields.
- L70 `def calculate_metrics(*, case: PilotCase, result: ExperimentResult, field_scores: dict[str, FieldRating]) -> SystemMetrics` — Implements calculate metrics.
- L98 `def _prompt_rating(*, system_label: str, field: str, input_fn: InputCallable, output_fn: OutputCallable) -> FieldRating` — Implements prompt rating.
- L115 `def conduct_blind_evaluation(*, case: PilotCase, results: Sequence[ExperimentResult], input_fn: InputCallable=input, output_fn: OutputCallable=print, rng: ShuffleLike | None=None) -> EvaluationResult` — Implements conduct blind evaluation.
- L185 `def save_evaluation(evaluation: EvaluationResult, path: Path) -> Path` — Persists evaluation.
- L194 `def build_argument_parser() -> argparse.ArgumentParser` — Builds argument parser.
- L202 `def main() -> None` — Implements main.

### [`experiments/followup_pilot/runner.py`](../../experiments/followup_pilot/runner.py)

Purpose: Terminal runner for the bounded follow-up pilot.

- L52 `class FollowUpPolicyLike(Protocol)` — Encapsulates followuppolicylike.
- L53 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]) -> FollowUpDecision` — Implements decide.
- L62 `class HumanAnswer` — Encapsulates humananswer.
- L71 `def utc_now() -> datetime` — Implements utc now.
- L75 `def load_case(path: Path) -> PilotCase` — Retrieves case.
- L79 `def build_initial_query(case: PilotCase) -> str` — Build the one frozen initial query shared by both conditions.
- L88 `def _normalize_question(question: str) -> str` — Normalizes question.
- L92 `async def _timed_rag_call(*, query: str, round_number: int, rag_call: RagCallable) -> tuple[QueryResponse, RagCallRecord]` — Implements timed rag call.
- L111 `def _interactive_answer_provider(*, input_fn: InputCallable, output_fn: OutputCallable) -> AnswerProvider` — Implements interactive answer provider.
- L116 `def provide(case: PilotCase, round_number: int, question: str) -> HumanAnswer` — Implements provide.
- L155 `def print_answer_sheet(case: PilotCase, output_fn: OutputCallable=print) -> None` — Implements print answer sheet.
- L162 `async def _build_result(*, case: PilotCase, method: Method, policy_position: str, policy_calls: int, started_at: datetime, total_started: float, questions: list[QuestionRecord], current_query: str, latest_response: QueryResponse, stopped_by: str, failure_reason: str | None, rag_calls: list[RagCallRecord], experiment_id: str | None, rag_model: str, followup_model: str) -> ExperimentResult` — Builds result.
- L204 `def _get_answer_provider(*, case: PilotCase, answer_provider: AnswerProvider | None, input_fn: InputCallable, output_fn: OutputCallable) -> AnswerProvider` — Retrieves answer provider.
- L217 `async def _decide(policy: FollowUpPolicyLike, *, original_user_content: str, exchanges: Sequence[ClarificationExchange]) -> FollowUpDecision` — Implements decide.
- L230 `def _record_answer(*, case: PilotCase, answer_provider: AnswerProvider, round_number: int, question: str, questions: list[QuestionRecord], exchanges: list[ClarificationExchange]) -> str` — Persists answer.
- L262 `async def run_no_followup(case: PilotCase, *, rag_call: RagCallable=request_rag, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model) -> ExperimentResult` — Executes no followup.
- L297 `async def _run_post_rag_adaptive(case: PilotCase, *, method: Method, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes post rag adaptive.
- L396 `async def run_post_rag_adaptive(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes post rag adaptive.
- L424 `async def run_adaptive_followup(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Backward-compatible name for the historical post-RAG baseline.
- L453 `async def run_pre_rag_adaptive(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes pre rag adaptive.
- L566 `def save_result(result: ExperimentResult, results_dir: Path=DEFAULT_RESULTS_DIR) -> Path` — Persists result.
- L582 `async def run_method(case: PilotCase, method: Method, **kwargs: object) -> ExperimentResult` — Executes method.
- L601 `def build_argument_parser() -> argparse.ArgumentParser` — Builds argument parser.
- L618 `async def _run_cli(args: argparse.Namespace) -> list[Path]` — Executes cli.
- L640 `def main() -> None` — Implements main.

### [`experiments/followup_pilot/schemas.py`](../../experiments/followup_pilot/schemas.py)

Purpose: Strict, serializable contracts for the follow-up pilot.

- L47 `class StrictModel(BaseModel)` — Encapsulates strictmodel.
- L51 `class PilotCase(StrictModel)` — Encapsulates pilotcase.
- L61 `def validate_case_contract(self) -> 'PilotCase'` — Validates case contract.
- L73 `class QuestionRecord(StrictModel)` — Encapsulates questionrecord.
- L81 `def requested_fields_are_unique(self) -> 'QuestionRecord'` — Implements requested fields are unique.
- L87 `class RagCallRecord(StrictModel)` — Encapsulates ragcallrecord.
- L94 `class ExperimentResult(StrictModel)` — Encapsulates experimentresult.
- L117 `def backfill_legacy_metadata(self) -> 'ExperimentResult'` — Implements backfill legacy metadata.
- L126 `class SystemMetrics(StrictModel)` — Encapsulates systemmetrics.
- L136 `class SystemEvaluation(StrictModel)` — Encapsulates systemevaluation.
- L142 `class EvaluationResult(StrictModel)` — Encapsulates evaluationresult.

### [`experiments/followup_pilot/tests/__init__.py`](../../experiments/followup_pilot/tests/__init__.py)

Purpose: Offline tests for the follow-up pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/followup_pilot/tests/test_runner.py`](../../experiments/followup_pilot/tests/test_runner.py)

Purpose: Verifies runner behavior in the research and evaluation workspace.

- L49 `class FakeRag` — Encapsulates fakerag.
- L50 `def __init__(self, answers: list[str], events: list[str] | None=None) -> None` — Implements init.
- L62 `async def __call__(self, query: str) -> QueryResponse` — Implements call.
- L70 `class FakePolicy` — Encapsulates fakepolicy.
- L71 `def __init__(self, outcomes: list[FollowUpDecision | Exception], events: list[str] | None=None) -> None` — Implements init.
- L80 `async def decide(self, *, original_user_content: str, clarification_exchanges: object) -> FollowUpDecision` — Implements decide.
- L100 `class FixedRng` — Encapsulates fixedrng.
- L101 `def shuffle(self, values: list[ExperimentResult]) -> None` — Implements shuffle.
- L105 `def answer_provider(answers: list[HumanAnswer])` — Implements answer provider.
- L108 `def provide(case, round_number, question)` — Implements provide.
- L117 `def result_for(method: str, *, analysis: str, questions: list[QuestionRecord] | None=None) -> ExperimentResult` — Implements result for.
- L151 `class RunnerTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates runnertests.
- L152 `def setUp(self) -> None` — Implements setup.
- L155 `async def test_no_followup_calls_rag_once_and_never_needs_policy(self) -> None` — Implements test no followup calls rag once and never needs policy.
- L166 `async def test_adaptive_rebuilds_query_and_preserves_exchange_order(self) -> None` — Implements test adaptive rebuilds query and preserves exchange order.
- L210 `async def test_adaptive_stops_immediately_when_policy_answers(self) -> None` — Implements test adaptive stops immediately when policy answers.
- L225 `async def test_adaptive_stops_after_three_answered_rounds(self) -> None` — Implements test adaptive stops after three answered rounds.
- L250 `async def test_policy_exception_fails_open_to_latest_rag_answer(self) -> None` — Implements test policy exception fails open to latest rag answer.
- L266 `async def test_pre_rag_asks_before_any_rag_call(self) -> None` — Implements test pre rag asks before any rag call.
- L297 `async def test_insufficient_case_asks_for_material_fact_before_rag(self) -> None` — Implements test insufficient case asks for material fact before rag.
- L338 `async def test_sufficient_case_proceeds_to_rag_without_followup(self) -> None` — Implements test sufficient case proceeds to rag without followup.
- L361 `async def test_pre_rag_max_rounds_calls_rag_after_the_last_answer(self) -> None` — Implements test pre rag max rounds calls rag after the last answer.
- L388 `async def test_pre_rag_policy_failure_fails_open_to_one_rag_call(self) -> None` — Implements test pre rag policy failure fails open to one rag call.
- L405 `async def test_post_rag_baseline_keeps_rag_before_policy(self) -> None` — Implements test post rag baseline keeps rag before policy.
- L426 `def test_historical_result_files_remain_loadable(self) -> None` — Implements test historical result files remain loadable.
- L439 `async def test_result_file_contains_required_metadata(self) -> None` — Implements test result file contains required metadata.
- L454 `class EvaluatorTests(unittest.TestCase)` — Encapsulates evaluatortests.
- L455 `def setUp(self) -> None` — Implements setup.
- L458 `def test_completeness_and_manual_metrics_are_calculated(self) -> None` — Implements test completeness and manual metrics are calculated.
- L490 `def test_unknown_fallback_does_not_count_as_recovery(self) -> None` — Implements test unknown fallback does not count as recovery.
- L513 `def test_evaluator_hides_mapping_until_all_scores_are_collected(self) -> None` — Implements test evaluator hides mapping until all scores are collected.
- L517 `def fake_input(prompt: str) -> str` — Implements fake input.
- L546 `def test_fixture_hides_exactly_two_recoverable_fields(self) -> None` — Implements test fixture hides exactly two recoverable fields.

### [`experiments/representation_analysis/__init__.py`](../../experiments/representation_analysis/__init__.py)

Purpose: Isolated SEvenLLM representation analysis experiment.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/__main__.py`](../../experiments/representation_analysis/__main__.py)

Purpose: Owns main behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/analysis.py`](../../experiments/representation_analysis/analysis.py)

Purpose: Owns analysis behavior for the research and evaluation workspace.

- L12 `def analysis_record(row: dict[str, Any], condition: str, context: str, response: dict[str, Any], reused_from: str | None=None) -> dict[str, Any]` — Implements analysis record.
- L21 `def validated_b0_cache(path: Path, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]` — Implements validated b0 cache.
- L39 `def validate_shared_prompt(row: dict[str, Any], context: str) -> None` — Validates shared prompt.

### [`experiments/representation_analysis/b3.py`](../../experiments/representation_analysis/b3.py)

Purpose: Owns b3 behavior for the research and evaluation workspace.

- L26 `def build_augmented_context(raw: str, events: str) -> str` — Builds augmented context.
- L31 `def validate_sources(rows: list[dict[str, Any]], source_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]` — Validates sources.
- L46 `def metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements metric stats.
- L50 `def paired_stats(records: list[dict[str, Any]], left: str, right: str, metric: str) -> dict[str, Any]` — Implements paired stats.
- L55 `def build_results(rows: list[dict[str, Any]], b0: dict[str, dict[str, Any]], b2: dict[str, dict[str, Any]], b3: dict[str, dict[str, Any]], source_dir: Path, model: Any) -> list[dict[str, Any]]` — Builds results.
- L66 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary.
- L73 `def render_report(summary: dict[str, Any]) -> str` — Renders report.
- L85 `def run(args: Any) -> None` — Executes run.
- L101 `def main() -> None` — Implements main.

### [`experiments/representation_analysis/cli.py`](../../experiments/representation_analysis/cli.py)

Purpose: Owns cli behavior for the research and evaluation workspace.

- L14 `def build_parser() -> argparse.ArgumentParser` — Builds parser.
- L34 `def main(argv: list[str] | None=None) -> None` — Implements main.

### [`experiments/representation_analysis/constants.py`](../../experiments/representation_analysis/constants.py)

Purpose: Owns constants behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/dataset.py`](../../experiments/representation_analysis/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/diagnostics.py`](../../experiments/representation_analysis/diagnostics.py)

Purpose: Owns diagnostics behavior for the research and evaluation workspace.

- L20 `def detect_source_strings(text: str) -> dict[str, list[str]]` — Implements detect source strings.
- L24 `def retention_diagnostics(source: str, representation: str) -> dict[str, Any]` — Implements retention diagnostics.
- L34 `def case_state_surface_values(case_state: dict[str, Any]) -> list[str]` — Implements case state surface values.
- L37 `def visit(value: Any, key: str='') -> None` — Implements visit.
- L50 `def possible_unsupported_surface_values(source: str, case_state: dict[str, Any]) -> list[str]` — Implements possible unsupported surface values.

### [`experiments/representation_analysis/gliner_adapter.py`](../../experiments/representation_analysis/gliner_adapter.py)

Purpose: Owns gliner adapter behavior for the research and evaluation workspace.

- L10 `class GlinerEventExtractor` — Encapsulates glinereventextractor.
- L11 `def __init__(self, model_name: str, device: str, threshold: float=0.5, model: Any=None) -> None` — Implements init.
- L20 `def extract(self, source: str) -> dict[str, Any]` — Extracts extract.
- L36 `def _ground_events(self, source: str, raw_events: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements ground events.
- L59 `def _ground_value(source: str, value: Any) -> dict[str, Any] | None` — Implements ground value.

### [`experiments/representation_analysis/production_extraction.py`](../../experiments/representation_analysis/production_extraction.py)

Purpose: Owns production extraction behavior for the research and evaluation workspace.

- L10 `def production_extraction_contract() -> dict[str, Any]` — Implements production extraction contract.
- L21 `async def extract_case_state(sample_id: str, source: str) -> dict[str, Any]` — Extracts case state.

### [`experiments/representation_analysis/prompting.py`](../../experiments/representation_analysis/prompting.py)

Purpose: Owns prompting behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/reporting.py`](../../experiments/representation_analysis/reporting.py)

Purpose: Owns reporting behavior for the research and evaluation workspace.

- L10 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary.
- L11 `def stats(selected: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements stats.
- L34 `def failure_examples(records: list[dict[str, Any]]) -> dict[str, Any]` — Implements failure examples.
- L36 `def item(record: dict[str, Any], condition: str) -> dict[str, Any]` — Implements item.
- L47 `def size_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements size stats.
- L52 `def render_markdown(summary: dict[str, Any]) -> str` — Renders markdown.

### [`experiments/representation_analysis/runner.py`](../../experiments/representation_analysis/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L26 `def run_config(args: Any, manifest: dict[str, Any]) -> dict[str, Any]` — Executes config.
- L38 `async def ensure_b1(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]` — Implements ensure b1.
- L54 `def ensure_b2(rows: list[dict[str, Any]], path: Path, args: Any) -> dict[str, dict[str, Any]]` — Implements ensure b2.
- L68 `def ensure_analysis(rows: list[dict[str, Any]], condition: str, contexts: dict[str, str], path: Path, args: Any, cache: dict[str, dict[str, Any]] | None=None) -> dict[str, dict[str, Any]]` — Implements ensure analysis.
- L88 `def assemble(rows: list[dict[str, Any]], analyses: dict[str, dict[str, dict[str, Any]]], extractions: dict[str, dict[str, dict[str, Any]]], model: Any) -> list[dict[str, Any]]` — Builds assemble.
- L107 `def run_experiment(args: Any) -> None` — Executes experiment.

### [`experiments/representation_analysis/serializers.py`](../../experiments/representation_analysis/serializers.py)

Purpose: Owns serializers behavior for the research and evaluation workspace.

- L10 `def serialize_case_state(value: dict[str, Any]) -> str` — Serializes case state.
- L14 `def serialize_events(events: list[dict[str, Any]]) -> str` — Serializes events.
- L23 `def estimate_tokens(text: str) -> int` — Implements estimate tokens.

### [`experiments/representation_analysis/storage.py`](../../experiments/representation_analysis/storage.py)

Purpose: Owns storage behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/tests/__init__.py`](../../experiments/representation_analysis/tests/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/tests/test_b3.py`](../../experiments/representation_analysis/tests/test_b3.py)

Purpose: Verifies b3 behavior in the research and evaluation workspace.

- L8 `class B3ContextTests(unittest.TestCase)` — Encapsulates b3contexttests.
- L9 `def test_raw_and_events_are_preserved_verbatim(self)` — Implements test raw and events are preserved verbatim.
- L17 `def test_empty_extraction_is_explicit(self)` — Implements test empty extraction is explicit.

### [`experiments/representation_analysis/tests/test_contracts.py`](../../experiments/representation_analysis/tests/test_contracts.py)

Purpose: Verifies contracts behavior in the research and evaluation workspace.

- L10 `class FakeGliner` — Encapsulates fakegliner.
- L11 `def extract_json(self, source, schema, **kwargs)` — Extracts json.
- L15 `class ContractTests(unittest.TestCase)` — Encapsulates contracttests.
- L16 `def test_gliner_keeps_only_exact_source_spans(self)` — Implements test gliner keeps only exact source spans.
- L24 `def test_retention_and_case_state_diagnostics(self)` — Implements test retention and case state diagnostics.

### [`experiments/semantic_verification/__init__.py`](../../experiments/semantic_verification/__init__.py)

Purpose: Offline-only synthetic semantic verification fixture construction.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/__main__.py`](../../experiments/semantic_verification/__main__.py)

Purpose: CLI entrypoint for the isolated offline benchmark.

- L20 `def _parser()` — Implements parser.
- L37 `def main(argv=None)` — Implements main.

### [`experiments/semantic_verification/constants.py`](../../experiments/semantic_verification/constants.py)

Purpose: Constants shared by the isolated offline benchmark package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/generator.py`](../../experiments/semantic_verification/generator.py)

Purpose: Gold-first deterministic construction of the bilingual benchmark.

- L18 `def _entity(case_id, suffix, entity_type, name)` — Implements entity.
- L22 `def _relationship(case_id, number, subject, predicate, target, timestamp=None, certainty='reported', negated=False)` — Implements relationship.
- L31 `def _timeline(case_id, number, event_type, actor, predicate, target, timestamp, certainty='reported')` — Implements timeline.
- L41 `def _timestamps(case_number)` — Implements timestamps.
- L52 `def _gold(case_id, case_number, language, scenario)` — Implements gold.
- L109 `def _propositions(case_id, layout_index, facts_by_slot, language, gold_facts)` — Implements propositions.
- L121 `def _negative_sources(error_type, facts_by_slot)` — Implements negative sources.
- L131 `def _pairs(case_id, case_number, language, gold_facts, facts)` — Implements pairs.
- L153 `def generate_cases(case_count=DEFAULT_CASE_COUNT, seed=DEFAULT_SEED)` — Generates cases.
- L175 `def write_jsonl(cases, path)` — Implements write jsonl.

### [`experiments/semantic_verification/rendering.py`](../../experiments/semantic_verification/rendering.py)

Purpose: Deterministic bilingual renderers and semantic corruption operators.

- L33 `def entity_map(gold_facts)` — Implements entity map.
- L37 `def semantic_signature(fact)` — Implements semantic signature.
- L47 `def fact_edge(fact)` — Implements fact edge.
- L53 `def _timestamp_text(timestamp, language)` — Implements timestamp text.
- L59 `def render_fact(fact, language, gold_facts, sentence=True)` — Renders fact.
- L79 `def render_proposition(proposition, facts_by_id, language, gold_facts)` — Renders proposition.
- L98 `def normalized_claim(text)` — Implements normalized claim.
- L102 `def _alternate_entity(entity_id, gold_facts)` — Implements alternate entity.
- L111 `def _shift_timestamp(value)` — Implements shift timestamp.
- L118 `def corrupt_fact(source_fact, error_type, gold_facts)` — Implements corrupt fact.
- L143 `def render_corruption(source_facts, error_type, language, gold_facts)` — Renders corruption.

### [`experiments/semantic_verification/reporting.py`](../../experiments/semantic_verification/reporting.py)

Purpose: Deterministic report writing for benchmark construction results.

- L7 `def summary_markdown(summary)` — Implements summary markdown.
- L52 `def write_summary_reports(summary, json_path, markdown_path)` — Implements write summary reports.

### [`experiments/semantic_verification/tests/__init__.py`](../../experiments/semantic_verification/tests/__init__.py)

Purpose: Focused tests for the offline fixture construction package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/tests/test_benchmark.py`](../../experiments/semantic_verification/tests/test_benchmark.py)

Purpose: Offline integrity and tamper tests for the proposition-backed benchmark.

- L19 `def _validate_rows(rows, strict=False)` — Validates rows.
- L26 `class SemanticVerificationTests(unittest.TestCase)` — Encapsulates semanticverificationtests.
- L27 `def test_exact_counts_diversity_and_coverage(self)` — Implements test exact counts diversity and coverage.
- L45 `def test_repeatability_including_reports(self)` — Implements test repeatability including reports.
- L58 `def test_claims_have_no_label_markers(self)` — Implements test claims have no label markers.
- L64 `def test_narrative_tamper_is_rejected(self)` — Implements test narrative tamper is rejected.
- L71 `def test_absent_entity_and_timestamp_are_rejected(self)` — Implements test absent entity and timestamp are rejected.
- L89 `def test_positive_and_trivial_negative_tamper_are_rejected(self)` — Implements test positive and trivial negative tamper are rejected.
- L105 `def test_timeline_edge_without_relationship_is_rejected(self)` — Implements test timeline edge without relationship is rejected.
- L112 `def test_malformed_blank_and_duplicate_json_are_rejected(self)` — Implements test malformed blank and duplicate json are rejected.
- L126 `def test_import_and_network_isolation(self)` — Implements test import and network isolation.

### [`experiments/semantic_verification/validator.py`](../../experiments/semantic_verification/validator.py)

Purpose: Strict construction validator for the synthetic JSONL fixture.

- L11 `class _DuplicateKeyError(ValueError)` — Encapsulates duplicatekeyerror.
- L15 `def _reject_duplicate_keys(pairs)` — Implements reject duplicate keys.
- L24 `def _reject_non_finite(value)` — Implements reject non finite.
- L28 `def _record(failures, message)` — Persists record.
- L33 `def _sentence_count(narrative)` — Implements sentence count.
- L37 `def _parse_dataset(path, failures)` — Parses dataset.
- L60 `def _fact_entities(fact)` — Implements fact entities.
- L66 `def validate_dataset(path, strict=True)` — Validates dataset.

### [`research/attribute_first_pilot/__init__.py`](../../research/attribute_first_pilot/__init__.py)

Purpose: Attribute-First Reasoning Research Pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/attribute_first_pilot/contracts.py`](../../research/attribute_first_pilot/contracts.py)

Purpose: Domain contracts, schemas, and enums for the Attribute-First Reasoning Pilot.

- L10 `class AnswerabilityEnum(str, Enum)` — Encapsulates answerabilityenum.
- L16 `class QuestionTypeEnum(str, Enum)` — Encapsulates questiontypeenum.
- L25 `class EpistemicStateEnum(str, Enum)` — Encapsulates epistemicstateenum.
- L31 `class ConditionEnum(str, Enum)` — Encapsulates conditionenum.
- L39 `class SentenceEvidence(BaseModel)` — A numbered sentence unit in the cybersecurity case context.
- L45 `class AttributeContract(BaseModel)` — The concise intermediate context-analysis attribute representation.
- L69 `class EvaluationNotes(BaseModel)` — Ground truth analytical notes for manual or deterministic verification.
- L76 `class BenchmarkItem(BaseModel)` — Single benchmark instance.
- L86 `def formatted_context(self) -> str` — Format sentences with bracketed sentence IDs.
- L91 `class BenchmarkSuite(BaseModel)` — Full benchmark suite containing all instances.
- L98 `class ModelCallUsage(BaseModel)` — Token usage metadata for a single LLM invocation.
- L105 `class GenerationResult(BaseModel)` — Result of an answer generation call.
- L115 `class AttributePredictionResult(BaseModel)` — Result of an attribute prediction call.
- L125 `class ItemRunResult(BaseModel)` — Full experimental execution records for a single benchmark item across all 3 conditions.
- L138 `class PilotRunOutput(BaseModel)` — Complete serialized experiment run output.

### [`research/attribute_first_pilot/evaluator.py`](../../research/attribute_first_pilot/evaluator.py)

Purpose: Evaluation and metrics module for the Attribute-First Reasoning Research Pilot.

- L30 `def calculate_macro_f1(gold: list[str], pred: list[str], labels: list[str]) -> float` — Calculate macro-averaged F1 score over discrete categories.
- L60 `def calculate_evidence_metrics(gold_sets: list[set[str]], pred_sets: list[set[str]]) -> tuple[float, float, float]` — Calculate mean precision, recall, and F1 for relevant evidence sentence selection.
- L104 `class AttributeEvaluationReport` — Encapsulates attributeevaluationreport.
- L123 `def evaluate_attributes(run_output: PilotRunOutput) -> AttributeEvaluationReport` — Evaluate predicted attributes against gold attributes.
- L278 `class EfficiencyReport` — Encapsulates efficiencyreport.
- L289 `def evaluate_efficiency(run_output: PilotRunOutput) -> EfficiencyReport` — Evaluate latency and token usage across conditions.
- L328 `def load_manual_scores(csv_path: Path) -> dict[str, dict[str, float]]` — Parse manual scores from CSV file if filled.
- L371 `def generate_markdown_report(run_output: PilotRunOutput, attr_report: AttributeEvaluationReport, eff_report: EfficiencyReport, manual_scores: dict[str, dict[str, float]] | None=None) -> str` — Generate Markdown evaluation summary.
- L477 `def main() -> None` — Implements main.

### [`research/attribute_first_pilot/llm_judge.py`](../../research/attribute_first_pilot/llm_judge.py)

Purpose: LLM Judge for scoring B0, A1, and A2 downstream answers.

- L34 `class JudgeScore(BaseModel)` — Encapsulates judgescore.
- L93 `async def judge_single_answer(client: httpx.AsyncClient, model: str, api_key: str, context: str, question: str, expected_behavior: str, required_points: list[str], forbidden_points: list[str], candidate_answer: str, base_url: str='https://openrouter.ai/api/v1') -> JudgeScore` — Judge a single candidate answer.
- L148 `async def run_judge_pipeline(results_path: Path, benchmark_path: Path, output_csv_path: Path, judge_model: str=DEFAULT_JUDGE_MODEL) -> None` — Run LLM judge across all items for B0, A1, and A2.
- L252 `def main() -> None` — Implements main.

### [`research/attribute_first_pilot/prompts.py`](../../research/attribute_first_pilot/prompts.py)

Purpose: Prompts and prompt builders for the Attribute-First Reasoning Pilot.

- L109 `def build_attribute_prediction_messages(context: str, question: str) -> list[dict[str, str]]` — Build messages payload for attribute prediction.
- L117 `def build_direct_baseline_messages(context: str, question: str) -> list[dict[str, str]]` — Build messages payload for direct zero-shot baseline (B0).
- L125 `def build_attribute_first_messages(context: str, question: str, attributes: AttributeContract | dict) -> list[dict[str, str]]` — Build messages payload for attribute-first generation (A1 and A2).

### [`research/attribute_first_pilot/provider.py`](../../research/attribute_first_pilot/provider.py)

Purpose: LLM Provider wrapper for the Attribute-First Reasoning Pilot.

- L30 `def get_api_key() -> str` — Retrieve the OpenRouter API key from environment variables or .env.
- L53 `def clean_json_text(text: str) -> str` — Strip markdown code fences and whitespace from model JSON output.
- L66 `class AttributePredictionError(Exception)` — Raised when the model output fails strict attribute JSON validation.
- L68 `def __init__(self, message: str, raw_text: str)` — Implements init.
- L73 `class PilotLlmProvider` — OpenRouter provider for the pilot experiment.
- L76 `def __init__(self, model: str=DEFAULT_MODEL, api_key: str | None=None, base_url: str=DEFAULT_OPENROUTER_BASE_URL, timeout: float=60.0, temperature: float=0.0, dry_run: bool=False)` — Implements init.
- L97 `async def _call_chat_completions(self, messages: list[dict[str, str]], max_tokens: int=1024, response_format: dict[str, str] | None=None) -> tuple[str, float, ModelCallUsage]` — Execute chat completion and track latency + usage.
- L162 `async def generate_answer(self, messages: list[dict[str, str]], max_tokens: int=1024) -> GenerationResult` — Generate text answer for direct or attribute-first condition.
- L188 `async def predict_attributes(self, messages: list[dict[str, str]], max_tokens: int=512) -> AttributePredictionResult` — Predict structured attributes with strict validation.

### [`research/attribute_first_pilot/runner.py`](../../research/attribute_first_pilot/runner.py)

Purpose: CLI Runner for the Attribute-First Reasoning Research Pilot.

- L35 `def load_benchmark(path: Path) -> BenchmarkSuite` — Load and validate benchmark suite.
- L43 `def export_manual_scoring_template(run_output: PilotRunOutput, csv_path: Path) -> None` — Export blank manual scoring CSV template with blind/comparative answer rows.
- L104 `async def run_single_item(item: BenchmarkItem, provider: PilotLlmProvider) -> ItemRunResult` — Run B0, A1 (step 1 & 2), and A2 for a single benchmark item.
- L155 `async def run_pilot(benchmark_path: Path=DEFAULT_BENCHMARK_PATH, results_dir: Path=DEFAULT_RESULTS_DIR, model: str=DEFAULT_MODEL, temperature: float=0.0, limit: int | None=None, dry_run: bool=False) -> Path` — Execute the full pilot pipeline and write results.
- L221 `def main() -> None` — Implements main.

### [`research/attribute_first_pilot/tests/__init__.py`](../../research/attribute_first_pilot/tests/__init__.py)

Purpose: Unit tests for the Attribute-First Reasoning Pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/attribute_first_pilot/tests/test_pilot.py`](../../research/attribute_first_pilot/tests/test_pilot.py)

Purpose: Unit tests for the Attribute-First Reasoning Pilot components.

- L44 `def test_attribute_contract_valid()` — Test standard validation of AttributeContract.
- L60 `def test_attribute_contract_invalid_enum()` — Test that invalid enums raise ValidationError.
- L70 `def test_clean_json_text()` — Test stripping markdown code fences.
- L77 `def test_benchmark_json_integrity()` — Validate all items in benchmark.json match the Pydantic schema.
- L97 `def test_prompt_builders()` — Test that prompt builder functions construct the expected message structure.
- L127 `def test_macro_f1_calculation()` — Test macro F1 calculation.
- L136 `def test_evidence_metrics_calculation()` — Test evidence precision/recall/F1 calculation.
- L146 `def test_runner_mock_single_item(tmp_path)` — Test executing a mock item through PilotLlmProvider dry_run.
- L177 `def test_evaluator_report_generation()` — Test evaluating mock run output and generating report.

### [`research/diagnostic/run_no_rag_diagnostic.py`](../../research/diagnostic/run_no_rag_diagnostic.py)

Purpose: Run the Main Case Analysis diagnostic with RAG explicitly skipped.

- L92 `class AtomicClaim(BaseModel)` — Encapsulates atomicclaim.
- L100 `class AtomicClaimsResponse(BaseModel)` — Encapsulates atomicclaimsresponse.
- L106 `class ClaimAuditResponse(BaseModel)` — Encapsulates claimauditresponse.
- L117 `class ClaimAuditBatchResponse(BaseModel)` — Encapsulates claimauditbatchresponse.
- L123 `class CoverageItem(BaseModel)` — Encapsulates coverageitem.
- L131 `class CoverageResponse(BaseModel)` — Encapsulates coverageresponse.
- L141 `class StructuredCallResult` — Encapsulates structuredcallresult.
- L150 `def _json(value: object) -> str` — Implements json.
- L154 `def _compact_json(value: object) -> str` — Implements compact json.
- L158 `def _extract_text(payload: object) -> str` — Extracts text.
- L177 `def _clean_json_text(value: str) -> str` — Normalizes json text.
- L184 `def _usage_value(usage: object, names: tuple[str, ...]) -> int | None` — Implements usage value.
- L194 `async def _structured_call(*, model: str, system_prompt: str, user_prompt: str, output_model: type[T], max_tokens: int, timeout_seconds: float=RESEARCH_TIMEOUT_SECONDS) -> StructuredCallResult` — Implements structured call.
- L318 `def _claim_prompt(analysis_text: str) -> str` — Implements claim prompt.
- L327 `def _decompose_claims_deterministically(analysis_text: str) -> list[AtomicClaim]` — Split only generated text into auditable sentence-level claims.
- L364 `def _audit_prompt(*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object]) -> str` — Implements audit prompt.
- L382 `def _audit_batch_prompt(*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object]) -> str` — Implements audit batch prompt.
- L400 `def _coverage_prompt(analysis_text: str, observations: list[str]) -> str` — Implements coverage prompt.
- L416 `def _empty_analysis_context() -> dict[str, object]` — Implements empty analysis context.
- L420 `def _allowed_evidence_ids(case_state: dict[str, object]) -> set[str]` — Implements allowed evidence ids.
- L431 `def _sanitize_audit(audit: ClaimAuditResponse, *, allowed_evidence_ids: set[str]) -> tuple[ClaimAuditResponse, list[str]]` — Normalizes audit.
- L459 `def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None` — Implements write jsonl.
- L467 `def _read_cases(path: Path) -> list[dict[str, object]]` — Retrieves cases.
- L481 `def _read_jsonl_records(path: Path) -> list[dict[str, object]]` — Retrieves jsonl records.
- L493 `def _case_state_for(case: dict[str, object]) -> dict[str, object]` — Implements case state for.
- L501 `async def _run_claim_extraction(analysis_text: str, *, model: str) -> StructuredCallResult` — Executes claim extraction.
- L515 `async def _run_one_audit(*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object], model: str) -> tuple[ClaimAuditResponse | None, StructuredCallResult, list[str]]` — Executes one audit.
- L547 `async def _run_audits(*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object], model: str) -> list[dict[str, object]]` — Executes audits.
- L601 `async def _run_coverage(*, analysis_text: str, observations: list[str], model: str) -> tuple[list[dict[str, object]], StructuredCallResult]` — Executes coverage.
- L674 `def _evidence_lookup(case_state: dict[str, object]) -> dict[str, str]` — Implements evidence lookup.
- L685 `def _percent(count: int, denominator: int) -> float` — Implements percent.
- L689 `def _aggregate(*, cases: list[dict[str, object]], analysis_records: list[dict[str, object]], claim_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], coverage_records: list[dict[str, object]], main_model: str, claim_model: str, judge_a_model: str, judge_b_model: str, second_judge_requested: bool) -> dict[str, object]` — Implements aggregate.
- L900 `def _report(*, summary: dict[str, object], analysis_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], cases_by_id: dict[str, dict[str, object]]) -> str` — Implements report.
- L1068 `async def run(args: argparse.Namespace) -> int` — Executes run.
- L1420 `def _parse_args() -> argparse.Namespace` — Parses args.

### [`research/render_sample_report.py`](../../research/render_sample_report.py)

Purpose: Render sample CyberCase incident reports in both Thai and English (HTML & PDF).

- L21 `def build_sample_report() -> ChatReportRead` — Builds sample report.
- L143 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/__init__.py`](../../research/sevenllm_preflight/__init__.py)

Purpose: SEvenLLM tokenizer and protocol preflight utilities.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/b2_config.py`](../../research/sevenllm_preflight/b2_config.py)

Purpose: Owns b2 config behavior for the research and evaluation workspace.

- L95 `def default_fixed_selection_path() -> Path` — Implements default fixed selection path.
- L99 `def training_defaults() -> dict[str, object]` — Implements training defaults.

### [`research/sevenllm_preflight/b2_leakage.py`](../../research/sevenllm_preflight/b2_leakage.py)

Purpose: Owns b2 leakage behavior for the research and evaluation workspace.

- L10 `def load_fixed_benchmark_ids(path: Path) -> list[str]` — Retrieves fixed benchmark ids.
- L21 `def benchmark_reference(rows: list[dict[str, Any]], fixed_ids: list[str]) -> dict[str, Any]` — Implements benchmark reference.
- L43 `def _overlap_details(examples: list[dict[str, Any]], reference: dict[str, Any]) -> dict[str, Any]` — Implements overlap details.
- L69 `def check_leakage(splits: dict[str, list[dict[str, Any]]], benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]) -> dict[str, Any]` — Validates leakage.

### [`research/sevenllm_preflight/b2_metrics.py`](../../research/sevenllm_preflight/b2_metrics.py)

Purpose: Owns b2 metrics behavior for the research and evaluation workspace.

- L13 `def prediction_text(record: dict[str, Any]) -> str` — Implements prediction text.
- L20 `def parse_json_prediction(raw: str) -> Any | None` — Parses json prediction.
- L34 `def flatten_values(value: Any) -> list[str]` — Implements flatten values.
- L42 `def extraction_scores(gold: Any, prediction: Any | None) -> tuple[float, float, float]` — Implements extraction scores.
- L57 `def rouge_l(gold: str, prediction: str) -> float` — Implements rouge l.
- L63 `def mean(records: list[dict[str, Any]], field: str) -> float` — Implements mean.
- L67 `def grouped_mean(records: list[dict[str, Any]], group_field: str, metric_field: str) -> dict[str, float]` — Implements grouped mean.
- L74 `def score_rows(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]` — Implements score rows.

### [`research/sevenllm_preflight/b2_preflight.py`](../../research/sevenllm_preflight/b2_preflight.py)

Purpose: Owns b2 preflight behavior for the research and evaluation workspace.

- L36 `def file_sha256(path: Path) -> str` — Implements file sha256.
- L44 `def tokenize_lengths(tokenizer: Any, input_text: str, target_text: str) -> tuple[int, int]` — Implements tokenize lengths.
- L50 `def measure_examples(examples: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]` — Implements measure examples.
- L58 `def length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]` — Implements length summary.
- L82 `def category_length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]` — Implements category length summary.
- L89 `def tokenizer_metadata(tokenizer: Any, tokenizer_source: str) -> dict[str, Any]` — Implements tokenizer metadata.
- L104 `def parse_args() -> argparse.Namespace` — Parses args.
- L118 `def build_manifest(args: argparse.Namespace, filtered: list[dict[str, Any]], train: list[dict[str, Any]], validation: list[dict[str, Any]], invalid: list[dict[str, Any]], leakage: dict[str, Any], tokenizer: dict[str, Any], hard_blockers: list[str], train_path: Path, validation_path: Path) -> dict[str, Any]` — Builds manifest.
- L224 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/b2_records.py`](../../research/sevenllm_preflight/b2_records.py)

Purpose: Owns b2 records behavior for the research and evaluation workspace.

- L16 `def load_data_file(path: Path) -> list[dict[str, Any]]` — Retrieves data file.
- L31 `def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None` — Implements write jsonl.
- L39 `def _json_text(value: Any) -> str` — Implements json text.
- L45 `def instruction_text(row: dict[str, Any]) -> str` — Implements instruction text.
- L62 `def language_for(row: dict[str, Any]) -> str` — Implements language for.
- L81 `def source_id_for(row: dict[str, Any]) -> str | None` — Implements source id for.
- L89 `def output_text(row: dict[str, Any]) -> str` — Implements output text.
- L99 `def prompt_fingerprint(row: dict[str, Any]) -> str` — Implements prompt fingerprint.
- L108 `def example_fingerprint(row: dict[str, Any]) -> str` — Implements example fingerprint.
- L118 `def _fingerprint(payload: dict[str, str]) -> str` — Implements fingerprint.
- L123 `def build_input_text(row: dict[str, Any]) -> str` — Builds input text.
- L133 `def build_example(row: dict[str, Any], source_line: int) -> dict[str, Any]` — Builds example.
- L154 `def filter_english_training_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements filter english training rows.
- L167 `def benchmark_id_for(row: dict[str, Any]) -> str` — Implements benchmark id for.

### [`research/sevenllm_preflight/b2_split.py`](../../research/sevenllm_preflight/b2_split.py)

Purpose: Owns b2 split behavior for the research and evaluation workspace.

- L10 `def split_examples(examples: list[dict[str, Any]], validation_ratio: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements split examples.
- L30 `def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]` — Implements category counts.

### [`research/sevenllm_preflight/b2_training.py`](../../research/sevenllm_preflight/b2_training.py)

Purpose: Owns b2 training behavior for the research and evaluation workspace.

- L42 `def file_sha256(path: Path) -> str` — Implements file sha256.
- L49 `def load_preflight_manifest(path: Path) -> dict[str, Any]` — Retrieves preflight manifest.
- L77 `def select_precision() -> dict[str, Any]` — Extracts precision.
- L91 `def seed_runtime(seed: int) -> None` — Implements seed runtime.
- L100 `def tokenized_dataset(path: Path, tokenizer: Any, split_name: str) -> Any` — Implements tokenized dataset.
- L103 `def encode(batch: dict[str, list[str]]) -> dict[str, Any]` — Serializes encode.
- L120 `def latest_checkpoint(output_dir: Path) -> Path` — Implements latest checkpoint.
- L129 `def warmup_steps_for(dataset_size: int, args: Any) -> int` — Implements warmup steps for.
- L136 `def build_training_arguments(output_dir: Path, precision: dict[str, Any], args: Any, dataset_size: int, seed: int) -> Seq2SeqTrainingArguments` — Builds training arguments.
- L184 `def build_run_config(manifest_path: Path, output_dir: Path, precision: dict[str, Any], args: Any, resume_from_checkpoint: Path | None, warmup_steps: int, model_revision: str, seed: int) -> dict[str, Any]` — Builds run config.
- L224 `def run_training(args: Any) -> dict[str, Any]` — Executes training.

### [`research/sevenllm_preflight/evaluate_b2_benchmark.py`](../../research/sevenllm_preflight/evaluate_b2_benchmark.py)

Purpose: Owns evaluate b2 benchmark behavior for the research and evaluation workspace.

- L31 `def file_sha256(path: Path) -> str` — Implements file sha256.
- L39 `def fixed_rows(benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]) -> list[dict[str, Any]]` — Implements fixed rows.
- L60 `def parse_args() -> argparse.Namespace` — Parses args.
- L71 `def choose_device(value: str) -> torch.device` — Implements choose device.
- L79 `def predict(rows: list[dict[str, Any]], model: Any, tokenizer: Any, device: torch.device, batch_size: int) -> list[dict[str, Any]]` — Implements predict.
- L117 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/evaluation.py`](../../research/sevenllm_preflight/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/models.py`](../../research/sevenllm_preflight/models.py)

Purpose: Owns models behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/protocol.py`](../../research/sevenllm_preflight/protocol.py)

Purpose: Owns protocol behavior for the research and evaluation workspace.

- L48 `def language_for(row: dict[str, Any]) -> str` — Implements language for.
- L52 `def format_for(row: dict[str, Any]) -> str` — Implements format for.
- L61 `def instruction_text(row: dict[str, Any]) -> str` — Implements instruction text.
- L71 `def _build_input(row: dict[str, Any], include_choice_marker: bool) -> str` — Builds input.
- L82 `def build_mt5_input(row: dict[str, Any]) -> str` — Builds mt5 input.
- L86 `def build_b0_prompt(row: dict[str, Any]) -> str` — Builds b0 prompt.
- L100 `def normalize_choice_output(raw: str) -> str | None` — Normalizes choice output.
- L108 `def gold_output_text(row: dict[str, Any]) -> str` — Implements gold output text.
- L115 `def metadata_for(row: dict[str, Any]) -> dict[str, Any]` — Implements metadata for.

### [`research/sevenllm_preflight/run_openrouter_b0.py`](../../research/sevenllm_preflight/run_openrouter_b0.py)

Purpose: Owns run openrouter b0 behavior for the research and evaluation workspace.

- L30 `class RequestFailure(RuntimeError)` — Encapsulates requestfailure.
- L31 `def __init__(self, message: str, metadata: dict[str, Any]) -> None` — Implements init.
- L36 `def utc_now() -> str` — Implements utc now.
- L40 `def completed_ids(path: Path) -> set[str]` — Implements completed ids.
- L57 `def retry_delay(response: httpx.Response | None, attempt: int, base: float) -> float` — Implements retry delay.
- L68 `def response_error(response: httpx.Response) -> str` — Implements response error.
- L77 `def request_prediction(client: httpx.Client, prompt: str, sample_id: str, max_attempts: int, backoff_base: float) -> tuple[str, str, str, dict[str, Any]]` — Implements request prediction.
- L144 `def normalized_prediction(row: dict[str, Any], raw: str) -> str | None` — Implements normalized prediction.
- L150 `def base_record(row: dict[str, Any], base_url: str, key_env: str) -> dict[str, Any]` — Implements base record.
- L169 `def write_record(handle: Any, record: dict[str, Any]) -> None` — Implements write record.
- L175 `def seed_records(path: Path | None, selected_ids: set[str]) -> dict[str, dict[str, Any]]` — Implements seed records.
- L183 `def run(args: argparse.Namespace) -> None` — Executes run.
- L226 `def parse_args() -> argparse.Namespace` — Parses args.
- L243 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/run_pilot.py`](../../research/sevenllm_preflight/run_pilot.py)

Purpose: Owns run pilot behavior for the research and evaluation workspace.

- L20 `def load_rows(path: Path) -> list[dict[str, Any]]` — Retrieves rows.
- L25 `def english_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]` — Implements english rows.
- L34 `def tokenized_input(tokenizer: Any, prompt: str) -> dict[str, torch.Tensor]` — Implements tokenized input.
- L43 `def load_model(model_dir: Path, device: torch.device) -> tuple[Any, Any]` — Retrieves model.
- L51 `def generate_prediction(tokenizer: Any, model: Any, row: dict[str, Any], device: torch.device) -> tuple[str, str, int]` — Generates prediction.
- L67 `def write_predictions(rows: list[dict[str, Any]], model_dir: Path, output_path: Path, device: torch.device) -> None` — Implements write predictions.
- L93 `def parse_args() -> argparse.Namespace` — Parses args.
- L102 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/run_preflight.py`](../../research/sevenllm_preflight/run_preflight.py)

Purpose: Owns run preflight behavior for the research and evaluation workspace.

- L33 `def load_rows(path: Path) -> list[dict[str, Any]]` — Retrieves rows.
- L38 `def load_json(path: Path) -> dict[str, Any]` — Retrieves json.
- L43 `def token_count(tokenizer: Any, text: str, add_eos: bool=True) -> int` — Implements token count.
- L47 `def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]` — Validates rows.
- L77 `def build_records(rows: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]` — Builds records.
- L100 `def truncation_analysis(records: list[dict[str, Any]], limit: int) -> dict[str, Any]` — Implements truncation analysis.
- L122 `def longest_records(records: list[dict[str, Any]], limit: int=20) -> list[dict[str, Any]]` — Implements longest records.
- L128 `def build_manifest(args: argparse.Namespace, tokenizer: dict[str, Any], config: dict[str, Any], validation: dict[str, Any], records: list[dict[str, Any]], input_stats: dict[str, Any], output_stats: dict[str, Any], truncation: dict[str, Any]) -> dict[str, Any]` — Builds manifest.
- L190 `def parse_args() -> argparse.Namespace` — Parses args.
- L201 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/score_pilot.py`](../../research/sevenllm_preflight/score_pilot.py)

Purpose: Owns score pilot behavior for the research and evaluation workspace.

- L17 `def predictions_by_id(path: Path, expected_ids: set[str], limit: int | None=None, restrict_to_ids: bool=False) -> dict[str, dict[str, Any]]` — Implements predictions by id.
- L35 `def prediction_text(record: dict[str, Any]) -> str` — Implements prediction text.
- L45 `def flatten_values(value: Any) -> list[str]` — Implements flatten values.
- L58 `def extraction_f1(gold: Any, prediction: Any) -> tuple[float, float, float]` — Implements extraction f1.
- L68 `def parse_json_prediction(raw: str) -> Any | None` — Parses json prediction.
- L82 `def rouge_l(gold: str, prediction: str) -> float` — Implements rouge l.
- L88 `def english_sentences(text: str) -> list[str]` — Implements english sentences.
- L92 `def sbert_records(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], model: SentenceTransformer) -> list[dict[str, Any]]` — Implements sbert records.
- L116 `def group_mean(records: list[dict[str, Any]], key: str, metric: str) -> dict[str, float]` — Implements group mean.
- L123 `def metric_mean(records: list[dict[str, Any]], metric: str) -> float` — Implements metric mean.
- L127 `def model_identity(predictions: dict[str, dict[str, Any]]) -> dict[str, Any]` — Implements model identity.
- L145 `def score_model(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], sbert_model: SentenceTransformer | None=None) -> dict[str, Any]` — Implements score model.
- L192 `def parse_args() -> argparse.Namespace` — Parses args.
- L205 `def main() -> None` — Implements main.

### [`research/sevenllm_preflight/selection.py`](../../research/sevenllm_preflight/selection.py)

Purpose: Owns selection behavior for the research and evaluation workspace.

- L10 `def load_jsonl(path: Path) -> list[dict[str, Any]]` — Retrieves jsonl.
- L15 `def parse_category_counts(values: list[str]) -> dict[str, int] | None` — Parses category counts.
- L35 `def selected_english(rows: list[dict[str, Any]], limit: int | None=None, category_counts: dict[str, int] | None=None) -> list[dict[str, Any]]` — Implements selected english.
- L58 `def selection_manifest(rows: list[dict[str, Any]], category_counts: dict[str, int] | None) -> dict[str, Any]` — Implements selection manifest.

### [`research/sevenllm_preflight/statistics.py`](../../research/sevenllm_preflight/statistics.py)

Purpose: Owns statistics behavior for the research and evaluation workspace.

- L8 `def percentile(values: list[int], probability: float) -> float` — Implements percentile.
- L21 `def distribution(values: Iterable[int], thresholds: Iterable[int]) -> dict[str, object]` — Implements distribution.
- L45 `def grouped_distributions(records: list[dict[str, object]], field: str, thresholds: Iterable[int]) -> dict[str, dict[str, object]]` — Implements grouped distributions.
- L53 `def grouped_output_distributions(records: list[dict[str, object]], field: str) -> dict[str, dict[str, object]]` — Implements grouped output distributions.

### [`research/sevenllm_preflight/tests/test_b2_contract.py`](../../research/sevenllm_preflight/tests/test_b2_contract.py)

Purpose: Verifies b2 contract behavior in the research and evaluation workspace.

- L11 `def row(category: str, source_line: int, language: str='en') -> dict[str, object]` — Implements row.
- L22 `def test_b2_input_and_target_exclude_thought() -> None` — Implements test b2 input and target exclude thought.
- L33 `def test_filter_keeps_exact_categories_and_english_only() -> None` — Implements test filter keeps exact categories and english only.
- L45 `def test_split_is_deterministic_and_category_stratified() -> None` — Implements test split is deterministic and category stratified.
- L63 `def test_fixed_selection_matches_existing_manifest() -> None` — Implements test fixed selection matches existing manifest.
- L68 `def test_leakage_check_fails_on_prompt_overlap() -> None` — Implements test leakage check fails on prompt overlap.

### [`research/sevenllm_preflight/train_b2.py`](../../research/sevenllm_preflight/train_b2.py)

Purpose: Owns train b2 behavior for the research and evaluation workspace.

- L15 `def parse_args() -> argparse.Namespace` — Parses args.
- L28 `def main() -> None` — Implements main.

## Frontend Application

### [`frontend/src/app/chat/[threadId]/chat/page.tsx`](../../frontend/src/app/chat/[threadId]/chat/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/chat` route segment.

- L1 `function ThreadSpecificChatPage()` — Renders or constructs threadspecificchatpage.

### [`frontend/src/app/chat/[threadId]/intake/page.tsx`](../../frontend/src/app/chat/[threadId]/intake/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/intake` route segment.

- L1 `function ThreadIntakePage()` — Renders or constructs threadintakepage.

### [`frontend/src/app/chat/[threadId]/materials/page.tsx`](../../frontend/src/app/chat/[threadId]/materials/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/materials` route segment.

- L1 `function ThreadMaterialsPage()` — Renders or constructs threadmaterialspage.

### [`frontend/src/app/chat/[threadId]/overview/page.tsx`](../../frontend/src/app/chat/[threadId]/overview/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/overview` route segment.

- L1 `function ThreadOverviewPage()` — Renders or constructs threadoverviewpage.

### [`frontend/src/app/chat/[threadId]/page.tsx`](../../frontend/src/app/chat/[threadId]/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]` route segment.

- L1 `function ThreadChatPage()` — Renders or constructs threadchatpage.

### [`frontend/src/app/chat/[threadId]/report/page.tsx`](../../frontend/src/app/chat/[threadId]/report/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/report` route segment.

- L1 `function ThreadReportPage()` — Renders or constructs threadreportpage.

### [`frontend/src/app/chat/[threadId]/technical-context/page.tsx`](../../frontend/src/app/chat/[threadId]/technical-context/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/technical-context` route segment.

- L1 `function ThreadTechnicalContextPage()` — Renders or constructs threadtechnicalcontextpage.

### [`frontend/src/app/chat/layout.tsx`](../../frontend/src/app/chat/layout.tsx)

Purpose: Implements the Next.js layout entry for the `chat` route segment.

- L5 `interface ChatLayoutProps` — Defines the structural contract for chatlayoutprops.
- L9 `function ChatLayout({ children }: ChatLayoutProps)` — Renders or constructs chatlayout.

### [`frontend/src/app/chat/page.tsx`](../../frontend/src/app/chat/page.tsx)

Purpose: Implements the Next.js page entry for the `chat` route segment.

- L1 `function ChatPage()` — Renders or constructs chatpage.

### [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx)

Purpose: Implements the Next.js layout entry for the `frontend/src/app` route segment.

- L24 `function RootLayout({ children, }: Readonly<{ children: React.ReactNode; }>)` — Renders or constructs rootlayout.

### [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx)

Purpose: Implements the Next.js page entry for the `frontend/src/app` route segment.

- L5 `function Home()` — Renders or constructs home.

### [`frontend/src/app/providers.tsx`](../../frontend/src/app/providers.tsx)

Purpose: Implements the Next.js providers entry for the `frontend/src/app` route segment.

- L6 `function Providers({ children }: { children: ReactNode })` — Renders or constructs providers.

### [`frontend/src/components/ChatWorkspace.tsx`](../../frontend/src/components/ChatWorkspace.tsx)

Purpose: Renders and coordinates the chatworkspace user-interface component.

- L37 `function ChatWorkspace()` — Renders or constructs chatworkspace.
- L244 `handleSubmit(event: FormEvent<HTMLFormElement>)` — Implements handlesubmit.

### [`frontend/src/components/ChatWorkspaceLayout.tsx`](../../frontend/src/components/ChatWorkspaceLayout.tsx)

Purpose: Renders and coordinates the chatworkspacelayout user-interface component.

- L29 `function EmptyStateCaseRequired({ title, subtitle, description, onOpenIntake, }: { title: string; subtitle: string; description: string; onOpenIntake: () => void; })` — Renders or constructs emptystatecaserequired.
- L64 `function ChatWorkspaceLayout({ activeThread, activeThreadId, activeView, activeWorkspaceView, threads, threadsLoading, threadsError, creatingThread, deletingThreadId, phase, threadStatus, queryError, input, postAnswerAct` — Renders or constructs chatworkspacelayout.

### [`frontend/src/components/common/DeleteChatDialog.tsx`](../../frontend/src/components/common/DeleteChatDialog.tsx)

Purpose: Renders and coordinates the deletechatdialog user-interface component.

- L6 `interface DeleteChatDialogProps` — Defines the structural contract for deletechatdialogprops.
- L13 `function DeleteChatDialog({ thread, isDeleting, onCancel, onConfirm, }: DeleteChatDialogProps)` — Renders or constructs deletechatdialog.

### [`frontend/src/components/common/icons.tsx`](../../frontend/src/components/common/icons.tsx)

Purpose: Renders and coordinates the icons user-interface component.

- L3 `type IconName` — Defines the type contract for iconname.
- L99 `interface IconProps` — Defines the structural contract for iconprops.
- L103 `function Icon({ name, ...props }: IconProps)` — Renders or constructs icon.

### [`frontend/src/components/common/MeaningfulErrorModal.tsx`](../../frontend/src/components/common/MeaningfulErrorModal.tsx)

Purpose: Renders and coordinates the meaningfulerrormodal user-interface component.

- L7 `interface MeaningfulErrorModalProps` — Defines the structural contract for meaningfulerrormodalprops.
- L14 `function MeaningfulErrorModal({ isOpen, error, onClose, onRetry, }: MeaningfulErrorModalProps)` — Renders or constructs meaningfulerrormodal.
- L31 `handleKeyDown(event: KeyboardEvent)` — Implements handlekeydown.
- L90 `handleBackdropClick(event: React.MouseEvent<HTMLDivElement>)` — Implements handlebackdropclick.

### [`frontend/src/components/common/types.ts`](../../frontend/src/components/common/types.ts)

Purpose: Renders and coordinates the types user-interface component.

- L1 `type RunPhase` — Defines the type contract for runphase.
- L9 `type WorkspaceView` — Defines the type contract for workspaceview.
- L17 `type WorkspaceRouteView` — Defines the type contract for workspacerouteview.
- L19 `function workspaceViewForRoute(view: WorkspaceRouteView): WorkspaceView` — Implements workspaceviewforroute.

### [`frontend/src/components/conversation/ChatMessageMarkdown.tsx`](../../frontend/src/components/conversation/ChatMessageMarkdown.tsx)

Purpose: Renders and coordinates the chatmessagemarkdown user-interface component.

- L6 `interface ChatMessageMarkdownProps` — Defines the structural contract for chatmessagemarkdownprops.
- L10 `function ChatMessageMarkdown({ content }: ChatMessageMarkdownProps)` — Renders or constructs chatmessagemarkdown.

### [`frontend/src/components/conversation/ChatPanel.tsx`](../../frontend/src/components/conversation/ChatPanel.tsx)

Purpose: Renders and coordinates the chatpanel user-interface component.

- L11 `interface ChatPanelProps` — Defines the structural contract for chatpanelprops.
- L22 `function ChatPanel({ messages, input, threadStatus, phase, postAnswerAction, onInputChange, onPostAnswerActionChange, onSubmit, }: ChatPanelProps)` — Renders or constructs chatpanel.
- L91 `interface ChatComposerProps` — Defines the structural contract for chatcomposerprops.
- L98 `function ChatComposer({ input, isSubmitting, onInputChange, onSubmit, }: ChatComposerProps)` — Renders or constructs chatcomposer.
- L114 `handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>)` — Implements handlekeydown.

### [`frontend/src/components/conversation/ChatTranscript.tsx`](../../frontend/src/components/conversation/ChatTranscript.tsx)

Purpose: Renders and coordinates the chattranscript user-interface component.

- L13 `interface ChatTranscriptProps` — Defines the structural contract for chattranscriptprops.
- L18 `function ChatTranscript({ messages, isProcessing, }: ChatTranscriptProps)` — Renders or constructs chattranscript.
- L104 `function FollowUpExplanation({ detail }: { detail: ChatFollowUpGapDetail })` — Renders or constructs followupexplanation.

### [`frontend/src/components/conversation/MitreCandidatePanel.tsx`](../../frontend/src/components/conversation/MitreCandidatePanel.tsx)

Purpose: Renders and coordinates the mitrecandidatepanel user-interface component.

- L3 `interface MitreCandidatePanelProps` — Defines the structural contract for mitrecandidatepanelprops.
- L7 `function MitreCandidatePanel({ candidates, }: MitreCandidatePanelProps)` — Renders or constructs mitrecandidatepanel.

### [`frontend/src/components/home/home-content.ts`](../../frontend/src/components/home/home-content.ts)

Purpose: Renders and coordinates the home content user-interface component.

- L1 `type HomePillarVisual` — Defines the type contract for homepillarvisual.
- L3 `interface HomePillar` — Defines the structural contract for homepillar.

### [`frontend/src/components/home/HomeFooter.tsx`](../../frontend/src/components/home/HomeFooter.tsx)

Purpose: Renders and coordinates the homefooter user-interface component.

- L3 `function HomeFooter()` — Renders or constructs homefooter.

### [`frontend/src/components/home/HomeHero.tsx`](../../frontend/src/components/home/HomeHero.tsx)

Purpose: Renders and coordinates the homehero user-interface component.

- L3 `function HomeHero()` — Renders or constructs homehero.

### [`frontend/src/components/home/HomeIntelligence.tsx`](../../frontend/src/components/home/HomeIntelligence.tsx)

Purpose: Renders and coordinates the homeintelligence user-interface component.

- L3 `function HomeIntelligence()` — Renders or constructs homeintelligence.

### [`frontend/src/components/home/HomeMiniVisual.tsx`](../../frontend/src/components/home/HomeMiniVisual.tsx)

Purpose: Renders and coordinates the homeminivisual user-interface component.

- L3 `function HomeMiniVisual({ type }: { type: HomePillarVisual })` — Renders or constructs homeminivisual.

### [`frontend/src/components/home/HomeNavigation.tsx`](../../frontend/src/components/home/HomeNavigation.tsx)

Purpose: Renders and coordinates the homenavigation user-interface component.

- L3 `function HomeNavigation()` — Renders or constructs homenavigation.

### [`frontend/src/components/home/HomePage.tsx`](../../frontend/src/components/home/HomePage.tsx)

Purpose: Renders and coordinates the homepage user-interface component.

- L8 `function HomePage()` — Renders or constructs homepage.

### [`frontend/src/components/home/HomePlatform.tsx`](../../frontend/src/components/home/HomePlatform.tsx)

Purpose: Renders and coordinates the homeplatform user-interface component.

- L4 `function HomePlatform()` — Renders or constructs homeplatform.

### [`frontend/src/components/home/HomeWorkflow.tsx`](../../frontend/src/components/home/HomeWorkflow.tsx)

Purpose: Renders and coordinates the homeworkflow user-interface component.

- L4 `function HomeWorkflow()` — Renders or constructs homeworkflow.

### [`frontend/src/components/intake/CaseIntakeView.tsx`](../../frontend/src/components/intake/CaseIntakeView.tsx)

Purpose: Renders and coordinates the caseintakeview user-interface component.

- L12 `interface CaseIntakeViewProps` — Defines the structural contract for caseintakeviewprops.
- L22 `function CaseIntakeView({ isSubmitting, onSubmitCase, messages = [], onOpenOverview, onOpenChat, onOpenMaterials, }: CaseIntakeViewProps)` — Renders or constructs caseintakeview.
- L38 `handleSubmit(event: FormEvent<HTMLFormElement>)` — Implements handlesubmit.

### [`frontend/src/components/intake/DocumentIngestionPreview.tsx`](../../frontend/src/components/intake/DocumentIngestionPreview.tsx)

Purpose: Renders and coordinates the documentingestionpreview user-interface component.

- L15 `function DocumentIngestionPreview()` — Renders or constructs documentingestionpreview.
- L33 `processDocument()` — Implements processdocument.
- L49 `handleClear()` — Implements handleclear.

### [`frontend/src/components/intake/DocumentIngestionResult.tsx`](../../frontend/src/components/intake/DocumentIngestionResult.tsx)

Purpose: Renders and coordinates the documentingestionresult user-interface component.

- L8 `function formatBox(box: DocumentBoundingBox | null): string` — Implements formatbox.
- L15 `function RegionResult({ region }: { region: DocumentRegionPreview })` — Renders or constructs regionresult.
- L57 `function PageResult({ page }: { page: DocumentPagePreview })` — Renders or constructs pageresult.
- L77 `function DocumentIngestionResult({ result, }: { result: IngestedDocumentPreview; })` — Renders or constructs documentingestionresult.

### [`frontend/src/components/layout/WorkspaceSidebar.tsx`](../../frontend/src/components/layout/WorkspaceSidebar.tsx)

Purpose: Renders and coordinates the workspacesidebar user-interface component.

- L13 `interface WorkspaceNavigationProps` — Defines the structural contract for workspacenavigationprops.
- L59 `function WorkspaceSidebar({ threads, activeThreadId, threadsLoading, threadsError, onSelectThread, onNewChat, onRequestDelete, deletingThreadId, activeView, onViewChange, }: WorkspaceNavigationProps)` — Renders or constructs workspacesidebar.

### [`frontend/src/components/materials/CaseMaterialsView.tsx`](../../frontend/src/components/materials/CaseMaterialsView.tsx)

Purpose: Renders and coordinates the casematerialsview user-interface component.

- L8 `interface CaseMaterialsViewProps` — Defines the structural contract for casematerialsviewprops.
- L14 `function MaterialRow({ item, onOpenChat, }: { item: CaseMaterialItem; onOpenChat?: () => void; })` — Renders or constructs materialrow.
- L83 `function CaseMaterialsView({ messages, onOpenChat, onOpenIntake, }: CaseMaterialsViewProps)` — Renders or constructs casematerialsview.

### [`frontend/src/components/overview/AttackStoryTimeline.tsx`](../../frontend/src/components/overview/AttackStoryTimeline.tsx)

Purpose: Renders and coordinates the attackstorytimeline user-interface component.

- L3 `interface AttackStoryTimelineProps` — Defines the structural contract for attackstorytimelineprops.
- L14 `function AttackStoryTimeline({ steps, onNavigateToSource, onSelectSource, activeSourceKey, }: AttackStoryTimelineProps)` — Renders or constructs attackstorytimeline.

### [`frontend/src/components/overview/CaseOverviewView.tsx`](../../frontend/src/components/overview/CaseOverviewView.tsx)

Purpose: Renders and coordinates the caseoverviewview user-interface component.

- L14 `interface CaseOverviewViewProps` — Defines the structural contract for caseoverviewviewprops.
- L26 `function CaseOverviewView({ threadId, threadTitle, threadStatus, messages, onOpenChat, onOpenReport, onOpenMaterials, onOpenTechnicalContext, onNavigateToSource, }: CaseOverviewViewProps)` — Renders or constructs caseoverviewview.
- L48 `handleSelectSource(sourceRef: SourceMessageRef, anchorEl: HTMLElement, sourceKey: string)` — Implements handleselectsource.
- L269 `function WhatHappenedCard({ summary }: { summary: string })` — Renders or constructs whathappenedcard.

### [`frontend/src/components/overview/EstablishedVsUnclearSection.tsx`](../../frontend/src/components/overview/EstablishedVsUnclearSection.tsx)

Purpose: Renders and coordinates the establishedvsunclearsection user-interface component.

- L3 `interface EstablishedVsUnclearSectionProps` — Defines the structural contract for establishedvsunclearsectionprops.
- L16 `function EstablishedVsUnclearSection({ establishedFacts, unclearItems, onNavigateToSource, onSelectSource, activeSourceKey, onOpenMaterials, }: EstablishedVsUnclearSectionProps)` — Renders or constructs establishedvsunclearsection.

### [`frontend/src/components/overview/InvestigationPointsSection.tsx`](../../frontend/src/components/overview/InvestigationPointsSection.tsx)

Purpose: Renders and coordinates the investigationpointssection user-interface component.

- L3 `interface InvestigationPointsSectionProps` — Defines the structural contract for investigationpointssectionprops.
- L7 `function InvestigationPointsSection({ points, }: InvestigationPointsSectionProps)` — Renders or constructs investigationpointssection.

### [`frontend/src/components/overview/MitreExplainedSimply.tsx`](../../frontend/src/components/overview/MitreExplainedSimply.tsx)

Purpose: Renders and coordinates the mitreexplainedsimply user-interface component.

- L3 `interface MitreExplainedSimplyProps` — Defines the structural contract for mitreexplainedsimplyprops.
- L8 `function MitreExplainedSimply({ techniques, onOpenTechnicalContext, }: MitreExplainedSimplyProps)` — Renders or constructs mitreexplainedsimply.

### [`frontend/src/components/overview/SourceEvidencePopover.tsx`](../../frontend/src/components/overview/SourceEvidencePopover.tsx)

Purpose: Renders and coordinates the sourceevidencepopover user-interface component.

- L8 `interface SourceEvidencePopoverProps` — Defines the structural contract for sourceevidencepopoverprops.
- L15 `function SourceEvidencePopover({ sourceRef, anchorElement, onClose, onNavigateToSource, }: SourceEvidencePopoverProps)` — Renders or constructs sourceevidencepopover.
- L32 `updatePosition()` — Implements updateposition.
- L79 `handleKeyDown(event: KeyboardEvent)` — Implements handlekeydown.
- L86 `handlePointerDown(event: PointerEvent | MouseEvent)` — Implements handlepointerdown.

### [`frontend/src/components/report/ChatReportView.tsx`](../../frontend/src/components/report/ChatReportView.tsx)

Purpose: Renders and coordinates the chatreportview user-interface component.

- L21 `interface ChatReportViewProps` — Defines the structural contract for chatreportviewprops.
- L31 `function ChatReportView({ threadId, threadTitle, threadStatus, hasMessages, hasCompletedAnalysis, onOpenChat, onOpenOverview, }: ChatReportViewProps)` — Renders or constructs chatreportview.
- L113 `handleClearReportError()` — Implements handleclearreporterror.
- L118 `handleRetryReport()` — Implements handleretryreport.
- L144 `handleGenerate()` — Implements handlegenerate.
- L162 `handleDownloadPdf(report: ChatReportRead)` — Implements handledownloadpdf.
- L304 `function reportRequestKey(): string` — Implements reportrequestkey.
- L311 `function downloadPdf(blob: Blob, versionNumber: number): void` — Implements downloadpdf.

### [`frontend/src/components/report/PersistedReportCard.tsx`](../../frontend/src/components/report/PersistedReportCard.tsx)

Purpose: Renders and coordinates the persistedreportcard user-interface component.

- L12 `interface PersistedReportCardProps` — Defines the structural contract for persistedreportcardprops.
- L20 `function PersistedReportCard({ report, threadId, threadTitle, isDownloading, onDownloadPdf, }: PersistedReportCardProps)` — Renders or constructs persistedreportcard.
- L74 `function ReportPdfViewer({ threadId, reportId, title, }: { threadId: string; reportId: string; title: string; })` — Renders or constructs reportpdfviewer.
- L192 `function ReportFailure({ report }: { report: ChatReportRead })` — Renders or constructs reportfailure.

### [`frontend/src/components/report/ReportHistory.tsx`](../../frontend/src/components/report/ReportHistory.tsx)

Purpose: Renders and coordinates the reporthistory user-interface component.

- L4 `interface ReportVersionSelectorProps` — Defines the structural contract for reportversionselectorprops.
- L10 `function ReportVersionSelector({ reports, selectedReportId, onSelect, }: ReportVersionSelectorProps)` — Renders or constructs reportversionselector.
- L46 `function NoSavedReport({ canGenerate, isGenerating, onGenerate, onOpenOverview, }: { canGenerate: boolean; isGenerating: boolean; onGenerate: () => void; onOpenOverview?: () => void; })` — Renders or constructs nosavedreport.

### [`frontend/src/components/technical/TechnicalContextView.tsx`](../../frontend/src/components/technical/TechnicalContextView.tsx)

Purpose: Renders and coordinates the technicalcontextview user-interface component.

- L13 `interface TechnicalContextViewProps` — Defines the structural contract for technicalcontextviewprops.
- L19 `function TechnicalItem({ item, onSelectSource, activeSourceKey, }: { item: TechnicalContextCard; onSelectSource: ( source: SourceMessageRef, element: HTMLElement, key: string, ) => void; activeSourceKey: string | null; }` — Renders or constructs technicalitem.
- L130 `function TechnicalContextView({ messages, onOpenIntake, onNavigateToSource, }: TechnicalContextViewProps)` — Renders or constructs technicalcontextview.
- L143 `handleSelectSource(source: SourceMessageRef, element: HTMLElement, key: string)` — Implements handleselectsource.
- L157 `handleClosePopover()` — Implements handleclosepopover.

### [`frontend/src/features/chat/routing/chat-route.ts`](../../frontend/src/features/chat/routing/chat-route.ts)

Purpose: Owns chat route behavior for the frontend application.

- L3 `interface ChatRouteState` — Defines the structural contract for chatroutestate.
- L8 `function decodeThreadId(segment: string): string` — Implements decodethreadid.
- L16 `function chatRouteState(pathname: string): ChatRouteState` — Implements chatroutestate.
- L39 `function chatPath(threadId: string, view: WorkspaceRouteView): string` — Implements chatpath.

### [`frontend/src/features/chat/runs/chat-polling.ts`](../../frontend/src/features/chat/runs/chat-polling.ts)

Purpose: Owns chat polling behavior for the frontend application.

- L9 `function waitForNextChatPoll(signal: AbortSignal): Promise<void>` — Implements waitfornextchatpoll.
- L28 `function isChatRequestCanceled(signal: AbortSignal, error: unknown): boolean` — Implements ischatrequestcanceled.
- L41 `interface ChatRunPollingOptions` — Defines the structural contract for chatrunpollingoptions.
- L53 `function pollChatRunUntilCompleted({ threadId, runId, generation, signal, isCurrentSelection, applyThreadDetail, }: ChatRunPollingOptions): Promise<ChatThreadDetail | null>` — Implements pollchatrununtilcompleted.

### [`frontend/src/features/chat/runs/use-chat-submission.ts`](../../frontend/src/features/chat/runs/use-chat-submission.ts)

Purpose: Owns use chat submission behavior for the frontend application.

- L22 `interface RouterLike` — Defines the structural contract for routerlike.
- L26 `interface UseChatSubmissionOptions` — Defines the structural contract for usechatsubmissionoptions.
- L59 `function useChatSubmission({ activeThreadIdRef, selectionGenerationRef, pollControllerRef, pendingSubmissionRef, messages, threads, phase, threadStatus, postAnswerAction, createThread, updateThread, router, chatPath, sel` — Implements usechatsubmission.

### [`frontend/src/features/chat/workspace/chat-workspace-types.ts`](../../frontend/src/features/chat/workspace/chat-workspace-types.ts)

Purpose: Owns chat workspace types behavior for the frontend application.

- L15 `interface PendingChatSubmission` — Defines the structural contract for pendingchatsubmission.
- L25 `interface ChatWorkspaceLayoutProps` — Defines the structural contract for chatworkspacelayoutprops.

### [`frontend/src/features/chat/workspace/use-chat-thread-deletion.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-deletion.ts)

Purpose: Owns use chat thread deletion behavior for the frontend application.

- L9 `interface RouterLike` — Defines the structural contract for routerlike.
- L13 `interface UseChatThreadDeletionOptions` — Defines the structural contract for usechatthreaddeletionoptions.
- L40 `function useChatThreadDeletion({ deleteCandidate, deletingThreadId, activeThreadIdRef, pollControllerRef, selectionGenerationRef, pendingSubmissionRef, deletedThreadIdsRef, activeView, threads, deleteThread, router, sele` — Implements usechatthreaddeletion.

### [`frontend/src/features/chat/workspace/use-chat-thread-selection.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-selection.ts)

Purpose: Owns use chat thread selection behavior for the frontend application.

- L21 `interface UseChatThreadSelectionOptions` — Defines the structural contract for usechatthreadselectionoptions.
- L27 `interface ChatThreadSelection` — Defines the structural contract for chatthreadselection.
- L76 `function phaseForThread(detail: ChatThreadDetail): RunPhase` — Implements phaseforthread.
- L83 `function useChatThreadSelection({ cacheUpsertThread, deletedThreadIdsRef, pendingSubmissionRef, }: UseChatThreadSelectionOptions): ChatThreadSelection` — Implements usechatthreadselection.

### [`frontend/src/hooks/use-chat-queries.ts`](../../frontend/src/hooks/use-chat-queries.ts)

Purpose: Owns use chat queries behavior for the frontend application.

- L16 `function sortThreads(threads: ChatThreadRead[]): ChatThreadRead[]` — Implements sortthreads.
- L22 `function useChatThreads()` — Implements usechatthreads.
- L30 `function useChatThreadMutations()` — Implements usechatthreadmutations.

### [`frontend/src/lib/api-client.ts`](../../frontend/src/lib/api-client.ts)

Purpose: Owns api client behavior for the frontend application.

- L14 `function getApiBaseUrl(): string` — Implements getapibaseurl.
- L36 `listChatThreads(signal?: AbortSignal): Promise<ChatThreadRead[]>` — Implements listchatthreads.
- L45 `createChatThread(title: string = "New case", signal?: AbortSignal): Promise<ChatThreadRead>` — Implements createchatthread.
- L57 `getChatThread(threadId: string, signal?: AbortSignal): Promise<ChatThreadDetail>` — Implements getchatthread.
- L68 `updateChatThread(threadId: string, title: string, signal?: AbortSignal): Promise<ChatThreadRead>` — Implements updatechatthread.
- L81 `deleteChatThread(threadId: string, signal?: AbortSignal): Promise<void>` — Implements deletechatthread.
- L90 `createChatMessage(threadId: string, content: string, idempotencyKey: string, signal?: AbortSignal, action?: ChatMessageAction): Promise<ChatMessageAccepted>` — Implements createchatmessage.
- L109 `getChatRun(threadId: string, runId: string, signal?: AbortSignal): Promise<ChatRun>` — Implements getchatrun.
- L121 `listChatReports(threadId: string, signal?: AbortSignal): Promise<ChatReportRead[]>` — Implements listchatreports.
- L132 `getChatReport(threadId: string, reportId: string, signal?: AbortSignal): Promise<ChatReportRead>` — Implements getchatreport.
- L144 `downloadChatReportPdf(threadId: string, reportId: string, signal?: AbortSignal): Promise<Blob>` — Implements downloadchatreportpdf.
- L156 `generateChatReport(threadId: string, idempotencyKey?: string, signal?: AbortSignal): Promise<ChatReportRead>` — Implements generatechatreport.
- L169 `function getApiErrorMessage(error: unknown, fallback: string): string` — Implements getapierrormessage.

### [`frontend/src/lib/api-types.ts`](../../frontend/src/lib/api-types.ts)

Purpose: Owns api types behavior for the frontend application.

- L1 `type ThreadStatus` — Defines the type contract for threadstatus.
- L8 `type ChatMessageAction` — Defines the type contract for chatmessageaction.
- L10 `type RunStatus` — Defines the type contract for runstatus.
- L12 `interface ChatThreadRead` — Defines the structural contract for chatthreadread.
- L20 `interface PersistedChatMessage` — Defines the structural contract for persistedchatmessage.
- L31 `interface ChatThreadDetail` — Defines the structural contract for chatthreaddetail.
- L35 `interface ChatRun` — Defines the structural contract for chatrun.
- L46 `interface ChatMessageAccepted` — Defines the structural contract for chatmessageaccepted.
- L51 `type ChatReportSupportType` — Defines the type contract for chatreportsupporttype.
- L58 `interface ChatReportClaim` — Defines the structural contract for chatreportclaim.
- L67 `interface ChatReportSection` — Defines the structural contract for chatreportsection.
- L74 `interface ChatStructuredReport` — Defines the structural contract for chatstructuredreport.
- L83 `interface ChatReportRead` — Defines the structural contract for chatreportread.

### [`frontend/src/lib/api.ts`](../../frontend/src/lib/api.ts)

Purpose: Owns api behavior for the frontend application.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/lib/case-evidence.ts`](../../frontend/src/lib/case-evidence.ts)

Purpose: Owns case evidence behavior for the frontend application.

- L3 `type CaseEvidenceKind` — Defines the type contract for caseevidencekind.
- L8 `type EvidenceSourceType` — Defines the type contract for evidencesourcetype.
- L13 `type MaterialType` — Defines the type contract for materialtype.
- L18 `interface CaseEvidencePresentation` — Defines the structural contract for caseevidencepresentation.
- L29 `function getCaseEvidenceKind(message: PersistedChatMessage): CaseEvidenceKind | null` — Implements getcaseevidencekind.
- L48 `function isCaseEvidenceMessage(message: PersistedChatMessage): boolean` — Implements iscaseevidencemessage.
- L54 `function getCaseEvidencePresentation(message: PersistedChatMessage): CaseEvidencePresentation | null` — Implements getcaseevidencepresentation.

### [`frontend/src/lib/case-materials.ts`](../../frontend/src/lib/case-materials.ts)

Purpose: Owns case materials behavior for the frontend application.

- L9 `interface CaseMaterialItem` — Defines the structural contract for casematerialitem.
- L21 `interface CaseMaterialsData` — Defines the structural contract for casematerialsdata.
- L27 `function formatTimestamp(isoString: string, ordinal: number): string` — Implements formattimestamp.
- L44 `function buildCaseMaterials(messages: PersistedChatMessage[]): CaseMaterialsData` — Implements buildcasematerials.

### [`frontend/src/lib/case-overview.ts`](../../frontend/src/lib/case-overview.ts)

Purpose: Owns case overview behavior for the frontend application.

- L7 `interface SourceMessageRef` — Defines the structural contract for sourcemessageref.
- L17 `interface MitreTechniqueRef` — Defines the structural contract for mitretechniqueref.
- L24 `interface AttackStoryStep` — Defines the structural contract for attackstorystep.
- L39 `interface EstablishedFact` — Defines the structural contract for establishedfact.
- L45 `interface UnclearItem` — Defines the structural contract for unclearitem.
- L55 `interface InvestigationPoint` — Defines the structural contract for investigationpoint.
- L63 `interface MitreExplainedCard` — Defines the structural contract for mitreexplainedcard.
- L72 `interface CaseOverviewData` — Defines the structural contract for caseoverviewdata.
- L84 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord.
- L90 `function asArray(value: unknown): unknown[] | null` — Implements asarray.
- L94 `function asString(value: unknown): string` — Implements asstring.
- L98 `interface RawTraceClaim` — Defines the structural contract for rawtraceclaim.
- L112 `interface RawTraceAssociation` — Defines the structural contract for rawtraceassociation.
- L121 `interface RawGapItem` — Defines the structural contract for rawgapitem.
- L131 `function parseAnalysisSections(markdown: string): Map<number, string>` — Implements parseanalysissections.
- L161 `function cleanMarkdownSnippet(text: string): string` — Implements cleanmarkdownsnippet.
- L170 `function mapSourceMessageIds(sourceIds: string[], allMessages: PersistedChatMessage[]): SourceMessageRef[]` — Implements mapsourcemessageids.
- L201 `function buildCaseOverview(messages: PersistedChatMessage[], threadStatus?: ThreadStatus | null): CaseOverviewData` — Implements buildcaseoverview.
- L515 `function formatInvestigationSuggestion(topic: string, description: string): string` — Implements formatinvestigationsuggestion.

### [`frontend/src/lib/chat-followup.ts`](../../frontend/src/lib/chat-followup.ts)

Purpose: Owns chat followup behavior for the frontend application.

- L7 `interface ChatFollowUpEntry` — Defines the structural contract for chatfollowupentry.
- L12 `interface ActiveChatFollowUp` — Defines the structural contract for activechatfollowup.
- L18 `interface ChatFollowUpGapDetail` — Defines the structural contract for chatfollowupgapdetail.
- L32 `interface FollowUpMetadata` — Defines the structural contract for followupmetadata.
- L37 `function followUpMetadata(message: PersistedChatMessage): FollowUpMetadata | null` — Implements followupmetadata.
- L64 `function isRecord(value: unknown): value is Record<string, unknown>` — Implements isrecord.
- L68 `function isNonEmptyString(value: unknown): value is string` — Implements isnonemptystring.
- L72 `function isGapStatus(value: unknown): value is ChatFollowUpGapDetail["status"]` — Implements isgapstatus.
- L83 `function isGapPriority(value: unknown): value is ChatFollowUpGapDetail["priority"]` — Implements isgappriority.
- L89 `function followUpGapDetailForMessage(message: PersistedChatMessage): ChatFollowUpGapDetail | null` — Implements followupgapdetailformessage.
- L120 `function orderedMessages(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements orderedmessages.
- L128 `function latestUserAnswerBetween(persistedMessages: PersistedChatMessage[], questionOrdinal: number, nextAssistantOrdinal?: number): PersistedChatMessage | null` — Implements latestuseranswerbetween.
- L143 `function activeChatFollowUpForThread(persistedMessages: PersistedChatMessage[], status: ThreadStatus | null): ActiveChatFollowUp | null` — Implements activechatfollowupforthread.
- L206 `function filterSupersededClarificationAnswers(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements filtersupersededclarificationanswers.
- L243 `function chatTranscriptMessages(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements chattranscriptmessages.
- L249 `function persistedRequestOrdinal(detail: ChatThreadDetail, lastKnownMessageOrdinal: number, content: string): number | undefined` — Implements persistedrequestordinal.
- L262 `function hasCompletedAssistantOutput(detail: ChatThreadDetail, requestOrdinal: number): boolean` — Implements hascompletedassistantoutput.

### [`frontend/src/lib/document-ingestion-store.ts`](../../frontend/src/lib/document-ingestion-store.ts)

Purpose: Owns document ingestion store behavior for the frontend application.

- L9 `interface DocumentIngestionState` — Defines the structural contract for documentingestionstate.
- L29 `function loadInitialState(): DocumentIngestionState` — Implements loadinitialstate.
- L52 `function saveToSessionStorage(state: DocumentIngestionState)` — Implements savetosessionstorage.
- L80 `function notify()` — Implements notify.
- L85 `function getDocumentIngestionSnapshot(): DocumentIngestionState` — Implements getdocumentingestionsnapshot.
- L89 `function getServerSnapshot(): DocumentIngestionState` — Implements getserversnapshot.
- L93 `function subscribeDocumentIngestion(listener: () => void): () => void` — Implements subscribedocumentingestion.
- L100 `function hydrateDocumentIngestionStore()` — Implements hydratedocumentingestionstore.
- L115 `function setDocumentIngestionFile(file: File | null)` — Implements setdocumentingestionfile.
- L128 `function setDocumentIngestionMode(mode: DocumentIngestionMode)` — Implements setdocumentingestionmode.
- L136 `function setDocumentIngestionProcessing(isProcessing: boolean)` — Implements setdocumentingestionprocessing.
- L144 `function setDocumentIngestionResult(result: IngestedDocumentPreview | null)` — Implements setdocumentingestionresult.
- L153 `function setDocumentIngestionError(error: string | null)` — Implements setdocumentingestionerror.
- L161 `function resetDocumentIngestionState()` — Implements resetdocumentingestionstate.
- L166 `function useDocumentIngestion()` — Implements usedocumentingestion.

### [`frontend/src/lib/document-ingestion.ts`](../../frontend/src/lib/document-ingestion.ts)

Purpose: Owns document ingestion behavior for the frontend application.

- L5 `type DocumentIngestionMode` — Defines the type contract for documentingestionmode.
- L7 `interface DocumentBoundingBox` — Defines the structural contract for documentboundingbox.
- L14 `interface DocumentRecognitionCandidate` — Defines the structural contract for documentrecognitioncandidate.
- L23 `interface DocumentGeneratedContent` — Defines the structural contract for documentgeneratedcontent.
- L29 `interface DocumentRegionPreview` — Defines the structural contract for documentregionpreview.
- L47 `interface DocumentRoutingSummary` — Defines the structural contract for documentroutingsummary.
- L56 `interface DocumentPagePreview` — Defines the structural contract for documentpagepreview.
- L63 `interface IngestedDocumentPreview` — Defines the structural contract for ingesteddocumentpreview.
- L74 `function previewDocumentIngestion(file: File, mode: DocumentIngestionMode, signal?: AbortSignal): Promise<IngestedDocumentPreview>` — Implements previewdocumentingestion.

### [`frontend/src/lib/mitre-candidate.ts`](../../frontend/src/lib/mitre-candidate.ts)

Purpose: Owns mitre candidate behavior for the frontend application.

- L3 `interface MitreLinkedClaimView` — Defines the structural contract for mitrelinkedclaimview.
- L16 `interface MitreCandidateView` — Defines the structural contract for mitrecandidateview.
- L38 `function mitreCandidatesForMessage(message: PersistedChatMessage): MitreCandidateView[] | null` — Implements mitrecandidatesformessage.
- L87 `function parseClaims(value: unknown): Map<string, MitreLinkedClaimView> | null` — Implements parseclaims.
- L120 `function admittedMitreRows(rows: unknown[]): Map<string, string>` — Implements admittedmitrerows.
- L136 `function isValidatedTrace(trace: Record<string, unknown> | null): trace is Record<string, unknown>` — Implements isvalidatedtrace.
- L150 `function hasOnlyAssociationKeys(value: Record<string, unknown>): boolean` — Implements hasonlyassociationkeys.
- L162 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord.
- L168 `function asArray(value: unknown): unknown[] | null` — Implements asarray.
- L172 `function requiredString(value: unknown): string | null` — Implements requiredstring.
- L176 `function stringArray(value: unknown): string[] | null` — Implements stringarray.

### [`frontend/src/lib/query-keys.ts`](../../frontend/src/lib/query-keys.ts)

Purpose: Owns query keys behavior for the frontend application.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/lib/technical-context.ts`](../../frontend/src/lib/technical-context.ts)

Purpose: Owns technical context behavior for the frontend application.

- L5 `interface TechnicalContextCard` — Defines the structural contract for technicalcontextcard.
- L16 `interface TechnicalContextData` — Defines the structural contract for technicalcontextdata.
- L22 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord.
- L28 `function asArray(value: unknown): unknown[] | null` — Implements asarray.
- L32 `function asString(value: unknown): string` — Implements asstring.
- L36 `function extractShortPlainMeaning(description: string): string` — Implements extractshortplainmeaning.
- L46 `function resolveCaseRelevance(reason: string): string` — Implements resolvecaserelevance.
- L58 `function mapSourceMessageIds(sourceIds: string[], allMessages: PersistedChatMessage[]): SourceMessageRef[]` — Implements mapsourcemessageids.
- L90 `function buildTechnicalContext(messages: PersistedChatMessage[]): TechnicalContextData` — Implements buildtechnicalcontext.
- L125 `interface MitreTableRow` — Defines the structural contract for mitretablerow.

### [`frontend/src/lib/user-facing-error.ts`](../../frontend/src/lib/user-facing-error.ts)

Purpose: Owns user facing error behavior for the frontend application.

- L3 `type ErrorCategory` — Defines the type contract for errorcategory.
- L11 `interface UserFacingError` — Defines the structural contract for userfacingerror.
- L49 `function isTimeoutString(str: string): boolean` — Implements istimeoutstring.
- L53 `function isNetworkString(str: string): boolean` — Implements isnetworkstring.
- L61 `function isRateLimitString(str: string): boolean` — Implements isratelimitstring.
- L65 `function isServerErrorString(str: string): boolean` — Implements isservererrorstring.
- L71 `function toUserFacingError(rawError: unknown, options?: { isUncertain?: boolean; actionLabel?: string; }): UserFacingError` — Implements touserfacingerror.

## Frontend Regression Suite

### [`frontend/src/test/components/chat/ChatMessageMarkdown.test.tsx`](../../frontend/src/test/components/chat/ChatMessageMarkdown.test.tsx)

Purpose: Verifies chatmessagemarkdown test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/chat/ChatPanelFollowUp.test.tsx`](../../frontend/src/test/components/chat/ChatPanelFollowUp.test.tsx)

Purpose: Verifies chatpanelfollowup test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/chat/MitreCandidatePanel.test.tsx`](../../frontend/src/test/components/chat/MitreCandidatePanel.test.tsx)

Purpose: Verifies mitrecandidatepanel test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/common/MeaningfulErrorModal.test.tsx`](../../frontend/src/test/components/common/MeaningfulErrorModal.test.tsx)

Purpose: Verifies meaningfulerrormodal test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/home/HomePage.test.tsx`](../../frontend/src/test/components/home/HomePage.test.tsx)

Purpose: Verifies homepage test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/CaseIntakeView.test.tsx`](../../frontend/src/test/components/intake/CaseIntakeView.test.tsx)

Purpose: Verifies caseintakeview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/DocumentIngestionPreview.test.tsx`](../../frontend/src/test/components/intake/DocumentIngestionPreview.test.tsx)

Purpose: Verifies documentingestionpreview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/layout/WorkspaceSidebar.test.tsx`](../../frontend/src/test/components/layout/WorkspaceSidebar.test.tsx)

Purpose: Verifies workspacesidebar test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/materials/CaseMaterialsView.test.tsx`](../../frontend/src/test/components/materials/CaseMaterialsView.test.tsx)

Purpose: Verifies casematerialsview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/overview/CaseOverviewView.test.tsx`](../../frontend/src/test/components/overview/CaseOverviewView.test.tsx)

Purpose: Verifies caseoverviewview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/overview/SourceEvidencePopover.test.tsx`](../../frontend/src/test/components/overview/SourceEvidencePopover.test.tsx)

Purpose: Verifies sourceevidencepopover test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/report/ChatReportView.test.tsx`](../../frontend/src/test/components/report/ChatReportView.test.tsx)

Purpose: Verifies chatreportview test behavior in the frontend regression suite.

- L7 `function sampleReport(): api.ChatReportRead` — Implements samplereport.

### [`frontend/src/test/components/report/PersistedReportCard.test.tsx`](../../frontend/src/test/components/report/PersistedReportCard.test.tsx)

Purpose: Verifies persistedreportcard test behavior in the frontend regression suite.

- L9 `function sampleReport(): ChatReportRead` — Implements samplereport.

### [`frontend/src/test/components/technical/TechnicalContextView.test.tsx`](../../frontend/src/test/components/technical/TechnicalContextView.test.tsx)

Purpose: Verifies technicalcontextview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-route.test.ts`](../../frontend/src/test/features/chat/chat-route.test.ts)

Purpose: Verifies chat route test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx`](../../frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx)

Purpose: Verifies chatworkspaceintake test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/case-evidence.test.ts`](../../frontend/src/test/lib/case-evidence.test.ts)

Purpose: Verifies case evidence test behavior in the frontend regression suite.

- L9 `function makeUserMessage(ordinal: number, metadata: Record<string, unknown> = {}, content = "Test content"): PersistedChatMessage` — Implements makeusermessage.
- L26 `function makeAssistantMessage(ordinal: number, metadata: Record<string, unknown> = {}, content = "Assistant response"): PersistedChatMessage` — Implements makeassistantmessage.

### [`frontend/src/test/lib/case-materials.test.ts`](../../frontend/src/test/lib/case-materials.test.ts)

Purpose: Verifies case materials test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/case-overview.test.ts`](../../frontend/src/test/lib/case-overview.test.ts)

Purpose: Verifies case overview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/chat-followup.test.ts`](../../frontend/src/test/lib/chat-followup.test.ts)

Purpose: Verifies chat followup test behavior in the frontend regression suite.

- L11 `function message(ordinal: number, role: PersistedChatMessage["role"], content: string, metadata_json: Record<string, unknown> = {}): PersistedChatMessage` — Implements message.
- L29 `function clarification(ordinal: number, content: string, round: number): PersistedChatMessage` — Implements clarification.

### [`frontend/src/test/lib/mitre-candidate.test.ts`](../../frontend/src/test/lib/mitre-candidate.test.ts)

Purpose: Verifies mitre candidate test behavior in the frontend regression suite.

- L6 `function message(metadataOverrides: Record<string, unknown> = {}): PersistedChatMessage` — Implements message.

### [`frontend/src/test/lib/technical-context.test.ts`](../../frontend/src/test/lib/technical-context.test.ts)

Purpose: Verifies technical context test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/user-facing-error.test.ts`](../../frontend/src/test/lib/user-facing-error.test.ts)

Purpose: Verifies user facing error test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/setup.ts`](../../frontend/src/test/setup.ts)

Purpose: Verifies setup behavior in the frontend regression suite.

- L3 `class MockResizeObserver` — Encapsulates mockresizeobserver.
- L4 `observe()` — Implements observe.
- L5 `unobserve()` — Implements unobserve.
- L6 `disconnect()` — Implements disconnect.
- L15 `get()` — Retrieves get.
- L21 `get()` — Retrieves get.
- L27 `get()` — Retrieves get.
- L33 `get()` — Retrieves get.

## Graphrag Runtime And Evaluation Package

### [`rag_service/app/main.py`](../../rag_service/app/main.py)

Purpose: Owns main behavior for the GraphRAG runtime and evaluation package.

- L16 `async def lifespan(app: FastAPI)` — Startup / shutdown lifecycle.

### [`rag_service/app/RAG/__init__.py`](../../rag_service/app/RAG/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/__init__.py`](../../rag_service/app/RAG/GraphRAG/__init__.py)

Purpose: MITRE ATT&CK GraphRAG Pipeline ================================ Hybrid Graph + Vector DB RAG with Cross-Lingual (Thai ↔ English) support.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/config.py`](../../rag_service/app/RAG/GraphRAG/config.py)

Purpose: Central Configuration for MITRE ATT&CK GraphRAG.

- L46 `def _resolve_device() -> str` — Implements resolve device.
- L110 `def validate_core_llm_provider(value: str) -> str` — Validates core llm provider.
- L313 `def sep(title='')` — Print a separator line for console output.

### [`rag_service/app/RAG/GraphRAG/docs/make_retrieval_ranking_report.py`](../../rag_service/app/RAG/GraphRAG/docs/make_retrieval_ranking_report.py)

Purpose: Build the Thai progress report PDF for the real-CTI evaluation work.

- L55 `def P(t, s='body')` — Renders or constructs p.
- L59 `def code(lines)` — Implements code.
- L63 `def table(rows, widths, header=True, aligns=None)` — Implements table.
- L89 `def chrome(canvas, doc)` — Implements chrome.

### [`rag_service/app/RAG/GraphRAG/evaluation/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/__init__.py)

Purpose: RAG Evaluation Framework ========================= Modular evaluation for retriever quality, generation quality (RAGAS), and end-to-end GraphRAG pipeline performance.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/attack_id_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/attack_id_metrics.py)

Purpose: ATT&CK ID-Based Generation Metrics ==================================== Deterministic metrics for scoring generated answers against gold ATT&CK technique IDs — TRAM/CTIBench-style correctness scoring, plus guard metrics for the Thai output contract.

- L53 `def extract_attack_ids(text: str) -> set[str]` — All MITRE ATT&CK IDs (any entity kind) in the text, uppercased.
- L58 `def extract_technique_ids(text: str) -> set[str]` — Technique IDs only (T####/T####.###), excluding tactics (TA####).
- L66 `def extract_technique_names(text: str, alias_map: dict[str, str]) -> set[str]` — Technique IDs whose canonical name/alias appears in the text.
- L88 `def extract_all_techniques(text: str, alias_map: Optional[dict[str, str]]=None) -> set[str]` — Union of ID-cited and name-cited techniques in the answer.
- L100 `def _base_technique(attack_id: str) -> str` — T1566.002 -> T1566; T1566 -> T1566.
- L105 `def technique_set_score(predicted: set[str], gold: set[str]) -> dict` — Soft precision/recall/F1 between predicted and gold technique IDs.
- L160 `def tactic_level_score(predicted: set[str], gold: set[str], technique_to_tactics: dict[str, list[str]]) -> dict` — Set precision/recall/F1 at the tactic level (coarser credit).
- L171 `def tactics_of(ids: set[str]) -> set[str]` — Implements tactics of.
- L206 `def thai_char_ratio(text: str) -> float` — Thai letters / (Thai + Latin letters).
- L220 `def structure_compliance(text: str, required_headings: list[str]) -> dict` — Which required section headings appear in the answer (case-insensitive).
- L232 `def id_survival(source_text: str, translated_text: str) -> dict` — Technique IDs preserved across the translation stage.

### [`rag_service/app/RAG/GraphRAG/evaluation/build_deprecated_blocklist.py`](../../rag_service/app/RAG/GraphRAG/evaluation/build_deprecated_blocklist.py)

Purpose: Build Deprecated/Revoked ATT&CK ID Blocklist ============================================== The Neo4j graph does not store `revoked` / `x_mitre_deprecated` flags (ingestion drops them), so deprecated techniques like T1064 (Scripting) look identical to live ones and leak into sampled kill-chains.

- L36 `def latest_bundle(domain_dir: Path) -> Path | None` — Newest versioned bundle in a domain folder (e.g.
- L50 `def attack_id_of(obj: dict) -> str | None` — Implements attack id of.
- L57 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/crosslingual_benchmark.py`](../../rag_service/app/RAG/GraphRAG/evaluation/crosslingual_benchmark.py)

Purpose: Cross-Lingual Retrieval Benchmark ================================== Compares three retrieval configurations for Thai queries against the English-only MITRE ATT&CK knowledge base: 1.

- L62 `def load_cache(path: Path) -> dict[str, str]` — Retrieves cache.
- L69 `def save_cache(cache: dict[str, str], path: Path) -> None` — Persists cache.
- L74 `def translate_all(samples: list[EvalSample], cache_path: Path, use_local: bool) -> dict[str, str]` — Translate every query once, reusing/extending the on-disk cache.
- L113 `class RetrievalBackend` — Shared retrieval stack: one embed model, one reranker, one Qdrant client.
- L122 `def __init__(self, with_graph: bool, top_k: int)` — Implements init.
- L146 `def close(self) -> None` — Implements close.
- L150 `def retrieve_ids(self, queries: list[str]) -> list[str]` — Implements retrieve ids.
- L155 `def _retrieve_vector_rerank(self, queries: list[str]) -> list[str]` — Implements retrieve vector rerank.
- L165 `def _retrieve_hybrid(self, queries: list[str]) -> list[str]` — Implements retrieve hybrid.
- L190 `def print_comparison(results: list[RetrieverEvalResult]) -> None` — Implements print comparison.
- L227 `def main() -> None` — Implements main.
- L267 `class Tee` — Encapsulates tee.
- L268 `def write(self, data)` — Implements write.
- L272 `def flush(self)` — Implements flush.
- L296 `def trag_fn(query: str) -> list[str]` — Implements trag fn.
- L299 `def thai_direct_fn(query: str) -> list[str]` — Implements thai direct fn.
- L302 `def dual_fn(query: str) -> list[str]` — Implements dual fn.

### [`rag_service/app/RAG/GraphRAG/evaluation/crosslingual_generation_benchmark.py`](../../rag_service/app/RAG/GraphRAG/evaluation/crosslingual_generation_benchmark.py)

Purpose: Cross-Lingual Generation Benchmark ==================================== Compares 5 generation-path variants over FROZEN retrieval contexts, so score differences are attributable to the generation stage only.

- L113 `def load_samples(dataset_path: Path, max_samples: int=0) -> list[dict]` — Thai incident samples with gold IDs (the benchmark's unit of work).
- L143 `def phase_retrieve(samples: list[dict], use_local: bool=False) -> None` — Retrieve ONCE per sample, mirroring the production agent path (_node_retrieve): Thai incident -> decomposer -> native-language sub-queries -> retrieve_multi_quota -> build_context(15/8).
- L282 `def _invoke(llm, system: str, user: str) -> tuple[str, dict]` — One LLM call -> (text, {input_tokens, output_tokens}).
- L299 `def _sum_usage(*usages: dict) -> dict` — Implements sum usage.
- L306 `def run_variant(variant: str, ctx: dict, reasoning_llm, cheap_llm) -> dict` — Execute one variant over a cached context.
- L377 `def phase_generate(variants: list[str], reasoning_model: str, cheap_model: str, max_samples: int=0) -> None` — Implements phase generate.
- L406 `def make_llm(model: str)` — Implements make llm.
- L466 `def _bootstrap_ci(deltas: list[float], n_boot: int=10000, seed: int=42) -> tuple[float, float]` — 95% bootstrap CI of the mean of paired deltas.
- L479 `def _wilcoxon_p(deltas: list[float]) -> float | None` — Two-sided Wilcoxon signed-rank p-value (scipy if available).
- L491 `def score_row(row: dict, sample: dict, lookup: dict) -> dict` — All deterministic metrics for one (sample, variant) generation.
- L535 `def phase_score(dataset_path: Path) -> None` — Implements phase score.
- L615 `def phase_score_retrieval(dataset_path: Path, k_values: tuple[int, ...]=(5, 10, 15, 20)) -> None` — Step-coverage@k of the production retrieval path, per cue_type.
- L648 `def mean(vals: list[float]) -> float` — Implements mean.
- L700 `def _shim_rag_result(raw: dict)` — Rebuild a GraphRAGResult look-alike from cached mapping_raw so the REAL production build_mitre_table runs offline — no logic duplication.
- L726 `def _is_technique_label(label: str) -> bool` — Determines technique label.
- L730 `def _technique_ids_from_rows(rows) -> set[str]` — Implements technique ids from rows.
- L737 `def _raw_retrieval_technique_ids(raw: dict) -> set[str]` — The no-filter baseline: every technique ID retrieval dragged in.
- L751 `def phase_score_mapping(dataset_path: Path, thresholds: list[float]) -> None` — Implements phase score mapping.
- L798 `def _mean(dicts: list[dict], key: str) -> float` — Implements mean.
- L869 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/__init__.py)

Purpose: Embedding-model A/B experiment (thesis section 5.1).

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/arms.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/arms.py)

Purpose: The three retrieval arms of the embedding-model comparison.

- L58 `def make_client() -> QdrantClient` — Implements make client.
- L66 `def load_bge()` — Retrieves bge.
- L72 `def load_e5()` — Retrieves e5.
- L83 `class Hit` — Encapsulates hit.
- L89 `class _ArmBase` — Shared search topology.
- L95 `def __init__(self, client: Optional[QdrantClient]=None)` — Implements init.
- L99 `def _query_collection(self, collection: str, query: str, top_k: int, qdrant_filter: Optional[Filter]) -> list[Hit]` — Implements query collection.
- L105 `def _normalize(hits: list[Hit]) -> None` — Normalizes normalize.
- L115 `def search_entities(self, query: str, top_k: int) -> list[Hit]` — Implements search entities.
- L123 `def search_relationships(self, query: str, top_k: int) -> list[Hit]` — Implements search relationships.
- L126 `def search_all(self, query: str, top_k: int=VECTOR_TOP_K) -> list[Hit]` — Implements search all.
- L135 `def retrieve_ids(self, query: str, top_k: int=VECTOR_TOP_K) -> list[str]` — Implements retrieve ids.
- L139 `def _parse(points) -> list[Hit]` — Parses parse.
- L151 `class BgeHybridArm(_ArmBase)` — Arm A — the deployed stack: BGE-M3 dense + sparse, Qdrant native RRF.
- L159 `def __init__(self, model, client=None)` — Implements init.
- L163 `def _encode(self, query: str)` — Serializes encode.
- L174 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection.
- L191 `class BgeDenseArm(_ArmBase)` — Arm B — BGE-M3 with the sparse component removed.
- L203 `def __init__(self, model, client=None)` — Implements init.
- L207 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection.
- L222 `class E5DenseArm(_ArmBase)` — Arm C — multilingual-e5-large, dense only (the model has no sparse head).
- L230 `def __init__(self, model, client=None)` — Implements init.
- L234 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/ingest_e5.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/ingest_e5.py)

Purpose: Re-embed the ATT&CK corpus with multilingual-e5-large into its own Qdrant collections, so arm C can be compared against the BGE-M3 arms.

- L55 `def _client() -> QdrantClient` — Implements client.
- L65 `def _init_collection(client: QdrantClient, name: str) -> None` — Dense-only collection.
- L78 `def _entity_docs(entities) -> tuple[list[str], list[str], list[dict]]` — Identical text/payload construction to VectorLoader.load_entities.
- L100 `def _relationship_docs(relationships) -> tuple[list[str], list[str], list[dict]]` — Identical text/payload construction to VectorLoader.load_relationships.
- L122 `def _load(client, model, collection: str, ids, docs, metas, label: str) -> int` — Retrieves load.
- L168 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/run_ab.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/run_ab.py)

Purpose: Run the embedding-model A/B/C comparison and write a report.

- L57 `def _pair_key(s: EvalSample) -> tuple` — Thai variants copy their source sample's gold IDs verbatim, so (category, gold set) identifies a translation pair.
- L63 `def build_pairs(samples: list[EvalSample], max_pairs: int, seed: int=42)` — Return [(th_sample, en_sample)], stratified across categories.
- L101 `def gold_coverage(client, pairs, collections_pair) -> dict` — What fraction of gold STIX IDs actually exist as points in the corpus? Gold comes from Neo4j; the vector corpus drops entities/relationships that have no description.
- L127 `def run_arm(arm, pairs, lang_label: str) -> dict` — Executes arm.
- L143 `def _fmt(v) -> str` — Implements fmt.
- L147 `def write_report(rows: list[dict], coverage: dict, out_dir: Path, meta: dict) -> Path` — Implements write report.
- L199 `def main() -> int` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/eval_runner.py`](../../rag_service/app/RAG/GraphRAG/evaluation/eval_runner.py)

Purpose: Evaluation Runner ================== CLI orchestrator for RAG evaluation.

- L47 `def _make_vector_retriever_fn(embed_model=None)` — Create a retriever function for vector-only search.
- L53 `def fn(query: str) -> list[str]` — Implements fn.
- L60 `def _make_graph_retriever_fn()` — Create a retriever function for graph-only search (requires STIX IDs as seed).
- L71 `def fn(query: str) -> list[str]` — Implements fn.
- L127 `def _subtechnique_parent_map() -> dict[str, str]` — sub-technique stix_id -> parent technique stix_id.
- L167 `def _normalise_to_parent(fn, parent_map: dict[str, str])` — Wrap a retriever fn so its ids are parent-granular, like the gold.
- L178 `def wrapped(query: str) -> list[str]` — Implements wrapped.
- L191 `def _collect_hybrid_ids(result) -> list[str]` — Flatten a GraphRAGResult into an ordered, deduped STIX-id list (vector hits first, then each subgraph's center node + neighbors).
- L211 `def _make_hybrid_retriever_fn(embed_model=None)` — Create a retriever function for hybrid (Vector + Graph) search — single-query baseline (no decomposition).
- L218 `def fn(query: str) -> list[str]` — Implements fn.
- L225 `def _make_hybrid_quota_retriever_fn(embed_model=None, use_local: bool=False)` — Hybrid retriever with query decomposition + per-query quota — mirrors the production agent path (``_node_retrieve``).
- L244 `def fn(query: str) -> list[str]` — Implements fn.
- L268 `def _make_generation_fn(embed_model=None)` — Create a generation function wrapping GraphRAGAgent — the served path.
- L287 `def fn(query: str) -> tuple[str, list[str]]` — Returns (answer, list_of_context_chunks).
- L312 `class _ArmSkipped(Exception)` — Raised to skip an arm the caller did not select in --arms.
- L316 `class EvalRunner` — Orchestrates the full evaluation pipeline.
- L324 `def __init__(self, dataset_path: str, mode: str='full', use_local: bool=False, max_samples: int=0, arms: tuple[str, ...] | None=None, k_values: list[int] | None=None)` — Implements init.
- L356 `def _get_embed_model(self)` — Lazy-load and share the embedding model.
- L366 `def run(self) -> dict` — Execute evaluation and return results dict.
- L386 `def _run_retriever_eval(self) -> list[RetrieverEvalResult]` — Run retriever benchmarks on all 3 retriever modes.
- L486 `def _run_generation_eval(self) -> GenerationEvalResult` — Run generation evaluation.
- L502 `def _print_comparison(self, results: list[RetrieverEvalResult]) -> None` — Print a side-by-side comparison table.
- L550 `def main()` — Implements main.
- L612 `class Tee` — Encapsulates tee.
- L613 `def write(self, data)` — Implements write.
- L617 `def flush(self)` — Implements flush.

### [`rag_service/app/RAG/GraphRAG/evaluation/export_alias_tables.py`](../../rag_service/app/RAG/GraphRAG/evaluation/export_alias_tables.py)

Purpose: Export Alias / Tactic Lookup Tables from Neo4j ================================================ One-off export for attack_id_metrics.py: - alias_map : lowercased technique name -> attack_id, used by extract_technique_names() to credit answers that name a technique without citing its ID - technique_to_tactics : attack_id -> tactic shortnames, used by tactic_level_score() Output: evaluation/data/attack_lookup.json Usage: cd rag_service/app/RAG/GraphRAG python -m evaluation.export_alias_tables.

- L49 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/generate_eval_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/generate_eval_dataset.py)

Purpose: Neo4j-Grounded Evaluation Dataset Generator ============================================= Generates a validated evaluation dataset by querying Neo4j directly, eliminating manual ground-truth labeling errors.

- L59 `class GeneratedSample` — A single generated evaluation sample.
- L82 `def to_dict(self) -> dict` — Transforms dict.
- L100 `class Neo4jGroundTruthBuilder` — Connects to Neo4j and runs Cypher queries for ground truth extraction.
- L103 `def __init__(self)` — Implements init.
- L107 `def close(self)` — Implements close.
- L110 `def run_query(self, cypher: str, params: dict | None=None) -> list[dict]` — Execute a Cypher query and return results as list of dicts.
- L118 `def get_top_techniques(self, limit: int=15) -> list[dict]` — Find techniques with the most relationships (well-connected nodes).
- L130 `def get_top_groups(self, limit: int=12) -> list[dict]` — Find groups with the most USES relationships.
- L141 `def get_top_software(self, limit: int=12) -> list[dict]` — Find software with the most USES relationships.
- L153 `def get_all_tactics(self) -> list[dict]` — Get all tactics.
- L162 `def get_groups_with_campaigns(self, limit: int=8) -> list[dict]` — Find groups that have campaigns attributed to them.
- L174 `def get_techniques_with_detection(self, limit: int=10) -> list[dict]` — Find techniques that have DataComponent detection links.
- L187 `def get_techniques_by_attack_ids(self, attack_ids: list[str]) -> dict[str, str]` — Return {attack_id: stix_id} for the given ATT&CK IDs (techniques + subtechniques).
- L211 `class QueryTemplateRegistry` — Defines evaluation query templates that map to Cypher traversal patterns.
- L214 `def __init__(self, neo4j: Neo4jGroundTruthBuilder)` — Implements init.
- L219 `def generate_mitigation_lookup(self, technique: dict) -> GeneratedSample | None` — 'What mitigations exist for [technique]?' → MITIGATES relationship.
- L269 `def generate_technique_lookup(self, technique: dict) -> GeneratedSample | None` — 'What is [technique] ([ATT&CK ID])?' → node + subtechniques + description.
- L315 `def generate_group_software(self, group: dict) -> GeneratedSample | None` — 'What tools and malware does [group] use?' → USES→Software.
- L361 `def generate_group_techniques(self, group: dict) -> GeneratedSample | None` — 'What techniques does [group] use?' → USES→Technique.
- L397 `def generate_tactic_techniques(self, tactic: dict) -> GeneratedSample | None` — 'What are all [tactic] techniques?' → IN_TACTIC relationship.
- L431 `def generate_software_techniques(self, software: dict) -> GeneratedSample | None` — 'What techniques does [software] use?' → USES→Technique.
- L466 `def generate_technique_detection(self, technique: dict) -> GeneratedSample | None` — 'How can I detect [technique]?' → DETECTS relationship.
- L509 `def generate_technique_groups(self, technique: dict) -> GeneratedSample | None` — 'What groups use [technique]?' → Group-USES→Technique.
- L543 `def generate_campaign_attribution(self, group: dict) -> GeneratedSample | None` — 'What campaigns are attributed to [group]?' → ATTRIBUTED_TO relationship.
- L606 `def _make_thai_variant(sample: GeneratedSample, seed_node: dict) -> GeneratedSample | None` — Create a Thai-language variant of an English sample.
- L1185 `class IncidentScenarioGenerator` — Generates incident-style evaluation samples grounded in Neo4j STIX IDs.
- L1188 `def __init__(self, neo4j: Neo4jGroundTruthBuilder)` — Implements init.
- L1191 `def generate(self) -> list[GeneratedSample]` — Build all incident samples, looking up STIX IDs from Neo4j.
- L1257 `class DatasetGenerator` — Iterates query templates × seed nodes to generate evaluation samples.
- L1260 `def __init__(self, neo4j: Neo4jGroundTruthBuilder, thai_ratio: float=0.2)` — Implements init.
- L1265 `def generate(self) -> list[GeneratedSample]` — Generate the full evaluation dataset.
- L1270 `def _add(sample: GeneratedSample | None, seed: dict | None=None) -> None` — Add sample if valid and not duplicate.
- L1439 `class ValidationResult` — Result of dataset validation.
- L1446 `def summary(self) -> str` — Implements summary.
- L1483 `class DatasetValidator` — Validates the generated dataset for consistency and completeness.
- L1486 `def __init__(self, min_samples: int=50, min_categories: int=8)` — Implements init.
- L1490 `def validate(self, samples: list[GeneratedSample]) -> ValidationResult` — Run all validation checks.
- L1604 `def save_dataset(samples: list[GeneratedSample], output_path: Path) -> None` — Save the generated dataset as JSON.
- L1616 `def load_dataset_for_validation(path: Path) -> list[GeneratedSample]` — Load an existing dataset JSON for validation.
- L1641 `def main()` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/generation_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/generation_metrics.py)

Purpose: Generation (Answer) Evaluation Metrics ======================================== Evaluates the quality of LLM-generated answers using: 1.

- L31 `def _tokenize(text: str) -> list[str]` — Simple whitespace + lowercase tokenizer.
- L36 `def token_f1(prediction: str, reference: str) -> dict[str, float]` — Token-level Precision, Recall, F1 between prediction and reference.
- L55 `def rouge_l(prediction: str, reference: str) -> float` — ROUGE-L score (longest common subsequence).
- L87 `def _try_ragas_evaluate(questions: list[str], answers: list[str], contexts: list[list[str]], reference_answers: list[str] | None=None, use_local: bool=False) -> dict[str, list[float]] | None` — Attempt RAGAS evaluation.
- L206 `def _try_bertscore(predictions: list[str], references: list[str]) -> list[float] | None` — Attempt BERTScore.
- L234 `class GenerationEvalResult` — Aggregated generation evaluation results.
- L256 `def to_table(self) -> str` — Format results as a printable table.
- L294 `def evaluate_generation(query_fn: Callable[[str], tuple[str, list[str]]], samples: list[EvalSample], use_local: bool=False) -> GenerationEvalResult` — Run generation evaluation across all samples.
- L382 `def _safe_mean(key)` — Implements safe mean.

### [`rag_service/app/RAG/GraphRAG/evaluation/ground_truth.py`](../../rag_service/app/RAG/GraphRAG/evaluation/ground_truth.py)

Purpose: Ground Truth Dataset ===================== Data model and I/O for evaluation datasets.

- L21 `class EvalSample` — A single evaluation sample.
- L42 `def has_reference_answer(self) -> bool` — Determines reference answer.
- L45 `def has_attack_steps(self) -> bool` — Determines attack steps.
- L49 `def load_ground_truth(path: str | Path) -> list[EvalSample]` — Load evaluation samples from a JSON file.
- L96 `def save_ground_truth(samples: list[EvalSample], path: str | Path) -> None` — Save evaluation samples to a JSON file.

### [`rag_service/app/RAG/GraphRAG/evaluation/make_incident_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/make_incident_dataset.py)

Purpose: Incident Dataset Builder (semi-automated) ========================================== Builds chronological Thai case-file incident samples for the eval dataset: 1.

- L52 `def load_deprecated_blocklist() -> set[str]` — Deprecated/revoked ATT&CK IDs to exclude from chains.
- L120 `def _tactic_order(tactic: str) -> int` — Implements tactic order.
- L127 `def sample_kill_chains(neo4j: Neo4jGroundTruthBuilder, num_chains: int, rng: random.Random, min_steps: int=3, max_steps: int=6, blocked_ids: set[str] | None=None, source: str='group') -> list[dict]` — Sample up to num_chains kill-chains from a Group or a real Campaign.
- L281 `def _parse_json_reply(text: str) -> dict` — Parses json reply.
- L287 `def draft_narrative(llm, chain: dict) -> dict | None` — One LLM call -> {narrative_th, narrative_en, cues}.
- L333 `def _entry_from_stored(sid: str, stored: dict, id_to_name: dict[str, str]) -> dict` — Rebuild a review entry from a previously drafted sample (--resume).
- L362 `def build_sample(idx: int, chain: dict, draft: dict) -> tuple[GeneratedSample, list[str]]` — Assemble a GeneratedSample; returns (sample, review_flags).
- L405 `def write_review_md(path: Path, entries: list[dict]) -> None` — Implements write review md.
- L439 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/__init__.py)

Purpose: Real-CTI evaluation tier.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/build_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/build_dataset.py)

Purpose: Select the real-CTI chain set ============================== Merges the CTID and CISA chain pools into one balanced selection of N chains — the input to Thai case-file drafting, not yet an eval dataset.

- L49 `def _load(path: Path) -> list[dict]` — Retrieves load.
- L55 `def _bucket_key(chain: dict) -> str` — The document a chain came from — the unit diversity is spread over.
- L60 `def round_robin(chains: list[dict], want: int, rng: random.Random) -> list[dict]` — Take up to `want` chains, cycling over source documents.
- L85 `def select(num: int, seed: int, ctid_share: float) -> tuple[list[dict], dict]` — Extracts select.
- L111 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/cisa_loader.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/cisa_loader.py)

Purpose: CISA advisories -> attack chains ================================= Turns the CISA TTP Articles Data Set (see fetch_cisa.py) into chains with the same shape ctid_loader.py produces.

- L91 `def load_lookups() -> tuple[dict[str, list[str]], dict[str, list[str]]]` — Return (attack_id -> tactics, attack_id -> known names/aliases).
- L100 `def is_observable(attack_id: str, raw_id: str, tactics: dict[str, list[str]]) -> bool` — False when every tactic the technique belongs to is unobservable.
- L113 `def extract_technical_details(raw_text: str) -> str` — Extracts technical details.
- L122 `def clean_cue(sentence: str) -> str` — Strip ATT&CK tags and CISA's numeric citations from a cue.
- L133 `def parse_advisory(record: dict, tactics: dict[str, list[str]]) -> tuple[str, list[dict]]` — Return (advisory_id, ordered steps) for one advisory record.
- L176 `def order_by_kill_chain(steps: list[dict]) -> list[dict]` — Reorder an advisory's steps into kill-chain phase order.
- L187 `def key(item: tuple[int, dict]) -> tuple[int, int]` — Implements key.
- L197 `def merge_repeat_steps(steps: list[dict]) -> list[dict]` — Drop a step whose technique set repeats the step just before it.
- L219 `def chunk_narrative(steps: list[dict]) -> list[list[dict]]` — Cut an advisory's ordered steps into MIN..MAX-technique chains.
- L227 `def uniq(ss: list[dict]) -> set[str]` — Implements uniq.
- L247 `def _tokens(text: str) -> set[str]` — Implements tokens.
- L251 `def classify_cue_type(step: dict, names: dict[str, list[str]]) -> str` — named when the cue spells the technique out, described otherwise.
- L286 `def dedupe_revisions(records: list[dict]) -> tuple[list[dict], list[str]]` — Keep one record per advisory, dropping CISA's revision duplicates.
- L312 `def build_chains(use_neo4j: bool=True) -> tuple[list[dict], dict]` — Builds chains.
- L380 `def print_stats(chains: list[dict], report: dict) -> None` — Implements print stats.
- L401 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/ctid_loader.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/ctid_loader.py)

Purpose: CTID Adversary Emulation Library -> attack chains ================================================== Reads the vendored emulation-plan YAMLs (see NOTICE.md) and cuts each plan into chains of consecutive steps suitable for one case-file sample.

- L87 `def _as_list(value) -> list[str]` — Implements as list.
- L95 `def parse_plan(path: Path) -> tuple[dict, list[dict], list[str], list[str]]` — Return (details, ordered steps, dropped raw ids, applied corrections).
- L145 `def _uniq_ids(steps: list[dict]) -> list[str]` — Implements uniq ids.
- L149 `def _split_oversized(group: list[dict]) -> list[list[dict]]` — Cut a single procedure_group that alone exceeds MAX_TECHNIQUES.
- L166 `def chunk_steps(steps: list[dict]) -> list[list[dict]]` — Group consecutive steps into chains of MIN..MAX distinct techniques.
- L200 `def collapse_repeats(steps: list[dict]) -> list[dict]` — Merge consecutive steps sharing one technique into a single step.
- L244 `def resolve_stix_ids(attack_ids: set[str]) -> dict[str, str]` — attack_id -> stix_id from Neo4j.
- L269 `def build_chains(use_neo4j: bool=True) -> tuple[list[dict], dict]` — Builds chains.
- L316 `def print_stats(chains: list[dict], report: dict) -> None` — Implements print stats.
- L347 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/fetch_cisa.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/fetch_cisa.py)

Purpose: Fetch the CISA TTP Articles Data Set (Zenodo, DOI 10.5281/zenodo.14659512) ========================================================================== 77 CISA cybersecurity advisories (Jul 2020 - Feb 2024) crawled from cisa.gov, kept because they carry an explicit MITRE ATT&CK section.

- L36 `def fetch(force: bool=False) -> Path` — Retrieves fetch.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/thai_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/thai_dataset.py)

Purpose: Thai case-file dataset builder for the real-CTI tier ===================================================== The narratives in CTI_dataset.json are written by hand, chain by chain, not generated by an API call — that is the whole point of this tier.

- L70 `def load_selection() -> dict[str, dict]` — Retrieves selection.
- L75 `def step_gold(step: dict) -> list[str]` — Gold ATT&CK IDs of a step, whichever loader produced it.
- L80 `def step_stix(step: dict) -> list[str]` — Implements step stix.
- L87 `def step_source_text(step: dict) -> str` — The English text the Thai narrative is rewritten from.
- L92 `def chain_gold(chain: dict) -> list[str]` — Implements chain gold.
- L99 `def chain_stix(chain: dict) -> list[str]` — Implements chain stix.
- L111 `def load_dataset() -> dict` — Retrieves dataset.
- L127 `def save_dataset(data: dict) -> None` — Persists dataset.
- L133 `def done_chain_ids(data: dict) -> set[str]` — Implements done chain ids.
- L142 `def validate(sample: dict, chain: dict, names: dict[str, list[str]]) -> list[str]` — Validates validate.
- L199 `def cmd_status(_args) -> None` — Implements cmd status.
- L230 `def cmd_brief(args) -> None` — Implements cmd brief.
- L246 `def _technique_names(attack_ids: set[str], use_neo4j: bool) -> dict[str, str]` — attack_id -> official name, for the reviewer to check cues against.
- L273 `def cmd_review(args) -> None` — Implements cmd review.
- L345 `def cmd_add(args) -> None` — Implements cmd add.
- L407 `def main() -> None` — Implements main.

### [`rag_service/app/RAG/GraphRAG/evaluation/retriever_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/retriever_metrics.py)

Purpose: Retriever Evaluation Metrics ============================== Pure functions for evaluating retrieval quality.

- L45 `def hit_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — 1.0 if any relevant doc appears in top-K, else 0.0.
- L51 `def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Capped recall: hits / min(|relevant|, K).
- L67 `def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Fraction of top-K results that are relevant.
- L75 `def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float` — Reciprocal rank of the first relevant result (1/rank).
- L83 `def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Normalized Discounted Cumulative Gain at K (binary relevance).
- L102 `def average_precision(retrieved_ids: list[str], relevant_ids: set[str]) -> float` — Average Precision — average of Precision@k at each relevant position.
- L131 `def _step_gold_ids(step: dict) -> set[str]` — Implements step gold ids.
- L138 `def scoreable_steps(steps: list[dict]) -> list[dict]` — Steps whose gold has at least one STIX ID the retriever could return.
- L149 `def step_coverage_at_k(retrieved_ids: list[str], steps: list[dict], k: int) -> float` — Fraction of steps with at least one gold ID in top-K (S-recall@K).
- L158 `def strict_step_coverage_at_k(retrieved_ids: list[str], steps: list[dict], k: int) -> float` — Fraction of steps whose gold IDs ALL appear in top-K.
- L170 `def step_best_rank(retrieved_ids: list[str], step: dict) -> Optional[int]` — 1-based rank of the first retrieved ID evidencing the step, else None.
- L183 `def step_coverage_by_cue_type(retrieved_ids: list[str], steps: list[dict], k: int) -> dict[str, float]` — StepCoverage@K broken down by cue_type ("named" vs "described").
- L208 `class RetrieverEvalResult` — Aggregated retriever evaluation results.
- L237 `def to_table(self) -> str` — Format results as a printable table.
- L302 `def evaluate_retriever(retriever_fn, samples: list[EvalSample], k_values: list[int] | None=None, retriever_name: str='Retriever') -> RetrieverEvalResult` — Run retriever evaluation across all samples.
- L389 `def mean(lst)` — Implements mean.

### [`rag_service/app/RAG/GraphRAG/evaluation/test_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/test_metrics.py)

Purpose: Unit Tests for Evaluation Metrics ==================================== Tests metric functions with known inputs/outputs.

- L49 `def test_hit_at_k()` — Implements test hit at k.
- L61 `def test_recall_at_k()` — Implements test recall at k.
- L80 `def test_step_coverage_at_k()` — Implements test step coverage at k.
- L111 `def test_precision_at_k()` — Implements test precision at k.
- L121 `def test_reciprocal_rank()` — Implements test reciprocal rank.
- L131 `def test_ndcg_at_k()` — Implements test ndcg at k.
- L144 `def test_average_precision()` — Implements test average precision.
- L159 `def test_token_f1()` — Implements test token f1.
- L167 `def test_rouge_l()` — Implements test rouge l.
- L175 `def test_extract_attack_ids()` — Implements test extract attack ids.
- L187 `def test_extract_technique_names()` — Implements test extract technique names.
- L201 `def test_technique_set_score()` — Implements test technique set score.
- L226 `def test_tactic_level_score()` — Implements test tactic level score.
- L239 `def test_guard_metrics()` — Implements test guard metrics.
- L268 `def test_ground_truth_io()` — Implements test ground truth io.
- L302 `def run_all_tests()` — Executes all tests.

### [`rag_service/app/RAG/GraphRAG/ingestion/__init__.py`](../../rag_service/app/RAG/GraphRAG/ingestion/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/ingestion/graph_loader.py`](../../rag_service/app/RAG/GraphRAG/ingestion/graph_loader.py)

Purpose: Neo4j Graph Database Loader ============================ Loads parsed ATT&CK entities and relationships into Neo4j.

- L18 `class GraphLoader` — Loads ATT&CK data into Neo4j.
- L21 `def __init__(self)` — Implements init.
- L25 `def close(self)` — Implements close.
- L28 `def clear_database(self)` — Remove all existing nodes and relationships.
- L34 `def create_constraints(self)` — Create uniqueness constraints for fast lookups.
- L53 `def create_indexes(self)` — Create indexes for common query patterns.
- L70 `def load_entities(self, entities: list[AttackEntity]) -> int` — Load all entities as nodes into Neo4j in bulk batches.
- L104 `def _entity_to_props(self, entity: AttackEntity) -> dict` — Convert entity to Neo4j property dict.
- L137 `def load_relationships(self, relationships)` — Retrieves relationships.
- L194 `def load_all(self, parser: StixParser) -> None` — Full ingestion: clear → constraints → nodes → edges.

### [`rag_service/app/RAG/GraphRAG/ingestion/stix_parser.py`](../../rag_service/app/RAG/GraphRAG/ingestion/stix_parser.py)

Purpose: STIX 2.1 Parser for MITRE ATT&CK Data ====================================== Parses enterprise-attack.json and mobile-attack.json into typed entities and relationships matching the schema_design.md specification.

- L32 `def _get_attack_id(obj: dict) -> str` — Extract ATT&CK ID (e.g., T1566) from external_references.
- L40 `def _get_url(obj: dict) -> str` — Extract ATT&CK URL from external_references.
- L48 `def _is_revoked_or_deprecated(obj: dict) -> bool` — Check if object is revoked or deprecated.
- L53 `def _get_tactics_from_kill_chain(obj: dict) -> list[str]` — Extract tactic shortnames from kill_chain_phases.
- L89 `class StixParser` — Parses MITRE ATT&CK STIX 2.1 JSON bundles into entities and relationships.
- L92 `def __init__(self)` — Implements init.
- L103 `def parse_folder(self, folder: Path, domain: str='enterprise') -> None` — Parse STIX bundle JSON files in a folder.
- L124 `def parse_file(self, filepath: Path, domain: str='enterprise', finalize: bool=True) -> None` — Parse a single STIX bundle JSON file.
- L239 `def _parse_technique(self, obj: dict, domain: str) -> Technique` — Parses technique.
- L254 `def _parse_group(self, obj: dict, domain: str) -> Group` — Parses group.
- L265 `def _parse_software(self, obj: dict, stix_type: str, domain: str) -> Software` — Parses software.
- L277 `def _parse_campaign(self, obj: dict, domain: str) -> Campaign` — Parses campaign.
- L288 `def _parse_mitigation(self, obj: dict, domain: str) -> Mitigation` — Parses mitigation.
- L298 `def _parse_tactic(self, obj: dict, domain: str) -> Tactic` — Parses tactic.
- L309 `def _parse_data_source(self, obj: dict, domain: str) -> DataSource` — Parses data source.
- L320 `def _parse_data_component(self, obj: dict, domain: str) -> DataComponent` — Parses data component.
- L331 `def _build_relationships(self, raw_rels: list[dict]) -> None` — Build typed relationships from raw STIX relationship objects.
- L363 `def _build_tactic_edges(self) -> None` — Derive IN_TACTIC edges from technique kill_chain_phases.
- L387 `def _build_data_source_edges(self) -> None` — Derive HAS_COMPONENT edges from x_mitre_data_source_ref.
- L409 `def get_entities_by_label(self, label: str) -> list[AttackEntity]` — Get all entities of a specific node label.
- L413 `def get_relationships_by_label(self, label: str) -> list[AttackRelationship]` — Get all relationships of a specific edge label.
- L417 `def finalize_parsing(self) -> None` — Apply tombstones and deduplicate entities and relationships.
- L447 `def parse_all_domains() -> StixParser` — Parse all configured ATT&CK domain folders and return a unified parser.

### [`rag_service/app/RAG/GraphRAG/ingestion/vector_loader.py`](../../rag_service/app/RAG/GraphRAG/ingestion/vector_loader.py)

Purpose: Qdrant Vector Loader ======================= Embeds ATT&CK entity descriptions and relationship descriptions into Qdrant.

- L33 `def uuid_from_stix_id(stix_id: str) -> str` — Generate a valid UUID from a STIX ID.
- L52 `class VectorLoader` — Embeds and stores ATT&CK data in Qdrant (Hybrid).
- L55 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None)` — Implements init.
- L72 `def _embed_texts(self, texts: list[str]) -> dict` — Embed a batch of texts returning dense and sparse vectors.
- L82 `def _init_collection(self, collection_name: str)` — Create Qdrant collection with both dense and sparse configurations.
- L100 `def load_entities(self, entities: list[AttackEntity]) -> int` — Embed and store entity descriptions.
- L184 `def load_relationships(self, relationships: list[AttackRelationship]) -> int` — Embed and store relationship descriptions.
- L267 `def load_all(self, parser: StixParser) -> None` — Full vector ingestion: embed entities + relationships.

### [`rag_service/app/RAG/GraphRAG/llm_content.py`](../../rag_service/app/RAG/GraphRAG/llm_content.py)

Purpose: Safe extraction of visible text from LangChain message responses.

- L6 `class LlmContentError(ValueError)` — Raised when an LLM response has no usable visible text.
- L10 `def require_message_text(message: BaseMessage, *, operation: str) -> str` — Return canonical visible message text or fail without exposing content.

### [`rag_service/app/RAG/GraphRAG/llm_provider.py`](../../rag_service/app/RAG/GraphRAG/llm_provider.py)

Purpose: Production cloud LLM factory for Anthropic-compatible chat clients.

- L16 `class CoreLlmConfigurationError(RuntimeError)` — The selected cloud provider cannot be constructed safely.
- L19 `def __init__(self, provider: CoreLlmProvider, key_env_name: str) -> None` — Implements init.
- L29 `class CoreLlmTarget` — Encapsulates corellmtarget.
- L38 `def resolve_core_llm_target(anthropic_model: str | None=None, *, require_key: bool=True) -> CoreLlmTarget` — Resolve the selected production provider without consulting eval keys.
- L86 `def create_core_chat_model(*, anthropic_model: str | None=None, temperature: float | int, max_tokens: int) -> ChatAnthropic` — Create one cloud ChatAnthropic client for the selected provider.

### [`rag_service/app/RAG/GraphRAG/main.py`](../../rag_service/app/RAG/GraphRAG/main.py)

Purpose: MITRE ATT&CK GraphRAG — CLI Entrypoint ======================================== Run as a module from rag_service/app — the package uses relative imports, so `python main.py` fails with ImportError: python -m RAG.GraphRAG.main --ingest # Parse STIX → Neo4j + Qdrant python -m RAG.GraphRAG.main --test # Run test queries python -m RAG.GraphRAG.main # Interactive mode python -m RAG.GraphRAG.main --retrieve-only # Retrieval without LLM.

- L41 `def run_ingest()` — Parse STIX data and load into Neo4j + Qdrant.
- L111 `def run_tests(retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False)` — Run test queries.
- L153 `def run_interactive(retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False)` — Interactive query mode.
- L219 `def main()` — Implements main.

### [`rag_service/app/RAG/GraphRAG/model_registry.py`](../../rag_service/app/RAG/GraphRAG/model_registry.py)

Purpose: Central OpenRouter model registry, curated presets, and alias resolver for GraphRAG.

- L12 `class ModelPreset` — Encapsulates modelpreset.
- L75 `def resolve_openrouter_model(name_or_alias: str | None) -> str` — Resolve a friendly model nickname, alias, or full ID to the canonical OpenRouter ID.
- L100 `def list_available_models() -> list[dict[str, object]]` — Return structured catalog of ready-selection models.
- L115 `def format_model_table() -> str` — Render formatted ASCII comparison table of curated ready-selection models.

### [`rag_service/app/RAG/GraphRAG/models.py`](../../rag_service/app/RAG/GraphRAG/models.py)

Purpose: Pydantic Models for MITRE ATT&CK Entities ========================================== Typed representations of STIX 2.1 objects parsed from ATT&CK data.

- L10 `class AttackEntity(BaseModel)` — Base model for all ATT&CK entities (graph nodes).
- L21 `class Technique(AttackEntity)` — Encapsulates technique.
- L28 `class Group(AttackEntity)` — Encapsulates group.
- L33 `class Software(AttackEntity)` — Encapsulates software.
- L39 `class Campaign(AttackEntity)` — Encapsulates campaign.
- L44 `class Mitigation(AttackEntity)` — Encapsulates mitigation.
- L48 `class Tactic(AttackEntity)` — Encapsulates tactic.
- L53 `class DataSource(AttackEntity)` — Encapsulates datasource.
- L58 `class DataComponent(AttackEntity)` — Encapsulates datacomponent.
- L62 `class AttackRelationship(BaseModel)` — Represents a STIX relationship between two ATT&CK entities.

### [`rag_service/app/RAG/GraphRAG/pipeline/__init__.py`](../../rag_service/app/RAG/GraphRAG/pipeline/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py`](../../rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py)

Purpose: LangGraph Agentic RAG Pipeline ================================ The only pipeline serving ``POST /query``.

- L75 `class AgentState(TypedDict)` — Shared state flowing through every node in the graph.
- L115 `class AgentResponse` — Structured response returned by ``GraphRAGAgent.query()``.
- L127 `def to_dict(self) -> dict` — Serialize for JSON API responses.
- L141 `class GraphRAGAgent` — Agentic RAG pipeline built on LangGraph.
- L148 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Any]=None) -> None` — Implements init.
- L213 `def close(self) -> None` — Clean up resources.
- L217 `def retrieve_only(self, user_query: str) -> str` — Execute only the retrieval portion of the pipeline.
- L230 `def query_fast(self, user_query: str, verbose: bool=True) -> AgentResponse` — Minimal-latency path — single retrieve → one combined reason+answer call.
- L293 `def _get_ultrafast_llm(self)` — Lazily build (and cache) a low-output-token LLM for ultrafast mode.
- L308 `def query_ultrafast(self, user_query: str, verbose: bool=True) -> AgentResponse` — Absolute-minimum-latency path.
- L360 `def query(self, user_query: str, verbose: bool=True) -> AgentResponse` — Execute the agentic RAG pipeline.
- L398 `def _build_graph(self) -> Any` — Construct and compile the LangGraph state machine.
- L461 `def _node_route_query(self, state: AgentState) -> dict` — Classify the query as GENERAL_EXPLANATION or INCIDENT_ANALYSIS.
- L477 `def _node_general_explanation(self, state: AgentState) -> dict` — Handle general knowledge questions without retrieval.
- L511 `def _node_prepare(self, state: AgentState) -> dict` — Detect the response language.
- L536 `def _node_retrieve(self, state: AgentState) -> dict` — Execute decomposed multi-query hybrid retrieval (Vector + Graph).
- L579 `def _node_evaluate_context(self, state: AgentState) -> dict` — Evaluate whether the retrieved context is sufficient.
- L600 `def _node_broaden_search(self, state: AgentState) -> dict` — Execute the BROADEN_SEARCH strategy by rewriting the query and looping.
- L623 `def _node_reasoning(self, state: AgentState) -> dict` — Reasoning LLM — synthesize the retrieved context into the answer.
- L694 `def _node_translate_output(self, state: AgentState) -> dict` — Stage 3: Translation LLM — render English answer into Thai.
- L726 `def _edge_after_route(state: AgentState) -> str` — Route based on query classification.
- L734 `def _edge_after_evaluation(state: AgentState) -> str` — Decide next step based on context evaluation.
- L771 `def _edge_after_reasoning(state: AgentState) -> str` — Decide whether to translate the answer to Thai.

### [`rag_service/app/RAG/GraphRAG/pipeline/chain.py`](../../rag_service/app/RAG/GraphRAG/pipeline/chain.py)

Purpose: LangChain LCEL Chain for MITRE ATT&CK GraphRAG — EVALUATION ONLY ================================================================== NOT a production path.

- L62 `def _print_sources(graphrag_result: GraphRAGResult, top_n: int=5) -> None` — Print the top retrieval sources for verbose/debug output.
- L75 `class ChainResponse` — Answer plus the retrieval artifacts behind it (for the MITRE table).
- L83 `class GraphRAGChain` — Full GraphRAG pipeline with cross-lingual support.
- L86 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, use_local: bool=False)` — Implements init.
- L153 `def close(self)` — Clean up resources.
- L157 `def query(self, user_query: str, verbose: bool=True) -> str` — Execute the full GraphRAG pipeline and return the answer text.
- L165 `def query_with_details(self, user_query: str, verbose: bool=True) -> ChainResponse` — Execute the full GraphRAG pipeline.
- L324 `def retrieve_only(self, user_query: str) -> str` — Run retrieval without LLM generation (for testing/debugging).

### [`rag_service/app/RAG/GraphRAG/pipeline/context_builder.py`](../../rag_service/app/RAG/GraphRAG/pipeline/context_builder.py)

Purpose: Context Builder ================ Assembles the final context from Vector + Graph retrieval results into a structured prompt for the LLM.

- L12 `def build_context(result: GraphRAGResult, max_context_length: int=10000, max_vector: int | None=None, max_graph: int=3) -> str` — Build a structured context string from GraphRAG results.
- L84 `def build_generation_prompt(context: str, original_query: str, english_query: str, respond_in_thai: bool=True) -> str` — Build the final prompt for LLM generation.

### [`rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py`](../../rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py)

Purpose: Cross-Lingual Translation Layer ================================= Language routing for the RAG pipeline.

- L138 `def _is_thai(text: str) -> bool` — Check if text contains Thai characters.
- L144 `def build_retrieval_queries(original_query: str, english_query: str, extra_queries: list[str] | None=None) -> list[str]` — Build the query list for cross-lingual retrieval.
- L175 `def _is_mostly_english(text: str) -> bool` — Check if text is predominantly English.
- L184 `class CrossLingualLayer` — Manages Thai ↔ English translation for cross-lingual RAG.
- L187 `def __init__(self, use_local: bool=False)` — Implements init.
- L208 `def translate_query(self, query: str) -> str` — Translate a Thai query to English for retrieval.
- L242 `def get_reasoning_system_prompt() -> str` — Return the system prompt for the Reasoning LLM (Stage 2).
- L251 `def get_translation_system_prompt() -> str` — Return the system prompt for the Translation LLM (Stage 3).
- L260 `def get_fast_system_prompt(respond_in_thai: bool) -> str` — The DEFAULT production prompt for Thai answers, despite the name.
- L283 `def get_ultrafast_system_prompt(respond_in_thai: bool) -> str` — Terse single-pass prompt for --ultrafast mode.
- L306 `def should_respond_in_thai(query: str) -> bool` — Determine if the final output should be in Thai based on the query language.

### [`rag_service/app/RAG/GraphRAG/pipeline/evaluator.py`](../../rag_service/app/RAG/GraphRAG/pipeline/evaluator.py)

Purpose: Context Sufficiency Evaluator ============================== Uses the LLM to judge whether retrieved context can adequately answer the user's query.

- L47 `class EvaluationResult` — Structured result from the context evaluator.
- L59 `def __post_init__(self)` — Implements post init.
- L162 `class ContextEvaluator` — Evaluates whether retrieved context is sufficient to answer a query.
- L165 `def __init__(self) -> None` — Implements init.
- L177 `def evaluate(self, original_query: str, english_query: str, context: str, retry_count: int=0, verbose: bool=True) -> EvaluationResult` — Judge context sufficiency.
- L267 `def _build_prompt(original_query: str, english_query: str, context: str, retry_count: int=0) -> str` — Build the evaluation prompt.
- L304 `def _parse_response(raw: str) -> EvaluationResult` — Parse the LLM's JSON response into an EvaluationResult.

### [`rag_service/app/RAG/GraphRAG/pipeline/mitre_table.py`](../../rag_service/app/RAG/GraphRAG/pipeline/mitre_table.py)

Purpose: MITRE Mapping Table Builder ============================ Converts a raw ``GraphRAGResult`` into a structured MITRE ATT&CK mapping table for the backend/frontend, filtering out retrieval noise.

- L52 `class MitreTableRow(BaseModel)` — One entry of the MITRE mapping table exposed to the backend.
- L66 `def build_mitre_table(rag_result, answer: str, score_threshold: Optional[float]=None) -> list[MitreTableRow]` — Build the filtered MITRE mapping table from raw retrieval results.
- L125 `def _collect_candidates(rag_result) -> dict[str, dict]` — Gather unique entities from vector hits, graph seeds, and neighbors.
- L166 `def _tactic_map(rag_result) -> dict[str, str]` — Map technique name → tactic name from IN_TACTIC graph edges.
- L176 `def _is_cited(attack_id: str, name: str, cited_ids: set[str], answer_lower: str) -> bool` — Determines cited.
- L197 `def _mitre_url(attack_id: str) -> Optional[str]` — Implements mitre url.

### [`rag_service/app/RAG/GraphRAG/pipeline/query_decomposer.py`](../../rag_service/app/RAG/GraphRAG/pipeline/query_decomposer.py)

Purpose: Query Decomposer ================ Breaks a compound security-incident query into multiple ATOMIC MITRE search queries — one per distinct attacker action — so each technique is retrieved on its own channel (parallel multi-query retrieval, fed into ``retrieve_multi_quota``).

- L105 `def _is_conversational(line: str) -> bool` — True when a line addresses the user rather than the retrieval engine.
- L114 `def _parse(text: str, cap: int) -> list[str]` — Turn the LLM's line-per-query output into a clean, deduped query list.
- L148 `class QueryDecomposer` — LLM step: incident → list of atomic, native-language sub-queries.
- L151 `def __init__(self, use_local: bool=False)` — Implements init.
- L175 `def decompose(self, incident: str, max_subqueries: int=_MAX_SUBQUERIES, verbose: bool=True) -> list[str]` — Return atomic native-language sub-queries, or a single-element fallback.

### [`rag_service/app/RAG/GraphRAG/pipeline/query_sanitizer.py`](../../rag_service/app/RAG/GraphRAG/pipeline/query_sanitizer.py)

Purpose: Retrieval Query Sanitizer ========================= Cleans LLM-written retrieval queries before they are embedded.

- L20 `def sanitize_retrieval_query(text: str) -> str` — Strip markdown and bare ATT&CK ID tokens from a rewritten query.

### [`rag_service/app/RAG/GraphRAG/pipeline/router.py`](../../rag_service/app/RAG/GraphRAG/pipeline/router.py)

Purpose: Query Router ================================= Classifies user queries to determine the appropriate processing pipeline.

- L71 `class QueryRouter` — Encapsulates queryrouter.
- L72 `def __init__(self, use_local: bool=False)` — Implements init.
- L93 `def route_query(self, query: str) -> str` — Classify the user query as GENERAL_EXPLANATION or INCIDENT_ANALYSIS.

### [`rag_service/app/RAG/GraphRAG/retrieval/__init__.py`](../../rag_service/app/RAG/GraphRAG/retrieval/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/retrieval/graph_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/graph_retriever.py)

Purpose: Neo4j Graph Retriever ====================== Expands subgraphs from Neo4j given STIX IDs retrieved from vector search.

- L26 `class GraphNode` — A node from the graph expansion.
- L37 `class GraphEdge` — An edge from the graph expansion.
- L47 `class SubgraphResult` — Result of a graph expansion query.
- L54 `def to_text(self) -> str` — Format the subgraph as readable text for LLM context.
- L100 `class GraphRetriever` — Expands subgraphs from Neo4j for GraphRAG context enrichment.
- L103 `def __init__(self)` — Implements init.
- L107 `def close(self)` — Implements close.
- L110 `def expand(self, stix_ids: list[str]) -> list[SubgraphResult]` — Expand subgraphs for a list of STIX IDs.
- L120 `def expand_batch(self, stix_ids: list[str]) -> list[SubgraphResult]` — Batched graph expansion — 3 Cypher queries for the whole seed list.
- L225 `def _expand_single(self, stix_id: str) -> SubgraphResult` — Expand a single node's subgraph.
- L323 `def query_cypher(self, cypher: str, params: Optional[dict]=None) -> list[dict]` — Execute an arbitrary Cypher query and return results as dicts.
- L329 `def get_multi_hop_path(self, start_name: str, end_name: str, max_hops: int=4) -> str` — Find paths between two named entities.

### [`rag_service/app/RAG/GraphRAG/retrieval/hybrid_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/hybrid_retriever.py)

Purpose: Hybrid GraphRAG Retriever ========================== Combines Vector Search + Graph Expansion into a single retrieval step.

- L24 `class GraphRAGResult` — Combined result from vector search + graph expansion.
- L32 `def get_context_text(self, max_length: int=8000) -> str` — Format combined results as text for LLM context.
- L77 `class HybridRetriever` — Orchestrates Vector + Graph retrieval for GraphRAG.
- L80 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Reranker]=None)` — Implements init.
- L90 `def close(self)` — Implements close.
- L100 `def _reweight_by_type(vector_results: list) -> list` — Down/up-weight reranked vector hits by node type, then re-sort so the graph-seed order (taken from this list) is technique-first.
- L111 `def retrieve(self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None, expand_graph: bool=True) -> GraphRAGResult` — Execute the full GraphRAG retrieval pipeline.
- L189 `def retrieve_multi(self, queries: list[str], top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None) -> GraphRAGResult` — Execute hybrid retrieval for multiple queries and merge results.
- L260 `def retrieve_multi_quota(self, queries: list[str], per_query_k: int=3, top_k: int=VECTOR_TOP_K, max_vector: int=15, max_graph: int=8, node_label_filter: Optional[str]=None) -> 'GraphRAGResult'` — Multi-query retrieval with a PER-QUERY QUOTA.

### [`rag_service/app/RAG/GraphRAG/retrieval/reranker.py`](../../rag_service/app/RAG/GraphRAG/retrieval/reranker.py)

Purpose: Cross-Encoder Reranker ======================= Post-retrieval reranker that rescores vector search results using a cross-encoder model for joint query-document relevance.

- L15 `class Reranker` — Reranks a list of VectorResults using a cross-encoder model.
- L18 `def __init__(self, model_name: str=RERANKER_MODEL) -> None` — Implements init.
- L24 `def rerank(self, query: str, results: list[VectorResult], top_k: int=FINAL_TOP_K) -> list[VectorResult]` — Score each (query, document) pair and return top_k results sorted by cross-encoder score, in [0, 1].

### [`rag_service/app/RAG/GraphRAG/retrieval/vector_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/vector_retriever.py)

Purpose: Qdrant Vector Retriever ========================== Performs hybrid search (Dense + Sparse) over entity and relationship embeddings using BGE-M3 and Qdrant's native RRF fusion.

- L38 `class VectorResult` — A single result from vector search.
- L47 `class VectorRetriever` — Retrieves semantically similar ATT&CK documents from Qdrant using Hybrid Search.
- L50 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None)` — Implements init.
- L75 `def _search_hybrid(self, collection_name: str, query: str, top_k: int, qdrant_filter: Optional[Filter]=None) -> list[VectorResult]` — Hybrid search: dense + sparse with RRF fusion natively in Qdrant.
- L140 `def search_entities(self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None) -> list[VectorResult]` — Search entity descriptions semantically.
- L181 `def search_relationships(self, query: str, top_k: int=VECTOR_TOP_K, edge_label_filter: Optional[str]=None) -> list[VectorResult]` — Search relationship descriptions semantically.
- L208 `def _normalize_scores(results: list['VectorResult']) -> None` — Min-max normalize scores in-place so results from different collections are comparable on the same [0, 1] scale.
- L221 `def search_all(self, query: str, top_k: int=VECTOR_TOP_K) -> list[VectorResult]` — Search both entity and relationship collections.

### [`rag_service/app/routers/__init__.py`](../../rag_service/app/routers/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/routers/context_store.py`](../../rag_service/app/routers/context_store.py)

Purpose: Owns context store behavior for the GraphRAG runtime and evaluation package.

- L13 `def get_retrieval_contexts(req: Request) -> dict[str, dict[str, Any]]` — Retrieves retrieval contexts.
- L21 `def prune_retrieval_contexts(req: Request) -> None` — Removes retrieval contexts.
- L33 `def store_retrieval_context(req: Request, *, query: str, context: str, rag_result: Any, mitre_table: list[Any] | None=None) -> str` — Persists retrieval context.
- L58 `def load_retrieval_context(req: Request, context_id: str) -> dict[str, Any] | None` — Retrieves retrieval context.
- L69 `def export_retrieval_context(req: Request, context_id: str) -> dict[str, Any] | None` — Serializes retrieval context.

### [`rag_service/app/routers/rag.py`](../../rag_service/app/routers/rag.py)

Purpose: Owns rag behavior for the GraphRAG runtime and evaluation package.

- L23 `def _get_query_limiter(req: Request) -> CapacityLimiter` — Process-wide cap on concurrent pipeline runs.
- L37 `def _run_pipeline(rag_agent: Any, query: str) -> tuple[Any, list[Any]]` — The whole blocking section, so one worker thread does all of it.
- L55 `async def health(request: Request)` — Implements health.
- L63 `async def query_rag(request: QueryRequest, req: Request)` — Implements query rag.
- L100 `async def get_retrieval_context(context_id: str, req: Request)` — Retrieves retrieval context.

### [`rag_service/app/schemas/__init__.py`](../../rag_service/app/schemas/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/schemas/rag.py`](../../rag_service/app/schemas/rag.py)

Purpose: Owns rag behavior for the GraphRAG runtime and evaluation package.

- L10 `class QueryRequest(BaseModel)` — Encapsulates queryrequest.
- L23 `class QueryResponse(BaseModel)` — Encapsulates queryresponse.
- L37 `def normalize_empty_retrieval_context_id(cls, value: Any) -> Any` — Normalizes empty retrieval context id.
- L41 `class RetrievalContextSnapshot(BaseModel)` — Encapsulates retrievalcontextsnapshot.

## Graphrag Regression Suite

### [`rag_service/tests/test_core_llm_provider.py`](../../rag_service/tests/test_core_llm_provider.py)

Purpose: Verifies core llm provider behavior in the GraphRAG regression suite.

- L23 `def test_default_provider_and_openrouter_target(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test default provider and openrouter target.
- L38 `def test_explicit_anthropic_target(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test explicit anthropic target.
- L51 `def test_invalid_selector_is_rejected() -> None` — Implements test invalid selector is rejected.
- L56 `def test_missing_selected_key_does_not_fallback_to_other_or_evaluation_key(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test missing selected key does not fallback to other or evaluation key.
- L75 `def test_factory_constructs_selected_client(monkeypatch: pytest.MonkeyPatch, provider: str, expected_model: str, has_openrouter_headers: bool) -> None` — Implements test factory constructs selected client.
- L83 `class FakeChatAnthropic` — Encapsulates fakechatanthropic.
- L84 `def __init__(self, **kwargs: object) -> None` — Implements init.
- L109 `def test_local_mode_takes_precedence_over_cloud_factory(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test local mode takes precedence over cloud factory.
- L116 `class FakeChatOllama` — Encapsulates fakechatollama.
- L117 `def __init__(self, **kwargs: object) -> None` — Implements init.
- L123 `def fail_cloud_factory(**kwargs: object) -> None` — Implements fail cloud factory.
- L133 `def test_all_production_pipeline_modules_use_central_factory() -> None` — Implements test all production pipeline modules use central factory.

### [`rag_service/tests/test_llm_content.py`](../../rag_service/tests/test_llm_content.py)

Purpose: Verifies llm content behavior in the GraphRAG regression suite.

- L27 `class StubLlm` — Encapsulates stubllm.
- L28 `def __init__(self, response: AIMessage) -> None` — Implements init.
- L31 `def invoke(self, messages: object) -> AIMessage` — Implements invoke.
- L35 `class RaisingLlm` — Encapsulates raisingllm.
- L36 `def invoke(self, messages: object) -> AIMessage` — Implements invoke.
- L40 `class StubRouter` — Encapsulates stubrouter.
- L41 `def route_query(self, query: str) -> str` — Implements route query.
- L45 `class BrokenTextMessage(AIMessage)` — Encapsulates brokentextmessage.
- L47 `def text(self) -> str` — Implements text.
- L51 `def message(content: Any) -> AIMessage` — Implements message.
- L55 `def test_string_content_is_returned_without_trimming() -> None` — Implements test string content is returned without trimming.
- L62 `def test_mixed_reasoning_and_text_returns_only_visible_text() -> None` — Implements test mixed reasoning and text returns only visible text.
- L78 `def test_text_blocks_are_concatenated_in_order() -> None` — Implements test text blocks are concatenated in order.
- L92 `def test_unknown_blocks_are_ignored_when_visible_text_exists() -> None` — Implements test unknown blocks are ignored when visible text exists.
- L118 `def test_empty_unknown_and_malformed_content_raises(content: Any) -> None` — Implements test empty unknown and malformed content raises.
- L123 `def test_error_does_not_expose_block_or_property_secrets() -> None` — Implements test error does not expose block or property secrets.
- L143 `def test_evaluator_reads_visible_json_and_propagates_empty_content() -> None` — Implements test evaluator reads visible json and propagates empty content.
- L169 `def test_router_falls_back_only_for_content_error() -> None` — Implements test router falls back only for content error.
- L182 `def test_decomposer_keeps_existing_whole_query_fallback() -> None` — Implements test decomposer keeps existing whole query fallback.
- L193 `def test_cross_lingual_translation_returns_original_on_content_error() -> None` — Implements test cross lingual translation returns original on content error.
- L207 `def test_chain_final_answer_excludes_non_text_blocks() -> None` — Implements test chain final answer excludes non text blocks.
- L231 `def test_pipeline_files_do_not_directly_consume_response_content() -> None` — Implements test pipeline files do not directly consume response content.

### [`rag_service/tests/test_rag_query_concurrency.py`](../../rag_service/tests/test_rag_query_concurrency.py)

Purpose: POST /query must not block the event loop, so sessions run concurrently.

- L19 `def anyio_backend() -> str` — Implements anyio backend.
- L23 `class BlockingRagAgent` — Stands in for GraphRAGAgent: query() blocks the calling thread.
- L26 `def __init__(self, duration: float=QUERY_DURATION) -> None` — Implements init.
- L33 `def query(self, query: str, *, verbose: bool) -> SimpleNamespace` — Implements query.
- L50 `def _make_app(agent: BlockingRagAgent) -> FastAPI` — Implements make app.
- L58 `def _client(app: FastAPI) -> httpx.AsyncClient` — Implements client.
- L65 `def stub_mitre_table(monkeypatch) -> None` — Implements stub mitre table.
- L70 `async def test_sessions_query_concurrently_and_keep_their_own_context() -> None` — Implements test sessions query concurrently and keep their own context.
- L78 `async def run(query: str) -> None` — Executes run.
- L108 `async def test_event_loop_stays_responsive_while_a_query_runs() -> None` — Implements test event loop stays responsive while a query runs.
- L130 `async def test_capacity_limiter_caps_parallel_pipelines() -> None` — Implements test capacity limiter caps parallel pipelines.

### [`rag_service/tests/test_rag_query_route.py`](../../rag_service/tests/test_rag_query_route.py)

Purpose: Verifies rag query route behavior in the GraphRAG regression suite.

- L12 `class FakeRagAgent` — Encapsulates fakeragagent.
- L13 `def __init__(self) -> None` — Implements init.
- L17 `def query(self, query: str, *, verbose: bool) -> SimpleNamespace` — Implements query.
- L25 `def retrieve_with_details(self, query: str) -> None` — Implements retrieve with details.
- L30 `def test_query_runs_full_agent_pipeline_without_exposing_generated_answer(monkeypatch) -> None` — Implements test query runs full agent pipeline without exposing generated answer.
- L40 `def build_table(result: object, answer: str) -> list[object]` — Builds table.

### [`rag_service/tests/test_stix_parser.py`](../../rag_service/tests/test_stix_parser.py)

Purpose: Unit Tests for STIX 2.1 Parser =============================== Validates tombstoning, version overrides, relationship filtering, latest-file folder parsing defaults, and T1527 regression logic.

- L22 `def make_mock_bundle(objects)` — Implements make mock bundle.
- L31 `def test_revoked_tombstone_exclusions()` — Parser test: older file has active object, newer file marks it revoked -> final entities exclude it.
- L72 `def test_newer_version_overrides()` — Parser test: older active object, newer active object with same STIX ID -> newer active wins.
- L115 `def test_relationships_referencing_tombstones_removed()` — Parser test: relationships referencing tombstoned objects are removed.
- L176 `def test_default_folder_parsing_prefers_main_file(monkeypatch)` — Parser test: default folder parsing prefers enterprise-attack.json when present.
- L228 `def test_regression_t1527()` — Regression test: T1527 is not present in parsed entities.
