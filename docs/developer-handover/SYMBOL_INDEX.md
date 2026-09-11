# CyberCase File and Function Index

Generated `2026-09-10T01:03:47+00:00` from branch `main` at commit `e4f1791`; working tree dirty: `yes`.

This is the exhaustive first-party source inventory for the checkout. Descriptions generated from code names are navigation aids; runtime truth is determined by imports, route registration, and the handover guide.
Coverage: **673 source files** and **3307 named symbols**.

Each symbol includes the declared input and output contract when the language exposes one; body-level effects and cross-file handoffs are explained in the integration guide.

## Database Migration Layer

### [`backend/alembic/baseline_versions/0001_raw_evidence_chat.py`](../../backend/alembic/baseline_versions/0001_raw_evidence_chat.py)

Purpose: Create the raw-evidence chat schema.

- L19 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L138 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0002_optional_report_retrieval_context.py`](../../backend/alembic/baseline_versions/0002_optional_report_retrieval_context.py)

Purpose: Allow reports without optional MITRE retrieval context.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L22 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0003_user_oauth_and_thread_ownership.py`](../../backend/alembic/baseline_versions/0003_user_oauth_and_thread_ownership.py)

Purpose: Add users table and user_id to chat_threads for OAuth authentication and thread ownership.

- L19 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L71 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0004_password_accounts.py`](../../backend/alembic/baseline_versions/0004_password_accounts.py)

Purpose: Owns 0004 password accounts behavior for the database migration layer.

- L10 `def upgrade()` — Implements upgrade. Receives: `not applicable`. Sends: `inferred or None`.
- L19 `def downgrade()` — Implements downgrade. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/alembic/baseline_versions/0005_case_domain.py`](../../backend/alembic/baseline_versions/0005_case_domain.py)

Purpose: Add first-class cases with one shared-identity chat thread each.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L50 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0006_case_materials.py`](../../backend/alembic/baseline_versions/0006_case_materials.py)

Purpose: Add immutable Case materials, evidence revisions, and snapshots.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L114 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0007_case_runs_and_results.py`](../../backend/alembic/baseline_versions/0007_case_runs_and_results.py)

Purpose: Add Case-owned runs, immutable analysis results, and Chat publication links.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L82 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0008_case_clarifications.py`](../../backend/alembic/baseline_versions/0008_case_clarifications.py)

Purpose: Persist Case-owned clarification questions and answer linkage.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L50 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0009_case_report_bindings.py`](../../backend/alembic/baseline_versions/0009_case_report_bindings.py)

Purpose: Add result and evidence bindings for Case-owned reports.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L108 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/baseline_versions/0010_preserve_reports_after_chat_delete.py`](../../backend/alembic/baseline_versions/0010_preserve_reports_after_chat_delete.py)

Purpose: Keep frozen reports when an optional ChatThread is removed.

- L13 `def upgrade() -> None` — Implements upgrade. Receives: `not applicable`. Sends: `None`.
- L35 `def downgrade() -> None` — Implements downgrade. Receives: `not applicable`. Sends: `None`.

### [`backend/alembic/env.py`](../../backend/alembic/env.py)

Purpose: Owns env behavior for the database migration layer.

- L24 `def run_migrations_offline() -> None` — Run migrations in 'offline' mode. Receives: `not applicable`. Sends: `None`.
- L39 `def do_run_migrations(connection) -> None` — Implements do run migrations. Receives: `connection`. Sends: `None`.
- L46 `async def run_migrations_online() -> None` — Run migrations in 'online' mode. Receives: `not applicable`. Sends: `None`.

## Backend Runtime

### [`backend/app/__init__.py`](../../backend/app/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/config.py`](../../backend/app/config.py)

Purpose: Application configuration — modular component mixins loaded from environment / .env.

- L12 `class DatabaseConfig(BaseModel)` — Encapsulates databaseconfig. Receives: `constructor arguments and class fields`. Sends: `DatabaseConfig`.
- L21 `def async_database_url(self) -> str` — Ensures the URL uses postgresql+asyncpg:// for SQLAlchemy async engine. Receives: `self`. Sends: `str`.
- L49 `class CORSConfig(BaseModel)` — Encapsulates corsconfig. Receives: `constructor arguments and class fields`. Sends: `CORSConfig`.
- L53 `def cors_origins_list(self) -> list[str]` — Implements cors origins list. Receives: `self`. Sends: `list[str]`.
- L72 `class LLMProviderConfig(BaseModel)` — Encapsulates llmproviderconfig. Receives: `constructor arguments and class fields`. Sends: `LLMProviderConfig`.
- L84 `class LLMTokenBudgetConfig(BaseModel)` — Encapsulates llmtokenbudgetconfig. Receives: `constructor arguments and class fields`. Sends: `LLMTokenBudgetConfig`.
- L92 `class FollowupPolicyConfig(BaseModel)` — Encapsulates followuppolicyconfig. Receives: `constructor arguments and class fields`. Sends: `FollowupPolicyConfig`.
- L105 `class CaseAnalysisConfig(BaseModel)` — Encapsulates caseanalysisconfig. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisConfig`.
- L120 `class ReportConfig(BaseModel)` — Encapsulates reportconfig. Receives: `constructor arguments and class fields`. Sends: `ReportConfig`.
- L129 `class DocumentIngestionConfig(BaseModel)` — Encapsulates documentingestionconfig. Receives: `constructor arguments and class fields`. Sends: `DocumentIngestionConfig`.
- L150 `class AuthConfig(BaseModel)` — Encapsulates authconfig. Receives: `constructor arguments and class fields`. Sends: `AuthConfig`.
- L167 `class Settings(DatabaseConfig, CORSConfig, AuthConfig, LLMProviderConfig, LLMTokenBudgetConfig, FollowupPolicyConfig, CaseAnalysisConfig, ReportConfig, DocumentIngestionConfig, BaseSettings)` — All configuration values are read from environment variables. Receives: `constructor arguments and class fields`. Sends: `Settings`.

### [`backend/app/database.py`](../../backend/app/database.py)

Purpose: Owns database behavior for the backend runtime.

- L34 `class Base(DeclarativeBase)` — Encapsulates base. Receives: `constructor arguments and class fields`. Sends: `Base`.
- L39 `async def get_db()` — Yield an async DB session for FastAPI dependency injection. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/app/main.py`](../../backend/app/main.py)

Purpose: FastAPI application for case and chat APIs plus document ingestion preview.

- L26 `async def lifespan(app: FastAPI)` — Implements lifespan. Receives: `app: FastAPI`. Sends: `inferred or None`.

### [`backend/app/models/__init__.py`](../../backend/app/models/__init__.py)

Purpose: Register the case, chat, retrieval, and report ORM models.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/models/case.py`](../../backend/app/models/case.py)

Purpose: Case aggregate owning one primary chat thread.

- L27 `class Case(Base)` — Encapsulates case. Receives: `constructor arguments and class fields`. Sends: `Case`.

### [`backend/app/models/case_clarification.py`](../../backend/app/models/case_clarification.py)

Purpose: Owns case clarification behavior for the backend runtime.

- L32 `class CaseClarification(Base)` — Encapsulates caseclarification. Receives: `constructor arguments and class fields`. Sends: `CaseClarification`.

### [`backend/app/models/case_materials.py`](../../backend/app/models/case_materials.py)

Purpose: Case documents, extraction revisions, admitted evidence, and snapshots.

- L34 `class CaseDocument(Base)` — Encapsulates casedocument. Receives: `constructor arguments and class fields`. Sends: `CaseDocument`.
- L63 `class DocumentExtraction(Base)` — Encapsulates documentextraction. Receives: `constructor arguments and class fields`. Sends: `DocumentExtraction`.
- L89 `class EvidenceSource(Base)` — Encapsulates evidencesource. Receives: `constructor arguments and class fields`. Sends: `EvidenceSource`.
- L123 `class EvidenceRevision(Base)` — Encapsulates evidencerevision. Receives: `constructor arguments and class fields`. Sends: `EvidenceRevision`.
- L150 `class CaseEvidenceSnapshot(Base)` — Encapsulates caseevidencesnapshot. Receives: `constructor arguments and class fields`. Sends: `CaseEvidenceSnapshot`.

### [`backend/app/models/case_run.py`](../../backend/app/models/case_run.py)

Purpose: Owns case run behavior for the backend runtime.

- L33 `class CaseRun(Base)` — Encapsulates caserun. Receives: `constructor arguments and class fields`. Sends: `CaseRun`.
- L92 `class CaseAnalysisResult(Base)` — Encapsulates caseanalysisresult. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisResult`.

### [`backend/app/models/chat.py`](../../backend/app/models/chat.py)

Purpose: Persistent chat threads, messages, and background processing runs.

- L35 `class ChatThread(Base)` — Encapsulates chatthread. Receives: `constructor arguments and class fields`. Sends: `ChatThread`.
- L122 `class ChatMessage(Base)` — Encapsulates chatmessage. Receives: `constructor arguments and class fields`. Sends: `ChatMessage`.
- L189 `class ChatRun(Base)` — Encapsulates chatrun. Receives: `constructor arguments and class fields`. Sends: `ChatRun`.

### [`backend/app/models/rag_context.py`](../../backend/app/models/rag_context.py)

Purpose: Durable retrieval context bound one-to-one to the chat run that produced it.

- L24 `class RagContext(Base)` — Encapsulates ragcontext. Receives: `constructor arguments and class fields`. Sends: `RagContext`.

### [`backend/app/models/report.py`](../../backend/app/models/report.py)

Purpose: Immutable report history scoped to a persisted chat thread.

- L35 `class ChatReport(Base)` — Encapsulates chatreport. Receives: `constructor arguments and class fields`. Sends: `ChatReport`.

### [`backend/app/models/user.py`](../../backend/app/models/user.py)

Purpose: User model for OAuth authentication and chat ownership.

- L27 `class User(Base)` — Encapsulates user. Receives: `constructor arguments and class fields`. Sends: `User`.

### [`backend/app/routers/__init__.py`](../../backend/app/routers/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/routers/auth.py`](../../backend/app/routers/auth.py)

Purpose: Authentication API router for OAuth login, callbacks, user profile, and dev-mode login.

- L29 `async def oauth_login(provider: str) -> RedirectResponse` — Redirect user to OAuth provider's authorization screen. Receives: `provider: str`. Sends: `RedirectResponse`.
- L47 `async def oauth_callback(provider: str, request: Request, code: str=Query(..., description='OAuth authorization code'), state: str | None=Query(default=None, description='OAuth state parameter'), db: AsyncSession=Depends(get_db)) -> RedirectResponse` — Exchange authorization code for user profile, issue session cookie, and redirect to frontend. Receives: `provider: str, request: Request, code: str=Query(..., description='OAuth authorization code'), state: str | None=Query(default=None, description='OAuth state parameter'), db: AsyncSession=Depends(get_db)`. Sends: `RedirectResponse`.
- L80 `async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead` — Return user profile for the currently logged-in user. Receives: `current_user: Annotated[User, Depends(get_current_user)]`. Sends: `UserRead`.
- L88 `async def get_session(user: Annotated[User | None, Depends(get_optional_user)]) -> UserRead | None` — Return user profile if logged in, or null without 401 challenge. Receives: `user: Annotated[User | None, Depends(get_optional_user)]`. Sends: `UserRead | None`.
- L98 `async def logout(response: Response) -> dict[str, str]` — Clear session cookie and log out. Receives: `response: Response`. Sends: `dict[str, str]`.
- L114 `async def dev_login(payload: DevLoginRequest, response: Response, db: AsyncSession=Depends(get_db)) -> AuthTokenResponse` — Simulate OAuth login locally for development and automated testing. Receives: `payload: DevLoginRequest, response: Response, db: AsyncSession=Depends(get_db)`. Sends: `AuthTokenResponse`.
- L146 `async def available_providers() -> list[str]` — Implements available providers. Receives: `not applicable`. Sends: `list[str]`.

### [`backend/app/routers/case_analysis.py`](../../backend/app/routers/case_analysis.py)

Purpose: Owns case analysis behavior for the backend runtime.

- L30 `def _case_run_http_error(error: CaseRunError | CaseMaterialsError) -> HTTPException` — Implements case run http error. Receives: `error: CaseRunError | CaseMaterialsError`. Sends: `HTTPException`.
- L38 `async def start_case_analysis(case_id: UUID, request: CaseAnalysisCreate, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements start case analysis. Receives: `case_id: UUID, request: CaseAnalysisCreate, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L62 `async def get_latest_analysis(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves latest analysis. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L82 `async def get_case_run(case_id: UUID, run_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves case run. Receives: `case_id: UUID, run_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.

### [`backend/app/routers/case_clarifications.py`](../../backend/app/routers/case_clarifications.py)

Purpose: Owns case clarifications behavior for the backend runtime.

- L26 `def _clarification_http_error(error: CaseClarificationError) -> HTTPException` — Implements clarification http error. Receives: `error: CaseClarificationError`. Sends: `HTTPException`.
- L34 `async def list_case_clarifications(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists case clarifications. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L50 `async def answer_case_clarification(case_id: UUID, clarification_id: UUID, request: CaseClarificationAnswer, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements answer case clarification. Receives: `case_id: UUID, clarification_id: UUID, request: CaseClarificationAnswer, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.

### [`backend/app/routers/case_materials.py`](../../backend/app/routers/case_materials.py)

Purpose: Owns case materials behavior for the backend runtime.

- L30 `def _materials_http_error(error: CaseMaterialsError) -> HTTPException` — Implements materials http error. Receives: `error: CaseMaterialsError`. Sends: `HTTPException`.
- L37 `def _ingestion_http_error(error: DocumentIngestionError) -> HTTPException` — Implements ingestion http error. Receives: `error: DocumentIngestionError`. Sends: `HTTPException`.
- L52 `async def list_case_documents(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists case documents. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L64 `async def add_case_document(case_id: UUID, file: UploadFile=File(...), db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements add case document. Receives: `case_id: UUID, file: UploadFile=File(...), db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L103 `async def admit_case_document(case_id: UUID, document_id: UUID, request: AdmitExtractionRequest, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements admit case document. Receives: `case_id: UUID, document_id: UUID, request: AdmitExtractionRequest, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L127 `async def list_case_evidence(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists case evidence. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L139 `async def get_case_evidence_snapshot(case_id: UUID, snapshot_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves case evidence snapshot. Receives: `case_id: UUID, snapshot_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L156 `async def add_case_evidence(case_id: UUID, request: CaseEvidenceCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements add case evidence. Receives: `case_id: UUID, request: CaseEvidenceCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L177 `async def revise_case_evidence(case_id: UUID, source_id: UUID, request: CaseEvidenceCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements revise case evidence. Receives: `case_id: UUID, source_id: UUID, request: CaseEvidenceCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L198 `async def archive_case_evidence(case_id: UUID, source_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements archive case evidence. Receives: `case_id: UUID, source_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L216 `async def create_case_evidence_snapshot(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Creates case evidence snapshot. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.

### [`backend/app/routers/case_reports.py`](../../backend/app/routers/case_reports.py)

Purpose: Owns case reports behavior for the backend runtime.

- L18 `def _report_http_error(error: ReportServiceError) -> HTTPException` — Implements report http error. Receives: `error: ReportServiceError`. Sends: `HTTPException`.
- L27 `async def generate_case_report(case_id: UUID, request: CaseReportCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Generates case report. Receives: `case_id: UUID, request: CaseReportCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L41 `async def list_case_reports(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists case reports. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L53 `async def get_case_report(case_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves case report. Receives: `case_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L66 `async def download_case_report_pdf(case_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements download case report pdf. Receives: `case_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.

### [`backend/app/routers/cases.py`](../../backend/app/routers/cases.py)

Purpose: Case aggregate HTTP endpoints.

- L20 `async def ensure_case_chat(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements ensure case chat. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L29 `async def list_cases(db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists cases. Receives: `db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L37 `async def get_case(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves case. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L46 `async def create_case(request: CaseCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Creates case. Receives: `request: CaseCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L55 `async def update_case(case_id: UUID, request: CaseUpdate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Updates case. Receives: `case_id: UUID, request: CaseUpdate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L65 `async def delete_case(case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)) -> Response` — Removes case. Receives: `case_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `Response`.

### [`backend/app/routers/chat.py`](../../backend/app/routers/chat.py)

Purpose: Chat thread, message, and report HTTP endpoints.

- L45 `async def list_chat_threads(db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists chat threads. Receives: `db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L58 `async def get_chat_thread(thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves chat thread. Receives: `thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L72 `async def create_chat_thread(request: ChatThreadCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Creates chat thread. Receives: `request: ChatThreadCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L86 `async def update_chat_thread(thread_id: UUID, request: ChatThreadUpdate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Updates chat thread. Receives: `thread_id: UUID, request: ChatThreadUpdate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L102 `async def delete_chat_thread(thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)) -> Response` — Removes chat thread. Receives: `thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `Response`.
- L117 `async def create_chat_message(thread_id: UUID, request: ChatMessageCreate, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Creates chat message. Receives: `thread_id: UUID, request: ChatMessageCreate, background_tasks: BackgroundTasks, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L157 `async def get_chat_run(thread_id: UUID, run_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves chat run. Receives: `thread_id: UUID, run_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L169 `def _report_http_exception(error: ReportGenerationError) -> HTTPException` — Implements report http exception. Receives: `error: ReportGenerationError`. Sends: `HTTPException`.
- L186 `async def generate_chat_report(thread_id: UUID, request: ChatReportCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Generates chat report. Receives: `thread_id: UUID, request: ChatReportCreate, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L207 `async def list_chat_reports(thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Lists chat reports. Receives: `thread_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L226 `async def get_chat_report(thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Retrieves chat report. Receives: `thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.
- L246 `async def download_chat_report_pdf(thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user))` — Implements download chat report pdf. Receives: `thread_id: UUID, report_id: UUID, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)`. Sends: `inferred or None`.

### [`backend/app/routers/document_ingestion.py`](../../backend/app/routers/document_ingestion.py)

Purpose: Owns document ingestion behavior for the backend runtime.

- L24 `def _build_recognizer() -> DocumentRecognizer` — Builds recognizer. Receives: `not applicable`. Sends: `DocumentRecognizer`.
- L48 `def _build_region_pipeline(recognizer) -> RegionRecognitionPipeline` — Builds region pipeline. Receives: `recognizer`. Sends: `RegionRecognitionPipeline`.
- L61 `def _build_service() -> DocumentIngestionService` — Builds service. Receives: `not applicable`. Sends: `DocumentIngestionService`.
- L76 `async def _read_limited(upload: UploadFile, max_bytes: int) -> bytes` — Retrieves limited. Receives: `upload: UploadFile, max_bytes: int`. Sends: `bytes`.
- L98 `async def preview_document_ingestion(file: UploadFile=File(...), mode: IngestionMode=Query(default=IngestionMode.UNIFIED), segmentation: bool | None=Query(default=None), case_key: str | None=Query(default=None), x_idempotency_key: str | None=Header(default=None, alias='X-Idempotency-Key'), x_case_key: str | None=Header(default=None, alias='X-Case-Key')) -> IngestedDocument` — Implements preview document ingestion. Receives: `file: UploadFile=File(...), mode: IngestionMode=Query(default=IngestionMode.UNIFIED), segmentation: bool | None=Query(default=None), case_key: str | None=Query(default=None), x_idempotency_key: str | None=Header(default=None, alias='X-Idempotency-Key'), x_case_key: str | None=Header(default=None, alias='X-Case-Key')`. Sends: `IngestedDocument`.

### [`backend/app/routers/health.py`](../../backend/app/routers/health.py)

Purpose: Health-check router.

- L14 `async def health_check(db: AsyncSession=Depends(get_db))` — Returns service health and database connectivity status. Receives: `db: AsyncSession=Depends(get_db)`. Sends: `inferred or None`.

### [`backend/app/routers/password_auth.py`](../../backend/app/routers/password_auth.py)

Purpose: Owns password auth behavior for the backend runtime.

- L19 `def start_session(user: User, response: Response) -> UserRead` — Implements start session. Receives: `user: User, response: Response`. Sends: `UserRead`.
- L27 `async def register(payload: RegisterRequest, response: Response, db: AsyncSession=Depends(get_db))` — Implements register. Receives: `payload: RegisterRequest, response: Response, db: AsyncSession=Depends(get_db)`. Sends: `inferred or None`.
- L53 `async def login(payload: PasswordLoginRequest, response: Response, db: AsyncSession=Depends(get_db))` — Implements login. Receives: `payload: PasswordLoginRequest, response: Response, db: AsyncSession=Depends(get_db)`. Sends: `inferred or None`.

### [`backend/app/schemas/__init__.py`](../../backend/app/schemas/__init__.py)

Purpose: Pydantic request and response schemas for all API domains.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/schemas/auth.py`](../../backend/app/schemas/auth.py)

Purpose: Pydantic schemas for authentication and user profiles.

- L11 `class UserRead(BaseModel)` — Encapsulates userread. Receives: `constructor arguments and class fields`. Sends: `UserRead`.
- L22 `class AuthTokenResponse(BaseModel)` — Encapsulates authtokenresponse. Receives: `constructor arguments and class fields`. Sends: `AuthTokenResponse`.
- L29 `class DevLoginRequest(BaseModel)` — Encapsulates devloginrequest. Receives: `constructor arguments and class fields`. Sends: `DevLoginRequest`.
- L35 `class PasswordLoginRequest(BaseModel)` — Encapsulates passwordloginrequest. Receives: `constructor arguments and class fields`. Sends: `PasswordLoginRequest`.
- L40 `class RegisterRequest(PasswordLoginRequest)` — Encapsulates registerrequest. Receives: `constructor arguments and class fields`. Sends: `RegisterRequest`.

### [`backend/app/schemas/case_clarifications.py`](../../backend/app/schemas/case_clarifications.py)

Purpose: Owns case clarifications behavior for the backend runtime.

- L14 `class CaseClarificationRead(BaseModel)` — Encapsulates caseclarificationread. Receives: `constructor arguments and class fields`. Sends: `CaseClarificationRead`.
- L36 `class CaseClarificationAnswer(BaseModel)` — Encapsulates caseclarificationanswer. Receives: `constructor arguments and class fields`. Sends: `CaseClarificationAnswer`.
- L42 `class CaseClarificationAccepted(BaseModel)` — Encapsulates caseclarificationaccepted. Receives: `constructor arguments and class fields`. Sends: `CaseClarificationAccepted`.

### [`backend/app/schemas/case_materials.py`](../../backend/app/schemas/case_materials.py)

Purpose: HTTP contracts for Case materials and admitted evidence.

- L12 `class DocumentExtractionRead(BaseModel)` — Encapsulates documentextractionread. Receives: `constructor arguments and class fields`. Sends: `DocumentExtractionRead`.
- L27 `class CaseDocumentRead(BaseModel)` — Encapsulates casedocumentread. Receives: `constructor arguments and class fields`. Sends: `CaseDocumentRead`.
- L41 `class AdmitExtractionRequest(BaseModel)` — Encapsulates admitextractionrequest. Receives: `constructor arguments and class fields`. Sends: `AdmitExtractionRequest`.
- L45 `class EvidenceRevisionCreate(BaseModel)` — Encapsulates evidencerevisioncreate. Receives: `constructor arguments and class fields`. Sends: `EvidenceRevisionCreate`.
- L50 `class CaseEvidenceCreate(EvidenceRevisionCreate)` — Encapsulates caseevidencecreate. Receives: `constructor arguments and class fields`. Sends: `CaseEvidenceCreate`.
- L55 `class EvidenceRevisionRead(BaseModel)` — Encapsulates evidencerevisionread. Receives: `constructor arguments and class fields`. Sends: `EvidenceRevisionRead`.
- L69 `class EvidenceSourceRead(BaseModel)` — Encapsulates evidencesourceread. Receives: `constructor arguments and class fields`. Sends: `EvidenceSourceRead`.
- L83 `class CaseEvidenceSnapshotRead(BaseModel)` — Encapsulates caseevidencesnapshotread. Receives: `constructor arguments and class fields`. Sends: `CaseEvidenceSnapshotRead`.

### [`backend/app/schemas/case_runs.py`](../../backend/app/schemas/case_runs.py)

Purpose: Owns case runs behavior for the backend runtime.

- L14 `class CaseAnalysisCreate(BaseModel)` — Encapsulates caseanalysiscreate. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisCreate`.
- L20 `class CaseRunRead(BaseModel)` — Encapsulates caserunread. Receives: `constructor arguments and class fields`. Sends: `CaseRunRead`.
- L40 `class CaseAnalysisResultRead(BaseModel)` — Encapsulates caseanalysisresultread. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisResultRead`.
- L60 `class CaseAnalysisAccepted(BaseModel)` — Encapsulates caseanalysisaccepted. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisAccepted`.

### [`backend/app/schemas/cases.py`](../../backend/app/schemas/cases.py)

Purpose: Case aggregate API schemas.

- L17 `class CaseCreate(BaseModel)` — Encapsulates casecreate. Receives: `constructor arguments and class fields`. Sends: `CaseCreate`.
- L21 `class CaseUpdate(BaseModel)` — Encapsulates caseupdate. Receives: `constructor arguments and class fields`. Sends: `CaseUpdate`.
- L25 `class CaseRead(BaseModel)` — Encapsulates caseread. Receives: `constructor arguments and class fields`. Sends: `CaseRead`.

### [`backend/app/schemas/chat.py`](../../backend/app/schemas/chat.py)

Purpose: Chat Thread, Message, and Run API schemas.

- L37 `class ChatThreadCreate(BaseModel)` — Encapsulates chatthreadcreate. Receives: `constructor arguments and class fields`. Sends: `ChatThreadCreate`.
- L45 `class ChatThreadUpdate(BaseModel)` — Encapsulates chatthreadupdate. Receives: `constructor arguments and class fields`. Sends: `ChatThreadUpdate`.
- L52 `class ChatMessageCreate(BaseModel)` — Encapsulates chatmessagecreate. Receives: `constructor arguments and class fields`. Sends: `ChatMessageCreate`.
- L66 `class ChatThreadRead(BaseModel)` — Encapsulates chatthreadread. Receives: `constructor arguments and class fields`. Sends: `ChatThreadRead`.
- L77 `class ChatMessageRead(BaseModel)` — Encapsulates chatmessageread. Receives: `constructor arguments and class fields`. Sends: `ChatMessageRead`.
- L92 `class ChatRetryRequest(ChatMessageCreate)` — Encapsulates chatretryrequest. Receives: `constructor arguments and class fields`. Sends: `ChatRetryRequest`.
- L97 `class ChatThreadDetail(ChatThreadRead)` — Encapsulates chatthreaddetail. Receives: `constructor arguments and class fields`. Sends: `ChatThreadDetail`.
- L102 `class ChatRunRead(BaseModel)` — Encapsulates chatrunread. Receives: `constructor arguments and class fields`. Sends: `ChatRunRead`.
- L115 `class ChatMessageAccepted(BaseModel)` — Encapsulates chatmessageaccepted. Receives: `constructor arguments and class fields`. Sends: `ChatMessageAccepted`.
- L120 `class CaseChatMessageAccepted(BaseModel)` — Encapsulates casechatmessageaccepted. Receives: `constructor arguments and class fields`. Sends: `CaseChatMessageAccepted`.

### [`backend/app/schemas/document_sources.py`](../../backend/app/schemas/document_sources.py)

Purpose: Owns document sources behavior for the backend runtime.

- L15 `class CaseNarrativeDocumentPageSpan(BaseModel)` — Encapsulates casenarrativedocumentpagespan. Receives: `constructor arguments and class fields`. Sends: `CaseNarrativeDocumentPageSpan`.
- L24 `def validate_offsets(self) -> 'CaseNarrativeDocumentPageSpan'` — Validates offsets. Receives: `self`. Sends: `'CaseNarrativeDocumentPageSpan'`.
- L30 `class CaseNarrativeDocumentSource(BaseModel)` — Encapsulates casenarrativedocumentsource. Receives: `constructor arguments and class fields`. Sends: `CaseNarrativeDocumentSource`.
- L48 `def normalize_text(cls, value: str) -> str` — Normalizes text. Receives: `cls, value: str`. Sends: `str`.
- L53 `def normalize_warnings(cls, value: list[str]) -> list[str]` — Normalizes warnings. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L62 `def validate_confidence(self) -> 'CaseNarrativeDocumentSource'` — Validates confidence. Receives: `self`. Sends: `'CaseNarrativeDocumentSource'`.

### [`backend/app/schemas/message_metadata.py`](../../backend/app/schemas/message_metadata.py)

Purpose: Owns message metadata behavior for the backend runtime.

- L9 `class DocumentSourceMetadata(TypedDict)` — Encapsulates documentsourcemetadata. Receives: `constructor arguments and class fields`. Sends: `DocumentSourceMetadata`.
- L22 `class ChatActionMetadata(TypedDict)` — Encapsulates chatactionmetadata. Receives: `constructor arguments and class fields`. Sends: `ChatActionMetadata`.
- L32 `class RagAttemptMetadata(TypedDict)` — Encapsulates ragattemptmetadata. Receives: `constructor arguments and class fields`. Sends: `RagAttemptMetadata`.
- L38 `class FollowUpMetadata(TypedDict)` — Encapsulates followupmetadata. Receives: `constructor arguments and class fields`. Sends: `FollowUpMetadata`.
- L55 `class MessageMetadata(TypedDict)` — Encapsulates messagemetadata. Receives: `constructor arguments and class fields`. Sends: `MessageMetadata`.
- L82 `def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]` — Serializes message metadata. Receives: `value: dict[str, object]`. Sends: `dict[str, object]`.

### [`backend/app/schemas/rag.py`](../../backend/app/schemas/rag.py)

Purpose: Owns rag behavior for the backend runtime.

- L8 `class RagQueryRequest(BaseModel)` — Encapsulates ragqueryrequest. Receives: `constructor arguments and class fields`. Sends: `RagQueryRequest`.
- L15 `class QueryRequest(RagQueryRequest)` — Encapsulates queryrequest. Receives: `constructor arguments and class fields`. Sends: `QueryRequest`.
- L19 `class MitreTableRow(BaseModel)` — One entry of the MITRE mapping table produced by the RAG service. Receives: `constructor arguments and class fields`. Sends: `MitreTableRow`.
- L35 `class LegalProvision(BaseModel)` — One provision returned by the external legal service. Receives: `constructor arguments and class fields`. Sends: `LegalProvision`.
- L47 `class LegalReferenceResult(BaseModel)` — Provisions that may be relevant — references, not recommendations. Receives: `constructor arguments and class fields`. Sends: `LegalReferenceResult`.
- L59 `class QueryResponse(BaseModel)` — Encapsulates queryresponse. Receives: `constructor arguments and class fields`. Sends: `QueryResponse`.
- L73 `def normalize_empty_retrieval_context_id(cls, value: Any) -> Any` — Treat the RAG service's empty-string sentinel as no frozen context. Receives: `cls, value: Any`. Sends: `Any`.

### [`backend/app/schemas/reports.py`](../../backend/app/schemas/reports.py)

Purpose: Typed report output and chat-report API contracts.

- L63 `class ReportClaim(BaseModel)` — Encapsulates reportclaim. Receives: `constructor arguments and class fields`. Sends: `ReportClaim`.
- L75 `class ReportSection(BaseModel)` — Encapsulates reportsection. Receives: `constructor arguments and class fields`. Sends: `ReportSection`.
- L84 `class StructuredReport(BaseModel)` — Encapsulates structuredreport. Receives: `constructor arguments and class fields`. Sends: `StructuredReport`.
- L95 `class ChatReportCreate(BaseModel)` — Encapsulates chatreportcreate. Receives: `constructor arguments and class fields`. Sends: `ChatReportCreate`.
- L102 `def normalize_idempotency_key(cls, value: str | None) -> str | None` — Normalizes idempotency key. Receives: `cls, value: str | None`. Sends: `str | None`.
- L109 `class CaseReportCreate(BaseModel)` — Encapsulates casereportcreate. Receives: `constructor arguments and class fields`. Sends: `CaseReportCreate`.
- L117 `def normalize_idempotency_key(cls, value: str | None) -> str | None` — Normalizes idempotency key. Receives: `cls, value: str | None`. Sends: `str | None`.
- L124 `class ChatReportRead(BaseModel)` — Encapsulates chatreportread. Receives: `constructor arguments and class fields`. Sends: `ChatReportRead`.

### [`backend/app/services/__init__.py`](../../backend/app/services/__init__.py)

Purpose: Backend domain services.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/auth/auth_service.py`](../../backend/app/services/auth/auth_service.py)

Purpose: Authentication service for managing user persistence and token generation.

- L17 `async def get_or_create_oauth_user(db: AsyncSession, profile: OAuthUserProfile) -> User` — Find existing user by (provider, subject_id) or email, or create a new user. Receives: `db: AsyncSession, profile: OAuthUserProfile`. Sends: `User`.
- L57 `async def get_or_create_dev_user(db: AsyncSession, email: str='dev@cybercase.local', name: str='Developer User', avatar_url: str | None=None) -> User` — Create or retrieve a developer user for local development and test runs. Receives: `db: AsyncSession, email: str='dev@cybercase.local', name: str='Developer User', avatar_url: str | None=None`. Sends: `User`.
- L74 `def build_auth_cookie_options() -> dict[str, Any]` — Build standardized Set-Cookie options for JWT session cookie. Receives: `not applicable`. Sends: `dict[str, Any]`.

### [`backend/app/services/auth/dependencies.py`](../../backend/app/services/auth/dependencies.py)

Purpose: FastAPI dependencies for resolving the authenticated user.

- L17 `def _extract_token_from_request(request: Request) -> str | None` — Extract token from Authorization header or HTTP-only auth cookie. Receives: `request: Request`. Sends: `str | None`.
- L32 `async def get_optional_user(request: Request, db: Annotated[AsyncSession, Depends(get_db)]) -> User | None` — Resolve current user if a valid token exists, otherwise return None. Receives: `request: Request, db: Annotated[AsyncSession, Depends(get_db)]`. Sends: `User | None`.
- L59 `async def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User` — Enforce that an authenticated user is present. Receives: `user: Annotated[User | None, Depends(get_optional_user)]`. Sends: `User`.

### [`backend/app/services/auth/jwt.py`](../../backend/app/services/auth/jwt.py)

Purpose: JWT encoding and decoding helpers.

- L13 `def create_access_token(user_id: uuid.UUID, email: str, expires_delta: timedelta | None=None) -> str` — Create a signed JWT access token for the given user. Receives: `user_id: uuid.UUID, email: str, expires_delta: timedelta | None=None`. Sends: `str`.
- L40 `def decode_access_token(token: str) -> dict[str, Any] | None` — Decode and validate a JWT access token. Receives: `token: str`. Sends: `dict[str, Any] | None`.

### [`backend/app/services/auth/oauth_clients.py`](../../backend/app/services/auth/oauth_clients.py)

Purpose: OAuth client adapters for Google, GitHub, and OIDC providers.

- L13 `class OAuthUserProfile` — Encapsulates oauthuserprofile. Receives: `constructor arguments and class fields`. Sends: `OAuthUserProfile`.
- L21 `class OAuthProviderClient` — Base class for OAuth identity providers. Receives: `constructor arguments and class fields`. Sends: `OAuthProviderClient`.
- L24 `def get_authorization_url(self, state: str) -> str` — Retrieves authorization url. Receives: `self, state: str`. Sends: `str`.
- L27 `async def exchange_code_for_profile(self, code: str) -> OAuthUserProfile` — Implements exchange code for profile. Receives: `self, code: str`. Sends: `OAuthUserProfile`.
- L31 `class GoogleOAuthClient(OAuthProviderClient)` — Encapsulates googleoauthclient. Receives: `constructor arguments and class fields`. Sends: `GoogleOAuthClient`.
- L36 `def __init__(self, client_id: str | None=None, client_secret: str | None=None, redirect_uri: str | None=None)` — Implements init. Receives: `self, client_id: str | None=None, client_secret: str | None=None, redirect_uri: str | None=None`. Sends: `inferred or None`.
- L48 `def get_authorization_url(self, state: str) -> str` — Retrieves authorization url. Receives: `self, state: str`. Sends: `str`.
- L60 `async def exchange_code_for_profile(self, code: str) -> OAuthUserProfile` — Implements exchange code for profile. Receives: `self, code: str`. Sends: `OAuthUserProfile`.
- L97 `class GitHubOAuthClient(OAuthProviderClient)` — Encapsulates githuboauthclient. Receives: `constructor arguments and class fields`. Sends: `GitHubOAuthClient`.
- L103 `def __init__(self, client_id: str | None=None, client_secret: str | None=None, redirect_uri: str | None=None)` — Implements init. Receives: `self, client_id: str | None=None, client_secret: str | None=None, redirect_uri: str | None=None`. Sends: `inferred or None`.
- L115 `def get_authorization_url(self, state: str) -> str` — Retrieves authorization url. Receives: `self, state: str`. Sends: `str`.
- L124 `async def exchange_code_for_profile(self, code: str) -> OAuthUserProfile` — Implements exchange code for profile. Receives: `self, code: str`. Sends: `OAuthUserProfile`.
- L171 `def get_oauth_client(provider: str) -> OAuthProviderClient` — Retrieves oauth client. Receives: `provider: str`. Sends: `OAuthProviderClient`.

### [`backend/app/services/auth/passwords.py`](../../backend/app/services/auth/passwords.py)

Purpose: Owns passwords behavior for the backend runtime.

- L5 `def hash_password(password: str) -> str` — Implements hash password. Receives: `password: str`. Sends: `str`.
- L11 `def verify_password(password: str, stored: str) -> bool` — Validates password. Receives: `password: str, stored: str`. Sends: `bool`.

### [`backend/app/services/auth/request_guard.py`](../../backend/app/services/auth/request_guard.py)

Purpose: Owns request guard behavior for the backend runtime.

- L5 `async def guard_browser_request(request, call_next)` — Implements guard browser request. Receives: `request, call_next`. Sends: `inferred or None`.

### [`backend/app/services/case_analysis/__init__.py`](../../backend/app/services/case_analysis/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/case_analysis/case_analysis_executor.py`](../../backend/app/services/case_analysis/case_analysis_executor.py)

Purpose: Owns case analysis executor behavior for the backend runtime.

- L35 `class MainCaseAnalysisService` — Run internal analysis without retrieval, persistence, or state mutation. Receives: `constructor arguments and class fields`. Sends: `MainCaseAnalysisService`.
- L38 `def __init__(self, *, client: httpx.AsyncClient | None=None) -> None` — Implements init. Receives: `self, *, client: httpx.AsyncClient | None=None`. Sends: `None`.
- L41 `async def analyze(self, *, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object) -> CaseAnalysisResult` — Analyze defensive snapshots of Case Narrative and retrieval context. Receives: `self, *, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object`. Sends: `CaseAnalysisResult`.
- L162 `async def _post(client: httpx.AsyncClient, messages_url: str, headers: dict[str, str], request_payload: dict[str, object]) -> httpx.Response` — Implements post. Receives: `client: httpx.AsyncClient, messages_url: str, headers: dict[str, str], request_payload: dict[str, object]`. Sends: `httpx.Response`.
- L186 `async def request_case_analysis(*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object, client: httpx.AsyncClient | None=None) -> CaseAnalysisResult` — Implements request case analysis. Receives: `*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, user_message: object, client: httpx.AsyncClient | None=None`. Sends: `CaseAnalysisResult`.

### [`backend/app/services/case_analysis/case_analysis_prompt_builder.py`](../../backend/app/services/case_analysis/case_analysis_prompt_builder.py)

Purpose: Owns case analysis prompt builder behavior for the backend runtime.

- L22 `def build_case_analysis_prompt(*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, response_language: ResponseLanguage) -> str` — Builds case analysis prompt. Receives: `*, mode: AnalysisMode, raw_evidence: str, analysis_context: dict[str, object] | None, question: str | None, response_language: ResponseLanguage`. Sends: `str`.
- L82 `def _validate_analysis_request(mode: object, question: object) -> tuple[AnalysisMode, str | None]` — Validates analysis request. Receives: `mode: object, question: object`. Sends: `tuple[AnalysisMode, str | None]`.
- L106 `def build_overflow_case_context(*, payload: dict[str, object], prefix: str, suffix: str, token_budget: int) -> str` — Build bounded case context when the full prompt exceeds token budget. Receives: `*, payload: dict[str, object], prefix: str, suffix: str, token_budget: int`. Sends: `str`.
- L231 `def _separate_analysis_context(analysis_context: dict[str, object] | None) -> tuple[list[str], dict[str, object] | None]` — Implements separate analysis context. Receives: `analysis_context: dict[str, object] | None`. Sends: `tuple[list[str], dict[str, object] | None]`.
- L268 `def _dump(value: object) -> str` — Implements dump. Receives: `value: object`. Sends: `str`.

### [`backend/app/services/case_analysis/case_analysis_prompt_config.py`](../../backend/app/services/case_analysis/case_analysis_prompt_config.py)

Purpose: Owns case analysis prompt config behavior for the backend runtime.

- L65 `class CaseAnalysisFailure(Exception)` — Encapsulates caseanalysisfailure. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisFailure`.
- L66 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.

### [`backend/app/services/case_analysis/case_analysis_response_parser.py`](../../backend/app/services/case_analysis/case_analysis_response_parser.py)

Purpose: Owns case analysis response parser behavior for the backend runtime.

- L38 `def parse_case_analysis_response(response: httpx.Response, *, source_message_ids: set[str], analysis_context: Mapping[str, object], analysis_mode: AnalysisMode, evidence_sha256: str) -> CaseAnalysisResult` — Parses case analysis response. Receives: `response: httpx.Response, *, source_message_ids: set[str], analysis_context: Mapping[str, object], analysis_mode: AnalysisMode, evidence_sha256: str`. Sends: `CaseAnalysisResult`.
- L140 `def _retrieval_context_id(analysis_context: Mapping[str, object]) -> str | None` — Implements retrieval context id. Receives: `analysis_context: Mapping[str, object]`. Sends: `str | None`.

### [`backend/app/services/case_analysis/case_analysis_response_utils.py`](../../backend/app/services/case_analysis/case_analysis_response_utils.py)

Purpose: Owns case analysis response utils behavior for the backend runtime.

- L10 `def _extract_visible_text(payload: Mapping[str, object]) -> str` — Extract visible assistant text across supported provider response shapes. Receives: `payload: Mapping[str, object]`. Sends: `str`.
- L36 `def _extract_text_value(value: object) -> str` — Extracts text value. Receives: `value: object`. Sends: `str`.
- L65 `def _log_response_shape(status_code: int, payload: Mapping[str, object]) -> None` — Log provider shape metadata without logging prompts or answer text. Receives: `status_code: int, payload: Mapping[str, object]`. Sends: `None`.
- L90 `def _strip_trailing_ocr_boilerplate(text: str) -> str` — Strip default trailing OCR metadata disclaimers emitted by provider. Receives: `text: str`. Sends: `str`.

### [`backend/app/services/case_analysis/case_native_analysis.py`](../../backend/app/services/case_analysis/case_native_analysis.py)

Purpose: Owns case native analysis behavior for the backend runtime.

- L42 `async def analyze_case_native(*, raw_evidence: str, analysis_context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, mode: str='case_overview', question: str | None=None, client: httpx.AsyncClient | None=None) -> CaseAnalysisResult` — Implements analyze case native. Receives: `*, raw_evidence: str, analysis_context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, mode: str='case_overview', question: str | None=None, client: httpx.AsyncClient | None=None`. Sends: `CaseAnalysisResult`.
- L90 `async def _run(raw_evidence: str, context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, receipt: dict[str, object], mode: str, question: str | None) -> CaseAnalysisResult` — Executes run. Receives: `raw_evidence: str, context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, receipt: dict[str, object], mode: str, question: str | None`. Sends: `CaseAnalysisResult`.
- L123 `async def _run_claim_anchored(raw_evidence: str, context: dict[str, object], language: str, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, digest: str, receipt: dict[str, object]) -> CaseAnalysisResult` — Executes claim anchored. Receives: `raw_evidence: str, context: dict[str, object], language: str, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, digest: str, receipt: dict[str, object]`. Sends: `CaseAnalysisResult`.
- L194 `async def _run_raw_direct(raw_evidence: str, context: dict[str, object], language: str, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, digest: str, receipt: dict[str, object], mode: str, question: str | None) -> CaseAnalysisResult` — Executes raw direct. Receives: `raw_evidence: str, context: dict[str, object], language: str, config: AnalysisPipelineConfig, sources: tuple[NativeAdmittedSource, ...], client: httpx.AsyncClient, digest: str, receipt: dict[str, object], mode: str, question: str | None`. Sends: `CaseAnalysisResult`.
- L239 `async def _stage(client: httpx.AsyncClient, config: AnalysisPipelineConfig, stage: str, system: str, content: dict[str, object], schema: type, receipt: dict[str, object])` — Implements stage. Receives: `client: httpx.AsyncClient, config: AnalysisPipelineConfig, stage: str, system: str, content: dict[str, object], schema: type, receipt: dict[str, object]`. Sends: `inferred or None`.

### [`backend/app/services/case_analysis/case_native_binding.py`](../../backend/app/services/case_analysis/case_native_binding.py)

Purpose: Owns case native binding behavior for the backend runtime.

- L19 `class NativeBoundSpan` — Encapsulates nativeboundspan. Receives: `constructor arguments and class fields`. Sends: `NativeBoundSpan`.
- L28 `class NativeBoundClaim` — Encapsulates nativeboundclaim. Receives: `constructor arguments and class fields`. Sends: `NativeBoundClaim`.
- L34 `def bind_native_claims(extracted: NativeExtractedClaims, sources: tuple[NativeAdmittedSource, ...], document_context: object) -> tuple[NativeBoundClaim, ...]` — Implements bind native claims. Receives: `extracted: NativeExtractedClaims, sources: tuple[NativeAdmittedSource, ...], document_context: object`. Sends: `tuple[NativeBoundClaim, ...]`.

### [`backend/app/services/case_analysis/case_native_contracts.py`](../../backend/app/services/case_analysis/case_native_contracts.py)

Purpose: Owns case native contracts behavior for the backend runtime.

- L20 `class NativeCaseEvidenceCitation(BaseModel)` — Encapsulates nativecaseevidencecitation. Receives: `constructor arguments and class fields`. Sends: `NativeCaseEvidenceCitation`.
- L32 `def normalize_text(cls, value: str | None) -> str | None` — Normalizes text. Receives: `cls, value: str | None`. Sends: `str | None`.
- L37 `def unique_page_numbers(cls, value: list[int]) -> list[int]` — Implements unique page numbers. Receives: `cls, value: list[int]`. Sends: `list[int]`.
- L45 `def validate_document_locator(self) -> 'NativeCaseEvidenceCitation'` — Validates document locator. Receives: `self`. Sends: `'NativeCaseEvidenceCitation'`.
- L58 `class NativeClaimCandidate(BaseModel)` — Encapsulates nativeclaimcandidate. Receives: `constructor arguments and class fields`. Sends: `NativeClaimCandidate`.
- L68 `class NativeQuoteCandidate(BaseModel)` — Encapsulates nativequotecandidate. Receives: `constructor arguments and class fields`. Sends: `NativeQuoteCandidate`.
- L78 `def require_trimmed_text(cls, value: str) -> str` — Implements require trimmed text. Receives: `cls, value: str`. Sends: `str`.
- L85 `class NativeExtractedClaims(BaseModel)` — Encapsulates nativeextractedclaims. Receives: `constructor arguments and class fields`. Sends: `NativeExtractedClaims`.
- L91 `class NativeGeneratedUnit(BaseModel)` — Encapsulates nativegeneratedunit. Receives: `constructor arguments and class fields`. Sends: `NativeGeneratedUnit`.
- L99 `def normalize_text(cls, value: str) -> str` — Normalizes text. Receives: `cls, value: str`. Sends: `str`.
- L106 `class NativeGeneratedSummary(BaseModel)` — Encapsulates nativegeneratedsummary. Receives: `constructor arguments and class fields`. Sends: `NativeGeneratedSummary`.
- L112 `class NativeCaseAnalysisClaim(BaseModel)` — Encapsulates nativecaseanalysisclaim. Receives: `constructor arguments and class fields`. Sends: `NativeCaseAnalysisClaim`.
- L131 `def normalize_text(cls, value: str | None) -> str | None` — Normalizes text. Receives: `cls, value: str | None`. Sends: `str | None`.
- L141 `def unique_source_ids(cls, value: list[str]) -> list[str]` — Implements unique source ids. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L148 `class NativeCaseAnalysisGap(BaseModel)` — Encapsulates nativecaseanalysisgap. Receives: `constructor arguments and class fields`. Sends: `NativeCaseAnalysisGap`.
- L161 `class NativeMitreAssociation(BaseModel)` — Encapsulates nativemitreassociation. Receives: `constructor arguments and class fields`. Sends: `NativeMitreAssociation`.
- L172 `class NativeCaseAnalysisTrace(BaseModel)` — Encapsulates nativecaseanalysistrace. Receives: `constructor arguments and class fields`. Sends: `NativeCaseAnalysisTrace`.
- L188 `class NativeProviderCaseAnalysis(BaseModel)` — Encapsulates nativeprovidercaseanalysis. Receives: `constructor arguments and class fields`. Sends: `NativeProviderCaseAnalysis`.
- L200 `class NativeCaseAnalysisFailureMetadata(BaseModel)` — Encapsulates nativecaseanalysisfailuremetadata. Receives: `constructor arguments and class fields`. Sends: `NativeCaseAnalysisFailureMetadata`.
- L212 `class NativeCaseAnalysisResult` — Encapsulates nativecaseanalysisresult. Receives: `constructor arguments and class fields`. Sends: `NativeCaseAnalysisResult`.

### [`backend/app/services/case_analysis/case_native_prompts.py`](../../backend/app/services/case_analysis/case_native_prompts.py)

Purpose: Owns case native prompts behavior for the backend runtime.

- L48 `def native_system_prompt() -> str` — Implements native system prompt. Receives: `not applicable`. Sends: `str`.
- L60 `def native_generation_input(claims: tuple[NativeBoundClaim, ...], language: str) -> dict[str, object]` — Implements native generation input. Receives: `claims: tuple[NativeBoundClaim, ...], language: str`. Sends: `dict[str, object]`.
- L87 `def build_native_direct_prompt(*, mode: str, raw_evidence: str, analysis_context: dict[str, object], question: str | None, response_language: str) -> str` — Builds native direct prompt. Receives: `*, mode: str, raw_evidence: str, analysis_context: dict[str, object], question: str | None, response_language: str`. Sends: `str`.

### [`backend/app/services/case_analysis/case_native_selection.py`](../../backend/app/services/case_analysis/case_native_selection.py)

Purpose: Owns case native selection behavior for the backend runtime.

- L13 `class NativeSelection` — Encapsulates nativeselection. Receives: `constructor arguments and class fields`. Sends: `NativeSelection`.
- L18 `def assign_native_ids(claims: tuple[NativeBoundClaim, ...]) -> tuple[NativeBoundClaim, ...]` — Implements assign native ids. Receives: `claims: tuple[NativeBoundClaim, ...]`. Sends: `tuple[NativeBoundClaim, ...]`.
- L31 `def select_native_claims(claims: tuple[NativeBoundClaim, ...], *, source_ids: tuple[str, ...], max_claims: int, fits: Callable[[tuple[NativeBoundClaim, ...]], bool]) -> NativeSelection` — Extracts native claims. Receives: `claims: tuple[NativeBoundClaim, ...], *, source_ids: tuple[str, ...], max_claims: int, fits: Callable[[tuple[NativeBoundClaim, ...]], bool]`. Sends: `NativeSelection`.

### [`backend/app/services/case_analysis/case_native_source.py`](../../backend/app/services/case_analysis/case_native_source.py)

Purpose: Owns case native source behavior for the backend runtime.

- L11 `class NativeAdmittedSource` — Encapsulates nativeadmittedsource. Receives: `constructor arguments and class fields`. Sends: `NativeAdmittedSource`.
- L18 `def build_native_source_registry(context: Mapping[str, object]) -> tuple[NativeAdmittedSource, ...]` — Builds native source registry. Receives: `context: Mapping[str, object]`. Sends: `tuple[NativeAdmittedSource, ...]`.

### [`backend/app/services/case_analysis/case_native_validation.py`](../../backend/app/services/case_analysis/case_native_validation.py)

Purpose: Owns case native validation behavior for the backend runtime.

- L18 `def validate_native_trace(trace: NativeCaseAnalysisTrace, sources: tuple[NativeAdmittedSource, ...], document_context: object, mitre_table: object=None) -> NativeCaseAnalysisTrace` — Validates native trace. Receives: `trace: NativeCaseAnalysisTrace, sources: tuple[NativeAdmittedSource, ...], document_context: object, mitre_table: object=None`. Sends: `NativeCaseAnalysisTrace`.
- L66 `def _validate_claim(claim: NativeCaseAnalysisClaim, registry: dict[str, NativeAdmittedSource], document_context: object) -> NativeCaseAnalysisClaim` — Validates claim. Receives: `claim: NativeCaseAnalysisClaim, registry: dict[str, NativeAdmittedSource], document_context: object`. Sends: `NativeCaseAnalysisClaim`.
- L118 `def _normalize_citations(citations: list[NativeCaseEvidenceCitation], allowed_ids: set[str], role: str, registry: dict[str, NativeAdmittedSource], document_context: object) -> list[NativeCaseEvidenceCitation]` — Normalizes citations. Receives: `citations: list[NativeCaseEvidenceCitation], allowed_ids: set[str], role: str, registry: dict[str, NativeAdmittedSource], document_context: object`. Sends: `list[NativeCaseEvidenceCitation]`.
- L163 `def _admitted_technique_ids(value: object) -> set[str]` — Implements admitted technique ids. Receives: `value: object`. Sends: `set[str]`.

### [`backend/app/services/case_analysis/citation_contracts.py`](../../backend/app/services/case_analysis/citation_contracts.py)

Purpose: Owns citation contracts behavior for the backend runtime.

- L4 `class AnalysisEvidenceCitation(BaseModel)` — Encapsulates analysisevidencecitation. Receives: `constructor arguments and class fields`. Sends: `AnalysisEvidenceCitation`.
- L15 `def normalize_text(cls, value: str | None) -> str | None` — Normalizes text. Receives: `cls, value: str | None`. Sends: `str | None`.
- L20 `def unique_page_numbers(cls, value: list[int]) -> list[int]` — Implements unique page numbers. Receives: `cls, value: list[int]`. Sends: `list[int]`.
- L28 `def validate_document_locator(self) -> 'AnalysisEvidenceCitation'` — Validates document locator. Receives: `self`. Sends: `'AnalysisEvidenceCitation'`.

### [`backend/app/services/case_analysis/claim_anchored/__init__.py`](../../backend/app/services/case_analysis/claim_anchored/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/case_analysis/claim_anchored/assembly.py`](../../backend/app/services/case_analysis/claim_anchored/assembly.py)

Purpose: Owns assembly behavior for the backend runtime.

- L10 `def assemble_trace(generated: GeneratedSummary, claims: tuple[BoundClaim, ...], evidence_sha256: str, source_ids: set[str]) -> AnalysisTraceV3` — Builds trace. Receives: `generated: GeneratedSummary, claims: tuple[BoundClaim, ...], evidence_sha256: str, source_ids: set[str]`. Sends: `AnalysisTraceV3`.

### [`backend/app/services/case_analysis/claim_anchored/binder.py`](../../backend/app/services/case_analysis/claim_anchored/binder.py)

Purpose: Owns binder behavior for the backend runtime.

- L18 `def bind_claims(extracted: ExtractedClaims, sources: tuple[AdmittedSource, ...], document_context: object) -> tuple[BoundClaim, ...]` — Implements bind claims. Receives: `extracted: ExtractedClaims, sources: tuple[AdmittedSource, ...], document_context: object`. Sends: `tuple[BoundClaim, ...]`.

### [`backend/app/services/case_analysis/claim_anchored/contracts.py`](../../backend/app/services/case_analysis/claim_anchored/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L15 `class StrictRecord(BaseModel)` — Encapsulates strictrecord. Receives: `constructor arguments and class fields`. Sends: `StrictRecord`.
- L19 `class QuoteCandidate(StrictRecord)` — Encapsulates quotecandidate. Receives: `constructor arguments and class fields`. Sends: `QuoteCandidate`.
- L26 `def require_literal_quote(cls, value: str) -> str` — Implements require literal quote. Receives: `cls, value: str`. Sends: `str`.
- L32 `class ClaimCandidate(StrictRecord)` — Encapsulates claimcandidate. Receives: `constructor arguments and class fields`. Sends: `ClaimCandidate`.
- L40 `class ExtractedClaims(StrictRecord)` — Encapsulates extractedclaims. Receives: `constructor arguments and class fields`. Sends: `ExtractedClaims`.
- L44 `class BoundSpan(StrictRecord)` — Encapsulates boundspan. Receives: `constructor arguments and class fields`. Sends: `BoundSpan`.
- L53 `class BoundClaim(StrictRecord)` — Encapsulates boundclaim. Receives: `constructor arguments and class fields`. Sends: `BoundClaim`.
- L59 `class GeneratedUnit(StrictRecord)` — Encapsulates generatedunit. Receives: `constructor arguments and class fields`. Sends: `GeneratedUnit`.
- L65 `def require_text(cls, value: str) -> str` — Implements require text. Receives: `cls, value: str`. Sends: `str`.
- L71 `class GeneratedSummary(StrictRecord)` — Encapsulates generatedsummary. Receives: `constructor arguments and class fields`. Sends: `GeneratedSummary`.
- L76 `class Selection` — Encapsulates selection. Receives: `constructor arguments and class fields`. Sends: `Selection`.
- L81 `class SemanticVerifier(Protocol)` — Encapsulates semanticverifier. Receives: `constructor arguments and class fields`. Sends: `SemanticVerifier`.
- L82 `async def check_claims(self, claims: tuple[BoundClaim, ...]) -> None` — Validates claims. Receives: `self, claims: tuple[BoundClaim, ...]`. Sends: `None`.
- L84 `async def check_summary(self, summary: GeneratedSummary, claims: tuple[BoundClaim, ...]) -> None` — Validates summary. Receives: `self, summary: GeneratedSummary, claims: tuple[BoundClaim, ...]`. Sends: `None`.

### [`backend/app/services/case_analysis/claim_anchored/failure.py`](../../backend/app/services/case_analysis/claim_anchored/failure.py)

Purpose: Owns failure behavior for the backend runtime.

- L6 `class ClaimAnchoredFailure(CaseAnalysisFailure)` — Encapsulates claimanchoredfailure. Receives: `constructor arguments and class fields`. Sends: `ClaimAnchoredFailure`.
- L7 `def __init__(self, code: str, message: str, receipt: dict[str, object] | None=None)` — Implements init. Receives: `self, code: str, message: str, receipt: dict[str, object] | None=None`. Sends: `inferred or None`.

### [`backend/app/services/case_analysis/claim_anchored/prompts.py`](../../backend/app/services/case_analysis/claim_anchored/prompts.py)

Purpose: Owns prompts behavior for the backend runtime.

- L33 `def generation_input(claims: tuple[BoundClaim, ...], language: str) -> dict[str, object]` — Implements generation input. Receives: `claims: tuple[BoundClaim, ...], language: str`. Sends: `dict[str, object]`.

### [`backend/app/services/case_analysis/claim_anchored/provider.py`](../../backend/app/services/case_analysis/claim_anchored/provider.py)

Purpose: Owns provider behavior for the backend runtime.

- L30 `def encoding()` — Implements encoding. Receives: `not applicable`. Sends: `inferred or None`.
- L34 `def token_count(value: object) -> int` — Implements token count. Receives: `value: object`. Sends: `int`.
- L39 `def stage_payload(config: AnalysisPipelineConfig, system: str, content: dict[str, object], schema: type[BaseModel]) -> dict[str, object]` — Implements stage payload. Receives: `config: AnalysisPipelineConfig, system: str, content: dict[str, object], schema: type[BaseModel]`. Sends: `dict[str, object]`.
- L65 `def input_budget(config: AnalysisPipelineConfig) -> int` — Implements input budget. Receives: `config: AnalysisPipelineConfig`. Sends: `int`.
- L72 `def resolve_target(config: AnalysisPipelineConfig) -> CoreLlmTarget` — Implements resolve target. Receives: `config: AnalysisPipelineConfig`. Sends: `CoreLlmTarget`.
- L77 `async def request_stage(*, client: httpx.AsyncClient, target: CoreLlmTarget, config: AnalysisPipelineConfig, stage: str, system: str, content: dict[str, object], schema: type[Record], calls: list[dict[str, object]], checkpoint: Callable[[], Awaitable[None]] | None=None) -> Record` — Implements request stage. Receives: `*, client: httpx.AsyncClient, target: CoreLlmTarget, config: AnalysisPipelineConfig, stage: str, system: str, content: dict[str, object], schema: type[Record], calls: list[dict[str, object]], checkpoint: Callable[[], Awaitable[None]] | None=None`. Sends: `Record`.

### [`backend/app/services/case_analysis/claim_anchored/selector.py`](../../backend/app/services/case_analysis/claim_anchored/selector.py)

Purpose: Owns selector behavior for the backend runtime.

- L9 `def assign_ids(claims: tuple[BoundClaim, ...]) -> tuple[BoundClaim, ...]` — Implements assign ids. Receives: `claims: tuple[BoundClaim, ...]`. Sends: `tuple[BoundClaim, ...]`.
- L20 `def select_claims(claims: tuple[BoundClaim, ...], *, source_ids: tuple[str, ...], max_claims: int, fits: Callable[[tuple[BoundClaim, ...]], bool]) -> Selection` — Extracts claims. Receives: `claims: tuple[BoundClaim, ...], *, source_ids: tuple[str, ...], max_claims: int, fits: Callable[[tuple[BoundClaim, ...]], bool]`. Sends: `Selection`.

### [`backend/app/services/case_analysis/claim_anchored/service.py`](../../backend/app/services/case_analysis/claim_anchored/service.py)

Purpose: Owns service behavior for the backend runtime.

- L44 `async def analyze_claim_anchored(*, raw_evidence: str, analysis_context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, client: httpx.AsyncClient | None=None, verifier: SemanticVerifier | None=None) -> CaseAnalysisResult` — Implements analyze claim anchored. Receives: `*, raw_evidence: str, analysis_context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, client: httpx.AsyncClient | None=None, verifier: SemanticVerifier | None=None`. Sends: `CaseAnalysisResult`.
- L95 `async def _analyze(raw_evidence: str, context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, client: httpx.AsyncClient, verifier: SemanticVerifier | None, receipt: dict[str, object]) -> CaseAnalysisResult` — Implements analyze. Receives: `raw_evidence: str, context: dict[str, object], user_message: object, config: AnalysisPipelineConfig, client: httpx.AsyncClient, verifier: SemanticVerifier | None, receipt: dict[str, object]`. Sends: `CaseAnalysisResult`.
- L107 `async def checkpoint() -> None` — Implements checkpoint. Receives: `not applicable`. Sends: `None`.

### [`backend/app/services/case_analysis/claim_anchored/source_registry.py`](../../backend/app/services/case_analysis/claim_anchored/source_registry.py)

Purpose: Owns source registry behavior for the backend runtime.

- L9 `class AdmittedSource` — Encapsulates admittedsource. Receives: `constructor arguments and class fields`. Sends: `AdmittedSource`.
- L15 `def build_source_registry(context: Mapping[str, object]) -> tuple[AdmittedSource, ...]` — Builds source registry. Receives: `context: Mapping[str, object]`. Sends: `tuple[AdmittedSource, ...]`.

### [`backend/app/services/case_analysis/contracts.py`](../../backend/app/services/case_analysis/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L43 `class AnalysisClaim(BaseModel)` — Encapsulates analysisclaim. Receives: `constructor arguments and class fields`. Sends: `AnalysisClaim`.
- L54 `def normalize_text(cls, value: str) -> str` — Normalizes text. Receives: `cls, value: str`. Sends: `str`.
- L59 `def unique_source_ids(cls, value: list[str]) -> list[str]` — Implements unique source ids. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L68 `class MitreAssociation(BaseModel)` — Encapsulates mitreassociation. Receives: `constructor arguments and class fields`. Sends: `MitreAssociation`.
- L79 `class AnalysisClaimV3(BaseModel)` — Encapsulates analysisclaimv3. Receives: `constructor arguments and class fields`. Sends: `AnalysisClaimV3`.
- L102 `def normalize_optional_text(cls, value: str | None) -> str | None` — Normalizes optional text. Receives: `cls, value: str | None`. Sends: `str | None`.
- L114 `def unique_evidence_source_ids(cls, value: list[str]) -> list[str]` — Implements unique evidence source ids. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L123 `class AnalysisGapV3(BaseModel)` — Encapsulates analysisgapv3. Receives: `constructor arguments and class fields`. Sends: `AnalysisGapV3`.
- L137 `def normalize_gap_text(cls, value: str) -> str` — Normalizes gap text. Receives: `cls, value: str`. Sends: `str`.
- L145 `def unique_affected_claim_ids(cls, value: list[str]) -> list[str]` — Implements unique affected claim ids. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L154 `class AnalysisTraceV3(BaseModel)` — Encapsulates analysistracev3. Receives: `constructor arguments and class fields`. Sends: `AnalysisTraceV3`.
- L171 `def normalize_summary(cls, value: str) -> str` — Normalizes summary. Receives: `cls, value: str`. Sends: `str`.
- L178 `class ProviderAnalysisClaimV3(AnalysisClaimV3)` — Encapsulates provideranalysisclaimv3. Receives: `constructor arguments and class fields`. Sends: `ProviderAnalysisClaimV3`.
- L182 `class ProviderMitreAssociation(MitreAssociation)` — Encapsulates providermitreassociation. Receives: `constructor arguments and class fields`. Sends: `ProviderMitreAssociation`.
- L186 `class ProviderCaseAnalysisV3(BaseModel)` — Encapsulates providercaseanalysisv3. Receives: `constructor arguments and class fields`. Sends: `ProviderCaseAnalysisV3`.
- L199 `class AnalysisTrace(BaseModel)` — Historical v2 analysis trace model retained strictly for read-only deserialization. Receives: `constructor arguments and class fields`. Sends: `AnalysisTrace`.
- L213 `class AnalysisTraceFailureMetadata(BaseModel)` — Encapsulates analysistracefailuremetadata. Receives: `constructor arguments and class fields`. Sends: `AnalysisTraceFailureMetadata`.
- L221 `class AnalysisTraceV3FailureMetadata(BaseModel)` — Encapsulates analysistracev3failuremetadata. Receives: `constructor arguments and class fields`. Sends: `AnalysisTraceV3FailureMetadata`.
- L238 `class CaseAnalysisResult` — Encapsulates caseanalysisresult. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisResult`.
- L255 `def read_analysis_trace(payload: object) -> ReadableAnalysisTrace` — Retrieves analysis trace. Receives: `payload: object`. Sends: `ReadableAnalysisTrace`.

### [`backend/app/services/case_analysis/evidence_quote_resolver.py`](../../backend/app/services/case_analysis/evidence_quote_resolver.py)

Purpose: Owns evidence quote resolver behavior for the backend runtime.

- L5 `def resolve_document_locator(source_id: str, quote: str, content: str, document_context: object, *, require_complete_coverage: bool=False) -> dict[str, object]` — Implements resolve document locator. Receives: `source_id: str, quote: str, content: str, document_context: object, *, require_complete_coverage: bool=False`. Sends: `dict[str, object]`.
- L31 `def _documents_for_source(source_id: str, context: object) -> list[Mapping[str, object]]` — Implements documents for source. Receives: `source_id: str, context: object`. Sends: `list[Mapping[str, object]]`.
- L51 `def _locator_for_document(document: Mapping[str, object], content: str, occurrences: list[int], quote_length: int, require_complete_coverage: bool) -> tuple[str, str, tuple[int, ...]] | None` — Implements locator for document. Receives: `document: Mapping[str, object], content: str, occurrences: list[int], quote_length: int, require_complete_coverage: bool`. Sends: `tuple[str, str, tuple[int, ...]] | None`.
- L84 `def _covers_quote(spans: list[tuple[int, int, int]], start: int, end: int) -> bool` — Implements covers quote. Receives: `spans: list[tuple[int, int, int]], start: int, end: int`. Sends: `bool`.
- L99 `def _valid_page_spans(value: object, content: str) -> list[tuple[int, int, int]]` — Implements valid page spans. Receives: `value: object, content: str`. Sends: `list[tuple[int, int, int]]`.
- L132 `def quote_occurrences(content: str, quote: str) -> list[int]` — Implements quote occurrences. Receives: `content: str, quote: str`. Sends: `list[int]`.

### [`backend/app/services/case_analysis/gap_assembly.py`](../../backend/app/services/case_analysis/gap_assembly.py)

Purpose: Owns gap assembly behavior for the backend runtime.

- L45 `def assemble_claim_linked_gaps(trace: AnalysisTraceV3, gap_analysis: GapAnalysis, *, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3` — Builds claim linked gaps. Receives: `trace: AnalysisTraceV3, gap_analysis: GapAnalysis, *, source_message_ids: set[str], mitre_table: object=None`. Sends: `AnalysisTraceV3`.
- L78 `def enrich_case_analysis_result(result: CaseAnalysisResult, gap_analysis: GapAnalysis | None, *, source_message_ids: set[str], mitre_table: object=None) -> CaseAnalysisResult` — Implements enrich case analysis result. Receives: `result: CaseAnalysisResult, gap_analysis: GapAnalysis | None, *, source_message_ids: set[str], mitre_table: object=None`. Sends: `CaseAnalysisResult`.
- L118 `def _affected_claim_ids(gap: GapItem, claims: list[AnalysisClaimV3]) -> list[str]` — Implements affected claim ids. Receives: `gap: GapItem, claims: list[AnalysisClaimV3]`. Sends: `list[str]`.
- L137 `def _claim_linking_text(claim: AnalysisClaimV3) -> str` — Implements claim linking text. Receives: `claim: AnalysisClaimV3`. Sends: `str`.
- L144 `def _text_matches(gap_text: str, gap_tokens: set[str], claim_text: str) -> bool` — Implements text matches. Receives: `gap_text: str, gap_tokens: set[str], claim_text: str`. Sends: `bool`.
- L156 `def _normalized_text(value: str) -> str` — Implements normalized text. Receives: `value: str`. Sends: `str`.
- L161 `def _tokens(value: str) -> set[str]` — Implements tokens. Receives: `value: str`. Sends: `set[str]`.
- L169 `def _validate_unchanged_trace_bindings(original: AnalysisTraceV3, enriched: AnalysisTraceV3) -> None` — Validates unchanged trace bindings. Receives: `original: AnalysisTraceV3, enriched: AnalysisTraceV3`. Sends: `None`.

### [`backend/app/services/case_analysis/mitre_applicability_contracts.py`](../../backend/app/services/case_analysis/mitre_applicability_contracts.py)

Purpose: Owns mitre applicability contracts behavior for the backend runtime.

- L12 `class ProviderMitreApplicability(BaseModel)` — Encapsulates providermitreapplicability. Receives: `constructor arguments and class fields`. Sends: `ProviderMitreApplicability`.
- L21 `def normalize_source_ids(cls, value: list[str]) -> list[str]` — Normalizes source ids. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L31 `def normalize_trigger_text(cls, value: list[str]) -> list[str]` — Normalizes trigger text. Receives: `cls, value: list[str]`. Sends: `list[str]`.
- L40 `class MitreApplicabilityRecord(BaseModel)` — Encapsulates mitreapplicabilityrecord. Receives: `constructor arguments and class fields`. Sends: `MitreApplicabilityRecord`.
- L50 `def validate_routing_record(self) -> 'MitreApplicabilityRecord'` — Validates routing record. Receives: `self`. Sends: `'MitreApplicabilityRecord'`.
- L60 `def skipped_mitre_applicability(failure_code: str | None=None) -> MitreApplicabilityRecord` — Implements skipped mitre applicability. Receives: `failure_code: str | None=None`. Sends: `MitreApplicabilityRecord`.

### [`backend/app/services/case_analysis/mitre_applicability_gate.py`](../../backend/app/services/case_analysis/mitre_applicability_gate.py)

Purpose: Owns mitre applicability gate behavior for the backend runtime.

- L38 `class MitreApplicabilityFailure(Exception)` — Encapsulates mitreapplicabilityfailure. Receives: `constructor arguments and class fields`. Sends: `MitreApplicabilityFailure`.
- L39 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L44 `class MitreApplicabilityGate` — Encapsulates mitreapplicabilitygate. Receives: `constructor arguments and class fields`. Sends: `MitreApplicabilityGate`.
- L45 `def __init__(self, *, client: httpx.AsyncClient | None=None) -> None` — Implements init. Receives: `self, *, client: httpx.AsyncClient | None=None`. Sends: `None`.
- L48 `async def evaluate(self, evidence_sources: Sequence[RawEvidenceSource]) -> MitreApplicabilityRecord` — Implements evaluate. Receives: `self, evidence_sources: Sequence[RawEvidenceSource]`. Sends: `MitreApplicabilityRecord`.
- L101 `async def _post(client: httpx.AsyncClient, url: str, headers: dict[str, str], payload: dict[str, object]) -> httpx.Response` — Implements post. Receives: `client: httpx.AsyncClient, url: str, headers: dict[str, str], payload: dict[str, object]`. Sends: `httpx.Response`.
- L121 `async def evaluate_mitre_applicability(*, source_run_id: UUID, evidence_sources: Sequence[RawEvidenceSource], gate: MitreApplicabilityGate | None=None) -> MitreApplicabilityRecord` — Implements evaluate mitre applicability. Receives: `*, source_run_id: UUID, evidence_sources: Sequence[RawEvidenceSource], gate: MitreApplicabilityGate | None=None`. Sends: `MitreApplicabilityRecord`.
- L152 `def _parse_provider_response(response: httpx.Response) -> dict[str, object]` — Parses provider response. Receives: `response: httpx.Response`. Sends: `dict[str, object]`.

### [`backend/app/services/case_analysis/mitre_applicability_prompt.py`](../../backend/app/services/case_analysis/mitre_applicability_prompt.py)

Purpose: Owns mitre applicability prompt behavior for the backend runtime.

- L67 `def build_mitre_applicability_prompt(evidence_sources: Sequence[RawEvidenceSource]) -> str` — Builds mitre applicability prompt. Receives: `evidence_sources: Sequence[RawEvidenceSource]`. Sends: `str`.

### [`backend/app/services/case_analysis/mitre_applicability_validation.py`](../../backend/app/services/case_analysis/mitre_applicability_validation.py)

Purpose: Owns mitre applicability validation behavior for the backend runtime.

- L16 `def validate_mitre_applicability(payload: object, evidence_sources: Sequence[RawEvidenceSource]) -> MitreApplicabilityRecord` — Validates mitre applicability. Receives: `payload: object, evidence_sources: Sequence[RawEvidenceSource]`. Sends: `MitreApplicabilityRecord`.
- L57 `def _normalize(value: str) -> str` — Normalizes normalize. Receives: `value: str`. Sends: `str`.

### [`backend/app/services/case_analysis/personalization.py`](../../backend/app/services/case_analysis/personalization.py)

Purpose: Owns personalization behavior for the backend runtime.

- L8 `def validate_response_language(value: object) -> ResponseLanguage` — Validates response language. Receives: `value: object`. Sends: `ResponseLanguage`.
- L16 `def resolve_response_language(user_message: object) -> ResponseLanguage` — Implements resolve response language. Receives: `user_message: object`. Sends: `ResponseLanguage`.

### [`backend/app/services/case_analysis/pipeline_config.py`](../../backend/app/services/case_analysis/pipeline_config.py)

Purpose: Owns pipeline config behavior for the backend runtime.

- L10 `class AnalysisPipelineConfig(BaseModel)` — Encapsulates analysispipelineconfig. Receives: `constructor arguments and class fields`. Sends: `AnalysisPipelineConfig`.
- L32 `def assign_version(cls, value: object) -> object` — Implements assign version. Receives: `cls, value: object`. Sends: `object`.
- L43 `def validate_budget(self) -> 'AnalysisPipelineConfig'` — Validates budget. Receives: `self`. Sends: `'AnalysisPipelineConfig'`.
- L62 `def configured_pipeline(*, pipeline: Literal['raw_direct', 'claim_anchored'] | None=None) -> AnalysisPipelineConfig` — Implements configured pipeline. Receives: `*, pipeline: Literal['raw_direct', 'claim_anchored'] | None=None`. Sends: `AnalysisPipelineConfig`.
- L94 `def read_pipeline(value: object) -> AnalysisPipelineConfig` — Retrieves pipeline. Receives: `value: object`. Sends: `AnalysisPipelineConfig`.

### [`backend/app/services/case_analysis/response_decoder.py`](../../backend/app/services/case_analysis/response_decoder.py)

Purpose: Owns response decoder behavior for the backend runtime.

- L7 `def validated_response_payload(response: httpx.Response) -> dict[str, object]` — Implements validated response payload. Receives: `response: httpx.Response`. Sends: `dict[str, object]`.

### [`backend/app/services/case_analysis/response_identifiers.py`](../../backend/app/services/case_analysis/response_identifiers.py)

Purpose: Owns response identifiers behavior for the backend runtime.

- L5 `def _format_identifier(value: object, prefix: str, aliases: str) -> object` — Implements format identifier. Receives: `value: object, prefix: str, aliases: str`. Sends: `object`.
- L12 `def normalize_analysis_identifiers(payload: dict[str, object]) -> dict[str, object]` — Normalizes analysis identifiers. Receives: `payload: dict[str, object]`. Sends: `dict[str, object]`.

### [`backend/app/services/case_analysis/source_citations.py`](../../backend/app/services/case_analysis/source_citations.py)

Purpose: Owns source citations behavior for the backend runtime.

- L12 `def bind_analysis_claim_citations(claims: list[AnalysisClaimV3], analysis_context: Mapping[str, object]) -> list[AnalysisClaimV3]` — Implements bind analysis claim citations. Receives: `claims: list[AnalysisClaimV3], analysis_context: Mapping[str, object]`. Sends: `list[AnalysisClaimV3]`.
- L39 `def _bind_citations(citations: list[AnalysisEvidenceCitation], allowed_source_ids: set[str], source_texts: dict[str, str], document_context: object) -> list[AnalysisEvidenceCitation]` — Implements bind citations. Receives: `citations: list[AnalysisEvidenceCitation], allowed_source_ids: set[str], source_texts: dict[str, str], document_context: object`. Sends: `list[AnalysisEvidenceCitation]`.
- L77 `def _source_texts(analysis_context: Mapping[str, object]) -> dict[str, str]` — Implements source texts. Receives: `analysis_context: Mapping[str, object]`. Sends: `dict[str, str]`.

### [`backend/app/services/case_analysis/state_selector.py`](../../backend/app/services/case_analysis/state_selector.py)

Purpose: Owns state selector behavior for the backend runtime.

- L18 `class CanonicalCaseAnalysisState` — Encapsulates canonicalcaseanalysisstate. Receives: `constructor arguments and class fields`. Sends: `CanonicalCaseAnalysisState`.
- L23 `def validate_canonical_case_overview_trace(trace: AnalysisTraceV3, *, evidence_sha256: str, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3 | None` — Validates canonical case overview trace. Receives: `trace: AnalysisTraceV3, *, evidence_sha256: str, source_message_ids: set[str], mitre_table: object=None`. Sends: `AnalysisTraceV3 | None`.
- L44 `def is_case_overview_record(metadata: dict) -> bool` — Determines case overview record. Receives: `metadata: dict`. Sends: `bool`.
- L65 `def select_latest_canonical_case_overview(messages: Sequence[ChatMessage], *, evidence_sha256: str, source_message_ids: set[str]) -> CanonicalCaseAnalysisState | None` — Extracts latest canonical case overview. Receives: `messages: Sequence[ChatMessage], *, evidence_sha256: str, source_message_ids: set[str]`. Sends: `CanonicalCaseAnalysisState | None`.

### [`backend/app/services/case_analysis/validation.py`](../../backend/app/services/case_analysis/validation.py)

Purpose: Owns validation behavior for the backend runtime.

- L8 `class AnalysisTraceStructureError(ValueError)` — Encapsulates analysistracestructureerror. Receives: `constructor arguments and class fields`. Sends: `AnalysisTraceStructureError`.
- L9 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L14 `class AnalysisTraceProvenanceError(ValueError)` — Encapsulates analysistraceprovenanceerror. Receives: `constructor arguments and class fields`. Sends: `AnalysisTraceProvenanceError`.
- L15 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L20 `def validate_analysis_trace_v3(analysis: AnalysisTraceV3, *, source_message_ids: set[str], mitre_table: object=None) -> AnalysisTraceV3` — Validates analysis trace v3. Receives: `analysis: AnalysisTraceV3, *, source_message_ids: set[str], mitre_table: object=None`. Sends: `AnalysisTraceV3`.
- L120 `def detect_forbidden_provenance(raw_payload: object) -> None` — Implements detect forbidden provenance. Receives: `raw_payload: object`. Sends: `None`.
- L135 `def _admitted_technique_ids(value: object) -> set[str]` — Implements admitted technique ids. Receives: `value: object`. Sends: `set[str]`.
- L149 `def _contains_key(value: object, forbidden: set[str]) -> bool` — Implements contains key. Receives: `value: object, forbidden: set[str]`. Sends: `bool`.

### [`backend/app/services/case_materials/__init__.py`](../../backend/app/services/case_materials/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/case_materials/errors.py`](../../backend/app/services/case_materials/errors.py)

Purpose: Owns errors behavior for the backend runtime.

- L4 `class CaseMaterialsError(Exception)` — Encapsulates casematerialserror. Receives: `constructor arguments and class fields`. Sends: `CaseMaterialsError`.
- L5 `def __init__(self, code: str, message: str, status_code: int=status.HTTP_422_UNPROCESSABLE_CONTENT) -> None` — Implements init. Receives: `self, code: str, message: str, status_code: int=status.HTTP_422_UNPROCESSABLE_CONTENT`. Sends: `None`.

### [`backend/app/services/case_materials/material_service.py`](../../backend/app/services/case_materials/material_service.py)

Purpose: Owns material service behavior for the backend runtime.

- L23 `class CaseMaterialsService` — Encapsulates casematerialsservice. Receives: `constructor arguments and class fields`. Sends: `CaseMaterialsService`.
- L24 `def __init__(self, db: AsyncSession)` — Implements init. Receives: `self, db: AsyncSession`. Sends: `inferred or None`.
- L27 `async def get_owned_case(self, case_id: UUID, user_id: UUID | None, *, lock: bool=False) -> Case` — Retrieves owned case. Receives: `self, case_id: UUID, user_id: UUID | None, *, lock: bool=False`. Sends: `Case`.
- L37 `async def add_document(self, *, case_id: UUID, user_id: UUID | None, filename: str, mime_type: str, content: bytes, extraction: dict[str, object]) -> CaseDocument` — Implements add document. Receives: `self, *, case_id: UUID, user_id: UUID | None, filename: str, mime_type: str, content: bytes, extraction: dict[str, object]`. Sends: `CaseDocument`.
- L76 `async def list_documents(self, case_id: UUID, user_id: UUID | None) -> list[CaseDocument]` — Lists documents. Receives: `self, case_id: UUID, user_id: UUID | None`. Sends: `list[CaseDocument]`.
- L86 `async def admit_extraction(self, *, case_id: UUID, user_id: UUID | None, extraction_id: UUID) -> EvidenceSource` — Implements admit extraction. Receives: `self, *, case_id: UUID, user_id: UUID | None, extraction_id: UUID`. Sends: `EvidenceSource`.
- L143 `async def admit_text(self, *, case_id: UUID, user_id: UUID | None, source_kind: str, exact_text: str, provenance_json: dict[str, object], source_metadata_json: dict[str, object] | None=None, origin_message_id: UUID | None=None) -> EvidenceSource` — Implements admit text. Receives: `self, *, case_id: UUID, user_id: UUID | None, source_kind: str, exact_text: str, provenance_json: dict[str, object], source_metadata_json: dict[str, object] | None=None, origin_message_id: UUID | None=None`. Sends: `EvidenceSource`.
- L181 `async def add_revision(self, *, case_id: UUID, user_id: UUID | None, source_id: UUID, exact_text: str, provenance_json: dict[str, object]) -> EvidenceSource` — Implements add revision. Receives: `self, *, case_id: UUID, user_id: UUID | None, source_id: UUID, exact_text: str, provenance_json: dict[str, object]`. Sends: `EvidenceSource`.
- L220 `async def archive_source(self, *, case_id: UUID, user_id: UUID | None, source_id: UUID) -> None` — Implements archive source. Receives: `self, *, case_id: UUID, user_id: UUID | None, source_id: UUID`. Sends: `None`.
- L234 `async def list_evidence(self, case_id: UUID, user_id: UUID | None) -> list[EvidenceSource]` — Lists evidence. Receives: `self, case_id: UUID, user_id: UUID | None`. Sends: `list[EvidenceSource]`.
- L244 `async def get_evidence_snapshot(self, *, case_id: UUID, user_id: UUID | None, snapshot_id: UUID) -> CaseEvidenceSnapshot` — Retrieves evidence snapshot. Receives: `self, *, case_id: UUID, user_id: UUID | None, snapshot_id: UUID`. Sends: `CaseEvidenceSnapshot`.
- L263 `async def _next_revision(self, source_id: UUID) -> int` — Implements next revision. Receives: `self, source_id: UUID`. Sends: `int`.
- L270 `def _required_string(value: dict[str, object], key: str) -> str` — Implements required string. Receives: `value: dict[str, object], key: str`. Sends: `str`.
- L277 `def _dictionary(value: object) -> dict[str, object]` — Implements dictionary. Receives: `value: object`. Sends: `dict[str, object]`.
- L281 `def _list(value: object) -> list[object]` — Lists list. Receives: `value: object`. Sends: `list[object]`.

### [`backend/app/services/case_materials/snapshot_builder.py`](../../backend/app/services/case_materials/snapshot_builder.py)

Purpose: Owns snapshot builder behavior for the backend runtime.

- L19 `def canonical_json(value: object) -> str` — Implements canonical json. Receives: `value: object`. Sends: `str`.
- L23 `def _active_revision(source: EvidenceSource) -> EvidenceRevision | None` — Implements active revision. Receives: `source: EvidenceSource`. Sends: `EvidenceRevision | None`.
- L28 `def _source_label(source: EvidenceSource) -> str` — Implements source label. Receives: `source: EvidenceSource`. Sends: `str`.
- L39 `async def build_case_evidence_snapshot(db: AsyncSession, *, case_id: UUID, user_id: UUID | None) -> CaseEvidenceSnapshot` — Builds case evidence snapshot. Receives: `db: AsyncSession, *, case_id: UUID, user_id: UUID | None`. Sends: `CaseEvidenceSnapshot`.

### [`backend/app/services/cases/__init__.py`](../../backend/app/services/cases/__init__.py)

Purpose: Case aggregate services.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/cases/case_factory.py`](../../backend/app/services/cases/case_factory.py)

Purpose: Construct a case and its one primary chat thread.

- L9 `def build_case_with_chat(title: str, user_id: UUID | None) -> tuple[Case, ChatThread]` — Builds case with chat. Receives: `title: str, user_id: UUID | None`. Sends: `tuple[Case, ChatThread]`.

### [`backend/app/services/cases/case_management.py`](../../backend/app/services/cases/case_management.py)

Purpose: Case aggregate lifecycle and ownership service.

- L15 `def serialize_case(case: Case) -> CaseRead` — Serializes case. Receives: `case: Case`. Sends: `CaseRead`.
- L55 `class CaseService` — Encapsulates caseservice. Receives: `constructor arguments and class fields`. Sends: `CaseService`.
- L56 `def __init__(self, db: AsyncSession)` — Implements init. Receives: `self, db: AsyncSession`. Sends: `inferred or None`.
- L60 `def _verify_case_access(case: Case, user_id: UUID | None) -> None` — Validates case access. Receives: `case: Case, user_id: UUID | None`. Sends: `None`.
- L67 `async def create_case(self, request: CaseCreate, user_id: UUID | None=None) -> CaseRead` — Creates case. Receives: `self, request: CaseCreate, user_id: UUID | None=None`. Sends: `CaseRead`.
- L77 `async def list_cases(self, user_id: UUID | None=None) -> list[CaseRead]` — Lists cases. Receives: `self, user_id: UUID | None=None`. Sends: `list[CaseRead]`.
- L90 `async def get_case(self, case_id: UUID, user_id: UUID | None=None) -> CaseRead` — Retrieves case. Receives: `self, case_id: UUID, user_id: UUID | None=None`. Sends: `CaseRead`.
- L99 `async def update_case(self, case_id: UUID, request: CaseUpdate, user_id: UUID | None=None) -> CaseRead` — Updates case. Receives: `self, case_id: UUID, request: CaseUpdate, user_id: UUID | None=None`. Sends: `CaseRead`.
- L113 `async def delete_case(self, case_id: UUID, user_id: UUID | None=None) -> None` — Removes case. Receives: `self, case_id: UUID, user_id: UUID | None=None`. Sends: `None`.
- L123 `async def _load_case(self, case_id: UUID, *, lock: bool=False) -> Case` — Retrieves case. Receives: `self, case_id: UUID, *, lock: bool=False`. Sends: `Case`.

### [`backend/app/services/chat/__init__.py`](../../backend/app/services/chat/__init__.py)

Purpose: Chat Thread and Message Domain Services.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/chat/analysis_run_config.py`](../../backend/app/services/chat/analysis_run_config.py)

Purpose: Owns analysis run config behavior for the backend runtime.

- L14 `async def pipeline_for_new_run(db: AsyncSession, *, thread_id: UUID, root_ordinal: int, action: str, clarification_answer: bool) -> dict[str, object]` — Implements pipeline for new run. Receives: `db: AsyncSession, *, thread_id: UUID, root_ordinal: int, action: str, clarification_answer: bool`. Sends: `dict[str, object]`.

### [`backend/app/services/chat/case_chat.py`](../../backend/app/services/chat/case_chat.py)

Purpose: Owns case chat behavior for the backend runtime.

- L36 `async def create_case_chat_message_and_run(db: AsyncSession, *, case_id: UUID, user_id: UUID | None, request: ChatMessageCreate) -> tuple[ChatMessage, CaseRun]` — Creates case chat message and run. Receives: `db: AsyncSession, *, case_id: UUID, user_id: UUID | None, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, CaseRun]`.
- L91 `async def _submit_clarification(db: AsyncSession, case_id: UUID, user_id: UUID | None, clarification: CaseClarification, request: ChatMessageCreate) -> tuple[ChatMessage, CaseRun]` — Implements submit clarification. Receives: `db: AsyncSession, case_id: UUID, user_id: UUID | None, clarification: CaseClarification, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, CaseRun]`.
- L114 `async def _create_case_addition(db: AsyncSession, case: Case, thread: ChatThread, request: ChatMessageCreate) -> tuple[ChatMessage, CaseRun]` — Creates case addition. Receives: `db: AsyncSession, case: Case, thread: ChatThread, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, CaseRun]`.
- L169 `async def _create_case_ask(db: AsyncSession, case: Case, thread: ChatThread, request: ChatMessageCreate) -> tuple[ChatMessage, CaseRun]` — Creates case ask. Receives: `db: AsyncSession, case: Case, thread: ChatThread, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, CaseRun]`.

### [`backend/app/services/chat/case_chat_errors.py`](../../backend/app/services/chat/case_chat_errors.py)

Purpose: Owns case chat errors behavior for the backend runtime.

- L4 `class CaseChatError(Exception)` — Encapsulates casechaterror. Receives: `constructor arguments and class fields`. Sends: `CaseChatError`.
- L5 `def __init__(self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT) -> None` — Implements init. Receives: `self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT`. Sends: `None`.

### [`backend/app/services/chat/case_chat_helpers.py`](../../backend/app/services/chat/case_chat_helpers.py)

Purpose: Owns case chat helpers behavior for the backend runtime.

- L18 `async def locked_case_chat(db: AsyncSession, case_id: UUID, user_id: UUID | None) -> tuple[Case, ChatThread]` — Implements locked case chat. Receives: `db: AsyncSession, case_id: UUID, user_id: UUID | None`. Sends: `tuple[Case, ChatThread]`.
- L36 `async def pending_clarification(db: AsyncSession, case_id: UUID) -> CaseClarification | None` — Implements pending clarification. Receives: `db: AsyncSession, case_id: UUID`. Sends: `CaseClarification | None`.
- L44 `async def existing_case_run(db: AsyncSession, case_id: UUID, idempotency_key: str, expected_payload: dict[str, object]) -> tuple[ChatMessage, CaseRun] | None` — Implements existing case run. Receives: `db: AsyncSession, case_id: UUID, idempotency_key: str, expected_payload: dict[str, object]`. Sends: `tuple[ChatMessage, CaseRun] | None`.
- L74 `def request_payload(request: ChatMessageCreate, operation: str) -> dict[str, object]` — Implements request payload. Receives: `request: ChatMessageCreate, operation: str`. Sends: `dict[str, object]`.
- L83 `def clarification_request(request: ChatMessageCreate) -> CaseClarificationAnswer` — Implements clarification request. Receives: `request: ChatMessageCreate`. Sends: `CaseClarificationAnswer`.

### [`backend/app/services/chat/chat_management.py`](../../backend/app/services/chat/chat_management.py)

Purpose: Owns chat management behavior for the backend runtime.

- L13 `class ChatService` — Encapsulates chatservice. Receives: `constructor arguments and class fields`. Sends: `ChatService`.
- L14 `def __init__(self, db: AsyncSession)` — Implements init. Receives: `self, db: AsyncSession`. Sends: `inferred or None`.
- L17 `def _verify_thread_access(self, thread: ChatThread, user_id: UUID | None) -> None` — Validates thread access. Receives: `self, thread: ChatThread, user_id: UUID | None`. Sends: `None`.
- L29 `async def create_thread(self, request: ChatThreadCreate, user_id: UUID | None=None) -> ChatThread` — Creates thread. Receives: `self, request: ChatThreadCreate, user_id: UUID | None=None`. Sends: `ChatThread`.
- L42 `async def ensure_thread_for_case(self, case_id: UUID, user_id: UUID | None=None) -> ChatThread` — Implements ensure thread for case. Receives: `self, case_id: UUID, user_id: UUID | None=None`. Sends: `ChatThread`.
- L64 `async def update_thread(self, thread_id: UUID, request: ChatThreadUpdate, user_id: UUID | None=None) -> ChatThread` — Updates thread. Receives: `self, thread_id: UUID, request: ChatThreadUpdate, user_id: UUID | None=None`. Sends: `ChatThread`.
- L90 `async def delete_thread(self, thread_id: UUID, user_id: UUID | None=None) -> None` — Removes thread. Receives: `self, thread_id: UUID, user_id: UUID | None=None`. Sends: `None`.
- L114 `async def list_threads(self, user_id: UUID | None=None) -> list[ChatThread]` — Lists threads. Receives: `self, user_id: UUID | None=None`. Sends: `list[ChatThread]`.
- L135 `async def get_thread(self, thread_id: UUID, user_id: UUID | None=None) -> ChatThread` — Retrieves thread. Receives: `self, thread_id: UUID, user_id: UUID | None=None`. Sends: `ChatThread`.

### [`backend/app/services/chat/chat_message.py`](../../backend/app/services/chat/chat_message.py)

Purpose: Owns chat message behavior for the backend runtime.

- L16 `class ChatMessageService` — Encapsulates chatmessageservice. Receives: `constructor arguments and class fields`. Sends: `ChatMessageService`.
- L17 `def __init__(self, db: AsyncSession)` — Implements init. Receives: `self, db: AsyncSession`. Sends: `inferred or None`.
- L20 `async def create_message_and_run(self, thread_id: UUID, request: ChatMessageCreate) -> tuple[ChatMessage, ChatRun]` — Creates message and run. Receives: `self, thread_id: UUID, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, ChatRun]`.
- L27 `async def get_run(self, thread_id: UUID, run_id: UUID) -> ChatRun` — Retrieves run. Receives: `self, thread_id: UUID, run_id: UUID`. Sends: `ChatRun`.
- L44 `async def list_messages(self, thread_id: UUID) -> list[ChatMessageRead]` — Lists messages. Receives: `self, thread_id: UUID`. Sends: `list[ChatMessageRead]`.

### [`backend/app/services/chat/chat_run_creation.py`](../../backend/app/services/chat/chat_run_creation.py)

Purpose: Owns chat run creation behavior for the backend runtime.

- L19 `def request_fingerprint(request: ChatMessageCreate) -> str` — Implements request fingerprint. Receives: `request: ChatMessageCreate`. Sends: `str`.
- L32 `async def create_message_and_run(db: AsyncSession, thread_id: UUID, request: ChatMessageCreate) -> tuple[ChatMessage, ChatRun]` — Creates message and run. Receives: `db: AsyncSession, thread_id: UUID, request: ChatMessageCreate`. Sends: `tuple[ChatMessage, ChatRun]`.
- L106 `async def _locked_thread(db: AsyncSession, thread_id: UUID) -> ChatThread` — Implements locked thread. Receives: `db: AsyncSession, thread_id: UUID`. Sends: `ChatThread`.
- L116 `async def _existing_run(db: AsyncSession, thread_id: UUID, request: ChatMessageCreate, fingerprint: str) -> tuple[ChatMessage, ChatRun] | None` — Implements existing run. Receives: `db: AsyncSession, thread_id: UUID, request: ChatMessageCreate, fingerprint: str`. Sends: `tuple[ChatMessage, ChatRun] | None`.
- L142 `async def _ensure_no_active_run(db: AsyncSession, thread_id: UUID) -> None` — Implements ensure no active run. Receives: `db: AsyncSession, thread_id: UUID`. Sends: `None`.
- L156 `def _resolve_action(thread: ChatThread, requested_action: str | None) -> tuple[str, str]` — Implements resolve action. Receives: `thread: ChatThread, requested_action: str | None`. Sends: `tuple[str, str]`.
- L184 `async def _followup_position(db: AsyncSession, thread: ChatThread, pending_answer: str, ordinal: int) -> tuple[int, int, dict[str, str] | None]` — Implements followup position. Receives: `db: AsyncSession, thread: ChatThread, pending_answer: str, ordinal: int`. Sends: `tuple[int, int, dict[str, str] | None]`.

### [`backend/app/services/chat/chat_run_retry.py`](../../backend/app/services/chat/chat_run_retry.py)

Purpose: Owns chat run retry behavior for the backend runtime.

- L12 `async def requeue_interrupted_run(db: AsyncSession, thread: ChatThread, message: ChatMessage, run: ChatRun) -> None` — Implements requeue interrupted run. Receives: `db: AsyncSession, thread: ChatThread, message: ChatMessage, run: ChatRun`. Sends: `None`.
- L39 `async def read_retry_request(db: AsyncSession, thread: ChatThread) -> ChatRetryRequest | None` — Retrieves retry request. Receives: `db: AsyncSession, thread: ChatThread`. Sends: `ChatRetryRequest | None`.

### [`backend/app/services/chat/clarification_chain.py`](../../backend/app/services/chat/clarification_chain.py)

Purpose: Owns clarification chain behavior for the backend runtime.

- L9 `class ClarificationChain` — Encapsulates clarificationchain. Receives: `constructor arguments and class fields`. Sends: `ClarificationChain`.
- L17 `def _followup_root_ordinal(message: ChatMessage) -> int | None` — Implements followup root ordinal. Receives: `message: ChatMessage`. Sends: `int | None`.
- L34 `def _is_clarification_message(message: ChatMessage) -> bool` — Determines clarification message. Receives: `message: ChatMessage`. Sends: `bool`.
- L42 `def _is_terminal_assistant_message(message: ChatMessage) -> bool` — Determines terminal assistant message. Receives: `message: ChatMessage`. Sends: `bool`.
- L53 `def _followup_context(message: ChatMessage) -> dict[str, str]` — Implements followup context. Receives: `message: ChatMessage`. Sends: `dict[str, str]`.
- L66 `def _answer_context(message: ChatMessage | None) -> dict[str, str]` — Implements answer context. Receives: `message: ChatMessage | None`. Sends: `dict[str, str]`.
- L86 `def _exchange(question: ChatMessage, answer: str, answer_message: ChatMessage | None) -> ClarificationExchange` — Implements exchange. Receives: `question: ChatMessage, answer: str, answer_message: ChatMessage | None`. Sends: `ClarificationExchange`.
- L109 `def reconstruct_clarification_chain(messages: Sequence[ChatMessage], *, root_ordinal: int | None=None, pending_answer: str | None=None) -> ClarificationChain | None` — Implements reconstruct clarification chain. Receives: `messages: Sequence[ChatMessage], *, root_ordinal: int | None=None, pending_answer: str | None=None`. Sends: `ClarificationChain | None`.

### [`backend/app/services/chat/document_provenance.py`](../../backend/app/services/chat/document_provenance.py)

Purpose: Owns document provenance behavior for the backend runtime.

- L8 `def validated_document_source_payloads(content: str, sources: list[CaseNarrativeDocumentSource]) -> list[dict[str, object]]` — Implements validated document source payloads. Receives: `content: str, sources: list[CaseNarrativeDocumentSource]`. Sends: `list[dict[str, object]]`.
- L15 `def _validated_source_payload(content: str, source: CaseNarrativeDocumentSource) -> dict[str, object]` — Implements validated source payload. Receives: `content: str, source: CaseNarrativeDocumentSource`. Sends: `dict[str, object]`.
- L29 `def _span_matches(content: str, start: int, end: int, expected_hash: str) -> bool` — Implements span matches. Receives: `content: str, start: int, end: int, expected_hash: str`. Sends: `bool`.

### [`backend/app/services/chat/raw_evidence.py`](../../backend/app/services/chat/raw_evidence.py)

Purpose: Owns raw evidence behavior for the backend runtime.

- L15 `class RawEvidenceSource` — Encapsulates rawevidencesource. Receives: `constructor arguments and class fields`. Sends: `RawEvidenceSource`.
- L22 `class RawEvidenceSnapshot` — Encapsulates rawevidencesnapshot. Receives: `constructor arguments and class fields`. Sends: `RawEvidenceSnapshot`.
- L28 `def source_message_ids(self) -> tuple[UUID, ...]` — Implements source message ids. Receives: `self`. Sends: `tuple[UUID, ...]`.
- L32 `def document_source_context(self) -> tuple[dict[str, object], ...]` — Implements document source context. Receives: `self`. Sends: `tuple[dict[str, object], ...]`.
- L43 `def build_raw_evidence_snapshot(messages: list[ChatMessage]) -> RawEvidenceSnapshot` — Builds raw evidence snapshot. Receives: `messages: list[ChatMessage]`. Sends: `RawEvidenceSnapshot`.
- L91 `async def load_raw_evidence_snapshot(db: AsyncSession, *, thread_id: UUID, through_ordinal: int | None=None) -> RawEvidenceSnapshot` — Retrieves raw evidence snapshot. Receives: `db: AsyncSession, *, thread_id: UUID, through_ordinal: int | None=None`. Sends: `RawEvidenceSnapshot`.

### [`backend/app/services/clients/__init__.py`](../../backend/app/services/clients/__init__.py)

Purpose: External Service Clients.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/clients/rag_client.py`](../../backend/app/services/clients/rag_client.py)

Purpose: Typed HTTP boundary for chat requests to the RAG service.

- L15 `class RagCallFailure(Exception)` — A safe, stable failure that may be persisted on a chat run. Receives: `constructor arguments and class fields`. Sends: `RagCallFailure`.
- L18 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L24 `async def request_rag(content: str, *, client: httpx.AsyncClient | None=None) -> QueryResponse` — Call only the current completed-response RAG query boundary. Receives: `content: str, *, client: httpx.AsyncClient | None=None`. Sends: `QueryResponse`.
- L40 `async def _post_and_validate(client: httpx.AsyncClient, url: str, payload: dict[str, object]) -> QueryResponse` — Implements post and validate. Receives: `client: httpx.AsyncClient, url: str, payload: dict[str, object]`. Sends: `QueryResponse`.

### [`backend/app/services/document_ingestion/__init__.py`](../../backend/app/services/document_ingestion/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/contracts.py`](../../backend/app/services/document_ingestion/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L7 `class IngestionMode(StrEnum)` — Encapsulates ingestionmode. Receives: `constructor arguments and class fields`. Sends: `IngestionMode`.
- L12 `class ExtractionMethod(StrEnum)` — Encapsulates extractionmethod. Receives: `constructor arguments and class fields`. Sends: `ExtractionMethod`.
- L19 `class SourceType(StrEnum)` — Encapsulates sourcetype. Receives: `constructor arguments and class fields`. Sends: `SourceType`.
- L27 `class RegionType(StrEnum)` — Encapsulates regiontype. Receives: `constructor arguments and class fields`. Sends: `RegionType`.
- L37 `class RecognitionMethod(StrEnum)` — Encapsulates recognitionmethod. Receives: `constructor arguments and class fields`. Sends: `RecognitionMethod`.
- L45 `class VerificationStatus(StrEnum)` — Encapsulates verificationstatus. Receives: `constructor arguments and class fields`. Sends: `VerificationStatus`.
- L53 `class ContentRole(StrEnum)` — Encapsulates contentrole. Receives: `constructor arguments and class fields`. Sends: `ContentRole`.
- L59 `class BoundingBox(BaseModel)` — Encapsulates boundingbox. Receives: `constructor arguments and class fields`. Sends: `BoundingBox`.
- L66 `class OCRWord(BaseModel)` — Encapsulates ocrword. Receives: `constructor arguments and class fields`. Sends: `OCRWord`.
- L75 `class DocumentBlock(BaseModel)` — Encapsulates documentblock. Receives: `constructor arguments and class fields`. Sends: `DocumentBlock`.
- L83 `class RecognizedContent(BaseModel)` — Encapsulates recognizedcontent. Receives: `constructor arguments and class fields`. Sends: `RecognizedContent`.
- L89 `class RecognitionCandidate(BaseModel)` — Encapsulates recognitioncandidate. Receives: `constructor arguments and class fields`. Sends: `RecognitionCandidate`.
- L99 `class DocumentRegion(BaseModel)` — Encapsulates documentregion. Receives: `constructor arguments and class fields`. Sends: `DocumentRegion`.
- L119 `class RoutingSummary(BaseModel)` — Encapsulates routingsummary. Receives: `constructor arguments and class fields`. Sends: `RoutingSummary`.
- L128 `class DocumentPage(BaseModel)` — Encapsulates documentpage. Receives: `constructor arguments and class fields`. Sends: `DocumentPage`.
- L139 `def text_sha256(self) -> str` — Implements text sha256. Receives: `self`. Sends: `str`.
- L143 `class IngestedDocument(BaseModel)` — Encapsulates ingesteddocument. Receives: `constructor arguments and class fields`. Sends: `IngestedDocument`.

### [`backend/app/services/document_ingestion/detection.py`](../../backend/app/services/document_ingestion/detection.py)

Purpose: Owns detection behavior for the backend runtime.

- L9 `class DocumentKind(StrEnum)` — Encapsulates documentkind. Receives: `constructor arguments and class fields`. Sends: `DocumentKind`.
- L17 `class DetectedDocument` — Encapsulates detecteddocument. Receives: `constructor arguments and class fields`. Sends: `DetectedDocument`.
- L22 `def _is_docx(content: bytes) -> bool` — Determines docx. Receives: `content: bytes`. Sends: `bool`.
- L30 `def detect_document(content: bytes) -> DetectedDocument` — Implements detect document. Receives: `content: bytes`. Sends: `DetectedDocument`.

### [`backend/app/services/document_ingestion/errors.py`](../../backend/app/services/document_ingestion/errors.py)

Purpose: Owns errors behavior for the backend runtime.

- L1 `class DocumentIngestionError(Exception)` — Encapsulates documentingestionerror. Receives: `constructor arguments and class fields`. Sends: `DocumentIngestionError`.
- L2 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L8 `class UnsupportedDocumentError(DocumentIngestionError)` — Encapsulates unsupporteddocumenterror. Receives: `constructor arguments and class fields`. Sends: `UnsupportedDocumentError`.
- L9 `def __init__(self, message: str) -> None` — Implements init. Receives: `self, message: str`. Sends: `None`.
- L13 `class DocumentLimitError(DocumentIngestionError)` — Encapsulates documentlimiterror. Receives: `constructor arguments and class fields`. Sends: `DocumentLimitError`.
- L14 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L18 `class InvalidDocumentError(DocumentIngestionError)` — Encapsulates invaliddocumenterror. Receives: `constructor arguments and class fields`. Sends: `InvalidDocumentError`.
- L19 `def __init__(self, message: str) -> None` — Implements init. Receives: `self, message: str`. Sends: `None`.
- L23 `class DocumentRecognitionError(Exception)` — Encapsulates documentrecognitionerror. Receives: `constructor arguments and class fields`. Sends: `DocumentRecognitionError`.
- L27 `class RecognitionConfigurationError(DocumentRecognitionError)` — Encapsulates recognitionconfigurationerror. Receives: `constructor arguments and class fields`. Sends: `RecognitionConfigurationError`.
- L31 `class RecognitionTimeoutError(DocumentRecognitionError)` — Encapsulates recognitiontimeouterror. Receives: `constructor arguments and class fields`. Sends: `RecognitionTimeoutError`.
- L35 `class RecognitionProviderError(DocumentRecognitionError)` — Encapsulates recognitionprovidererror. Receives: `constructor arguments and class fields`. Sends: `RecognitionProviderError`.
- L39 `class RecognitionResponseError(DocumentRecognitionError)` — Encapsulates recognitionresponseerror. Receives: `constructor arguments and class fields`. Sends: `RecognitionResponseError`.
- L43 `class DocumentSegmentationError(Exception)` — Encapsulates documentsegmentationerror. Receives: `constructor arguments and class fields`. Sends: `DocumentSegmentationError`.
- L47 `class SegmentationConfigurationError(DocumentSegmentationError)` — Encapsulates segmentationconfigurationerror. Receives: `constructor arguments and class fields`. Sends: `SegmentationConfigurationError`.
- L51 `class SegmentationTimeoutError(DocumentSegmentationError)` — Encapsulates segmentationtimeouterror. Receives: `constructor arguments and class fields`. Sends: `SegmentationTimeoutError`.
- L55 `class SegmentationProviderError(DocumentSegmentationError)` — Encapsulates segmentationprovidererror. Receives: `constructor arguments and class fields`. Sends: `SegmentationProviderError`.
- L59 `class SegmentationResponseError(DocumentSegmentationError)` — Encapsulates segmentationresponseerror. Receives: `constructor arguments and class fields`. Sends: `SegmentationResponseError`.

### [`backend/app/services/document_ingestion/evaluation/__init__.py`](../../backend/app/services/document_ingestion/evaluation/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/evaluation/metrics.py`](../../backend/app/services/document_ingestion/evaluation/metrics.py)

Purpose: Owns metrics behavior for the backend runtime.

- L16 `def _edit_distance(reference: list[str], prediction: list[str]) -> int` — Implements edit distance. Receives: `reference: list[str], prediction: list[str]`. Sends: `int`.
- L33 `def character_error_rate(ground_truth: str, prediction: str) -> float` — Implements character error rate. Receives: `ground_truth: str, prediction: str`. Sends: `float`.
- L39 `def word_error_rate(ground_truth: str, prediction: str) -> float` — Implements word error rate. Receives: `ground_truth: str, prediction: str`. Sends: `float`.
- L47 `def _expanded_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]` — Implements expanded samples. Receives: `samples: list[dict[str, Any]]`. Sends: `list[dict[str, Any]]`.
- L59 `def _critical_field_scores(sample: dict[str, Any]) -> dict[str, float]` — Implements critical field scores. Receives: `sample: dict[str, Any]`. Sends: `dict[str, float]`.
- L71 `def _score_sample(sample: dict[str, Any]) -> dict[str, Any]` — Implements score sample. Receives: `sample: dict[str, Any]`. Sends: `dict[str, Any]`.
- L95 `def _average(rows: list[dict[str, Any]]) -> dict[str, Any]` — Implements average. Receives: `rows: list[dict[str, Any]]`. Sends: `dict[str, Any]`.
- L129 `def evaluate(samples: list[dict[str, Any]]) -> dict[str, Any]` — Implements evaluate. Receives: `samples: list[dict[str, Any]]`. Sends: `dict[str, Any]`.

### [`backend/app/services/document_ingestion/merge/__init__.py`](../../backend/app/services/document_ingestion/merge/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/merge/reading_order.py`](../../backend/app/services/document_ingestion/merge/reading_order.py)

Purpose: Owns reading order behavior for the backend runtime.

- L4 `def order_regions(regions: list[DocumentRegion]) -> list[DocumentRegion]` — Implements order regions. Receives: `regions: list[DocumentRegion]`. Sends: `list[DocumentRegion]`.
- L15 `def merge_region_text(regions: list[DocumentRegion]) -> str` — Implements merge region text. Receives: `regions: list[DocumentRegion]`. Sends: `str`.

### [`backend/app/services/document_ingestion/parsers/__init__.py`](../../backend/app/services/document_ingestion/parsers/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/parsers/docx_parser.py`](../../backend/app/services/document_ingestion/parsers/docx_parser.py)

Purpose: Owns docx parser behavior for the backend runtime.

- L22 `def _iter_document_blocks(document: DocumentObject)` — Implements iter document blocks. Receives: `document: DocumentObject`. Sends: `inferred or None`.
- L30 `def _table_text(table: Table) -> str` — Implements table text. Receives: `table: Table`. Sends: `str`.
- L39 `def parse_docx(content: bytes, document_id: str) -> tuple[list[DocumentPage], list[str]]` — Parses docx. Receives: `content: bytes, document_id: str`. Sends: `tuple[list[DocumentPage], list[str]]`.

### [`backend/app/services/document_ingestion/parsers/pdf_text_parser.py`](../../backend/app/services/document_ingestion/parsers/pdf_text_parser.py)

Purpose: Owns pdf text parser behavior for the backend runtime.

- L15 `class NativeTextPolicy` — Encapsulates nativetextpolicy. Receives: `constructor arguments and class fields`. Sends: `NativeTextPolicy`.
- L24 `class PdfPageInspection` — Encapsulates pdfpageinspection. Receives: `constructor arguments and class fields`. Sends: `PdfPageInspection`.
- L32 `class PdfInspection` — Encapsulates pdfinspection. Receives: `constructor arguments and class fields`. Sends: `PdfInspection`.
- L37 `def _normalize_text(text: str) -> str` — Normalizes text. Receives: `text: str`. Sends: `str`.
- L42 `def split_native_blocks(text: str) -> list[str]` — Implements split native blocks. Receives: `text: str`. Sends: `list[str]`.
- L46 `def _is_printable(character: str) -> bool` — Determines printable. Receives: `character: str`. Sends: `bool`.
- L50 `def _is_meaningful(character: str) -> bool` — Determines meaningful. Receives: `character: str`. Sends: `bool`.
- L55 `def _has_usable_text(text: str, width: float, height: float, policy: NativeTextPolicy) -> bool` — Determines usable text. Receives: `text: str, width: float, height: float, policy: NativeTextPolicy`. Sends: `bool`.
- L80 `def inspect_pdf(content: bytes, policy: NativeTextPolicy, max_pages: int) -> PdfInspection` — Implements inspect pdf. Receives: `content: bytes, policy: NativeTextPolicy, max_pages: int`. Sends: `PdfInspection`.

### [`backend/app/services/document_ingestion/provenance.py`](../../backend/app/services/document_ingestion/provenance.py)

Purpose: Owns provenance behavior for the backend runtime.

- L14 `def build_document_id(content: bytes) -> str` — Builds document id. Receives: `content: bytes`. Sends: `str`.
- L19 `def build_block_id(document_id: str, page_number: int, block_number: int) -> str` — Builds block id. Receives: `document_id: str, page_number: int, block_number: int`. Sends: `str`.
- L23 `def build_region_id(document_id: str, page_number: int, region_number: int) -> str` — Builds region id. Receives: `document_id: str, page_number: int, region_number: int`. Sends: `str`.
- L27 `def build_blocks(document_id: str, page_number: int, texts: list[str], source_type: SourceType) -> list[DocumentBlock]` — Builds blocks. Receives: `document_id: str, page_number: int, texts: list[str], source_type: SourceType`. Sends: `list[DocumentBlock]`.
- L44 `def build_native_regions(document_id: str, page_number: int, texts: list[str]) -> list[DocumentRegion]` — Builds native regions. Receives: `document_id: str, page_number: int, texts: list[str]`. Sends: `list[DocumentRegion]`.

### [`backend/app/services/document_ingestion/recognition/__init__.py`](../../backend/app/services/document_ingestion/recognition/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/recognition/base.py`](../../backend/app/services/document_ingestion/recognition/base.py)

Purpose: Owns base behavior for the backend runtime.

- L15 `class RenderedPage` — Encapsulates renderedpage. Receives: `constructor arguments and class fields`. Sends: `RenderedPage`.
- L23 `class RecognizedPage` — Encapsulates recognizedpage. Receives: `constructor arguments and class fields`. Sends: `RecognizedPage`.
- L36 `class RenderedRegion` — Encapsulates renderedregion. Receives: `constructor arguments and class fields`. Sends: `RenderedRegion`.
- L45 `class RecognitionResult` — Encapsulates recognitionresult. Receives: `constructor arguments and class fields`. Sends: `RecognitionResult`.
- L58 `class DocumentRecognizer(Protocol)` — Encapsulates documentrecognizer. Receives: `constructor arguments and class fields`. Sends: `DocumentRecognizer`.
- L59 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L62 `class OCRRecognizer(Protocol)` — Encapsulates ocrrecognizer. Receives: `constructor arguments and class fields`. Sends: `OCRRecognizer`.
- L63 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize. Receives: `self, region: RenderedRegion`. Sends: `RecognitionResult`.
- L66 `class HTRRecognizer(Protocol)` — Encapsulates htrrecognizer. Receives: `constructor arguments and class fields`. Sends: `HTRRecognizer`.
- L67 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize. Receives: `self, region: RenderedRegion`. Sends: `RecognitionResult`.

### [`backend/app/services/document_ingestion/recognition/content_filter.py`](../../backend/app/services/document_ingestion/recognition/content_filter.py)

Purpose: Owns content filter behavior for the backend runtime.

- L9 `def separate_generated_visual_descriptions(text: str) -> tuple[str, list[str]]` — Implements separate generated visual descriptions. Receives: `text: str`. Sends: `tuple[str, list[str]]`.

### [`backend/app/services/document_ingestion/recognition/google_vision.py`](../../backend/app/services/document_ingestion/recognition/google_vision.py)

Purpose: Owns google vision behavior for the backend runtime.

- L35 `class GoogleVisionDocumentRecognizer` — Encapsulates googlevisiondocumentrecognizer. Receives: `constructor arguments and class fields`. Sends: `GoogleVisionDocumentRecognizer`.
- L36 `def __init__(self, timeout_seconds: float=60.0) -> None` — Implements init. Receives: `self, timeout_seconds: float=60.0`. Sends: `None`.
- L39 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L50 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize. Receives: `self, region: RenderedRegion`. Sends: `RecognitionResult`.
- L63 `async def _request(self, image_bytes: bytes) -> object` — Implements request. Receives: `self, image_bytes: bytes`. Sends: `object`.
- L88 `def _post(self, image_bytes: bytes) -> object` — Implements post. Receives: `self, image_bytes: bytes`. Sends: `object`.

### [`backend/app/services/document_ingestion/recognition/google_vision_response.py`](../../backend/app/services/document_ingestion/recognition/google_vision_response.py)

Purpose: Owns google vision response behavior for the backend runtime.

- L10 `class _Vertex(BaseModel)` — Encapsulates vertex. Receives: `constructor arguments and class fields`. Sends: `_Vertex`.
- L15 `class _Polygon(BaseModel)` — Encapsulates polygon. Receives: `constructor arguments and class fields`. Sends: `_Polygon`.
- L19 `class _Symbol(BaseModel)` — Encapsulates symbol. Receives: `constructor arguments and class fields`. Sends: `_Symbol`.
- L23 `class _Word(BaseModel)` — Encapsulates word. Receives: `constructor arguments and class fields`. Sends: `_Word`.
- L29 `class _Paragraph(BaseModel)` — Encapsulates paragraph. Receives: `constructor arguments and class fields`. Sends: `_Paragraph`.
- L33 `class _Block(BaseModel)` — Encapsulates block. Receives: `constructor arguments and class fields`. Sends: `_Block`.
- L37 `class _Page(BaseModel)` — Encapsulates page. Receives: `constructor arguments and class fields`. Sends: `_Page`.
- L41 `class _Annotation(BaseModel)` — Encapsulates annotation. Receives: `constructor arguments and class fields`. Sends: `_Annotation`.
- L46 `class _ProviderError(BaseModel)` — Encapsulates providererror. Receives: `constructor arguments and class fields`. Sends: `_ProviderError`.
- L51 `class _ImageResponse(BaseModel)` — Encapsulates imageresponse. Receives: `constructor arguments and class fields`. Sends: `_ImageResponse`.
- L56 `class _BatchResponse(BaseModel)` — Encapsulates batchresponse. Receives: `constructor arguments and class fields`. Sends: `_BatchResponse`.
- L60 `def _bounding_box(polygon: _Polygon | None) -> BoundingBox | None` — Implements bounding box. Receives: `polygon: _Polygon | None`. Sends: `BoundingBox | None`.
- L70 `def normalize_response(payload: object) -> tuple[str, list[OCRWord]]` — Normalizes response. Receives: `payload: object`. Sends: `tuple[str, list[OCRWord]]`.
- L96 `def minimum_word_confidence(words: list[OCRWord]) -> float | None` — Implements minimum word confidence. Receives: `words: list[OCRWord]`. Sends: `float | None`.

### [`backend/app/services/document_ingestion/recognition/htr.py`](../../backend/app/services/document_ingestion/recognition/htr.py)

Purpose: Owns htr behavior for the backend runtime.

- L11 `class ReviewRequiredHTRRecognizer` — Encapsulates reviewrequiredhtrrecognizer. Receives: `constructor arguments and class fields`. Sends: `ReviewRequiredHTRRecognizer`.
- L12 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize. Receives: `self, region: RenderedRegion`. Sends: `RecognitionResult`.

### [`backend/app/services/document_ingestion/recognition/typhoon.py`](../../backend/app/services/document_ingestion/recognition/typhoon.py)

Purpose: Owns typhoon behavior for the backend runtime.

- L31 `class TyphoonRecognizerConfig` — Encapsulates typhoonrecognizerconfig. Receives: `constructor arguments and class fields`. Sends: `TyphoonRecognizerConfig`.
- L39 `def _prepare_messages(image_bytes: bytes, target_image_dimension: int)` — Implements prepare messages. Receives: `image_bytes: bytes, target_image_dimension: int`. Sends: `inferred or None`.
- L62 `class TyphoonDocumentRecognizer` — Encapsulates typhoondocumentrecognizer. Receives: `constructor arguments and class fields`. Sends: `TyphoonDocumentRecognizer`.
- L63 `def __init__(self, config: TyphoonRecognizerConfig) -> None` — Implements init. Receives: `self, config: TyphoonRecognizerConfig`. Sends: `None`.
- L66 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L76 `async def recognize(self, region: RenderedRegion) -> RecognitionResult` — Implements recognize. Receives: `self, region: RenderedRegion`. Sends: `RecognitionResult`.
- L87 `async def _request(self, image_bytes: bytes) -> tuple[str, list[str], Any]` — Implements request. Receives: `self, image_bytes: bytes`. Sends: `tuple[str, list[str], Any]`.
- L117 `async def _post(self, messages: list[dict[str, Any]]) -> Any` — Implements post. Receives: `self, messages: list[dict[str, Any]]`. Sends: `Any`.

### [`backend/app/services/document_ingestion/recognized_region.py`](../../backend/app/services/document_ingestion/recognized_region.py)

Purpose: Owns recognized region behavior for the backend runtime.

- L19 `def build_unified_region(page: RenderedPage, recognized: RecognizedPage) -> DocumentRegion` — Builds unified region. Receives: `page: RenderedPage, recognized: RecognizedPage`. Sends: `DocumentRegion`.

### [`backend/app/services/document_ingestion/region_pipeline.py`](../../backend/app/services/document_ingestion/region_pipeline.py)

Purpose: Owns region pipeline behavior for the backend runtime.

- L33 `class RegionRecognitionPipeline` — Encapsulates regionrecognitionpipeline. Receives: `constructor arguments and class fields`. Sends: `RegionRecognitionPipeline`.
- L34 `def __init__(self, segmenter: DocumentRegionSegmenter, router: RegionRouter, ocr_recognizer: OCRRecognizer, htr_recognizer: HTRRecognizer) -> None` — Implements init. Receives: `self, segmenter: DocumentRegionSegmenter, router: RegionRouter, ocr_recognizer: OCRRecognizer, htr_recognizer: HTRRecognizer`. Sends: `None`.
- L46 `async def process(self, page: RenderedPage) -> tuple[DocumentPage, list[str]]` — Executes process. Receives: `self, page: RenderedPage`. Sends: `tuple[DocumentPage, list[str]]`.
- L75 `async def _recognize_region(self, page: RenderedPage, segmented_region: SegmentedRegion, route: RegionRoute) -> DocumentRegion` — Implements recognize region. Receives: `self, page: RenderedPage, segmented_region: SegmentedRegion, route: RegionRoute`. Sends: `DocumentRegion`.
- L116 `def _result_region(segmented_region: SegmentedRegion, result: RecognitionResult) -> DocumentRegion` — Implements result region. Receives: `segmented_region: SegmentedRegion, result: RecognitionResult`. Sends: `DocumentRegion`.
- L158 `def _empty_region(segmented_region: SegmentedRegion, route: RegionRoute, warning: str | None=None) -> DocumentRegion` — Implements empty region. Receives: `segmented_region: SegmentedRegion, route: RegionRoute, warning: str | None=None`. Sends: `DocumentRegion`.
- L179 `def _count_route(summary: RoutingSummary, region: SegmentedRegion, route: RegionRoute) -> None` — Implements count route. Receives: `summary: RoutingSummary, region: SegmentedRegion, route: RegionRoute`. Sends: `None`.
- L193 `def _build_blocks(page: RenderedPage, regions: list[DocumentRegion]) -> list[DocumentBlock]` — Builds blocks. Receives: `page: RenderedPage, regions: list[DocumentRegion]`. Sends: `list[DocumentBlock]`.

### [`backend/app/services/document_ingestion/rendering.py`](../../backend/app/services/document_ingestion/rendering.py)

Purpose: Owns rendering behavior for the backend runtime.

- L11 `def _encode_png(image: Image.Image) -> bytes` — Serializes png. Receives: `image: Image.Image`. Sends: `bytes`.
- L17 `def render_pdf_page(content: bytes, page_number: int, longest_edge: int) -> bytes` — Renders pdf page. Receives: `content: bytes, page_number: int, longest_edge: int`. Sends: `bytes`.
- L38 `def normalize_image(content: bytes, longest_edge: int, max_pixels: int) -> bytes` — Normalizes image. Receives: `content: bytes, longest_edge: int, max_pixels: int`. Sends: `bytes`.
- L56 `def image_dimensions(content: bytes) -> tuple[int, int]` — Implements image dimensions. Receives: `content: bytes`. Sends: `tuple[int, int]`.
- L64 `def crop_image_region(content: bytes, bbox: BoundingBox) -> bytes` — Implements crop image region. Receives: `content: bytes, bbox: BoundingBox`. Sends: `bytes`.

### [`backend/app/services/document_ingestion/routing/__init__.py`](../../backend/app/services/document_ingestion/routing/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/routing/region_router.py`](../../backend/app/services/document_ingestion/routing/region_router.py)

Purpose: Owns region router behavior for the backend runtime.

- L13 `class RegionRoute` — Encapsulates regionroute. Receives: `constructor arguments and class fields`. Sends: `RegionRoute`.
- L20 `class RegionRouter` — Encapsulates regionrouter. Receives: `constructor arguments and class fields`. Sends: `RegionRouter`.
- L21 `def __init__(self, mixed_policy: str, unknown_policy: str, htr_enabled: bool=False) -> None` — Implements init. Receives: `self, mixed_policy: str, unknown_policy: str, htr_enabled: bool=False`. Sends: `None`.
- L31 `def route(self, region: SegmentedRegion) -> RegionRoute` — Implements route. Receives: `self, region: SegmentedRegion`. Sends: `RegionRoute`.
- L53 `def _machine_route(method: RecognitionMethod) -> RegionRoute` — Implements machine route. Receives: `method: RecognitionMethod`. Sends: `RegionRoute`.
- L61 `def _review_route(method: RecognitionMethod) -> RegionRoute` — Implements review route. Receives: `method: RecognitionMethod`. Sends: `RegionRoute`.
- L69 `def _fallback(policy: str) -> RegionRoute` — Implements fallback. Receives: `policy: str`. Sends: `RegionRoute`.
- L75 `def _disabled_htr_route() -> RegionRoute` — Implements disabled htr route. Receives: `not applicable`. Sends: `RegionRoute`.

### [`backend/app/services/document_ingestion/segmentation/__init__.py`](../../backend/app/services/document_ingestion/segmentation/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/document_ingestion/segmentation/base.py`](../../backend/app/services/document_ingestion/segmentation/base.py)

Purpose: Owns base behavior for the backend runtime.

- L9 `class SegmentedRegion` — Encapsulates segmentedregion. Receives: `constructor arguments and class fields`. Sends: `SegmentedRegion`.
- L19 `class SegmentedPage` — Encapsulates segmentedpage. Receives: `constructor arguments and class fields`. Sends: `SegmentedPage`.
- L24 `class DocumentRegionSegmenter(Protocol)` — Encapsulates documentregionsegmenter. Receives: `constructor arguments and class fields`. Sends: `DocumentRegionSegmenter`.
- L25 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page. Receives: `self, page: RenderedPage`. Sends: `SegmentedPage`.

### [`backend/app/services/document_ingestion/segmentation/whole_page.py`](../../backend/app/services/document_ingestion/segmentation/whole_page.py)

Purpose: Owns whole page behavior for the backend runtime.

- L11 `class WholePageRegionSegmenter` — Encapsulates wholepageregionsegmenter. Receives: `constructor arguments and class fields`. Sends: `WholePageRegionSegmenter`.
- L12 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page. Receives: `self, page: RenderedPage`. Sends: `SegmentedPage`.

### [`backend/app/services/document_ingestion/service.py`](../../backend/app/services/document_ingestion/service.py)

Purpose: Owns service behavior for the backend runtime.

- L40 `class DocumentIngestionLimits` — Encapsulates documentingestionlimits. Receives: `constructor arguments and class fields`. Sends: `DocumentIngestionLimits`.
- L47 `class DocumentIngestionService` — Encapsulates documentingestionservice. Receives: `constructor arguments and class fields`. Sends: `DocumentIngestionService`.
- L48 `def __init__(self, recognizer: DocumentRecognizer, limits: DocumentIngestionLimits, native_text_policy: NativeTextPolicy | None=None, region_pipeline: RegionRecognitionPipeline | None=None) -> None` — Implements init. Receives: `self, recognizer: DocumentRecognizer, limits: DocumentIngestionLimits, native_text_policy: NativeTextPolicy | None=None, region_pipeline: RegionRecognitionPipeline | None=None`. Sends: `None`.
- L60 `async def ingest(self, content: bytes, filename: str, mode: IngestionMode=IngestionMode.UNIFIED) -> IngestedDocument` — Implements ingest. Receives: `self, content: bytes, filename: str, mode: IngestionMode=IngestionMode.UNIFIED`. Sends: `IngestedDocument`.
- L92 `def _validate_content(self, content: bytes) -> None` — Validates content. Receives: `self, content: bytes`. Sends: `None`.
- L101 `async def _ingest_pdf(self, content: bytes, document_id: str, mode: IngestionMode) -> tuple[list[DocumentPage], list[str], ExtractionMethod]` — Implements ingest pdf. Receives: `self, content: bytes, document_id: str, mode: IngestionMode`. Sends: `tuple[list[DocumentPage], list[str], ExtractionMethod]`.
- L154 `async def _ingest_image(self, content: bytes, document_id: str, mode: IngestionMode) -> tuple[list[DocumentPage], list[str]]` — Implements ingest image. Receives: `self, content: bytes, document_id: str, mode: IngestionMode`. Sends: `tuple[list[DocumentPage], list[str]]`.
- L170 `async def _process_rendered_page(self, rendered_page: RenderedPage, mode: IngestionMode) -> tuple[DocumentPage, list[str]]` — Executes rendered page. Receives: `self, rendered_page: RenderedPage, mode: IngestionMode`. Sends: `tuple[DocumentPage, list[str]]`.
- L184 `async def _recognize_page(self, rendered_page: RenderedPage) -> tuple[DocumentPage, str | None]` — Implements recognize page. Receives: `self, rendered_page: RenderedPage`. Sends: `tuple[DocumentPage, str | None]`.
- L227 `def _native_page(document_id: str, page_number: int, texts: list[str]) -> DocumentPage` — Implements native page. Receives: `document_id: str, page_number: int, texts: list[str]`. Sends: `DocumentPage`.
- L245 `def _safe_filename(filename: str) -> str` — Implements safe filename. Receives: `filename: str`. Sends: `str`.

### [`backend/app/services/followup/__init__.py`](../../backend/app/services/followup/__init__.py)

Purpose: Gap Analysis and Follow-Up / Clarification Policy Package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/followup/case_clarification.py`](../../backend/app/services/followup/case_clarification.py)

Purpose: Owns case clarification behavior for the backend runtime.

- L23 `class CaseClarificationError(Exception)` — Encapsulates caseclarificationerror. Receives: `constructor arguments and class fields`. Sends: `CaseClarificationError`.
- L24 `def __init__(self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT) -> None` — Implements init. Receives: `self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT`. Sends: `None`.
- L31 `async def create_pending_clarification(db: AsyncSession, *, case_id: UUID, result_id: UUID, snapshot_id: UUID, question: str, metadata: dict[str, object]) -> CaseClarification` — Creates pending clarification. Receives: `db: AsyncSession, *, case_id: UUID, result_id: UUID, snapshot_id: UUID, question: str, metadata: dict[str, object]`. Sends: `CaseClarification`.
- L73 `async def supersede_prior_clarifications(db: AsyncSession, *, case_id: UUID, result_id: UUID) -> None` — Implements supersede prior clarifications. Receives: `db: AsyncSession, *, case_id: UUID, result_id: UUID`. Sends: `None`.
- L90 `async def get_owned_clarifications(db: AsyncSession, *, case_id: UUID, user_id: UUID | None) -> list[CaseClarification]` — Retrieves owned clarifications. Receives: `db: AsyncSession, *, case_id: UUID, user_id: UUID | None`. Sends: `list[CaseClarification]`.
- L105 `async def submit_clarification_answer(db: AsyncSession, *, case_id: UUID, clarification_id: UUID, user_id: UUID | None, request: CaseClarificationAnswer) -> tuple[CaseClarification, CaseRun]` — Implements submit clarification answer. Receives: `db: AsyncSession, *, case_id: UUID, clarification_id: UUID, user_id: UUID | None, request: CaseClarificationAnswer`. Sends: `tuple[CaseClarification, CaseRun]`.
- L211 `async def _owned_case(db: AsyncSession, case_id: UUID, user_id: UUID | None, *, lock: bool=False) -> Case` — Implements owned case. Receives: `db: AsyncSession, case_id: UUID, user_id: UUID | None, *, lock: bool=False`. Sends: `Case`.
- L227 `async def _locked_case_thread(db: AsyncSession, case: Case) -> ChatThread` — Implements locked case thread. Receives: `db: AsyncSession, case: Case`. Sends: `ChatThread`.
- L236 `async def find_answered_clarification(db: AsyncSession, *, case_id: UUID, request: CaseClarificationAnswer) -> CaseClarification | None` — Implements find answered clarification. Receives: `db: AsyncSession, *, case_id: UUID, request: CaseClarificationAnswer`. Sends: `CaseClarification | None`.
- L251 `def answer_fingerprint(request: CaseClarificationAnswer) -> str` — Implements answer fingerprint. Receives: `request: CaseClarificationAnswer`. Sends: `str`.

### [`backend/app/services/followup/claim_transport.py`](../../backend/app/services/followup/claim_transport.py)

Purpose: Owns claim transport behavior for the backend runtime.

- L12 `class GapAnalysisClaim(BaseModel)` — Encapsulates gapanalysisclaim. Receives: `constructor arguments and class fields`. Sends: `GapAnalysisClaim`.
- L28 `def build_gap_analysis_claim_transport(claims: Sequence[Mapping[str, object]]) -> list[dict[str, object]]` — Builds gap analysis claim transport. Receives: `claims: Sequence[Mapping[str, object]]`. Sends: `list[dict[str, object]]`.

### [`backend/app/services/followup/context.py`](../../backend/app/services/followup/context.py)

Purpose: Owns context behavior for the backend runtime.

- L15 `def build_bounded_context(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, gap_analysis: GapAnalysis | Mapping[str, object] | None=None) -> dict[str, object]` — Build the context payload for Gap Analysis and Follow-up Policy. Receives: `*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, gap_analysis: GapAnalysis | Mapping[str, object] | None=None`. Sends: `dict[str, object]`.
- L96 `def _build_overflow_followup_context(*, original_user_content: str, exchanges: list[dict[str, object]], raw_evidence: str | None, gap_analysis: Any, analysis_answer: str | None, analysis_context: Mapping[str, object] | None, token_budget: int) -> dict[str, object]` — Reduce optional context before authoritative evidence during overflow. Receives: `*, original_user_content: str, exchanges: list[dict[str, object]], raw_evidence: str | None, gap_analysis: Any, analysis_answer: str | None, analysis_context: Mapping[str, object] | None, token_budget: int`. Sends: `dict[str, object]`.
- L191 `def _bounded(value: str, limit: int) -> str` — Implements bounded. Receives: `value: str, limit: int`. Sends: `str`.
- L195 `def _bounded_mapping(value: Mapping[str, object], limit: int) -> dict[str, object]` — Implements bounded mapping. Receives: `value: Mapping[str, object], limit: int`. Sends: `dict[str, object]`.

### [`backend/app/services/followup/contracts.py`](../../backend/app/services/followup/contracts.py)

Purpose: Owns contracts behavior for the backend runtime.

- L15 `class FollowUpResolution` — The gate result and the audit record carried into the final message. Receives: `constructor arguments and class fields`. Sends: `FollowUpResolution`.
- L71 `def _answer_indicates_unavailable(answer: str) -> bool` — Implements answer indicates unavailable. Receives: `answer: str`. Sends: `bool`.

### [`backend/app/services/followup/decision.py`](../../backend/app/services/followup/decision.py)

Purpose: Owns decision behavior for the backend runtime.

- L38 `async def evaluate_followup_outcome(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], followup_root_ordinal: int, source_run_id: UUID, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, canonical_trace: AnalysisTraceV3 | None=None, precomputed_gap_stage: GapStageResult | None=None, evidence_sha256: str | None=None, canonical_state_required: bool=False) -> FollowUpResolution` — Implements evaluate followup outcome. Receives: `*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], followup_root_ordinal: int, source_run_id: UUID, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, canonical_trace: AnalysisTraceV3 | None=None, precomputed_gap_stage: GapStageResult | None=None, evidence_sha256: str | None=None, canonical_state_required: bool=False`. Sends: `FollowUpResolution`.
- L60 `def proceed_resolution(*, reason_code: str, stop_reason: str, **metadata_kwargs: Any) -> FollowUpResolution` — Implements proceed resolution. Receives: `*, reason_code: str, stop_reason: str, **metadata_kwargs: Any`. Sends: `FollowUpResolution`.
- L83 `def ask_resolution(*, selected_gap, question: str, reason_code: str, stop_reason: str, decision_source: str, policy_decision: str, **metadata_kwargs: Any) -> FollowUpResolution` — Implements ask resolution. Receives: `*, selected_gap, question: str, reason_code: str, stop_reason: str, decision_source: str, policy_decision: str, **metadata_kwargs: Any`. Sends: `FollowUpResolution`.

### [`backend/app/services/followup/gap_analysis.py`](../../backend/app/services/followup/gap_analysis.py)

Purpose: Provider-backed detection of case-specific analytical gaps.

- L32 `class AnthropicGapAnalysis` — Run the bounded Gap Analysis stage through the configured core LLM. Receives: `constructor arguments and class fields`. Sends: `AnthropicGapAnalysis`.
- L35 `async def analyze(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, client: httpx.AsyncClient | None=None) -> GapAnalysisResult` — Implements analyze. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None, client: httpx.AsyncClient | None=None`. Sends: `GapAnalysisResult`.
- L114 `async def _post(client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]) -> tuple[dict[str, object], int | None, int | None]` — Implements post. Receives: `client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]`. Sends: `tuple[dict[str, object], int | None, int | None]`.
- L154 `def _nonnegative_int(value: object) -> int | None` — Implements nonnegative int. Receives: `value: object`. Sends: `int | None`.

### [`backend/app/services/followup/gap_stage.py`](../../backend/app/services/followup/gap_stage.py)

Purpose: Owns gap stage behavior for the backend runtime.

- L32 `class GapStageResult` — Encapsulates gapstageresult. Receives: `constructor arguments and class fields`. Sends: `GapStageResult`.
- L40 `async def run_gap_analysis_stage(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None, raw_evidence: str | None, analysis_answer: str | None, analysis_context: Mapping[str, object] | None, analysis_claims: Sequence[Mapping[str, object]] | None, source_run_id: UUID) -> GapStageResult` — Executes gap analysis stage. Receives: `*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None, raw_evidence: str | None, analysis_answer: str | None, analysis_context: Mapping[str, object] | None, analysis_claims: Sequence[Mapping[str, object]] | None, source_run_id: UUID`. Sends: `GapStageResult`.

### [`backend/app/services/followup/helpers.py`](../../backend/app/services/followup/helpers.py)

Purpose: Owns helpers behavior for the backend runtime.

- L23 `def _coerce_gap_analysis_result(raw_result: object, *, elapsed_ms: float) -> GapAnalysisResult` — Implements coerce gap analysis result. Receives: `raw_result: object, *, elapsed_ms: float`. Sends: `GapAnalysisResult`.
- L51 `def _normalize_gap_analysis_semantics(analysis: GapAnalysis) -> GapAnalysis` — Normalizes gap analysis semantics. Receives: `analysis: GapAnalysis`. Sends: `GapAnalysis`.
- L67 `def _gap_reason_code(gap: GapItem) -> str` — Implements gap reason code. Receives: `gap: GapItem`. Sends: `str`.
- L76 `def _coerce_policy_result(raw_result: object, *, elapsed_ms: float) -> FollowUpPolicyResult` — Implements coerce policy result. Receives: `raw_result: object, *, elapsed_ms: float`. Sends: `FollowUpPolicyResult`.
- L100 `def _safe_token_count(value: object) -> int | None` — Implements safe token count. Receives: `value: object`. Sends: `int | None`.
- L106 `def _followup_failure_code(error: Exception) -> str` — Implements followup failure code. Receives: `error: Exception`. Sends: `str`.
- L114 `def _normalized_question(question: str) -> str` — Implements normalized question. Receives: `question: str`. Sends: `str`.

### [`backend/app/services/followup/metadata.py`](../../backend/app/services/followup/metadata.py)

Purpose: Owns metadata behavior for the backend runtime.

- L18 `def empty_gap_analysis_trace(*, status: str='not_run', latency_ms: float | None=None, failure_code: str | None=None) -> dict[str, Any]` — Implements empty gap analysis trace. Receives: `*, status: str='not_run', latency_ms: float | None=None, failure_code: str | None=None`. Sends: `dict[str, Any]`.
- L38 `def gap_analysis_trace(result: GapAnalysisResult) -> dict[str, Any]` — Implements gap analysis trace. Receives: `result: GapAnalysisResult`. Sends: `dict[str, Any]`.
- L53 `def followup_metadata(*, source_run_id: UUID, followup_root_ordinal: int, round_number: int, prior_exchange_count: int, action: str, question: str, reason_code: str, stop_reason: str, latency_ms: float | None=None, input_tokens: int | None=None, output_tokens: int | None=None, provider: str | None=None, model: str | None=None, failure_code: str | None=None, decision: str | None=None, decision_source: str | None=None, policy_decision: str | None=None, selected_gap: str | None=None, selected_gap_detail: dict[str, Any] | None=None, requested_selected_gap: str | None=None, followup_context: dict[str, str] | None=None, gap_analysis: dict[str, Any] | None=None, rag_skipped: bool=True, rag_invoked: bool=False) -> dict[str, Any]` — Implements followup metadata. Receives: `*, source_run_id: UUID, followup_root_ordinal: int, round_number: int, prior_exchange_count: int, action: str, question: str, reason_code: str, stop_reason: str, latency_ms: float | None=None, input_tokens: int | None=None, output_tokens: int | None=None, provider: str | None=None, model: str | None=None, failure_code: str | None=None, decision: str | None=None, decision_source: str | None=None, policy_decision: str | None=None, selected_gap: str | None=None, selected_gap_detail: dict[str, Any] | None=None, requested_selected_gap: str | None=None, followup_context: dict[str, str] | None=None, gap_analysis: dict[str, Any] | None=None, rag_skipped: bool=True, rag_invoked: bool=False`. Sends: `dict[str, Any]`.

### [`backend/app/services/followup/policy.py`](../../backend/app/services/followup/policy.py)

Purpose: Select one user follow-up from a previously computed Gap Analysis.

- L33 `def build_clarified_query(*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]) -> str` — Build one bounded legacy `/query` request containing untrusted case data. Receives: `*, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]`. Sends: `str`.
- L64 `def render() -> str` — Renders render. Receives: `not applicable`. Sends: `str`.
- L105 `class AnthropicFollowUpPolicy` — Run the second, decision-only stage against Gap Analysis output. Receives: `constructor arguments and class fields`. Sends: `AnthropicFollowUpPolicy`.
- L108 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None) -> FollowUpDecision` — Implements decide. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None`. Sends: `FollowUpDecision`.
- L130 `async def decide_with_metadata(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None) -> FollowUpPolicyResult` — Implements decide with metadata. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis | Mapping[str, object] | None=None, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, client: httpx.AsyncClient | None=None`. Sends: `FollowUpPolicyResult`.
- L209 `async def _post(client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]) -> FollowUpPolicyResult` — Implements post. Receives: `client: httpx.AsyncClient, messages_url: str, request_payload: dict[str, object], headers: dict[str, str]`. Sends: `FollowUpPolicyResult`.
- L249 `def _normalize_gap_analysis(value: GapAnalysis | Mapping[str, object] | None) -> GapAnalysis` — Normalizes gap analysis. Receives: `value: GapAnalysis | Mapping[str, object] | None`. Sends: `GapAnalysis`.
- L259 `def _bounded(value: str, limit: int) -> str` — Implements bounded. Receives: `value: str, limit: int`. Sends: `str`.
- L263 `def _nonnegative_int(value: object) -> int | None` — Implements nonnegative int. Receives: `value: object`. Sends: `int | None`.

### [`backend/app/services/followup/prompts.py`](../../backend/app/services/followup/prompts.py)

Purpose: Prompts and bounded provider payloads for the two follow-up stages.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/followup/response_content.py`](../../backend/app/services/followup/response_content.py)

Purpose: Owns response content behavior for the backend runtime.

- L12 `def _extract_llm_text(payload: Mapping[str, object] | object) -> str` — Extract raw text across supported provider response shapes (Anthropic, OpenRouter, etc.). Receives: `payload: Mapping[str, object] | object`. Sends: `str`.
- L42 `def _extract_text_value(value: object) -> str` — Extracts text value. Receives: `value: object`. Sends: `str`.
- L75 `def _extract_llm_json(raw: str) -> dict[str, object]` — Extracts llm json. Receives: `raw: str`. Sends: `dict[str, object]`.

### [`backend/app/services/followup/schemas.py`](../../backend/app/services/followup/schemas.py)

Purpose: Strict contracts shared by gap analysis and follow-up policy.

- L44 `class GapItem(BaseModel)` — One incident-specific information gap found in the current analysis. Receives: `constructor arguments and class fields`. Sends: `GapItem`.
- L59 `def normalize_status(cls, value: object) -> object` — Normalizes status. Receives: `cls, value: object`. Sends: `object`.
- L81 `def normalize_priority(cls, value: object) -> object` — Normalizes priority. Receives: `cls, value: object`. Sends: `object`.
- L97 `def validate_text(cls, value: str) -> str` — Validates text. Receives: `cls, value: str`. Sends: `str`.
- L106 `def explicitly_unknown_is_not_askable(self) -> 'GapItem'` — Implements explicitly unknown is not askable. Receives: `self`. Sends: `'GapItem'`.
- L112 `class GapAnalysis(BaseModel)` — All relevant gaps detected for one completed Main Case Analysis. Receives: `constructor arguments and class fields`. Sends: `GapAnalysis`.
- L121 `class GapAnalysisResult` — Gap output plus provider telemetry; never an evidence mutation. Receives: `constructor arguments and class fields`. Sends: `GapAnalysisResult`.
- L132 `class FollowUpDecision(BaseModel)` — One bounded decision made from an already-computed Gap Analysis. Receives: `constructor arguments and class fields`. Sends: `FollowUpDecision`.
- L143 `def normalize_decision_mode(cls, value: object) -> object` — Normalizes decision mode. Receives: `cls, value: object`. Sends: `object`.
- L155 `def validate_selected_gap(cls, value: object) -> str | None` — Validates selected gap. Receives: `cls, value: object`. Sends: `str | None`.
- L168 `def validate_decision(self) -> 'FollowUpDecision'` — Validates decision. Receives: `self`. Sends: `'FollowUpDecision'`.
- L189 `class FollowUpPolicyResult` — Decision plus safe provider metrics when the adapter supplies them. Receives: `constructor arguments and class fields`. Sends: `FollowUpPolicyResult`.
- L201 `class ClarificationExchange` — Encapsulates clarificationexchange. Receives: `constructor arguments and class fields`. Sends: `ClarificationExchange`.
- L212 `class GapAnalyzer(Protocol)` — Encapsulates gapanalyzer. Receives: `constructor arguments and class fields`. Sends: `GapAnalyzer`.
- L213 `async def analyze(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None) -> GapAnalysisResult` — Implements analyze. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None, analysis_claims: Sequence[Mapping[str, object]] | None=None`. Sends: `GapAnalysisResult`.
- L225 `class FollowUpPolicy(Protocol)` — Encapsulates followuppolicy. Receives: `constructor arguments and class fields`. Sends: `FollowUpPolicy`.
- L226 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None) -> FollowUpDecision` — Implements decide. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange], gap_analysis: GapAnalysis, raw_evidence: str | None=None, analysis_answer: str | None=None, analysis_context: Mapping[str, object] | None=None`. Sends: `FollowUpDecision`.

### [`backend/app/services/followup/stateful.py`](../../backend/app/services/followup/stateful.py)

Purpose: Owns stateful behavior for the backend runtime.

- L48 `def normalize_gap_key(topic: str) -> str` — Normalizes gap key. Receives: `topic: str`. Sends: `str`.
- L67 `def apply_clarification_history(analysis: GapAnalysis, exchanges: Sequence[ClarificationExchange]) -> GapAnalysis` — Implements apply clarification history. Receives: `analysis: GapAnalysis, exchanges: Sequence[ClarificationExchange]`. Sends: `GapAnalysis`.
- L87 `def exhausted_gap_keys(exchanges: Sequence[ClarificationExchange]) -> set[str]` — Implements exhausted gap keys. Receives: `exchanges: Sequence[ClarificationExchange]`. Sends: `set[str]`.
- L99 `def unavailable_gap_keys(exchanges: Sequence[ClarificationExchange]) -> set[str]` — Implements unavailable gap keys. Receives: `exchanges: Sequence[ClarificationExchange]`. Sends: `set[str]`.
- L111 `def select_next_gap(gaps: Sequence[AnalysisGapV3 | GapItem], exchanges: Sequence[ClarificationExchange]) -> AnalysisGapV3 | GapItem | None` — Extracts next gap. Receives: `gaps: Sequence[AnalysisGapV3 | GapItem], exchanges: Sequence[ClarificationExchange]`. Sends: `AnalysisGapV3 | GapItem | None`.
- L136 `def policy_gap(gap: AnalysisGapV3 | GapItem) -> GapItem` — Implements policy gap. Receives: `gap: AnalysisGapV3 | GapItem`. Sends: `GapItem`.
- L150 `def relevant_claim_context(trace: AnalysisTraceV3, gap: AnalysisGapV3) -> dict[str, object]` — Implements relevant claim context. Receives: `trace: AnalysisTraceV3, gap: AnalysisGapV3`. Sends: `dict[str, object]`.
- L168 `def followup_context(gap: AnalysisGapV3 | GapItem, *, evidence_sha256: str | None) -> dict[str, str]` — Implements followup context. Receives: `gap: AnalysisGapV3 | GapItem, *, evidence_sha256: str | None`. Sends: `dict[str, str]`.
- L185 `def clarification_answer_context(question_message_id: str, context: Mapping[str, object]) -> dict[str, str]` — Implements clarification answer context. Receives: `question_message_id: str, context: Mapping[str, object]`. Sends: `dict[str, str]`.
- L203 `def _exchange_gap_key(exchange: ClarificationExchange) -> str | None` — Implements exchange gap key. Receives: `exchange: ClarificationExchange`. Sends: `str | None`.
- L211 `def _has_claim_links(gap: AnalysisGapV3 | GapItem) -> bool` — Determines claim links. Receives: `gap: AnalysisGapV3 | GapItem`. Sends: `bool`.

### [`backend/app/services/llm/__init__.py`](../../backend/app/services/llm/__init__.py)

Purpose: Core LLM Provider & Structured Output Infrastructure.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/llm/core_llm.py`](../../backend/app/services/llm/core_llm.py)

Purpose: Resolve the single production chat LLM provider without fallback.

- L15 `class CoreLlmConfigurationError(RuntimeError)` — The selected production provider is missing required configuration. Receives: `constructor arguments and class fields`. Sends: `CoreLlmConfigurationError`.
- L18 `def __init__(self, provider: CoreLlmProvider, key_env_name: str) -> None` — Implements init. Receives: `self, provider: CoreLlmProvider, key_env_name: str`. Sends: `None`.
- L28 `class CoreLlmTarget` — Encapsulates corellmtarget. Receives: `constructor arguments and class fields`. Sends: `CoreLlmTarget`.
- L37 `def resolve_core_llm_target(feature_anthropic_model: str, *, require_key: bool=True, configured_settings: Settings | None=None) -> CoreLlmTarget` — Return the exact selected target for an Anthropic-format feature call. Receives: `feature_anthropic_model: str, *, require_key: bool=True, configured_settings: Settings | None=None`. Sends: `CoreLlmTarget`.

### [`backend/app/services/llm/model_registry.py`](../../backend/app/services/llm/model_registry.py)

Purpose: Central OpenRouter model registry, curated presets, and alias resolver for Backend services.

- L12 `class ModelPreset` — Encapsulates modelpreset. Receives: `constructor arguments and class fields`. Sends: `ModelPreset`.
- L72 `def resolve_openrouter_model(model_name_or_alias: str | None) -> str` — Resolve an alias or model name to its canonical OpenRouter model string. Receives: `model_name_or_alias: str | None`. Sends: `str`.
- L92 `def list_available_models() -> list[dict[str, object]]` — Return catalog list of all curated ready-selection models with their metadata. Receives: `not applicable`. Sends: `list[dict[str, object]]`.
- L110 `def format_model_table() -> str` — Render formatted ASCII comparison table of curated ready-selection models. Receives: `not applicable`. Sends: `str`.

### [`backend/app/services/llm/structured_output.py`](../../backend/app/services/llm/structured_output.py)

Purpose: Provider-facing JSON Schema and request helpers for structured model output.

- L63 `def anthropic_json_schema(model: type[BaseModel]) -> dict[str, Any]` — Build an Anthropic-compatible schema without weakening local validation. Receives: `model: type[BaseModel]`. Sends: `dict[str, Any]`.
- L77 `def structured_output_schema(model: type[BaseModel], *, provider: CoreLlmProvider) -> dict[str, Any]` — Build the provider-specific structured-output schema for ``model``. Receives: `model: type[BaseModel], *, provider: CoreLlmProvider`. Sends: `dict[str, Any]`.
- L93 `def structured_output_request_options(*, provider: CoreLlmProvider, feature: StructuredOutputFeature, configured_max_tokens: int, temperature: float | None=None) -> dict[str, object]` — Return only the provider-specific structured-output request options. Receives: `*, provider: CoreLlmProvider, feature: StructuredOutputFeature, configured_max_tokens: int, temperature: float | None=None`. Sends: `dict[str, object]`.
- L125 `def _normalize_schema(value: object) -> object` — Normalizes schema. Receives: `value: object`. Sends: `object`.
- L151 `def _require_all_object_properties(value: object) -> None` — Implements require all object properties. Receives: `value: object`. Sends: `None`.

### [`backend/app/services/llm/token_budget.py`](../../backend/app/services/llm/token_budget.py)

Purpose: Token budgeting, estimation, and context-window allocation for LLM prompts.

- L17 `def _get_tiktoken_encoding(encoding_name: str='cl100k_base')` — Retrieves tiktoken encoding. Receives: `encoding_name: str='cl100k_base'`. Sends: `inferred or None`.
- L31 `def estimate_tokens(text: str | None, encoding_name: str='cl100k_base') -> int` — Estimate token count for a string using tiktoken with conservative fallback. Receives: `text: str | None, encoding_name: str='cl100k_base'`. Sends: `int`.
- L47 `def estimate_json_tokens(data: Any, encoding_name: str='cl100k_base') -> int` — Estimate token count for a JSON-serializable data structure. Receives: `data: Any, encoding_name: str='cl100k_base'`. Sends: `int`.
- L61 `def get_safe_input_token_budget() -> int` — Return the safe input token budget for the active model context window. Receives: `not applicable`. Sends: `int`.
- L78 `class ContextBudgetDiagnostics` — Encapsulates contextbudgetdiagnostics. Receives: `constructor arguments and class fields`. Sends: `ContextBudgetDiagnostics`.
- L88 `def to_dict(self) -> dict[str, Any]` — Transforms dict. Receives: `self`. Sends: `dict[str, Any]`.
- L92 `def log_context_budget_diagnostics(*, feature: str, estimated_input_tokens: int, configured_input_token_budget: int, raw_evidence: str | None=None, external_context: Any=None, context_truncated: bool=False, retained_evidence_ratio: float=1.0, retained_external_context_ratio: float=1.0) -> ContextBudgetDiagnostics` — Implements log context budget diagnostics. Receives: `*, feature: str, estimated_input_tokens: int, configured_input_token_budget: int, raw_evidence: str | None=None, external_context: Any=None, context_truncated: bool=False, retained_evidence_ratio: float=1.0, retained_external_context_ratio: float=1.0`. Sends: `ContextBudgetDiagnostics`.

### [`backend/app/services/reports/__init__.py`](../../backend/app/services/reports/__init__.py)

Purpose: Defines the public package surface for the backend runtime.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/reports/case_report_contracts.py`](../../backend/app/services/reports/case_report_contracts.py)

Purpose: Owns case report contracts behavior for the backend runtime.

- L12 `class CaseReportSource(BaseModel)` — Encapsulates casereportsource. Receives: `constructor arguments and class fields`. Sends: `CaseReportSource`.
- L26 `class CaseReportInputSnapshot(BaseModel)` — Encapsulates casereportinputsnapshot. Receives: `constructor arguments and class fields`. Sends: `CaseReportInputSnapshot`.
- L47 `def native_source_ids(snapshot: CaseReportInputSnapshot) -> set[str]` — Implements native source ids. Receives: `snapshot: CaseReportInputSnapshot`. Sends: `set[str]`.
- L51 `def ensure_case_report_snapshot(snapshot: object) -> CaseReportInputSnapshot` — Implements ensure case report snapshot. Receives: `snapshot: object`. Sends: `CaseReportInputSnapshot`.

### [`backend/app/services/reports/case_report_generation.py`](../../backend/app/services/reports/case_report_generation.py)

Purpose: Owns case report generation behavior for the backend runtime.

- L14 `async def run_case_report_generation(snapshot: CaseReportInputSnapshot) -> ReportRunResult` — Executes case report generation. Receives: `snapshot: CaseReportInputSnapshot`. Sends: `ReportRunResult`.

### [`backend/app/services/reports/case_report_pdf.py`](../../backend/app/services/reports/case_report_pdf.py)

Purpose: Owns case report pdf behavior for the backend runtime.

- L25 `def render_case_report_pdf(snapshot: CaseReportInputSnapshot, report: StructuredReport, report_id: UUID) -> bytes` — Renders case report pdf. Receives: `snapshot: CaseReportInputSnapshot, report: StructuredReport, report_id: UUID`. Sends: `bytes`.
- L53 `def _story(snapshot: CaseReportInputSnapshot, report: StructuredReport, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements story. Receives: `snapshot: CaseReportInputSnapshot, report: StructuredReport, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L89 `def _metadata_table(snapshot: CaseReportInputSnapshot, styles: dict[str, ParagraphStyle]) -> Table` — Implements metadata table. Receives: `snapshot: CaseReportInputSnapshot, styles: dict[str, ParagraphStyle]`. Sends: `Table`.
- L121 `def _claim_story(report: StructuredReport, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements claim story. Receives: `report: StructuredReport, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L143 `def _source_story(snapshot: CaseReportInputSnapshot, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements source story. Receives: `snapshot: CaseReportInputSnapshot, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L165 `def _page_chrome(canvas, document, report_id: UUID) -> None` — Implements page chrome. Receives: `canvas, document, report_id: UUID`. Sends: `None`.

### [`backend/app/services/reports/case_report_persistence.py`](../../backend/app/services/reports/case_report_persistence.py)

Purpose: Owns case report persistence behavior for the backend runtime.

- L32 `class CaseReportService` — Encapsulates casereportservice. Receives: `constructor arguments and class fields`. Sends: `CaseReportService`.
- L33 `def __init__(self, db: AsyncSession) -> None` — Implements init. Receives: `self, db: AsyncSession`. Sends: `None`.
- L36 `async def generate_report(self, case_id: UUID, request: CaseReportCreate, user_id: UUID | None) -> ChatReportRead` — Generates report. Receives: `self, case_id: UUID, request: CaseReportCreate, user_id: UUID | None`. Sends: `ChatReportRead`.
- L87 `async def list_reports(self, case_id: UUID, user_id: UUID | None) -> list[ChatReportRead]` — Lists reports. Receives: `self, case_id: UUID, user_id: UUID | None`. Sends: `list[ChatReportRead]`.
- L96 `async def get_report(self, case_id: UUID, report_id: UUID, user_id: UUID | None) -> ChatReportRead` — Retrieves report. Receives: `self, case_id: UUID, report_id: UUID, user_id: UUID | None`. Sends: `ChatReportRead`.
- L105 `async def get_report_pdf(self, case_id: UUID, report_id: UUID, user_id: UUID | None) -> tuple[bytes, str]` — Retrieves report pdf. Receives: `self, case_id: UUID, report_id: UUID, user_id: UUID | None`. Sends: `tuple[bytes, str]`.
- L131 `async def _locked_case(self, case_id: UUID, user_id: UUID | None) -> Case` — Implements locked case. Receives: `self, case_id: UUID, user_id: UUID | None`. Sends: `Case`.
- L137 `async def _owned_case(self, case_id: UUID, user_id: UUID | None) -> Case` — Implements owned case. Receives: `self, case_id: UUID, user_id: UUID | None`. Sends: `Case`.
- L143 `async def _locked_or_create_thread(self, case: Case) -> ChatThread` — Implements locked or create thread. Receives: `self, case: Case`. Sends: `ChatThread`.
- L151 `async def _selected_result(self, case: Case, result_id: UUID | None) -> CaseAnalysisResult` — Implements selected result. Receives: `self, case: Case, result_id: UUID | None`. Sends: `CaseAnalysisResult`.
- L164 `async def _existing_report(self, thread_id: UUID, key: str) -> ChatReport | None` — Implements existing report. Receives: `self, thread_id: UUID, key: str`. Sends: `ChatReport | None`.
- L169 `async def _next_version(self, thread_id: UUID) -> int` — Implements next version. Receives: `self, thread_id: UUID`. Sends: `int`.
- L173 `async def _analysis_message_id(self, thread_id: UUID, result_id: UUID) -> UUID | None` — Implements analysis message id. Receives: `self, thread_id: UUID, result_id: UUID`. Sends: `UUID | None`.
- L185 `async def _report(self, case_id: UUID, report_id: UUID, *, load_thread: bool=False) -> ChatReport` — Implements report. Receives: `self, case_id: UUID, report_id: UUID, *, load_thread: bool=False`. Sends: `ChatReport`.

### [`backend/app/services/reports/case_report_snapshot.py`](../../backend/app/services/reports/case_report_snapshot.py)

Purpose: Owns case report snapshot behavior for the backend runtime.

- L24 `def build_case_report_snapshot(case: Case, result: CaseAnalysisResult, thread: ChatThread) -> CaseReportInputSnapshot` — Builds case report snapshot. Receives: `case: Case, result: CaseAnalysisResult, thread: ChatThread`. Sends: `CaseReportInputSnapshot`.
- L57 `def _validated_trace(result: CaseAnalysisResult, snapshot: CaseEvidenceSnapshot) -> NativeCaseAnalysisTrace` — Implements validated trace. Receives: `result: CaseAnalysisResult, snapshot: CaseEvidenceSnapshot`. Sends: `NativeCaseAnalysisTrace`.
- L82 `def _snapshot_sources(snapshot: CaseEvidenceSnapshot) -> list[CaseReportSource]` — Implements snapshot sources. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `list[CaseReportSource]`.
- L112 `def _ensure_snapshot_hashes(snapshot: CaseEvidenceSnapshot) -> None` — Implements ensure snapshot hashes. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `None`.
- L124 `def _native_sources(snapshot: CaseEvidenceSnapshot) -> tuple[NativeAdmittedSource, ...]` — Implements native sources. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `tuple[NativeAdmittedSource, ...]`.
- L137 `def _document_context(snapshot: CaseEvidenceSnapshot) -> list[dict[str, object]]` — Implements document context. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `list[dict[str, object]]`.

### [`backend/app/services/reports/case_report_template.py`](../../backend/app/services/reports/case_report_template.py)

Purpose: Owns case report template behavior for the backend runtime.

- L13 `def build_case_template_report(snapshot: CaseReportInputSnapshot) -> StructuredReport` — Builds case template report. Receives: `snapshot: CaseReportInputSnapshot`. Sends: `StructuredReport`.
- L103 `def _source_item(source_id: object, revision: int, filename: str | None, text: str) -> str` — Implements source item. Receives: `source_id: object, revision: int, filename: str | None, text: str`. Sends: `str`.
- L110 `def _support_type(claim_type: str) -> str` — Implements support type. Receives: `claim_type: str`. Sends: `str`.

### [`backend/app/services/reports/pdf_chrome.py`](../../backend/app/services/reports/pdf_chrome.py)

Purpose: Owns pdf chrome behavior for the backend runtime.

- L20 `def header_meta_table(view_model: ReportViewModel, *, styles: dict[str, object], width: float) -> Table` — Implements header meta table. Receives: `view_model: ReportViewModel, *, styles: dict[str, object], width: float`. Sends: `Table`.
- L54 `def table_style() -> TableStyle` — Implements table style. Receives: `not applicable`. Sends: `TableStyle`.
- L70 `def draw_page_chrome(canvas, document, *, font_names: tuple[str, str], report_id: str, view_model: ReportViewModel) -> None` — Implements draw page chrome. Receives: `canvas, document, *, font_names: tuple[str, str], report_id: str, view_model: ReportViewModel`. Sends: `None`.

### [`backend/app/services/reports/pdf_design.py`](../../backend/app/services/reports/pdf_design.py)

Purpose: Owns pdf design behavior for the backend runtime.

- L24 `def register_report_fonts() -> tuple[str, str]` — Implements register report fonts. Receives: `not applicable`. Sends: `tuple[str, str]`.
- L56 `def find_report_font(environment_name: str, candidates: tuple[str, ...]) -> str | None` — Implements find report font. Receives: `environment_name: str, candidates: tuple[str, ...]`. Sends: `str | None`.
- L70 `def build_report_styles(font_names: tuple[str, str]) -> dict[str, ParagraphStyle]` — Builds report styles. Receives: `font_names: tuple[str, str]`. Sends: `dict[str, ParagraphStyle]`.
- L94 `def formatted_text(value: object) -> str` — Format markdown text (bold, italic, code, line breaks) into safe ReportLab HTML. Receives: `value: object`. Sends: `str`.
- L106 `def paragraph_text(value: object) -> str` — Implements paragraph text. Receives: `value: object`. Sends: `str`.
- L110 `def plain_text(value: object) -> str` — Implements plain text. Receives: `value: object`. Sends: `str`.

### [`backend/app/services/reports/report_analysis_projection.py`](../../backend/app/services/reports/report_analysis_projection.py)

Purpose: Owns report analysis projection behavior for the backend runtime.

- L34 `def formal_case_title(value: str) -> str` — Implements formal case title. Receives: `value: str`. Sends: `str`.
- L44 `def project_summary_paragraphs(structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage) -> list[str]` — Implements project summary paragraphs. Receives: `structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage`. Sends: `list[str]`.
- L74 `def project_timeline_rows(structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage) -> list[TimelineViewRow]` — Implements project timeline rows. Receives: `structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage`. Sends: `list[TimelineViewRow]`.
- L108 `def _analysis_text(snapshot: ReportInputSnapshot | None) -> str` — Implements analysis text. Receives: `snapshot: ReportInputSnapshot | None`. Sends: `str`.
- L112 `def _trace_summary(snapshot: ReportInputSnapshot | None) -> str` — Implements trace summary. Receives: `snapshot: ReportInputSnapshot | None`. Sends: `str`.
- L120 `def _section_body(text: str, tokens: tuple[str, ...]) -> str` — Implements section body. Receives: `text: str, tokens: tuple[str, ...]`. Sends: `str`.
- L131 `def _list_items(body: str) -> list[str]` — Lists items. Receives: `body: str`. Sends: `list[str]`.
- L143 `def _split_timeline_item(item: str, language: ReportLanguage) -> tuple[str, str]` — Implements split timeline item. Receives: `item: str, language: ReportLanguage`. Sends: `tuple[str, str]`.
- L151 `def _looks_like_time(value: str) -> bool` — Implements looks like time. Receives: `value: str`. Sends: `bool`.
- L163 `def _trace_claims(snapshot: ReportInputSnapshot | None) -> list[dict[str, object]]` — Implements trace claims. Receives: `snapshot: ReportInputSnapshot | None`. Sends: `list[dict[str, object]]`.
- L172 `def _claim_source_ids(claim: dict[str, object]) -> list[str]` — Implements claim source ids. Receives: `claim: dict[str, object]`. Sends: `list[str]`.
- L179 `def _source_ids(structured: StructuredReport | None, snapshot: ReportInputSnapshot | None) -> list[str]` — Implements source ids. Receives: `structured: StructuredReport | None, snapshot: ReportInputSnapshot | None`. Sends: `list[str]`.
- L191 `def _source_label(source_ids: Iterable[str], snapshot: ReportInputSnapshot | None, language: ReportLanguage) -> str` — Implements source label. Receives: `source_ids: Iterable[str], snapshot: ReportInputSnapshot | None, language: ReportLanguage`. Sends: `str`.
- L207 `def _clean_inline(value: object) -> str` — Normalizes inline. Receives: `value: object`. Sends: `str`.
- L216 `def _bounded(value: str, limit: int) -> str` — Implements bounded. Receives: `value: str, limit: int`. Sends: `str`.
- L220 `def _unique(values: Iterable[str]) -> list[str]` — Implements unique. Receives: `values: Iterable[str]`. Sends: `list[str]`.
- L224 `def _plain_text(value: object) -> str` — Implements plain text. Receives: `value: object`. Sends: `str`.

### [`backend/app/services/reports/report_contracts.py`](../../backend/app/services/reports/report_contracts.py)

Purpose: Owns report contracts behavior for the backend runtime.

- L13 `class ReportSourceMessage(BaseModel)` — Encapsulates reportsourcemessage. Receives: `constructor arguments and class fields`. Sends: `ReportSourceMessage`.
- L26 `class AdmittedMitreRow(BaseModel)` — Encapsulates admittedmitrerow. Receives: `constructor arguments and class fields`. Sends: `AdmittedMitreRow`.
- L36 `class ReportInputSnapshot(BaseModel)` — Encapsulates reportinputsnapshot. Receives: `constructor arguments and class fields`. Sends: `ReportInputSnapshot`.
- L52 `class ReportServiceError(Exception)` — Encapsulates reportserviceerror. Receives: `constructor arguments and class fields`. Sends: `ReportServiceError`.
- L53 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L59 `class ReportGenerationConflict(ReportServiceError)` — Encapsulates reportgenerationconflict. Receives: `constructor arguments and class fields`. Sends: `ReportGenerationConflict`.
- L63 `class ReportNotFound(ReportServiceError)` — Encapsulates reportnotfound. Receives: `constructor arguments and class fields`. Sends: `ReportNotFound`.
- L67 `class ReportValidationError(ValueError)` — Encapsulates reportvalidationerror. Receives: `constructor arguments and class fields`. Sends: `ReportValidationError`.
- L72 `class ReportRunResult` — Encapsulates reportrunresult. Receives: `constructor arguments and class fields`. Sends: `ReportRunResult`.
- L86 `def read_render_snapshot(raw: dict[str, object] | ReportInputSnapshot | None) -> ReportInputSnapshot | None` — Retrieves render snapshot. Receives: `raw: dict[str, object] | ReportInputSnapshot | None`. Sends: `ReportInputSnapshot | None`.

### [`backend/app/services/reports/report_finding_projection.py`](../../backend/app/services/reports/report_finding_projection.py)

Purpose: Owns report finding projection behavior for the backend runtime.

- L22 `def project_finding_rows(structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage) -> list[EvidenceViewRow]` — Implements project finding rows. Receives: `structured: StructuredReport | None, snapshot: ReportInputSnapshot | None, *, language: ReportLanguage`. Sends: `list[EvidenceViewRow]`.
- L34 `def project_unresolved_issues(snapshot: ReportInputSnapshot | None, *, language: ReportLanguage) -> list[UnresolvedIssueViewRow]` — Implements project unresolved issues. Receives: `snapshot: ReportInputSnapshot | None, *, language: ReportLanguage`. Sends: `list[UnresolvedIssueViewRow]`.
- L68 `def _trace_finding_rows(snapshot: ReportInputSnapshot | None, language: ReportLanguage) -> list[EvidenceViewRow]` — Implements trace finding rows. Receives: `snapshot: ReportInputSnapshot | None, language: ReportLanguage`. Sends: `list[EvidenceViewRow]`.
- L95 `def _structured_finding_rows(structured: StructuredReport, snapshot: ReportInputSnapshot | None, language: ReportLanguage) -> list[EvidenceViewRow]` — Implements structured finding rows. Receives: `structured: StructuredReport, snapshot: ReportInputSnapshot | None, language: ReportLanguage`. Sends: `list[EvidenceViewRow]`.
- L119 `def _finding_type(status: str, language: ReportLanguage) -> str` — Implements finding type. Receives: `status: str, language: ReportLanguage`. Sends: `str`.

### [`backend/app/services/reports/report_generation.py`](../../backend/app/services/reports/report_generation.py)

Purpose: Owns report generation behavior for the backend runtime.

- L13 `async def run_report_generation(snapshot: ReportInputSnapshot) -> ReportRunResult` — Executes report generation. Receives: `snapshot: ReportInputSnapshot`. Sends: `ReportRunResult`.

### [`backend/app/services/reports/report_html.py`](../../backend/app/services/reports/report_html.py)

Purpose: Deterministic Jinja2 HTML rendering for CyberCase incident analysis reports.

- L26 `def get_report_css() -> str` — Return the embedded CSS stylesheet for HTML/PDF rendering. Receives: `not applicable`. Sends: `str`.
- L33 `def render_chat_report_html_from_view_model(view_model: ReportViewModel) -> str` — Render HTML string deterministically from a ReportViewModel. Receives: `view_model: ReportViewModel`. Sends: `str`.
- L43 `def render_chat_report_html(report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th') -> str` — Build the view model and render formal report HTML in Thai or English. Receives: `report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th'`. Sends: `str`.

### [`backend/app/services/reports/report_mitre_projection.py`](../../backend/app/services/reports/report_mitre_projection.py)

Purpose: Owns report mitre projection behavior for the backend runtime.

- L12 `def project_mitre_rows(snapshot: ReportInputSnapshot | None, sections_by_id: dict[str, ReportSection], *, lang: ReportLanguage) -> list[MitreMappingViewRow]` — Implements project mitre rows. Receives: `snapshot: ReportInputSnapshot | None, sections_by_id: dict[str, ReportSection], *, lang: ReportLanguage`. Sends: `list[MitreMappingViewRow]`.

### [`backend/app/services/reports/report_pdf.py`](../../backend/app/services/reports/report_pdf.py)

Purpose: Owns report pdf behavior for the backend runtime.

- L21 `def render_chat_report_pdf(report: ChatReportRead, *, thread_title: str, language: ReportLanguage='th') -> bytes` — Renders chat report pdf. Receives: `report: ChatReportRead, *, thread_title: str, language: ReportLanguage='th'`. Sends: `bytes`.

### [`backend/app/services/reports/report_pdf_story.py`](../../backend/app/services/reports/report_pdf_story.py)

Purpose: Owns report pdf story behavior for the backend runtime.

- L21 `def build_formal_report_story(view_model: ReportViewModel, *, report: ChatReportRead, styles: dict[str, ParagraphStyle]) -> list[object]` — Builds formal report story. Receives: `view_model: ReportViewModel, *, report: ChatReportRead, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L49 `def _summary_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements summary story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L67 `def _timeline_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements timeline story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L104 `def build_evidence_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Builds evidence story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L183 `def _mitre_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle], content_width: float) -> list[object]` — Implements mitre story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle], content_width: float`. Sends: `list[object]`.
- L233 `def _gap_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements gap story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L254 `def _next_steps_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Implements next steps story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.
- L275 `def build_provenance_story(view_model: ReportViewModel, styles: dict[str, ParagraphStyle]) -> list[object]` — Builds provenance story. Receives: `view_model: ReportViewModel, styles: dict[str, ParagraphStyle]`. Sends: `list[object]`.

### [`backend/app/services/reports/report_persistence.py`](../../backend/app/services/reports/report_persistence.py)

Purpose: Owns report persistence behavior for the backend runtime.

- L36 `def serialize_chat_report(report: ChatReport) -> ChatReportRead` — Serializes chat report. Receives: `report: ChatReport`. Sends: `ChatReportRead`.
- L76 `class ChatReportService` — Encapsulates chatreportservice. Receives: `constructor arguments and class fields`. Sends: `ChatReportService`.
- L77 `def __init__(self, db: AsyncSession) -> None` — Implements init. Receives: `self, db: AsyncSession`. Sends: `None`.
- L80 `async def generate_report(self, thread_id: UUID, request: ChatReportCreate) -> ChatReportRead` — Generates report. Receives: `self, thread_id: UUID, request: ChatReportCreate`. Sends: `ChatReportRead`.
- L137 `async def list_reports(self, thread_id: UUID) -> list[ChatReportRead]` — Lists reports. Receives: `self, thread_id: UUID`. Sends: `list[ChatReportRead]`.
- L146 `async def get_report(self, thread_id: UUID, report_id: UUID) -> ChatReportRead` — Retrieves report. Receives: `self, thread_id: UUID, report_id: UUID`. Sends: `ChatReportRead`.
- L150 `async def get_report_pdf(self, thread_id: UUID, report_id: UUID) -> tuple[bytes, str]` — Retrieves report pdf. Receives: `self, thread_id: UUID, report_id: UUID`. Sends: `tuple[bytes, str]`.
- L202 `async def _thread_with_messages(self, thread_id: UUID, *, lock: bool) -> ChatThread` — Implements thread with messages. Receives: `self, thread_id: UUID, *, lock: bool`. Sends: `ChatThread`.
- L214 `async def _latest_rag_context(self, thread_id: UUID) -> RagContext | None` — Implements latest rag context. Receives: `self, thread_id: UUID`. Sends: `RagContext | None`.
- L224 `async def _existing_report(self, thread_id: UUID, key: str) -> ChatReport | None` — Implements existing report. Receives: `self, thread_id: UUID, key: str`. Sends: `ChatReport | None`.
- L233 `async def _next_version(self, thread_id: UUID) -> int` — Implements next version. Receives: `self, thread_id: UUID`. Sends: `int`.
- L239 `async def _ensure_thread(self, thread_id: UUID) -> None` — Implements ensure thread. Receives: `self, thread_id: UUID`. Sends: `None`.
- L242 `async def _report(self, thread_id: UUID, report_id: UUID, *, load_thread: bool=False) -> ChatReport` — Implements report. Receives: `self, thread_id: UUID, report_id: UUID, *, load_thread: bool=False`. Sends: `ChatReport`.

### [`backend/app/services/reports/report_review_projection.py`](../../backend/app/services/reports/report_review_projection.py)

Purpose: Owns report review projection behavior for the backend runtime.

- L9 `def project_review_actions(unresolved_issues: list[UnresolvedIssueViewRow], *, lang: ReportLanguage, has_mitre_mappings: bool) -> tuple[list[VerificationActionViewRow], list[str]]` — Implements project review actions. Receives: `unresolved_issues: list[UnresolvedIssueViewRow], *, lang: ReportLanguage, has_mitre_mappings: bool`. Sends: `tuple[list[VerificationActionViewRow], list[str]]`.

### [`backend/app/services/reports/report_snapshot.py`](../../backend/app/services/reports/report_snapshot.py)

Purpose: Owns report snapshot behavior for the backend runtime.

- L16 `def build_current_report_snapshot(thread: ChatThread, *, rag_context: RagContext | None=None) -> ReportInputSnapshot` — Builds current report snapshot. Receives: `thread: ChatThread, *, rag_context: RagContext | None=None`. Sends: `ReportInputSnapshot`.
- L74 `def _analysis_message(messages: list[ChatMessage]) -> ChatMessage | None` — Implements analysis message. Receives: `messages: list[ChatMessage]`. Sends: `ChatMessage | None`.
- L86 `def _active_rag_context(analysis_message: ChatMessage, rag_context: RagContext | None) -> RagContext | None` — Implements active rag context. Receives: `analysis_message: ChatMessage, rag_context: RagContext | None`. Sends: `RagContext | None`.
- L97 `def _mitre_rows(value: object) -> list[AdmittedMitreRow]` — Implements mitre rows. Receives: `value: object`. Sends: `list[AdmittedMitreRow]`.
- L119 `def _unresolved_issues(metadata: dict[str, object]) -> list[str]` — Implements unresolved issues. Receives: `metadata: dict[str, object]`. Sends: `list[str]`.

### [`backend/app/services/reports/report_template.py`](../../backend/app/services/reports/report_template.py)

Purpose: Owns report template behavior for the backend runtime.

- L12 `def _extract_summary_paragraphs(analysis_answer: str) -> list[str]` — Extracts summary paragraphs. Receives: `analysis_answer: str`. Sends: `list[str]`.
- L31 `def _extract_progression_claims(snapshot: ReportInputSnapshot) -> list[ReportClaim]` — Extracts progression claims. Receives: `snapshot: ReportInputSnapshot`. Sends: `list[ReportClaim]`.
- L101 `def build_template_report(snapshot: ReportInputSnapshot) -> StructuredReport` — Builds template report. Receives: `snapshot: ReportInputSnapshot`. Sends: `StructuredReport`.

### [`backend/app/services/reports/report_validation.py`](../../backend/app/services/reports/report_validation.py)

Purpose: Owns report validation behavior for the backend runtime.

- L14 `def validate_structured_report(report: StructuredReport, *, source_message_ids: set[str], mitre_ids: set[str]) -> None` — Validates structured report. Receives: `report: StructuredReport, *, source_message_ids: set[str], mitre_ids: set[str]`. Sends: `None`.
- L34 `def validate_case_structured_report(report: StructuredReport, *, source_evidence_ids: set[str], mitre_ids: set[str]) -> None` — Validates case structured report. Receives: `report: StructuredReport, *, source_evidence_ids: set[str], mitre_ids: set[str]`. Sends: `None`.
- L56 `def source_snapshot_hash(snapshot: ReportInputSnapshot | CaseReportInputSnapshot | dict[str, object]) -> str` — Implements source snapshot hash. Receives: `snapshot: ReportInputSnapshot | CaseReportInputSnapshot | dict[str, object]`. Sends: `str`.

### [`backend/app/services/reports/report_view_model_builder.py`](../../backend/app/services/reports/report_view_model_builder.py)

Purpose: Owns report view model builder behavior for the backend runtime.

- L29 `def _clean_markdown_text(text: str) -> str` — Normalizes markdown text. Receives: `text: str`. Sends: `str`.
- L37 `def build_report_view_model(report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th') -> ReportViewModel` — Builds report view model. Receives: `report: ChatReportRead, *, thread_title: str='CyberCase Investigation', language: ReportLanguage='th'`. Sends: `ReportViewModel`.

### [`backend/app/services/reports/report_view_model_contracts.py`](../../backend/app/services/reports/report_view_model_contracts.py)

Purpose: Owns report view model contracts behavior for the backend runtime.

- L9 `class TimelineViewRow` — Encapsulates timelineviewrow. Receives: `constructor arguments and class fields`. Sends: `TimelineViewRow`.
- L19 `class EvidenceViewRow` — Encapsulates evidenceviewrow. Receives: `constructor arguments and class fields`. Sends: `EvidenceViewRow`.
- L29 `class IndicatorViewRow` — Encapsulates indicatorviewrow. Receives: `constructor arguments and class fields`. Sends: `IndicatorViewRow`.
- L36 `class MitreMappingViewRow` — Encapsulates mitremappingviewrow. Receives: `constructor arguments and class fields`. Sends: `MitreMappingViewRow`.
- L48 `class UnresolvedIssueViewRow` — Encapsulates unresolvedissueviewrow. Receives: `constructor arguments and class fields`. Sends: `UnresolvedIssueViewRow`.
- L55 `class VerificationActionViewRow` — Encapsulates verificationactionviewrow. Receives: `constructor arguments and class fields`. Sends: `VerificationActionViewRow`.
- L61 `class ProvenanceViewRow` — Encapsulates provenanceviewrow. Receives: `constructor arguments and class fields`. Sends: `ProvenanceViewRow`.
- L67 `class ReportViewModel` — Encapsulates reportviewmodel. Receives: `constructor arguments and class fields`. Sends: `ReportViewModel`.

### [`backend/app/services/reports/report_view_model_items.py`](../../backend/app/services/reports/report_view_model_items.py)

Purpose: Owns report view model items behavior for the backend runtime.

- L15 `class ParsedReportItems` — Encapsulates parsedreportitems. Receives: `constructor arguments and class fields`. Sends: `ParsedReportItems`.
- L22 `def _extract_timeline_from_text(text: str, *, language: ReportLanguage) -> list[TimelineViewRow]` — Extracts timeline from text. Receives: `text: str, *, language: ReportLanguage`. Sends: `list[TimelineViewRow]`.
- L78 `def parse_report_items(sections_by_id: dict[str, ReportSection], *, language: ReportLanguage) -> ParsedReportItems` — Parses report items. Receives: `sections_by_id: dict[str, ReportSection], *, language: ReportLanguage`. Sends: `ParsedReportItems`.

### [`backend/app/services/reports/report_view_model_text.py`](../../backend/app/services/reports/report_view_model_text.py)

Purpose: Owns report view model text behavior for the backend runtime.

- L193 `def _format_datetime(dt: datetime | None) -> str` — Implements format datetime. Receives: `dt: datetime | None`. Sends: `str`.
- L201 `def _extract_indicators_from_text(text: str, note: str, seen: set[str]) -> list[IndicatorViewRow]` — Extracts indicators from text. Receives: `text: str, note: str, seen: set[str]`. Sends: `list[IndicatorViewRow]`.

### [`backend/app/services/workflow/__init__.py`](../../backend/app/services/workflow/__init__.py)

Purpose: Chat Run Workflow and Execution Pipeline Package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/app/services/workflow/analysis_execution_receipt.py`](../../backend/app/services/workflow/analysis_execution_receipt.py)

Purpose: Owns analysis execution receipt behavior for the backend runtime.

- L6 `async def persist_analysis_receipt(session_factory, run_id, worker_id, receipt)` — Persists analysis receipt. Receives: `session_factory, run_id, worker_id, receipt`. Sends: `inferred or None`.

### [`backend/app/services/workflow/analysis_pipeline_context.py`](../../backend/app/services/workflow/analysis_pipeline_context.py)

Purpose: Owns analysis pipeline context behavior for the backend runtime.

- L19 `async def prepare_analysis_context(claimed, applicability_gate, rag_request)` — Implements prepare analysis context. Receives: `claimed, applicability_gate, rag_request`. Sends: `inferred or None`.
- L52 `def bind_pipeline_outcome(outcome: AssistantOutcome, result: CaseAnalysisResult, configuration: dict[str, object]) -> AssistantOutcome` — Implements bind pipeline outcome. Receives: `outcome: AssistantOutcome, result: CaseAnalysisResult, configuration: dict[str, object]`. Sends: `AssistantOutcome`.
- L81 `def coerce_analysis_result(value: object) -> CaseAnalysisResult` — Implements coerce analysis result. Receives: `value: object`. Sends: `CaseAnalysisResult`.

### [`backend/app/services/workflow/case_ask_completion.py`](../../backend/app/services/workflow/case_ask_completion.py)

Purpose: Owns case ask completion behavior for the backend runtime.

- L22 `async def complete_case_ask(db: AsyncSession, run_id: UUID, worker_id: str, output) -> bool` — Implements complete case ask. Receives: `db: AsyncSession, run_id: UUID, worker_id: str, output`. Sends: `bool`.
- L97 `def _complete_run(run: CaseRun, now: datetime) -> None` — Implements complete run. Receives: `run: CaseRun, now: datetime`. Sends: `None`.
- L106 `def _trace_source_ids(trace: NativeCaseAnalysisTrace) -> list[str]` — Implements trace source ids. Receives: `trace: NativeCaseAnalysisTrace`. Sends: `list[str]`.

### [`backend/app/services/workflow/case_run_claim.py`](../../backend/app/services/workflow/case_run_claim.py)

Purpose: Owns case run claim behavior for the backend runtime.

- L19 `async def claim_case_run(db: AsyncSession, run_id: UUID, worker_id: str) -> ClaimedCaseRun | None` — Implements claim case run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str`. Sends: `ClaimedCaseRun | None`.
- L69 `def _validated_manifest(snapshot: CaseEvidenceSnapshot) -> tuple[dict[str, object], ...]` — Implements validated manifest. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `tuple[dict[str, object], ...]`.
- L95 `def _fail(run: CaseRun, now: datetime, code: str, message: str) -> None` — Implements fail. Receives: `run: CaseRun, now: datetime, code: str, message: str`. Sends: `None`.

### [`backend/app/services/workflow/case_run_completion.py`](../../backend/app/services/workflow/case_run_completion.py)

Purpose: Owns case run completion behavior for the backend runtime.

- L27 `class CaseRunCompletionError(Exception)` — Encapsulates caseruncompletionerror. Receives: `constructor arguments and class fields`. Sends: `CaseRunCompletionError`.
- L28 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L34 `async def complete_case_run(db: AsyncSession, run_id: UUID, worker_id: str, output: AnalysisOutput) -> bool` — Implements complete case run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str, output: AnalysisOutput`. Sends: `bool`.
- L172 `def _owns_run(run: CaseRun | None, case_id: UUID, worker_id: str, now: datetime) -> bool` — Implements owns run. Receives: `run: CaseRun | None, case_id: UUID, worker_id: str, now: datetime`. Sends: `bool`.
- L183 `def _validated_output(output: AnalysisOutput, snapshot: CaseEvidenceSnapshot) -> NativeCaseAnalysisTrace` — Implements validated output. Receives: `output: AnalysisOutput, snapshot: CaseEvidenceSnapshot`. Sends: `NativeCaseAnalysisTrace`.
- L204 `def _snapshot_sources(snapshot: CaseEvidenceSnapshot) -> tuple[NativeAdmittedSource, ...]` — Implements snapshot sources. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `tuple[NativeAdmittedSource, ...]`.
- L223 `def _snapshot_document_context(snapshot: CaseEvidenceSnapshot) -> list[dict[str, object]]` — Implements snapshot document context. Receives: `snapshot: CaseEvidenceSnapshot`. Sends: `list[dict[str, object]]`.
- L244 `def _trace_source_ids(trace: NativeCaseAnalysisTrace) -> list[str]` — Implements trace source ids. Receives: `trace: NativeCaseAnalysisTrace`. Sends: `list[str]`.
- L252 `def _clarification_metadata(output: AnalysisOutput, trace: NativeCaseAnalysisTrace) -> dict[str, object]` — Implements clarification metadata. Receives: `output: AnalysisOutput, trace: NativeCaseAnalysisTrace`. Sends: `dict[str, object]`.

### [`backend/app/services/workflow/case_run_contracts.py`](../../backend/app/services/workflow/case_run_contracts.py)

Purpose: Owns case run contracts behavior for the backend runtime.

- L10 `class ClaimedCaseRun` — Encapsulates claimedcaserun. Receives: `constructor arguments and class fields`. Sends: `ClaimedCaseRun`.

### [`backend/app/services/workflow/case_run_execution.py`](../../backend/app/services/workflow/case_run_execution.py)

Purpose: Owns case run execution behavior for the backend runtime.

- L26 `class CaseRunExecutionError(Exception)` — Encapsulates caserunexecutionerror. Receives: `constructor arguments and class fields`. Sends: `CaseRunExecutionError`.
- L27 `def __init__(self, code: str, message: str) -> None` — Implements init. Receives: `self, code: str, message: str`. Sends: `None`.
- L33 `async def execute_case_run(run_id: UUID, *, session_factory: Callable, analysis_request=request_case_analysis) -> None` — Executes case run. Receives: `run_id: UUID, *, session_factory: Callable, analysis_request=request_case_analysis`. Sends: `None`.
- L84 `def _analysis_context(claimed: ClaimedCaseRun) -> dict[str, object]` — Implements analysis context. Receives: `claimed: ClaimedCaseRun`. Sends: `dict[str, object]`.
- L121 `def _analysis_request_language(claimed: ClaimedCaseRun) -> str` — Implements analysis request language. Receives: `claimed: ClaimedCaseRun`. Sends: `str`.
- L126 `def _run_question(claimed: ClaimedCaseRun) -> str | None` — Executes question. Receives: `claimed: ClaimedCaseRun`. Sends: `str | None`.
- L135 `async def _attach_case_followup(output, claimed: ClaimedCaseRun)` — Implements attach case followup. Receives: `output, claimed: ClaimedCaseRun`. Sends: `inferred or None`.
- L185 `async def _record_failure(session_factory, run_id, worker_id, code, message) -> None` — Persists failure. Receives: `session_factory, run_id, worker_id, code, message`. Sends: `None`.

### [`backend/app/services/workflow/case_run_failure.py`](../../backend/app/services/workflow/case_run_failure.py)

Purpose: Owns case run failure behavior for the backend runtime.

- L13 `async def fail_case_run(db: AsyncSession, run_id: UUID, worker_id: str, error_code: str, error_message: str) -> bool` — Implements fail case run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str, error_code: str, error_message: str`. Sends: `bool`.

### [`backend/app/services/workflow/case_run_heartbeat.py`](../../backend/app/services/workflow/case_run_heartbeat.py)

Purpose: Owns case run heartbeat behavior for the backend runtime.

- L17 `async def renew_case_run_lease(session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str) -> None` — Implements renew case run lease. Receives: `session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str`. Sends: `None`.
- L38 `async def _heartbeat(session_factory, run_id: UUID, worker_id: str) -> None` — Implements heartbeat. Receives: `session_factory, run_id: UUID, worker_id: str`. Sends: `None`.
- L45 `async def maintain_case_run_lease(session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str) -> AsyncIterator[None]` — Implements maintain case run lease. Receives: `session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str`. Sends: `AsyncIterator[None]`.

### [`backend/app/services/workflow/case_run_recovery.py`](../../backend/app/services/workflow/case_run_recovery.py)

Purpose: Owns case run recovery behavior for the backend runtime.

- L19 `async def recover_expired_case_runs(session_factory: Callable[[], AsyncSession]) -> int` — Implements recover expired case runs. Receives: `session_factory: Callable[[], AsyncSession]`. Sends: `int`.
- L51 `def _expired(run: CaseRun, now: datetime) -> bool` — Implements expired. Receives: `run: CaseRun, now: datetime`. Sends: `bool`.
- L57 `async def monitor_case_runs(session_factory: Callable[[], AsyncSession]) -> None` — Implements monitor case runs. Receives: `session_factory: Callable[[], AsyncSession]`. Sends: `None`.

### [`backend/app/services/workflow/case_run_service.py`](../../backend/app/services/workflow/case_run_service.py)

Purpose: Owns case run service behavior for the backend runtime.

- L20 `class CaseRunError(Exception)` — Encapsulates caserunerror. Receives: `constructor arguments and class fields`. Sends: `CaseRunError`.
- L21 `def __init__(self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT) -> None` — Implements init. Receives: `self, code: str, message: str, status_code: int=status.HTTP_409_CONFLICT`. Sends: `None`.
- L28 `async def enqueue_case_analysis(db: AsyncSession, *, case_id: UUID, user_id: UUID | None, request: CaseAnalysisCreate, clarification_id: UUID | None=None, request_message_id: UUID | None=None, request_payload_extra: dict[str, object] | None=None) -> CaseRun` — Implements enqueue case analysis. Receives: `db: AsyncSession, *, case_id: UUID, user_id: UUID | None, request: CaseAnalysisCreate, clarification_id: UUID | None=None, request_message_id: UUID | None=None, request_payload_extra: dict[str, object] | None=None`. Sends: `CaseRun`.
- L119 `async def get_owned_case_run(db: AsyncSession, *, case_id: UUID, run_id: UUID, user_id: UUID | None) -> CaseRun` — Retrieves owned case run. Receives: `db: AsyncSession, *, case_id: UUID, run_id: UUID, user_id: UUID | None`. Sends: `CaseRun`.
- L137 `async def get_latest_case_analysis(db: AsyncSession, *, case_id: UUID, user_id: UUID | None) -> tuple[Case, CaseAnalysisResult | None]` — Retrieves latest case analysis. Receives: `db: AsyncSession, *, case_id: UUID, user_id: UUID | None`. Sends: `tuple[Case, CaseAnalysisResult | None]`.
- L157 `def analysis_freshness(case: Case, result: CaseAnalysisResult) -> str` — Implements analysis freshness. Receives: `case: Case, result: CaseAnalysisResult`. Sends: `str`.
- L161 `async def _locked_case(db: AsyncSession, case_id: UUID, user_id: UUID | None) -> Case` — Implements locked case. Receives: `db: AsyncSession, case_id: UUID, user_id: UUID | None`. Sends: `Case`.
- L169 `def case_run_fingerprint(value: dict[str, object]) -> str` — Implements case run fingerprint. Receives: `value: dict[str, object]`. Sends: `str`.

### [`backend/app/services/workflow/chat_run_claim.py`](../../backend/app/services/workflow/chat_run_claim.py)

Purpose: Owns chat run claim behavior for the backend runtime.

- L24 `async def claim_run(db: AsyncSession, run_id: UUID, worker_id: str) -> ClaimedChatRun | None` — Implements claim run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str`. Sends: `ClaimedChatRun | None`.
- L131 `async def _analysis_context_for_state(db: AsyncSession, current_run: ChatRun, state: CanonicalCaseAnalysisState | None) -> dict[str, object] | None` — Implements analysis context for state. Receives: `db: AsyncSession, current_run: ChatRun, state: CanonicalCaseAnalysisState | None`. Sends: `dict[str, object] | None`.
- L155 `async def _latest_legacy_analysis_context(db: AsyncSession, current_run: ChatRun) -> dict[str, object] | None` — Implements latest legacy analysis context. Receives: `db: AsyncSession, current_run: ChatRun`. Sends: `dict[str, object] | None`.
- L192 `async def _fail_missing_request(run: ChatRun, now: datetime) -> None` — Implements fail missing request. Receives: `run: ChatRun, now: datetime`. Sends: `None`.
- L198 `async def _fail_missing_evidence(run: ChatRun, now: datetime) -> None` — Implements fail missing evidence. Receives: `run: ChatRun, now: datetime`. Sends: `None`.
- L204 `async def _fail_missing_context(run: ChatRun, now: datetime) -> None` — Implements fail missing context. Receives: `run: ChatRun, now: datetime`. Sends: `None`.
- L213 `async def _mark_claim_failure(run: ChatRun, now: datetime, code: str, message: str) -> None` — Implements mark claim failure. Receives: `run: ChatRun, now: datetime, code: str, message: str`. Sends: `None`.

### [`backend/app/services/workflow/chat_run_completion.py`](../../backend/app/services/workflow/chat_run_completion.py)

Purpose: Owns chat run completion behavior for the backend runtime.

- L18 `async def complete_run(db: AsyncSession, run_id: UUID, worker_id: str, outcome: AssistantOutcome, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None) -> bool` — Implements complete run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str, outcome: AssistantOutcome, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None`. Sends: `bool`.
- L83 `def _serialize_analysis_trace(outcome: AssistantOutcome) -> dict[str, object] | None` — Serializes analysis trace. Receives: `outcome: AssistantOutcome`. Sends: `dict[str, object] | None`.

### [`backend/app/services/workflow/chat_run_contracts.py`](../../backend/app/services/workflow/chat_run_contracts.py)

Purpose: Owns chat run contracts behavior for the backend runtime.

- L14 `class ClaimedChatRun` — Encapsulates claimedchatrun. Receives: `constructor arguments and class fields`. Sends: `ClaimedChatRun`.

### [`backend/app/services/workflow/chat_run_failure.py`](../../backend/app/services/workflow/chat_run_failure.py)

Purpose: Owns chat run failure behavior for the backend runtime.

- L14 `async def fail_run(db: AsyncSession, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None) -> bool` — Persist a safe failure without exposing upstream response content. Receives: `db: AsyncSession, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None, *, lock_run_thread_fn: Callable[[UUID], Awaitable[ChatThread | None]] | None=None, lock_owned_running_run_fn: Callable[[UUID, str], Awaitable[ChatRun | None]] | None=None`. Sends: `bool`.

### [`backend/app/services/workflow/chat_run_locks.py`](../../backend/app/services/workflow/chat_run_locks.py)

Purpose: Owns chat run locks behavior for the backend runtime.

- L12 `async def lock_run_thread(db: AsyncSession, run_id: UUID) -> ChatThread | None` — Lock the parent thread before the run to match message creation order. Receives: `db: AsyncSession, run_id: UUID`. Sends: `ChatThread | None`.
- L31 `async def lock_owned_running_run(db: AsyncSession, run_id: UUID, worker_id: str) -> ChatRun | None` — Implements lock owned running run. Receives: `db: AsyncSession, run_id: UUID, worker_id: str`. Sends: `ChatRun | None`.

### [`backend/app/services/workflow/chat_run_store.py`](../../backend/app/services/workflow/chat_run_store.py)

Purpose: Owns chat run store behavior for the backend runtime.

- L16 `class ChatRunWorker` — Encapsulates chatrunworker. Receives: `constructor arguments and class fields`. Sends: `ChatRunWorker`.
- L17 `def __init__(self, db: AsyncSession)` — Implements init. Receives: `self, db: AsyncSession`. Sends: `inferred or None`.
- L20 `async def claim_run(self, run_id: UUID, worker_id: str) -> ClaimedChatRun | None` — Implements claim run. Receives: `self, run_id: UUID, worker_id: str`. Sends: `ClaimedChatRun | None`.
- L27 `async def complete_run(self, run_id: UUID, worker_id: str, outcome: Any) -> bool` — Implements complete run. Receives: `self, run_id: UUID, worker_id: str, outcome: Any`. Sends: `bool`.
- L42 `async def fail_run(self, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None) -> bool` — Implements fail run. Receives: `self, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None`. Sends: `bool`.
- L61 `async def _lock_run_thread(self, run_id: UUID) -> ChatThread | None` — Implements lock run thread. Receives: `self, run_id: UUID`. Sends: `ChatThread | None`.
- L64 `async def _lock_owned_running_run(self, run_id: UUID, worker_id: str) -> ChatRun | None` — Implements lock owned running run. Receives: `self, run_id: UUID, worker_id: str`. Sends: `ChatRun | None`.

### [`backend/app/services/workflow/outcome.py`](../../backend/app/services/workflow/outcome.py)

Purpose: Owns outcome behavior for the backend runtime.

- L20 `class RagContextPayload` — Encapsulates ragcontextpayload. Receives: `constructor arguments and class fields`. Sends: `RagContextPayload`.
- L25 `def to_analysis_context(self) -> dict[str, object]` — Transforms analysis context. Receives: `self`. Sends: `dict[str, object]`.
- L34 `class AssistantOutcome` — Encapsulates assistantoutcome. Receives: `constructor arguments and class fields`. Sends: `AssistantOutcome`.
- L46 `def map_rag_response(response: QueryResponse) -> dict[str, object]` — Transforms rag response. Receives: `response: QueryResponse`. Sends: `dict[str, object]`.
- L55 `def validated_rag_context_payload(response: QueryResponse) -> RagContextPayload` — Implements validated rag context payload. Receives: `response: QueryResponse`. Sends: `RagContextPayload`.
- L79 `def fresh_analysis_outcome(answer: str, *, action: str, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], followup_metadata: dict[str, object], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements fresh analysis outcome. Receives: `answer: str, *, action: str, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], followup_metadata: dict[str, object], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None`. Sends: `AssistantOutcome`.
- L127 `def question_outcome(answer: str, *, analysis_context: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements question outcome. Receives: `answer: str, *, analysis_context: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None`. Sends: `AssistantOutcome`.
- L172 `def bind_followup_question(outcome: AssistantOutcome, *, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None) -> AssistantOutcome` — Implements bind followup question. Receives: `outcome: AssistantOutcome, *, rag_context: RagContextPayload | None, rag_status: RagAttemptStatus, rag_failure_code: str | None, rag_invoked: bool, mitre_applicability: dict[str, object], evidence_sha256: str, source_message_ids: tuple[UUID, ...], trace: ValidatedAnalysisTrace | None, trace_failure: AnalysisTraceFailure | None`. Sends: `AssistantOutcome`.
- L209 `def _retrieval_context_id(rag_context: RagContextPayload | None) -> str | None` — Implements retrieval context id. Receives: `rag_context: RagContextPayload | None`. Sends: `str | None`.
- L213 `def _mitre_table(rag_context: RagContextPayload | None) -> list[dict[str, object]]` — Implements mitre table. Receives: `rag_context: RagContextPayload | None`. Sends: `list[dict[str, object]]`.
- L217 `def _rag_attempt_metadata(status: RagAttemptStatus, failure_code: str | None) -> dict[str, object]` — Implements rag attempt metadata. Receives: `status: RagAttemptStatus, failure_code: str | None`. Sends: `dict[str, object]`.

### [`backend/app/services/workflow/pipeline.py`](../../backend/app/services/workflow/pipeline.py)

Purpose: Owns pipeline behavior for the backend runtime.

- L20 `def build_dependencies() -> PipelineDependencies` — Builds dependencies. Receives: `not applicable`. Sends: `PipelineDependencies`.
- L30 `async def process_chat_run(run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None) -> None` — Executes chat run. Receives: `run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None`. Sends: `None`.
- L48 `async def process_case_run(run_id: UUID) -> None` — Executes case run. Receives: `run_id: UUID`. Sends: `None`.

### [`backend/app/services/workflow/pipeline_execution.py`](../../backend/app/services/workflow/pipeline_execution.py)

Purpose: Owns pipeline execution behavior for the backend runtime.

- L51 `class PipelineDependencies` — Encapsulates pipelinedependencies. Receives: `constructor arguments and class fields`. Sends: `PipelineDependencies`.
- L59 `async def record_failure(dependencies: PipelineDependencies, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None) -> None` — Persists failure. Receives: `dependencies: PipelineDependencies, run_id: UUID, worker_id: str, error_code: str, error_message: str, followup_metadata_json: dict[str, Any] | None=None`. Sends: `None`.
- L80 `async def process_chat_run(run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None, applicability_call: Callable[..., Awaitable[MitreApplicabilityRecord]] | None=None, dependencies: PipelineDependencies) -> None` — Executes chat run. Receives: `run_id: UUID, *, policy: FollowUpPolicy | None=None, gap_analyzer: GapAnalyzer | None=None, rag_call: Callable[[str], Awaitable[QueryResponse]] | None=None, ask_call: Callable[..., Awaitable[object]] | None=None, applicability_call: Callable[..., Awaitable[MitreApplicabilityRecord]] | None=None, dependencies: PipelineDependencies`. Sends: `None`.
- L97 `async def checkpoint(receipt)` — Implements checkpoint. Receives: `receipt`. Sends: `inferred or None`.
- L160 `async def _run_fresh_analysis(claimed, *, rag_request, analysis_request, followup_evaluator, policy, gap_analyzer, applicability_gate, execution_checkpoint=None) -> AssistantOutcome` — Executes fresh analysis. Receives: `claimed, *, rag_request, analysis_request, followup_evaluator, policy, gap_analyzer, applicability_gate, execution_checkpoint=None`. Sends: `AssistantOutcome`.

### [`backend/app/services/workflow/question_execution.py`](../../backend/app/services/workflow/question_execution.py)

Purpose: Owns question execution behavior for the backend runtime.

- L9 `async def _run_question(claimed, analysis_request) -> AssistantOutcome` — Executes question. Receives: `claimed, analysis_request`. Sends: `AssistantOutcome`.

### [`backend/app/services/workflow/rag_routing.py`](../../backend/app/services/workflow/rag_routing.py)

Purpose: Owns rag routing behavior for the backend runtime.

- L23 `class RagAttempt` — Encapsulates ragattempt. Receives: `constructor arguments and class fields`. Sends: `RagAttempt`.
- L29 `async def attempt_mitre_applicability(claimed, applicability_gate) -> MitreApplicabilityRecord` — Implements attempt mitre applicability. Receives: `claimed, applicability_gate`. Sends: `MitreApplicabilityRecord`.
- L51 `async def attempt_optional_rag(claimed, rag_request) -> RagAttempt` — Implements attempt optional rag. Receives: `claimed, rag_request`. Sends: `RagAttempt`.

### [`backend/app/services/workflow/run_heartbeat.py`](../../backend/app/services/workflow/run_heartbeat.py)

Purpose: Owns run heartbeat behavior for the backend runtime.

- L13 `async def renew_run_lease(session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str) -> None` — Implements renew run lease. Receives: `session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str`. Sends: `None`.
- L24 `async def _heartbeat(session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str) -> None` — Implements heartbeat. Receives: `session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str`. Sends: `None`.
- L33 `async def maintain_run_lease(session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str) -> AsyncIterator[None]` — Implements maintain run lease. Receives: `session_factory: Callable[[], AsyncSession], run_id: UUID, worker_id: str`. Sends: `AsyncIterator[None]`.

### [`backend/app/services/workflow/run_recovery.py`](../../backend/app/services/workflow/run_recovery.py)

Purpose: Owns run recovery behavior for the backend runtime.

- L18 `def run_has_expired(run: ChatRun, now: datetime) -> bool` — Executes has expired. Receives: `run: ChatRun, now: datetime`. Sends: `bool`.
- L26 `async def recover_expired_runs(session_factory: Callable[[], AsyncSession]) -> int` — Implements recover expired runs. Receives: `session_factory: Callable[[], AsyncSession]`. Sends: `int`.
- L68 `async def monitor_interrupted_runs(session_factory: Callable[[], AsyncSession]) -> None` — Implements monitor interrupted runs. Receives: `session_factory: Callable[[], AsyncSession]`. Sends: `None`.

## Repository Tooling

### [`backend/manual_smoke.py`](../../backend/manual_smoke.py)

Purpose: Bounded smoke test for a running chat-only backend.

- L19 `def _require_success(response: httpx.Response) -> dict[str, object]` — Implements require success. Receives: `response: httpx.Response`. Sends: `dict[str, object]`.
- L27 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`backend/scripts/export_openapi.py`](../../backend/scripts/export_openapi.py)

Purpose: Owns export openapi behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/scripts/smoke_claim_anchored.py`](../../backend/scripts/smoke_claim_anchored.py)

Purpose: Owns smoke claim anchored behavior for the repository tooling.

- L14 `async def smoke(output: Path) -> None` — Implements smoke. Receives: `output: Path`. Sends: `None`.

### [`backend/tools/__init__.py`](../../backend/tools/__init__.py)

Purpose: Defines the public package surface for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`backend/tools/document_ingestion_eval.py`](../../backend/tools/document_ingestion_eval.py)

Purpose: Owns document ingestion eval behavior for the repository tooling.

- L15 `def _load_samples(path: Path) -> list[dict[str, Any]]` — Retrieves samples. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L30 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`docs/developer-handover/extract_typescript_symbols.mjs`](../../docs/developer-handover/extract_typescript_symbols.mjs)

Purpose: Owns extract typescript symbols behavior for the repository tooling.

- L9 `function clean(text)` — Normalizes clean. Receives: `text`. Sends: `inferred or void`.
- L13 `function lineOf(sourceFile, node)` — Implements lineof. Receives: `sourceFile, node`. Sends: `inferred or void`.
- L17 `function declarationName(node, fallback)` — Implements declarationname. Receives: `node, fallback`. Sends: `inferred or void`.
- L23 `function parameters(node, sourceFile)` — Implements parameters. Receives: `node, sourceFile`. Sends: `inferred or void`.
- L28 `function returnType(node, sourceFile)` — Implements returntype. Receives: `node, sourceFile`. Sends: `inferred or void`.
- L32 `function addSymbol(symbols, sourceFile, node, kind, name, signature, inputs = "", output = "", parent = "")` — Implements addsymbol. Receives: `symbols, sourceFile, node, kind, name, signature, inputs = "", output = "", parent = ""`. Sends: `inferred or void`.
- L44 `function walk(sourceFile)` — Implements walk. Receives: `sourceFile`. Sends: `inferred or void`.
- L47 `function visit(node, parentName = "")` — Implements visit. Receives: `node, parentName = ""`. Sends: `inferred or void`.

### [`docs/developer-handover/generate_symbol_index.py`](../../docs/developer-handover/generate_symbol_index.py)

Purpose: Owns generate symbol index behavior for the repository tooling.

- L15 `def run(command: list[str]) -> str` — Executes run. Receives: `command: list[str]`. Sends: `str`.
- L26 `def source_files() -> list[Path]` — Implements source files. Receives: `not applicable`. Sends: `list[Path]`.
- L40 `def first_sentence(text: str | None) -> str | None` — Implements first sentence. Receives: `text: str | None`. Sends: `str | None`.
- L50 `def words(name: str) -> str` — Implements words. Receives: `name: str`. Sends: `str`.
- L64 `def area_for(relative: str) -> str` — Implements area for. Receives: `relative: str`. Sends: `str`.
- L84 `def file_purpose(relative: str, module_doc: str | None=None) -> str` — Implements file purpose. Receives: `relative: str, module_doc: str | None=None`. Sends: `str`.
- L103 `def describe(name: str, kind: str) -> str` — Implements describe. Receives: `name: str, kind: str`. Sends: `str`.
- L144 `def python_signature(node: ast.AST) -> str` — Implements python signature. Receives: `node: ast.AST`. Sends: `str`.
- L153 `def python_io(node: ast.AST) -> tuple[str, str]` — Implements python io. Receives: `node: ast.AST`. Sends: `tuple[str, str]`.
- L161 `def python_symbols(path: Path) -> tuple[str | None, list[dict[str, object]]]` — Implements python symbols. Receives: `path: Path`. Sends: `tuple[str | None, list[dict[str, object]]]`.
- L165 `class SymbolVisitor(ast.NodeVisitor)` — Encapsulates symbolvisitor. Receives: `constructor arguments and class fields`. Sends: `SymbolVisitor`.
- L166 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L169 `def qualified(self, name: str) -> str` — Implements qualified. Receives: `self, name: str`. Sends: `str`.
- L173 `def visit_ClassDef(self, node: ast.ClassDef) -> None` — Implements visit classdef. Receives: `self, node: ast.ClassDef`. Sends: `None`.
- L181 `def record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None` — Persists function. Receives: `self, node: ast.FunctionDef | ast.AsyncFunctionDef`. Sends: `None`.
- L190 `def visit_FunctionDef(self, node: ast.FunctionDef) -> None` — Implements visit functiondef. Receives: `self, node: ast.FunctionDef`. Sends: `None`.
- L193 `def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None` — Implements visit asyncfunctiondef. Receives: `self, node: ast.AsyncFunctionDef`. Sends: `None`.
- L200 `def typescript_symbols(paths: list[Path]) -> dict[str, list[dict[str, object]]]` — Implements typescript symbols. Receives: `paths: list[Path]`. Sends: `dict[str, list[dict[str, object]]]`.
- L216 `def section_for(relative: str) -> str` — Implements section for. Receives: `relative: str`. Sends: `str`.
- L220 `def generate() -> str` — Generates generate. Receives: `not applicable`. Sends: `str`.

### [`docs/thesis_v1/_work/build_thesis_docx.py`](../../docs/thesis_v1/_work/build_thesis_docx.py)

Purpose: Owns build thesis docx behavior for the repository tooling.

- L30 `def set_font(run, name=FONT, size=None, bold=None, italic=None, color=None)` — Updates font. Receives: `run, name=FONT, size=None, bold=None, italic=None, color=None`. Sends: `inferred or None`.
- L45 `def shade(element, fill)` — Implements shade. Receives: `element, fill`. Sends: `inferred or None`.
- L54 `def set_cell_margins(cell, top=100, start=120, bottom=100, end=120)` — Updates cell margins. Receives: `cell, top=100, start=120, bottom=100, end=120`. Sends: `inferred or None`.
- L69 `def set_table_geometry(table, widths)` — Updates table geometry. Receives: `table, widths`. Sends: `inferred or None`.
- L98 `def add_field(paragraph, instruction, display='')` — Implements add field. Receives: `paragraph, instruction, display=''`. Sends: `inferred or None`.
- L115 `def configure_styles(doc)` — Implements configure styles. Receives: `doc`. Sends: `inferred or None`.
- L167 `def add_inline(paragraph, text, citation_numbers)` — Implements add inline. Receives: `paragraph, text, citation_numbers`. Sends: `inferred or None`.
- L192 `def table_widths(rows, total=9360)` — Implements table widths. Receives: `rows, total=9360`. Sends: `inferred or None`.
- L201 `def add_table(doc, rows, citation_numbers)` — Implements add table. Receives: `doc, rows, citation_numbers`. Sends: `inferred or None`.
- L222 `def add_markdown(doc, text, citation_numbers, skip_h1=False)` — Implements add markdown. Receives: `doc, text, citation_numbers, skip_h1=False`. Sends: `inferred or None`.
- L288 `def bib_entries(text)` — Implements bib entries. Receives: `text`. Sends: `inferred or None`.
- L301 `def format_reference(fields)` — Implements format reference. Receives: `fields`. Sends: `inferred or None`.
- L311 `def add_cover(doc)` — Implements add cover. Receives: `doc`. Sends: `inferred or None`.
- L337 `def add_toc(doc)` — Implements add toc. Receives: `doc`. Sends: `inferred or None`.
- L352 `def build()` — Builds build. Receives: `not applicable`. Sends: `inferred or None`.

### [`frontend/eslint.config.mjs`](../../frontend/eslint.config.mjs)

Purpose: Owns eslint config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/next.config.ts`](../../frontend/next.config.ts)

Purpose: Owns next config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/postcss.config.mjs`](../../frontend/postcss.config.mjs)

Purpose: Owns postcss config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/scripts/generate-api-types.mjs`](../../frontend/scripts/generate-api-types.mjs)

Purpose: Owns generate api types behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/tailwind.config.ts`](../../frontend/tailwind.config.ts)

Purpose: Owns tailwind config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/vitest.config.ts`](../../frontend/vitest.config.ts)

Purpose: Owns vitest config behavior for the repository tooling.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`install_deps.py`](../../install_deps.py)

Purpose: Owns install deps behavior for the repository tooling.

- L7 `def install_requirements(directory)` — Install requirements from a requirements.txt file in the specified directory. Receives: `directory`. Sends: `inferred or None`.
- L26 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/docs/_build_pdf.py`](../../rag_service/docs/_build_pdf.py)

Purpose: Build an HTML (mermaid-rendering, Thai-font) file from RAG_Module.md.

- L24 `def _stash_mermaid(m)` — Implements stash mermaid. Receives: `m`. Sends: `inferred or None`.
- L35 `def gh_slugify(value, separator='-')` — Implements gh slugify. Receives: `value, separator='-'`. Sends: `inferred or None`.
- L51 `def _restore_mermaid(m)` — Implements restore mermaid. Receives: `m`. Sends: `inferred or None`.

### [`rag_service/finetune/compare/run_comparison.py`](../../rag_service/finetune/compare/run_comparison.py)

Purpose: A/B Comparison — base qwen2.5:7b vs fine-tuned mitre-qwen:7b ============================================================= Runs the EXISTING generation evaluation (evaluation/eval_runner.py) once per model, switching models purely via the LOCAL_LLM_MODEL env var — no pipeline or eval code is modified.

- L49 `def run_eval(model: str, dataset: str, max_samples: int, out_md: Path) -> None` — Executes eval. Receives: `model: str, dataset: str, max_samples: int, out_md: Path`. Sends: `None`.
- L72 `def parse_metrics(md_path: Path) -> dict[str, float]` — Extract 'Metric -> value' pairs from the generation eval report. Receives: `md_path: Path`. Sends: `dict[str, float]`.
- L90 `def render(base_model, ft_model, base_m, ft_m) -> str` — Renders render. Receives: `base_model, ft_model, base_m, ft_m`. Sends: `str`.
- L124 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/finetune/data/build_dataset.py`](../../rag_service/finetune/data/build_dataset.py)

Purpose: Dataset Builder — MITRE ATT&CK STIX → SFT instruction pairs =========================================================== Reuses the existing ``StixParser`` (ingestion/stix_parser.py) to turn the MITRE ATT&CK STIX bundles into chat-format training examples for fine-tuning the local generation model into a MITRE specialist.

- L46 `def _latest_bundle(folder: Path) -> Path | None` — Return the newest versioned STIX json in a folder (e.g. Receives: `folder: Path`. Sends: `Path | None`.
- L52 `def version_key(p: Path)` — Implements version key. Receives: `p: Path`. Sends: `inferred or None`.
- L59 `def load_parser(domains: list[str], all_versions: bool) -> StixParser` — Retrieves parser. Receives: `domains: list[str], all_versions: bool`. Sends: `StixParser`.
- L85 `def load_heldout_ids() -> set[str]` — Retrieves heldout ids. Receives: `not applicable`. Sends: `set[str]`.
- L105 `def build_indices(parser: StixParser)` — Builds indices. Receives: `parser: StixParser`. Sends: `inferred or None`.
- L119 `def label(stix_id)` — Implements label. Receives: `stix_id`. Sends: `inferred or None`.
- L153 `def _record(system, user, assistant, category, subject_id, style, lang='en')` — Persists record. Receives: `system, user, assistant, category, subject_id, style, lang='en'`. Sends: `inferred or None`.
- L167 `def generate_examples(parser, by_id, idx, held, rng, grounded_ratio, abstention_ratio=0.45, holdout=False)` — Generates examples. Receives: `parser, by_id, idx, held, rng, grounded_ratio, abstention_ratio=0.45, holdout=False`. Sends: `inferred or None`.
- L173 `def add_grounded(category, sid, label, name, aid, desc, relation, neighbors, lead, q)` — Grounded twin of a list/relationship example — now ALWAYS emitted so grounded is the majority (the v4 model over-fit the closed-book template). Receives: `category, sid, label, name, aid, desc, relation, neighbors, lead, q`. Sends: `inferred or None`.
- L189 `def add_abstention(sid, label, name, aid, desc, present_rel, present_names, present_phrase, question, missing)` — Emit a grounded example whose question asks about something NOT in the context → the model must say so instead of guessing (the v4 model could not abstain; this category did not exist before). Receives: `sid, label, name, aid, desc, present_rel, present_names, present_phrase, question, missing`. Sends: `inferred or None`.
- L202 `def ok(stix_id)` — Implements ok. Receives: `stix_id`. Sends: `inferred or None`.
- L382 `def dedup(records)` — Implements dedup. Receives: `records`. Sends: `inferred or None`.
- L393 `def cap_per_category(records, max_per_cat, rng)` — Implements cap per category. Receives: `records, max_per_cat, rng`. Sends: `inferred or None`.
- L406 `def write_jsonl(path: Path, records)` — Implements write jsonl. Receives: `path: Path, records`. Sends: `inferred or None`.
- L414 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/finetune/data/templates.py`](../../rag_service/finetune/data/templates.py)

Purpose: Q&A Templates — STIX → instruction pairs ======================================== Pure formatting helpers that turn parsed MITRE ATT&CK entities/relationships into (question, answer) pairs.

- L33 `def clean_text(text: str, max_chars: int | None=None) -> str` — Strip MITRE markdown noise (citations, links) and collapse whitespace. Receives: `text: str, max_chars: int | None=None`. Sends: `str`.
- L61 `def first_sentence(text: str, max_chars: int=300) -> str` — First COMPLETE sentence of a description — used for per-mitigation blurbs so list answers never contain a sentence chopped mid-way. Receives: `text: str, max_chars: int=300`. Sends: `str`.
- L73 `def _pick(rng: random.Random | None, options: list[str]) -> str` — Extracts pick. Receives: `rng: random.Random | None, options: list[str]`. Sends: `str`.
- L77 `def _join_list(items: list[str], max_items: int) -> str` — Implements join list. Receives: `items: list[str], max_items: int`. Sends: `str`.
- L87 `def _ensure_period(s: str) -> str` — Implements ensure period. Receives: `s: str`. Sends: `str`.
- L91 `def technique_lookup(name, attack_id, desc, rng=None)` — Implements technique lookup. Receives: `name, attack_id, desc, rng=None`. Sends: `inferred or None`.
- L105 `def mitigation_lookup(name, attack_id, desc, mitigations, rng=None)` — mitigations: list of (m_name, m_id, m_desc_short). Receives: `name, attack_id, desc, mitigations, rng=None`. Sends: `inferred or None`.
- L135 `def technique_profile(name, attack_id, desc, mitigations, groups, tactics, rng=None)` — Compound 'full overview' answer — description + tactic(s) + mitigations + groups in one reply. Receives: `name, attack_id, desc, mitigations, groups, tactics, rng=None`. Sends: `inferred or None`.
- L167 `def technique_groups(name, attack_id, groups, rng=None)` — groups: list of (g_name, g_id). Receives: `name, attack_id, groups, rng=None`. Sends: `inferred or None`.
- L183 `def technique_detection(name, attack_id, components, rng=None)` — components: list of data source/component name strings. Receives: `name, attack_id, components, rng=None`. Sends: `inferred or None`.
- L197 `def tactic_techniques(tactic_name, tactic_id, techniques, rng=None)` — techniques: list of (t_name, t_id). Receives: `tactic_name, tactic_id, techniques, rng=None`. Sends: `inferred or None`.
- L218 `def group_techniques(group_name, group_id, techniques, rng=None)` — Implements group techniques. Receives: `group_name, group_id, techniques, rng=None`. Sends: `inferred or None`.
- L233 `def group_software(group_name, group_id, software, rng=None)` — Implements group software. Receives: `group_name, group_id, software, rng=None`. Sends: `inferred or None`.
- L253 `def software_techniques(sw_name, sw_id, sw_type, techniques, rng=None)` — Implements software techniques. Receives: `sw_name, sw_id, sw_type, techniques, rng=None`. Sends: `inferred or None`.
- L271 `def software_type_query(sw_name, sw_id, sw_type, desc, rng=None)` — Implements software type query. Receives: `sw_name, sw_id, sw_type, desc, rng=None`. Sends: `inferred or None`.
- L287 `def campaign_attribution(camp_name, camp_id, groups, rng=None)` — Implements campaign attribution. Receives: `camp_name, camp_id, groups, rng=None`. Sends: `inferred or None`.
- L305 `def build_entity_context(entity_type, node_label, name, attack_id, desc)` — Format one entity like context_builder.build_context's semantic block. Receives: `entity_type, node_label, name, attack_id, desc`. Sends: `inferred or None`.
- L323 `def build_relation_context(center_label, center_name, center_id, center_desc, relation_display, neighbor_names, rel_score=0.95)` — Context block for a LIST/relationship answer — mirrors the real pipeline's output: a semantic block PLUS a graph block (context_builder.build_context + SubgraphResult.to_text). Receives: `center_label, center_name, center_id, center_desc, relation_display, neighbor_names, rel_score=0.95`. Sends: `inferred or None`.
- L349 `def grounded_list_answer(center_name, center_id, lead, names, rng=None)` — Grounded list answer. Receives: `center_name, center_id, lead, names, rng=None`. Sends: `inferred or None`.
- L363 `def abstention_answer(name, attack_id, missing, present_phrase, rng=None)` — Answer for an abstention example: the question asks about something NOT in the context, so the model must say so plainly instead of guessing from memory. Receives: `name, attack_id, missing, present_phrase, rng=None`. Sends: `inferred or None`.
- L376 `def grounded_user_prompt(context: str, question: str) -> str` — User turn for a grounded example (context + question). Receives: `context: str, question: str`. Sends: `str`.

### [`rag_service/finetune/export/merge_and_gguf.py`](../../rag_service/finetune/export/merge_and_gguf.py)

Purpose: Merge LoRA → GGUF (fallback / non-Unsloth path) =============================================== Use this when you trained the adapter elsewhere, or want the explicit transformers + llama.cpp route instead of Unsloth's ``save_pretrained_gguf``.

- L32 `def merge(base_model: str, adapter_dir: str, merged_dir: Path)` — Implements merge. Receives: `base_model: str, adapter_dir: str, merged_dir: Path`. Sends: `inferred or None`.
- L54 `def to_gguf(merged_dir: Path, llama_cpp: Path, quant: str)` — Transforms gguf. Receives: `merged_dir: Path, llama_cpp: Path, quant: str`. Sends: `inferred or None`.
- L80 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/finetune/ft_config.py`](../../rag_service/finetune/ft_config.py)

Purpose: Fine-tune Module — Central Configuration ========================================= All knobs for turning the local generation model (``qwen2.5:7b``) into a MITRE ATT&CK specialist, while keeping the original model intact for A/B comparison.

- L155 `def add_rag_to_path() -> None` — Put ``rag_service/app/RAG`` on sys.path so ``import GraphRAG.*`` works. Receives: `not applicable`. Sends: `None`.

### [`rag_service/finetune/train/train_unsloth.py`](../../rag_service/finetune/train/train_unsloth.py)

Purpose: LoRA Trainer — Qwen → MITRE ATT&CK specialist ============================================= Run this on a Cloud GPU (Kaggle / Colab T4/P100 16 GB or better).

- L38 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.
- L125 `def to_text(ex)` — Transforms text. Receives: `ex`. Sends: `inferred or None`.

### [`scripts/build_all_thesis_docs.py`](../../scripts/build_all_thesis_docs.py)

Purpose: Owns build all thesis docs behavior for the repository tooling.

- L24 `def build_individual_chapters()` — Builds individual chapters. Receives: `not applicable`. Sends: `inferred or None`.
- L41 `def build_consolidated_thesis()` — Builds consolidated thesis. Receives: `not applicable`. Sends: `inferred or None`.

### [`scripts/build_full_kmutnb_thesis_thai.py`](../../scripts/build_full_kmutnb_thesis_thai.py)

Purpose: Owns build full kmutnb thesis thai behavior for the repository tooling.

- L20 `def build_monolithic_thesis()` — Builds monolithic thesis. Receives: `not applicable`. Sends: `inferred or None`.
- L57 `def build_individual_chapters()` — Builds individual chapters. Receives: `not applicable`. Sends: `inferred or None`.

### [`scripts/convert_thesis_to_docx.py`](../../scripts/convert_thesis_to_docx.py)

Purpose: Owns convert thesis to docx behavior for the repository tooling.

- L19 `def set_cell_background(cell, fill_hex)` — Updates cell background. Receives: `cell, fill_hex`. Sends: `inferred or None`.
- L24 `def set_cell_margins(cell, top=100, bottom=100, left=150, right=150)` — Updates cell margins. Receives: `cell, top=100, bottom=100, left=150, right=150`. Sends: `inferred or None`.
- L34 `def set_table_borders(table, color='D3D3D3', sz='4', val='single')` — Updates table borders. Receives: `table, color='D3D3D3', sz='4', val='single'`. Sends: `inferred or None`.
- L48 `def format_run(run, font_name=FONT_NAME, size=FONT_SIZE_BODY, bold=False, italic=False, color=None)` — Implements format run. Receives: `run, font_name=FONT_NAME, size=FONT_SIZE_BODY, bold=False, italic=False, color=None`. Sends: `inferred or None`.
- L60 `def add_formatted_text(paragraph, text, default_size=FONT_SIZE_BODY, default_bold=False, default_italic=False, default_color=None)` — Implements add formatted text. Receives: `paragraph, text, default_size=FONT_SIZE_BODY, default_bold=False, default_italic=False, default_color=None`. Sends: `inferred or None`.
- L83 `def setup_page_setup(section)` — Implements setup page setup. Receives: `section`. Sends: `inferred or None`.
- L91 `def convert_markdown_to_docx(md_content, doc=None)` — Transforms markdown to docx. Receives: `md_content, doc=None`. Sends: `inferred or None`.

### [`scripts/generate_architecture_pdf.py`](../../scripts/generate_architecture_pdf.py)

Purpose: Script to generate a comprehensive, highly-detailed PDF architecture document for CyberCase Intelligence Framework.

- L48 `def register_fonts()` — Implements register fonts. Receives: `not applicable`. Sends: `inferred or None`.
- L65 `def build_styles(reg, bold)` — Builds styles. Receives: `reg, bold`. Sends: `inferred or None`.
- L197 `def draw_header_footer(canvas, doc, reg, bold)` — Implements draw header footer. Receives: `canvas, doc, reg, bold`. Sends: `inferred or None`.
- L218 `def create_code_panel(code_text, styles)` — Creates code panel. Receives: `code_text, styles`. Sends: `inferred or None`.
- L232 `def create_info_panel(title, content, styles, bg_color=_PANEL, border_color=_BORDER)` — Creates info panel. Receives: `title, content, styles, bg_color=_PANEL, border_color=_BORDER`. Sends: `inferred or None`.
- L245 `def generate_pdf(output_path: str)` — Generates pdf. Receives: `output_path: str`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_chapter_1_2.py`](../../scripts/kmutnb_thai_chapter_1_2.py)

Purpose: Owns kmutnb thai chapter 1 2 behavior for the repository tooling.

- L9 `def build_chapter_1(doc)` — Builds chapter 1. Receives: `doc`. Sends: `inferred or None`.
- L71 `def build_chapter_2(doc)` — Builds chapter 2. Receives: `doc`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_chapter_3.py`](../../scripts/kmutnb_thai_chapter_3.py)

Purpose: Owns kmutnb thai chapter 3 behavior for the repository tooling.

- L10 `def build_chapter_3(doc)` — Builds chapter 3. Receives: `doc`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_chapter_4.py`](../../scripts/kmutnb_thai_chapter_4.py)

Purpose: Owns kmutnb thai chapter 4 behavior for the repository tooling.

- L10 `def build_chapter_4(doc)` — Builds chapter 4. Receives: `doc`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_chapter_5_6.py`](../../scripts/kmutnb_thai_chapter_5_6.py)

Purpose: Owns kmutnb thai chapter 5 6 behavior for the repository tooling.

- L10 `def add_ui_figure(doc, fig_num, fig_title, explanation)` — Implements add ui figure. Receives: `doc, fig_num, fig_title, explanation`. Sends: `inferred or None`.
- L39 `def build_chapter_5(doc)` — Builds chapter 5. Receives: `doc`. Sends: `inferred or None`.
- L236 `def build_chapter_6(doc)` — Builds chapter 6. Receives: `doc`. Sends: `inferred or None`.
- L279 `def build_bibliography(doc)` — Builds bibliography. Receives: `doc`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_front_matter.py`](../../scripts/kmutnb_thai_front_matter.py)

Purpose: Owns kmutnb thai front matter behavior for the repository tooling.

- L20 `def build_front_matter(doc)` — Builds front matter. Receives: `doc`. Sends: `inferred or None`.

### [`scripts/kmutnb_thai_helpers.py`](../../scripts/kmutnb_thai_helpers.py)

Purpose: Owns kmutnb thai helpers behavior for the repository tooling.

- L19 `def setup_page_setup(section)` — Implements setup page setup. Receives: `section`. Sends: `inferred or None`.
- L27 `def format_run(run, font_name=FONT_NAME, size=FONT_SIZE_BODY, bold=False, italic=False, color=None)` — Implements format run. Receives: `run, font_name=FONT_NAME, size=FONT_SIZE_BODY, bold=False, italic=False, color=None`. Sends: `inferred or None`.
- L38 `def set_cell_background(cell, fill_hex)` — Updates cell background. Receives: `cell, fill_hex`. Sends: `inferred or None`.
- L43 `def set_cell_margins(cell, top=100, bottom=100, left=150, right=150)` — Updates cell margins. Receives: `cell, top=100, bottom=100, left=150, right=150`. Sends: `inferred or None`.
- L53 `def set_table_borders(table, color='B0BEC5', sz='4', val='single')` — Updates table borders. Receives: `table, color='B0BEC5', sz='4', val='single'`. Sends: `inferred or None`.
- L67 `def add_p(doc, text='', align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.15, first_indent=0.5, bold=False, italic=False, font_size=FONT_SIZE_BODY, font_name=FONT_NAME, color=None)` — Implements add p. Receives: `doc, text='', align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.15, first_indent=0.5, bold=False, italic=False, font_size=FONT_SIZE_BODY, font_name=FONT_NAME, color=None`. Sends: `inferred or None`.
- L80 `def add_h1(doc, chapter_num, chapter_title)` — Implements add h1. Receives: `doc, chapter_num, chapter_title`. Sends: `inferred or None`.
- L95 `def add_h2(doc, title)` — Implements add h2. Receives: `doc, title`. Sends: `inferred or None`.
- L104 `def add_h3(doc, title)` — Implements add h3. Receives: `doc, title`. Sends: `inferred or None`.
- L113 `def add_h4(doc, title)` — Implements add h4. Receives: `doc, title`. Sends: `inferred or None`.
- L122 `def add_code_block(doc, title, code_text, explanation_text)` — Implements add code block. Receives: `doc, title, code_text, explanation_text`. Sends: `inferred or None`.
- L165 `def add_use_case_table(doc, table_num, uc_num, uc_name, brief_desc, actors, pre_cond, post_cond, main_flow_actor, main_flow_system, alt_flow, explanation)` — Implements add use case table. Receives: `doc, table_num, uc_num, uc_name, brief_desc, actors, pre_cond, post_cond, main_flow_actor, main_flow_system, alt_flow, explanation`. Sends: `inferred or None`.
- L266 `def add_data_dict_table(doc, table_num, table_name, table_desc, rows_data)` — Implements add data dict table. Receives: `doc, table_num, table_name, table_desc, rows_data`. Sends: `inferred or None`.

## Backend Regression Suite

### [`backend/tests/run_recovery_support.py`](../../backend/tests/run_recovery_support.py)

Purpose: Verifies run recovery support behavior in the backend regression suite.

- L16 `async def isolated_database()` — Implements isolated database. Receives: `not applicable`. Sends: `inferred or None`.
- L38 `async def create_request(factory)` — Creates request. Receives: `factory`. Sends: `inferred or None`.

### [`backend/tests/test_account_persistence.py`](../../backend/tests/test_account_persistence.py)

Purpose: Verifies account persistence behavior in the backend regression suite.

- L18 `def test_registered_accounts_persist_private_chats(monkeypatch)` — Implements test registered accounts persist private chats. Receives: `monkeypatch`. Sends: `inferred or None`.
- L21 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_analysis_pipeline_versioning.py`](../../backend/tests/test_analysis_pipeline_versioning.py)

Purpose: Verifies analysis pipeline versioning behavior in the backend regression suite.

- L16 `class RootDb` — Encapsulates rootdb. Receives: `constructor arguments and class fields`. Sends: `RootDb`.
- L17 `def __init__(self, config)` — Implements init. Receives: `self, config`. Sends: `inferred or None`.
- L20 `async def execute(self, statement)` — Executes execute. Receives: `self, statement`. Sends: `inferred or None`.
- L34 `def test_invalid_configuration_fails(payload)` — Implements test invalid configuration fails. Receives: `payload`. Sends: `inferred or None`.
- L39 `def test_missing_historical_configuration_means_legacy_even_after_setting_change(monkeypatch)` — Implements test missing historical configuration means legacy even after setting change. Receives: `monkeypatch`. Sends: `inferred or None`.
- L47 `def test_clarification_inherits_root_config_and_ask_stays_legacy(monkeypatch)` — Implements test clarification inherits root config and ask stays legacy. Receives: `monkeypatch`. Sends: `inferred or None`.
- L54 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L83 `def test_unknown_model_alias_cannot_silently_select_default(monkeypatch)` — Implements test unknown model alias cannot silently select default. Receives: `monkeypatch`. Sends: `inferred or None`.
- L90 `def test_historical_raw_direct_version_reads_without_mutating_saved_payload()` — Implements test historical raw direct version reads without mutating saved payload. Receives: `not applicable`. Sends: `inferred or None`.
- L97 `def test_historical_version_cannot_select_claim_anchored()` — Implements test historical version cannot select claim anchored. Receives: `not applicable`. Sends: `inferred or None`.
- L102 `def test_raw_direct_pipeline_matches_current_prompt_version()` — Implements test raw direct pipeline matches current prompt version. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_analysis_retirement_postgres.py`](../../backend/tests/test_analysis_retirement_postgres.py)

Purpose: Verifies analysis retirement postgres behavior in the backend regression suite.

- L19 `def test_ask_does_not_recover_context_behind_retired_analysis(metadata, blocked)` — Implements test ask does not recover context behind retired analysis. Receives: `metadata, blocked`. Sends: `inferred or None`.
- L20 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_analysis_retirement_selection.py`](../../backend/tests/test_analysis_retirement_selection.py)

Purpose: Verifies analysis retirement selection behavior in the backend regression suite.

- L14 `def test_newer_retired_or_invalid_overview_blocks_older_valid_record(trace)` — Implements test newer retired or invalid overview blocks older valid record. Receives: `trace`. Sends: `inferred or None`.
- L29 `def test_response_scope_wins_over_legacy_marker(scope)` — Implements test response scope wins over legacy marker. Receives: `scope`. Sends: `inferred or None`.

### [`backend/tests/test_analysis_trace.py`](../../backend/tests/test_analysis_trace.py)

Purpose: Verifies analysis trace behavior in the backend regression suite.

- L15 `def analysis_v3(source_ids: list[str], technique_id: str='T1190') -> AnalysisTraceV3` — Implements analysis v3. Receives: `source_ids: list[str], technique_id: str='T1190'`. Sends: `AnalysisTraceV3`.
- L52 `def test_trace_binds_reported_claims_to_messages_and_mitre_to_retrieval() -> None` — Implements test trace binds reported claims to messages and mitre to retrieval. Receives: `not applicable`. Sends: `None`.
- L62 `def test_reported_claim_cannot_cite_a_non_evidence_message() -> None` — Implements test reported claim cannot cite a non evidence message. Receives: `not applicable`. Sends: `None`.
- L71 `def test_mitre_association_cannot_escape_bound_context() -> None` — Implements test mitre association cannot escape bound context. Receives: `not applicable`. Sends: `None`.
- L80 `def test_v3_validation_rejects_legacy_v2_shape() -> None` — Implements test v3 validation rejects legacy v2 shape. Receives: `not applicable`. Sends: `None`.
- L90 `def test_legacy_v2_trace_read_only_deserialization() -> None` — Implements test legacy v2 trace read only deserialization. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_analysis_trace_cross_domain.py`](../../backend/tests/test_analysis_trace_cross_domain.py)

Purpose: Verifies analysis trace cross domain behavior in the backend regression suite.

- L17 `def test_v3_contract_is_domain_neutral(domain: str, claim_text: str) -> None` — Implements test v3 contract is domain neutral. Receives: `domain: str, claim_text: str`. Sends: `None`.

### [`backend/tests/test_analysis_trace_v3.py`](../../backend/tests/test_analysis_trace_v3.py)

Purpose: Verifies analysis trace v3 behavior in the backend regression suite.

- L16 `def build_trace(*, claims: list[dict[str, object]] | None=None, gaps: list[dict[str, object]] | None=None, retrieval_context_id: str | None=None) -> AnalysisTraceV3` — Builds trace. Receives: `*, claims: list[dict[str, object]] | None=None, gaps: list[dict[str, object]] | None=None, retrieval_context_id: str | None=None`. Sends: `AnalysisTraceV3`.
- L49 `def reported_claim(*, claim_id: str='A-01', supporting: list[str] | None=None, contradicting: list[str] | None=None) -> dict[str, object]` — Implements reported claim. Receives: `*, claim_id: str='A-01', supporting: list[str] | None=None, contradicting: list[str] | None=None`. Sends: `dict[str, object]`.
- L66 `def analysis_gap(*, gap_id: str='G-01', status: str='NOT_PROVIDED', affected_claim_ids: list[str] | None=None, askable: bool=True) -> dict[str, object]` — Implements analysis gap. Receives: `*, gap_id: str='G-01', status: str='NOT_PROVIDED', affected_claim_ids: list[str] | None=None, askable: bool=True`. Sends: `dict[str, object]`.
- L85 `def test_valid_reported_claim() -> None` — Implements test valid reported claim. Receives: `not applicable`. Sends: `None`.
- L91 `def test_reported_claim_without_support_is_rejected() -> None` — Implements test reported claim without support is rejected. Receives: `not applicable`. Sends: `None`.
- L98 `def test_valid_analytical_inference() -> None` — Implements test valid analytical inference. Receives: `not applicable`. Sends: `None`.
- L116 `def test_valid_unknown_not_established_claim() -> None` — Implements test valid unknown not established claim. Receives: `not applicable`. Sends: `None`.
- L144 `def test_claim_source_outside_evidence_snapshot_is_rejected(field_name: str, expected_code: str) -> None` — Implements test claim source outside evidence snapshot is rejected. Receives: `field_name: str, expected_code: str`. Sends: `None`.
- L156 `def test_same_source_cannot_support_and_contradict_claim() -> None` — Implements test same source cannot support and contradict claim. Receives: `not applicable`. Sends: `None`.
- L170 `def test_inference_without_reasoning_summary_is_rejected() -> None` — Implements test inference without reasoning summary is rejected. Receives: `not applicable`. Sends: `None`.
- L189 `def test_duplicate_claim_id_is_rejected() -> None` — Implements test duplicate claim id is rejected. Receives: `not applicable`. Sends: `None`.
- L204 `def test_duplicate_gap_id_is_rejected() -> None` — Implements test duplicate gap id is rejected. Receives: `not applicable`. Sends: `None`.
- L212 `def test_gap_referencing_nonexistent_claim_is_rejected() -> None` — Implements test gap referencing nonexistent claim is rejected. Receives: `not applicable`. Sends: `None`.
- L221 `def test_duplicate_affected_claim_id_is_rejected() -> None` — Implements test duplicate affected claim id is rejected. Receives: `not applicable`. Sends: `None`.
- L226 `def test_explicitly_unknown_case_level_gap_parses_correctly() -> None` — Implements test explicitly unknown case level gap parses correctly. Receives: `not applicable`. Sends: `None`.
- L233 `def test_explicitly_unknown_gap_cannot_be_askable() -> None` — Implements test explicitly unknown gap cannot be askable. Receives: `not applicable`. Sends: `None`.
- L240 `def test_reported_claim_can_preserve_conflicting_evidence() -> None` — Implements test reported claim can preserve conflicting evidence. Receives: `not applicable`. Sends: `None`.
- L256 `def test_v2_trace_remains_readable_without_v3_reinterpretation() -> None` — Implements test v2 trace remains readable without v3 reinterpretation. Receives: `not applicable`. Sends: `None`.
- L282 `def test_v3_trace_with_null_retrieval_context_is_valid() -> None` — Implements test v3 trace with null retrieval context is valid. Receives: `not applicable`. Sends: `None`.
- L288 `def test_v3_case_overview_requires_evidence_hash() -> None` — Implements test v3 case overview requires evidence hash. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_auth_jwt.py`](../../backend/tests/test_auth_jwt.py)

Purpose: Verifies auth jwt behavior in the backend regression suite.

- L11 `def test_create_and_decode_valid_access_token()` — Implements test create and decode valid access token. Receives: `not applicable`. Sends: `inferred or None`.
- L27 `def test_decode_token_with_wrong_secret()` — Implements test decode token with wrong secret. Receives: `not applicable`. Sends: `inferred or None`.
- L39 `def test_decode_expired_token()` — Implements test decode expired token. Receives: `not applicable`. Sends: `inferred or None`.
- L51 `def test_decode_invalid_token_format()` — Implements test decode invalid token format. Receives: `not applicable`. Sends: `inferred or None`.
- L57 `def test_signing_key(monkeypatch)` — Implements test signing key. Receives: `monkeypatch`. Sends: `inferred or None`.

### [`backend/tests/test_auth_routes.py`](../../backend/tests/test_auth_routes.py)

Purpose: Verifies auth routes behavior in the backend regression suite.

- L14 `def _fastapi_app() -> FastAPI` — Implements fastapi app. Receives: `not applicable`. Sends: `FastAPI`.
- L22 `def mock_db()` — Implements mock db. Receives: `not applicable`. Sends: `inferred or None`.
- L28 `def client(mock_db, monkeypatch)` — Implements client. Receives: `mock_db, monkeypatch`. Sends: `inferred or None`.
- L36 `def test_session_unauthenticated(client)` — Implements test session unauthenticated. Receives: `client`. Sends: `inferred or None`.
- L42 `def test_me_unauthenticated_returns_401(client)` — Implements test me unauthenticated returns 401. Receives: `client`. Sends: `inferred or None`.
- L47 `def test_dev_login_and_authenticated_session(client, mock_db, monkeypatch)` — Implements test dev login and authenticated session. Receives: `client, mock_db, monkeypatch`. Sends: `inferred or None`.
- L101 `def test_logout_clears_session(client, mock_db)` — Implements test logout clears session. Receives: `client, mock_db`. Sends: `inferred or None`.
- L111 `def test_oauth_login_redirect_google(client)` — Implements test oauth login redirect google. Receives: `client`. Sends: `inferred or None`.
- L120 `def test_oauth_login_unconfigured_provider(client)` — Implements test oauth login unconfigured provider. Receives: `client`. Sends: `inferred or None`.

### [`backend/tests/test_canonical_analysis_state.py`](../../backend/tests/test_canonical_analysis_state.py)

Purpose: Verifies canonical analysis state behavior in the backend regression suite.

- L13 `def claim(claim_id: str, text: str) -> dict[str, object]` — Implements claim. Receives: `claim_id: str, text: str`. Sends: `dict[str, object]`.
- L25 `def trace_payload(mode: str, *, summary: str, gaps: list[dict[str, object]]) -> dict[str, object]` — Implements trace payload. Receives: `mode: str, *, summary: str, gaps: list[dict[str, object]]`. Sends: `dict[str, object]`.
- L44 `def gap_payload() -> dict[str, object]` — Implements gap payload. Receives: `not applicable`. Sends: `dict[str, object]`.
- L57 `def message(ordinal: int, trace: dict[str, object]) -> ChatMessage` — Implements message. Receives: `ordinal: int, trace: dict[str, object]`. Sends: `ChatMessage`.
- L68 `def test_qa_trace_cannot_replace_canonical_case_overview() -> None` — Implements test qa trace cannot replace canonical case overview. Receives: `not applicable`. Sends: `None`.
- L95 `def test_invalid_main_trace_with_gap_metadata_is_not_canonical_state() -> None` — Implements test invalid main trace with gap metadata is not canonical state. Receives: `not applicable`. Sends: `None`.
- L121 `def test_invalid_later_main_trace_blocks_older_canonical_gaps() -> None` — Implements test invalid later main trace blocks older canonical gaps. Receives: `not applicable`. Sends: `None`.
- L155 `def test_question_answer_is_response_scoped_and_runs_main_analysis_once() -> None` — Implements test question answer is response scoped and runs main analysis once. Receives: `not applicable`. Sends: `None`.
- L177 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_case_chat_postgres.py`](../../backend/tests/test_case_chat_postgres.py)

Purpose: Verifies case chat postgres behavior in the backend regression suite.

- L34 `async def _case_with_source(factory)` — Implements case with source. Receives: `factory`. Sends: `inferred or None`.
- L48 `async def _enqueue(factory, case_id, key)` — Implements enqueue. Receives: `factory, case_id, key`. Sends: `inferred or None`.
- L63 `def _output(snapshot, source_id, *, mode='case_overview', followup=False)` — Implements output. Receives: `snapshot, source_id, *, mode='case_overview', followup=False`. Sends: `inferred or None`.
- L99 `async def _complete_initial(factory, case_id, source_id, *, followup=True)` — Implements complete initial. Receives: `factory, case_id, source_id, *, followup=True`. Sends: `inferred or None`.
- L116 `def test_case_publication_and_clarification_are_separate_and_idempotent()` — Implements test case publication and clarification are separate and idempotent. Receives: `not applicable`. Sends: `inferred or None`.
- L117 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L187 `def test_case_ask_uses_case_run_without_new_result_or_evidence()` — Implements test case ask uses case run without new result or evidence. Receives: `not applicable`. Sends: `inferred or None`.
- L188 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L238 `def test_first_case_chat_ask_requires_completed_analysis()` — Implements test first case chat ask requires completed analysis. Receives: `not applicable`. Sends: `inferred or None`.
- L239 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L260 `def test_removing_chat_preserves_case_history()` — Implements test removing chat preserves case history. Receives: `not applicable`. Sends: `inferred or None`.
- L261 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_case_materials_postgres.py`](../../backend/tests/test_case_materials_postgres.py)

Purpose: Verifies case materials postgres behavior in the backend regression suite.

- L13 `def test_case_materials_are_revisioned_and_snapshots_are_reproducible()` — Implements test case materials are revisioned and snapshots are reproducible. Receives: `not applicable`. Sends: `inferred or None`.
- L14 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L103 `def test_case_materials_case_lock_serializes_concurrent_admission()` — Implements test case materials case lock serializes concurrent admission. Receives: `not applicable`. Sends: `inferred or None`.
- L104 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L110 `async def admit(text)` — Implements admit. Receives: `text`. Sends: `inferred or None`.

### [`backend/tests/test_case_reports_postgres.py`](../../backend/tests/test_case_reports_postgres.py)

Purpose: Verifies case reports postgres behavior in the backend regression suite.

- L25 `async def _case_with_source(factory)` — Implements case with source. Receives: `factory`. Sends: `inferred or None`.
- L39 `async def _complete(factory, case_id, source_id, key)` — Implements complete. Receives: `factory, case_id, source_id, key`. Sends: `inferred or None`.
- L84 `def test_case_report_is_bound_to_selected_native_result_and_snapshot()` — Implements test case report is bound to selected native result and snapshot. Receives: `not applicable`. Sends: `inferred or None`.
- L85 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L125 `def test_case_report_reuses_old_result_snapshot_after_new_evidence()` — Implements test case report reuses old result snapshot after new evidence. Receives: `not applicable`. Sends: `inferred or None`.
- L126 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L158 `def test_chat_removal_preserves_case_report_and_history()` — Implements test chat removal preserves case report and history. Receives: `not applicable`. Sends: `inferred or None`.
- L159 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_case_runs_postgres.py`](../../backend/tests/test_case_runs_postgres.py)

Purpose: Verifies case runs postgres behavior in the backend regression suite.

- L26 `async def _case_with_source(factory)` — Implements case with source. Receives: `factory`. Sends: `inferred or None`.
- L41 `async def _enqueue(factory, case_id, key, expected_revision=1)` — Implements enqueue. Receives: `factory, case_id, key, expected_revision=1`. Sends: `inferred or None`.
- L56 `def _output(snapshot: CaseEvidenceSnapshot, source_id) -> AnalysisOutput` — Implements output. Receives: `snapshot: CaseEvidenceSnapshot, source_id`. Sends: `AnalysisOutput`.
- L86 `def test_case_analysis_is_case_owned_and_idempotent_under_postgres_race()` — Implements test case analysis is case owned and idempotent under postgres race. Receives: `not applicable`. Sends: `inferred or None`.
- L87 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L91 `async def submit()` — Implements submit. Receives: `not applicable`. Sends: `inferred or None`.
- L114 `def test_case_analysis_completion_publishes_only_after_valid_case_run()` — Implements test case analysis completion publishes only after valid case run. Receives: `not applicable`. Sends: `inferred or None`.
- L115 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L121 `async def fake_analysis(**kwargs)` — Implements fake analysis. Receives: `**kwargs`. Sends: `inferred or None`.
- L175 `def test_case_completion_failure_rolls_back_result_and_publication(monkeypatch)` — Implements test case completion failure rolls back result and publication. Receives: `monkeypatch`. Sends: `inferred or None`.
- L176 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L188 `def fail_metadata(_value)` — Implements fail metadata. Receives: `_value`. Sends: `inferred or None`.
- L217 `def test_expired_case_worker_is_fenced_and_recovery_marks_it_failed()` — Implements test expired case worker is fenced and recovery marks it failed. Receives: `not applicable`. Sends: `inferred or None`.
- L218 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_chat_delete.py`](../../backend/tests/test_chat_delete.py)

Purpose: Verifies chat delete behavior in the backend regression suite.

- L11 `class ChatDeleteServiceTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates chatdeleteservicetests. Receives: `constructor arguments and class fields`. Sends: `ChatDeleteServiceTests`.
- L12 `async def test_delete_thread_locks_and_deletes_parent(self) -> None` — Implements test delete thread locks and deletes parent. Receives: `self`. Sends: `None`.
- L28 `async def test_delete_missing_thread_returns_404(self) -> None` — Implements test delete missing thread returns 404. Receives: `self`. Sends: `None`.

### [`backend/tests/test_chat_followup_policy.py`](../../backend/tests/test_chat_followup_policy.py)

Purpose: Verifies chat followup policy behavior in the backend regression suite.

- L13 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L14 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L33 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L34 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L43 `def test_followup_consumes_raw_evidence_without_case_state() -> None` — Implements test followup consumes raw evidence without case state. Receives: `not applicable`. Sends: `None`.
- L74 `def test_gap_analysis_contract_uses_free_text_affects_and_preserves_unknown() -> None` — Implements test gap analysis contract uses free text affects and preserves unknown. Receives: `not applicable`. Sends: `None`.
- L98 `def test_extract_llm_json_markdown_fences() -> None` — Implements test extract llm json markdown fences. Receives: `not applicable`. Sends: `None`.
- L111 `def test_extract_llm_json_surrounding_text() -> None` — Implements test extract llm json surrounding text. Receives: `not applicable`. Sends: `None`.
- L119 `def test_extract_llm_text_and_thinking_blocks() -> None` — Implements test extract llm text and thinking blocks. Receives: `not applicable`. Sends: `None`.
- L145 `def test_followup_schemas_lenient_coercion() -> None` — Implements test followup schemas lenient coercion. Receives: `not applicable`. Sends: `None`.
- L177 `def test_reconstruct_clarification_chain_with_bound_metadata() -> None` — Implements test reconstruct clarification chain with bound metadata. Receives: `not applicable`. Sends: `None`.
- L225 `def test_answer_indicates_unavailable_thai_and_english() -> None` — Implements test answer indicates unavailable thai and english. Receives: `not applicable`. Sends: `None`.
- L245 `def test_evaluate_followup_proceeds_when_only_gap_is_explicitly_unknown() -> None` — Implements test evaluate followup proceeds when only gap is explicitly unknown. Receives: `not applicable`. Sends: `None`.
- L248 `class UnknownAnalyzer` — Encapsulates unknownanalyzer. Receives: `constructor arguments and class fields`. Sends: `UnknownAnalyzer`.
- L249 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_chat_ownership.py`](../../backend/tests/test_chat_ownership.py)

Purpose: Verifies chat ownership behavior in the backend regression suite.

- L18 `def _fastapi_app() -> FastAPI` — Implements fastapi app. Receives: `not applicable`. Sends: `FastAPI`.
- L25 `class ChatOwnershipServiceTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates chatownershipservicetests. Receives: `constructor arguments and class fields`. Sends: `ChatOwnershipServiceTests`.
- L26 `async def test_chat_service_create_thread_guest_and_user(self)` — Implements test chat service create thread guest and user. Receives: `self`. Sends: `inferred or None`.
- L46 `async def test_chat_service_access_verification(self)` — Implements test chat service access verification. Receives: `self`. Sends: `inferred or None`.
- L78 `async def test_chat_service_update_and_delete_ownership(self)` — Implements test chat service update and delete ownership. Receives: `self`. Sends: `inferred or None`.
- L118 `def mock_db()` — Implements mock db. Receives: `not applicable`. Sends: `inferred or None`.
- L124 `def client(mock_db)` — Implements client. Receives: `mock_db`. Sends: `inferred or None`.
- L131 `def test_api_chat_thread_ownership_routes(client, mock_db)` — Implements test api chat thread ownership routes. Receives: `client, mock_db`. Sends: `inferred or None`.

### [`backend/tests/test_chat_rag_client.py`](../../backend/tests/test_chat_rag_client.py)

Purpose: Verifies chat rag client behavior in the backend regression suite.

- L11 `class ChatRagClientTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates chatragclienttests. Receives: `constructor arguments and class fields`. Sends: `ChatRagClientTests`.
- L12 `async def test_query_payload_and_completed_mapping(self) -> None` — Implements test query payload and completed mapping. Receives: `self`. Sends: `None`.
- L15 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.
- L47 `async def test_answer_fields_are_rejected(self) -> None` — Implements test answer fields are rejected. Receives: `self`. Sends: `None`.
- L50 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.
- L69 `async def test_non_completed_response_is_rejected(self) -> None` — Implements test non completed response is rejected. Receives: `self`. Sends: `None`.
- L70 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.
- L94 `class ChatRagResponseMappingTests(unittest.TestCase)` — Encapsulates chatragresponsemappingtests. Receives: `constructor arguments and class fields`. Sends: `ChatRagResponseMappingTests`.
- L95 `def test_completed_mitre_rows_are_json_safe_and_preserve_fields(self) -> None` — Implements test completed mitre rows are json safe and preserve fields. Receives: `self`. Sends: `None`.
- L123 `def test_empty_no_hit_context_and_empty_id_sentinel_are_valid(self) -> None` — Implements test empty no hit context and empty id sentinel are valid. Receives: `self`. Sends: `None`.

### [`backend/tests/test_chat_raw_pipeline.py`](../../backend/tests/test_chat_raw_pipeline.py)

Purpose: Verifies chat raw pipeline behavior in the backend regression suite.

- L31 `def claimed(action: str)` — Implements claimed. Receives: `action: str`. Sends: `inferred or None`.
- L53 `async def retrieve_gate(**kwargs)` — Implements retrieve gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L63 `def test_initial_and_added_information_run_fresh_rag_on_raw_evidence(action: str) -> None` — Implements test initial and added information run fresh rag on raw evidence. Receives: `action: str`. Sends: `None`.
- L69 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L83 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L90 `async def followup_evaluator(**kwargs)` — Implements followup evaluator. Receives: `**kwargs`. Sends: `inferred or None`.
- L110 `def test_ask_reuses_context_and_does_not_create_rag_payload() -> None` — Implements test ask reuses context and does not create rag payload. Receives: `not applicable`. Sends: `None`.
- L113 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L124 `def test_v3_trace_persists_without_a_retrieval_context() -> None` — Implements test v3 trace persists without a retrieval context. Receives: `not applicable`. Sends: `None`.
- L158 `def test_v2_trace_reading_remains_backward_compatible() -> None` — Implements test v2 trace reading remains backward compatible. Receives: `not applicable`. Sends: `None`.
- L174 `def test_serialize_analysis_trace_rejects_unsupported_draft() -> None` — Implements test serialize analysis trace rejects unsupported draft. Receives: `not applicable`. Sends: `None`.
- L187 `def test_fresh_pipeline_uses_one_analysis_and_one_gap_result_for_both_surfaces() -> None` — Implements test fresh pipeline uses one analysis and one gap result for both surfaces. Receives: `not applicable`. Sends: `None`.
- L194 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L202 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L232 `class CountingGapAnalyzer` — Encapsulates countinggapanalyzer. Receives: `constructor arguments and class fields`. Sends: `CountingGapAnalyzer`.
- L233 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L253 `class AskPolicy` — Encapsulates askpolicy. Receives: `constructor arguments and class fields`. Sends: `AskPolicy`.
- L254 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_chat_report.py`](../../backend/tests/test_chat_report.py)

Purpose: Verifies chat report behavior in the backend regression suite.

- L15 `def report_snapshot(*, with_rag: bool=True)` — Implements report snapshot. Receives: `*, with_rag: bool=True`. Sends: `inferred or None`.
- L68 `def test_report_snapshot_uses_raw_messages_analysis_and_run_context() -> None` — Implements test report snapshot uses raw messages analysis and run context. Receives: `not applicable`. Sends: `None`.
- L77 `def test_report_snapshot_supports_general_analysis_without_rag_context() -> None` — Implements test report snapshot supports general analysis without rag context. Receives: `not applicable`. Sends: `None`.
- L87 `def test_report_snapshot_hash_ignores_capture_time() -> None` — Implements test report snapshot hash ignores capture time. Receives: `not applicable`. Sends: `None`.
- L96 `def test_deterministic_report_validates_against_source_and_mitre_bindings() -> None` — Implements test deterministic report validates against source and mitre bindings. Receives: `not applicable`. Sends: `None`.
- L109 `class ReportGenerationTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates reportgenerationtests. Receives: `constructor arguments and class fields`. Sends: `ReportGenerationTests`.
- L110 `async def test_generation_does_not_block_on_custom_binding_validation(self) -> None` — Implements test generation does not block on custom binding validation. Receives: `self`. Sends: `None`.

### [`backend/tests/test_claim_anchored_binding.py`](../../backend/tests/test_claim_anchored_binding.py)

Purpose: Verifies claim anchored binding behavior in the backend regression suite.

- L12 `def source_context(text='พยานไม่เห็นผู้ต้องหา', source_id='message-1')` — Implements source context. Receives: `text='พยานไม่เห็นผู้ต้องหา', source_id='message-1'`. Sends: `inferred or None`.
- L19 `def extraction(quote='พยานไม่เห็นผู้ต้องหา', source_id='message-1', **updates)` — Implements extraction. Receives: `quote='พยานไม่เห็นผู้ต้องหา', source_id='message-1', **updates`. Sends: `inferred or None`.
- L33 `def bind(text, quote, documents=None)` — Implements bind. Receives: `text, quote, documents=None`. Sends: `inferred or None`.
- L39 `def page(text, start, end, number)` — Implements page. Receives: `text, start, end, number`. Sends: `inferred or None`.
- L48 `def documents(spans)` — Implements documents. Receives: `spans`. Sends: `inferred or None`.
- L63 `def test_thai_offsets_preserve_exact_original_text()` — Implements test thai offsets preserve exact original text. Receives: `not applicable`. Sends: `inferred or None`.
- L82 `def test_literal_binding_does_not_claim_semantic_support(text, quote, code)` — Implements test literal binding does not claim semantic support. Receives: `text, quote, code`. Sends: `inferred or None`.
- L91 `def test_repeated_quote_on_one_page_remains_ambiguous()` — Implements test repeated quote on one page remains ambiguous. Receives: `not applicable`. Sends: `inferred or None`.
- L98 `def test_unknown_source_and_same_source_opposing_roles_fail()` — Implements test unknown source and same source opposing roles fail. Receives: `not applicable`. Sends: `inferred or None`.
- L118 `def test_cross_page_binding_and_stale_provenance()` — Implements test cross page binding and stale provenance. Receives: `not applicable`. Sends: `inferred or None`.
- L130 `def test_registry_requires_exact_admitted_source_set()` — Implements test registry requires exact admitted source set. Receives: `not applicable`. Sends: `inferred or None`.
- L137 `def test_uncovered_text_between_pages_cannot_gain_a_page_locator()` — Implements test uncovered text between pages cannot gain a page locator. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_claim_anchored_pipeline.py`](../../backend/tests/test_claim_anchored_pipeline.py)

Purpose: Verifies claim anchored pipeline behavior in the backend regression suite.

- L14 `def envelope(value)` — Implements envelope. Receives: `value`. Sends: `inferred or None`.
- L22 `def run_pipeline(monkeypatch, *, quote='พยานไม่เห็นผู้ต้องหา', config=None, generated=None, status=200)` — Executes pipeline. Receives: `monkeypatch, *, quote='พยานไม่เห็นผู้ต้องหา', config=None, generated=None, status=200`. Sends: `inferred or None`.
- L40 `def handler(request)` — Implements handler. Receives: `request`. Sends: `inferred or None`.
- L54 `async def execute()` — Executes execute. Receives: `not applicable`. Sends: `inferred or None`.
- L68 `def test_two_stage_pipeline_is_source_isolated_and_compatible(monkeypatch)` — Implements test two stage pipeline is source isolated and compatible. Receives: `monkeypatch`. Sends: `inferred or None`.
- L89 `def test_invalid_quote_fails_before_generation_without_legacy_fallback(monkeypatch)` — Implements test invalid quote fails before generation without legacy fallback. Receives: `monkeypatch`. Sends: `inferred or None`.
- L98 `def test_generation_failure_keeps_extraction_receipt(monkeypatch)` — Implements test generation failure keeps extraction receipt. Receives: `monkeypatch`. Sends: `inferred or None`.
- L107 `def test_input_budget_fails_before_any_provider_call(monkeypatch)` — Implements test input budget fails before any provider call. Receives: `monkeypatch`. Sends: `inferred or None`.
- L118 `def test_generator_cannot_rewrite_citations_or_claim_metadata(monkeypatch)` — Implements test generator cannot rewrite citations or claim metadata. Receives: `monkeypatch`. Sends: `inferred or None`.

### [`backend/tests/test_claim_anchored_postgres.py`](../../backend/tests/test_claim_anchored_postgres.py)

Purpose: Verifies claim anchored postgres behavior in the backend regression suite.

- L27 `async def forbidden(*args, **kwargs)` — Implements forbidden. Receives: `*args, **kwargs`. Sends: `inferred or None`.
- L31 `def transport(request, *, invalid=False)` — Implements transport. Receives: `request, *, invalid=False`. Sends: `inferred or None`.
- L53 `async def execute(factory, run_id, *, invalid=False, ask_followup=False)` — Executes execute. Receives: `factory, run_id, *, invalid=False, ask_followup=False`. Sends: `inferred or None`.
- L60 `async def analyze(**kwargs)` — Implements analyze. Receives: `**kwargs`. Sends: `inferred or None`.
- L79 `def configure(monkeypatch)` — Implements configure. Receives: `monkeypatch`. Sends: `inferred or None`.
- L86 `def test_interrupted_run_keeps_pinned_method_and_stage_receipt(monkeypatch)` — Implements test interrupted run keeps pinned method and stage receipt. Receives: `monkeypatch`. Sends: `inferred or None`.
- L89 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L158 `def test_provider_failure_survives_heartbeat_exception_group(monkeypatch)` — Implements test provider failure survives heartbeat exception group. Receives: `monkeypatch`. Sends: `inferred or None`.
- L161 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L185 `def test_clarification_inherits_pinned_root_after_setting_changes(monkeypatch)` — Implements test clarification inherits pinned root after setting changes. Receives: `monkeypatch`. Sends: `inferred or None`.
- L188 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_claim_anchored_selection.py`](../../backend/tests/test_claim_anchored_selection.py)

Purpose: Verifies claim anchored selection behavior in the backend regression suite.

- L16 `def candidates(count=3)` — Implements candidates. Receives: `count=3`. Sends: `inferred or None`.
- L28 `def select(values, max_claims=64, fits=lambda _: True)` — Extracts select. Receives: `values, max_claims=64, fits=lambda _: True`. Sends: `inferred or None`.
- L34 `def test_selector_records_duplicates_and_claim_cap_without_silent_overflow()` — Implements test selector records duplicates and claim cap without silent overflow. Receives: `not applicable`. Sends: `inferred or None`.
- L46 `def test_uncertainty_is_reserved_and_cannot_be_dropped_to_fit()` — Implements test uncertainty is reserved and cannot be dropped to fit. Receives: `not applicable`. Sends: `inferred or None`.
- L61 `def test_generation_cannot_lose_selected_claims_or_add_unknown_ids()` — Implements test generation cannot lose selected claims or add unknown ids. Receives: `not applicable`. Sends: `inferred or None`.
- L75 `def test_assembly_copies_citations_status_and_joins_only_valid_units()` — Implements test assembly copies citations status and joins only valid units. Receives: `not applicable`. Sends: `inferred or None`.
- L92 `def test_selection_is_stable_and_uses_actual_fit_function()` — Implements test selection is stable and uses actual fit function. Receives: `not applicable`. Sends: `inferred or None`.
- L95 `def budget(selected)` — Implements budget. Receives: `selected`. Sends: `inferred or None`.

### [`backend/tests/test_claim_anchored_verification_boundary.py`](../../backend/tests/test_claim_anchored_verification_boundary.py)

Purpose: Verifies claim anchored verification boundary behavior in the backend regression suite.

- L15 `def test_future_verifier_can_reject_but_cannot_mutate_bound_claims(monkeypatch, reject)` — Implements test future verifier can reject but cannot mutate bound claims. Receives: `monkeypatch, reject`. Sends: `inferred or None`.
- L21 `class Verifier` — Encapsulates verifier. Receives: `constructor arguments and class fields`. Sends: `Verifier`.
- L22 `async def check_claims(self, claims)` — Validates claims. Receives: `self, claims`. Sends: `inferred or None`.
- L30 `async def check_summary(self, summary, claims)` — Validates summary. Receives: `self, summary, claims`. Sends: `inferred or None`.
- L34 `def handler(request)` — Implements handler. Receives: `request`. Sends: `inferred or None`.
- L44 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_claim_anchored_workflow.py`](../../backend/tests/test_claim_anchored_workflow.py)

Purpose: Verifies claim anchored workflow behavior in the backend regression suite.

- L20 `async def forbidden(**kwargs)` — Implements forbidden. Receives: `**kwargs`. Sends: `inferred or None`.
- L24 `def test_followup_keeps_receipt_and_case_only_gap_input(monkeypatch)` — Implements test followup keeps receipt and case only gap input. Receives: `monkeypatch`. Sends: `inferred or None`.
- L33 `def handler(request)` — Implements handler. Receives: `request`. Sends: `inferred or None`.
- L44 `class CaseAnalyzer(Analyzer)` — Encapsulates caseanalyzer. Receives: `constructor arguments and class fields`. Sends: `CaseAnalyzer`.
- L45 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L51 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L54 `async def analyze(**kwargs)` — Implements analyze. Receives: `**kwargs`. Sends: `inferred or None`.
- L86 `def test_gap_failure_cannot_publish_attribute_first_without_trace()` — Implements test gap failure cannot publish attribute first without trace. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_context_budgeting.py`](../../backend/tests/test_context_budgeting.py)

Purpose: Verifies context budgeting behavior in the backend regression suite.

- L17 `def payload_from_prompt(prompt: str) -> dict[str, object]` — Implements payload from prompt. Receives: `prompt: str`. Sends: `dict[str, object]`.
- L25 `def test_full_evidence_below_budget_survives_in_full() -> None` — Implements test full evidence below budget survives in full. Receives: `not applicable`. Sends: `None`.
- L55 `def test_empty_external_context_does_not_arbitrarily_cut_evidence() -> None` — Implements test empty external context does not arbitrarily cut evidence. Receives: `not applicable`. Sends: `None`.
- L82 `def test_evidence_has_priority_over_external_context() -> None` — Implements test evidence has priority over external context. Receives: `not applicable`. Sends: `None`.
- L118 `def test_large_input_close_to_budget_accepted_without_truncation() -> None` — Implements test large input close to budget accepted without truncation. Receives: `not applicable`. Sends: `None`.
- L144 `def test_overflow_produces_valid_json_with_truncation_metadata() -> None` — Implements test overflow produces valid json with truncation metadata. Receives: `not applicable`. Sends: `None`.
- L173 `def test_thai_case_positional_regression_preserves_all_complainants() -> None` — Implements test thai case positional regression preserves all complainants. Receives: `not applicable`. Sends: `None`.
- L220 `def test_followup_context_builder_preserves_large_evidence() -> None` — Implements test followup context builder preserves large evidence. Receives: `not applicable`. Sends: `None`.
- L265 `def test_token_budget_diagnostics_calculation() -> None` — Implements test token budget diagnostics calculation. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_core_llm_provider.py`](../../backend/tests/test_core_llm_provider.py)

Purpose: Verifies core llm provider behavior in the backend regression suite.

- L12 `class CoreLlmProviderTests(unittest.TestCase)` — Encapsulates corellmprovidertests. Receives: `constructor arguments and class fields`. Sends: `CoreLlmProviderTests`.
- L14 `def _settings(*, provider: str='openrouter', openrouter_key: str='', anthropic_key: str='') -> Settings` — Implements settings. Receives: `*, provider: str='openrouter', openrouter_key: str='', anthropic_key: str=''`. Sends: `Settings`.
- L27 `def test_default_provider_is_openrouter(self) -> None` — Implements test default provider is openrouter. Receives: `self`. Sends: `None`.
- L33 `def test_openrouter_target_uses_dedicated_secret_and_bearer_auth(self) -> None` — Implements test openrouter target uses dedicated secret and bearer auth. Receives: `self`. Sends: `None`.
- L45 `def test_openrouter_target_resolves_aliases(self) -> None` — Implements test openrouter target resolves aliases. Receives: `self`. Sends: `None`.
- L52 `def test_anthropic_target_preserves_feature_model_and_native_auth(self) -> None` — Implements test anthropic target preserves feature model and native auth. Receives: `self`. Sends: `None`.
- L67 `def test_invalid_provider_is_rejected_by_settings(self) -> None` — Implements test invalid provider is rejected by settings. Receives: `self`. Sends: `None`.
- L71 `def test_selected_provider_missing_key_has_no_fallback(self) -> None` — Implements test selected provider missing key has no fallback. Receives: `self`. Sends: `None`.
- L87 `def test_openrouter_api_key_cannot_satisfy_production_target(self) -> None` — Implements test openrouter api key cannot satisfy production target. Receives: `self`. Sends: `None`.

### [`backend/tests/test_cors.py`](../../backend/tests/test_cors.py)

Purpose: Verifies cors behavior in the backend regression suite.

- L6 `def test_localhost_frontend_cors_preflight_is_allowed() -> None` — Implements test localhost frontend cors preflight is allowed. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_database_schema.py`](../../backend/tests/test_database_schema.py)

Purpose: Verifies database schema behavior in the backend regression suite.

- L5 `def test_schema_contains_only_product_runtime_tables() -> None` — Implements test schema contains only product runtime tables. Receives: `not applicable`. Sends: `None`.
- L25 `def test_case_state_columns_and_tables_are_absent() -> None` — Implements test case state columns and tables are absent. Receives: `not applicable`. Sends: `None`.
- L32 `def test_case_owns_one_shared_identity_chat_thread() -> None` — Implements test case owns one shared identity chat thread. Receives: `not applicable`. Sends: `None`.
- L45 `def test_case_first_workflow_schema_is_case_owned() -> None` — Implements test case first workflow schema is case owned. Receives: `not applicable`. Sends: `None`.
- L60 `def test_rag_context_is_bound_one_to_one_to_chat_run() -> None` — Implements test rag context is bound one to one to chat run. Receives: `not applicable`. Sends: `None`.
- L72 `def test_report_uses_analysis_and_retrieval_bindings() -> None` — Implements test report uses analysis and retrieval bindings. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_document_ingestion.py`](../../backend/tests/test_document_ingestion.py)

Purpose: Verifies document ingestion behavior in the backend regression suite.

- L25 `class RecordingRecognizer` — Encapsulates recordingrecognizer. Receives: `constructor arguments and class fields`. Sends: `RecordingRecognizer`.
- L26 `def __init__(self, text: str='recognized Thai document text') -> None` — Implements init. Receives: `self, text: str='recognized Thai document text'`. Sends: `None`.
- L30 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L35 `class FailingRecognizer` — Encapsulates failingrecognizer. Receives: `constructor arguments and class fields`. Sends: `FailingRecognizer`.
- L36 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L40 `def _service(recognizer) -> DocumentIngestionService` — Implements service. Receives: `recognizer`. Sends: `DocumentIngestionService`.
- L52 `def _docx_bytes(*paragraphs: str) -> bytes` — Implements docx bytes. Receives: `*paragraphs: str`. Sends: `bytes`.
- L61 `def _pdf_bytes(page_texts: list[str | None]) -> bytes` — Implements pdf bytes. Receives: `page_texts: list[str | None]`. Sends: `bytes`.
- L75 `def _png_bytes() -> bytes` — Implements png bytes. Receives: `not applicable`. Sends: `bytes`.
- L81 `def test_docx_uses_native_extraction() -> None` — Implements test docx uses native extraction. Receives: `not applicable`. Sends: `None`.
- L99 `def test_text_pdf_does_not_trigger_recognition() -> None` — Implements test text pdf does not trigger recognition. Receives: `not applicable`. Sends: `None`.
- L113 `def test_scanned_pdf_page_is_routed_to_recognizer() -> None` — Implements test scanned pdf page is routed to recognizer. Receives: `not applicable`. Sends: `None`.
- L122 `def test_pdf_with_tiny_text_layer_is_still_routed_to_recognizer() -> None` — Implements test pdf with tiny text layer is still routed to recognizer. Receives: `not applicable`. Sends: `None`.
- L132 `def test_mixed_pdf_routes_pages_independently_and_preserves_page_numbers() -> None` — Implements test mixed pdf routes pages independently and preserves page numbers. Receives: `not applicable`. Sends: `None`.
- L150 `def test_block_ids_are_deterministic() -> None` — Implements test block ids are deterministic. Receives: `not applicable`. Sends: `None`.
- L163 `def test_unsupported_file_type_fails_cleanly() -> None` — Implements test unsupported file type fails cleanly. Receives: `not applicable`. Sends: `None`.
- L170 `def test_recognizer_failure_is_returned_as_controlled_warning() -> None` — Implements test recognizer failure is returned as controlled warning. Receives: `not applicable`. Sends: `None`.
- L177 `def test_prompt_injection_like_document_text_remains_inert_data() -> None` — Implements test prompt injection like document text remains inert data. Receives: `not applicable`. Sends: `None`.
- L187 `def test_ingestion_does_not_call_rag_or_case_analysis(monkeypatch) -> None` — Implements test ingestion does not call rag or case analysis. Receives: `monkeypatch`. Sends: `None`.
- L190 `async def forbidden_rag(*args, **kwargs)` — Implements forbidden rag. Receives: `*args, **kwargs`. Sends: `inferred or None`.
- L193 `async def forbidden_analysis(*args, **kwargs)` — Implements forbidden analysis. Receives: `*args, **kwargs`. Sends: `inferred or None`.
- L210 `def test_ingestion_does_not_create_persisted_chat_or_case(monkeypatch) -> None` — Implements test ingestion does not create persisted chat or case. Receives: `monkeypatch`. Sends: `None`.
- L213 `async def forbidden_create(*args, **kwargs)` — Implements forbidden create. Receives: `*args, **kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_document_ingestion_api.py`](../../backend/tests/test_document_ingestion_api.py)

Purpose: Verifies document ingestion api behavior in the backend regression suite.

- L14 `def _docx_bytes(text: str) -> bytes` — Implements docx bytes. Receives: `text: str`. Sends: `bytes`.
- L22 `def _png_bytes() -> bytes` — Implements png bytes. Receives: `not applicable`. Sends: `bytes`.
- L28 `class StaticPageRecognizer` — Encapsulates staticpagerecognizer. Receives: `constructor arguments and class fields`. Sends: `StaticPageRecognizer`.
- L29 `async def recognize_page(self, page) -> RecognizedPage` — Implements recognize page. Receives: `self, page`. Sends: `RecognizedPage`.
- L37 `def test_preview_endpoint_is_independent_and_returns_structured_document() -> None` — Implements test preview endpoint is independent and returns structured document. Receives: `not applicable`. Sends: `None`.
- L57 `def test_preview_endpoint_supports_unified_mode_and_segmentation_alias() -> None` — Implements test preview endpoint supports unified mode and segmentation alias. Receives: `not applicable`. Sends: `None`.
- L78 `def test_preview_endpoint_rejects_unsupported_content() -> None` — Implements test preview endpoint rejects unsupported content. Receives: `not applicable`. Sends: `None`.
- L89 `def test_default_image_preview_does_not_require_google_configuration(monkeypatch) -> None` — Implements test default image preview does not require google configuration. Receives: `monkeypatch`. Sends: `None`.
- L111 `def authenticated_ingestion_request(monkeypatch)` — Implements authenticated ingestion request. Receives: `monkeypatch`. Sends: `inferred or None`.

### [`backend/tests/test_document_ingestion_eval.py`](../../backend/tests/test_document_ingestion_eval.py)

Purpose: Verifies document ingestion eval behavior in the backend regression suite.

- L10 `def test_cer_and_wer_use_edit_distance() -> None` — Implements test cer and wer use edit distance. Receives: `not applicable`. Sends: `None`.
- L15 `def test_evaluation_compares_unified_and_routed_predictions() -> None` — Implements test evaluation compares unified and routed predictions. Receives: `not applicable`. Sends: `None`.
- L34 `def test_evaluation_reports_region_and_critical_field_metrics() -> None` — Implements test evaluation reports region and critical field metrics. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_document_ingestion_google_response.py`](../../backend/tests/test_document_ingestion_google_response.py)

Purpose: Verifies document ingestion google response behavior in the backend regression suite.

- L20 `def sample()` — Implements sample. Receives: `not applicable`. Sends: `inferred or None`.
- L24 `def provider_words(payload)` — Implements provider words. Receives: `payload`. Sends: `inferred or None`.
- L30 `def test_synthetic_receipt_matches_text_thai_words_reading_order_boxes_and_minimum()` — Implements test synthetic receipt matches text thai words reading order boxes and minimum. Receives: `not applicable`. Sends: `inferred or None`.
- L44 `def test_confidence_preserves_real_zero_and_missing_values(confidence)` — Implements test confidence preserves real zero and missing values. Receives: `confidence`. Sends: `inferred or None`.
- L56 `def test_invalid_confidence_fails_without_clamping_or_fabricating(confidence)` — Implements test invalid confidence fails without clamping or fabricating. Receives: `confidence`. Sends: `inferred or None`.
- L68 `def test_missing_polygon_or_coordinates_produce_no_box(polygon)` — Implements test missing polygon or coordinates produce no box. Receives: `polygon`. Sends: `inferred or None`.
- L75 `def test_incomplete_four_vertex_polygon_does_not_invent_coordinates()` — Implements test incomplete four vertex polygon does not invent coordinates. Receives: `not applicable`. Sends: `inferred or None`.
- L81 `def test_multiple_paragraphs_blocks_pages_keep_provider_order_and_page_formatting()` — Implements test multiple paragraphs blocks pages keep provider order and page formatting. Receives: `not applicable`. Sends: `inferred or None`.
- L93 `def test_empty_annotation_is_safe_response_error(annotation)` — Implements test empty annotation is safe response error. Receives: `annotation`. Sends: `inferred or None`.
- L101 `def test_malformed_envelope_is_safe_response_error(payload)` — Implements test malformed envelope is safe response error. Receives: `payload`. Sends: `inferred or None`.
- L106 `def test_provider_error_is_sanitized()` — Implements test provider error is sanitized. Receives: `not applicable`. Sends: `inferred or None`.
- L114 `def test_aggregate_uses_only_reported_words_and_never_page_confidence()` — Implements test aggregate uses only reported words and never page confidence. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_document_ingestion_google_service.py`](../../backend/tests/test_document_ingestion_google_service.py)

Purpose: Verifies document ingestion google service behavior in the backend regression suite.

- L27 `def test_typhoon_router_loads_without_optional_google_packages(monkeypatch)` — Implements test typhoon router loads without optional google packages. Receives: `monkeypatch`. Sends: `inferred or None`.
- L55 `def test_provider_selection_from_environment_is_explicit_and_lazy(monkeypatch, provider)` — Implements test provider selection from environment is explicit and lazy. Receives: `monkeypatch, provider`. Sends: `inferred or None`.
- L71 `def test_google_flows_through_service_without_llm_rag_or_persistence(monkeypatch, kind)` — Implements test google flows through service without llm rag or persistence. Receives: `monkeypatch, kind`. Sends: `inferred or None`.
- L74 `async def forbidden(*args, **kwargs)` — Implements forbidden. Receives: `*args, **kwargs`. Sends: `inferred or None`.
- L103 `def test_native_documents_bypass_google_and_have_no_ocr_measurements(monkeypatch, kind)` — Implements test native documents bypass google and have no ocr measurements. Receives: `monkeypatch, kind`. Sends: `inferred or None`.
- L121 `def test_routed_ocr_keeps_segmentation_separate_and_preserves_words(monkeypatch, region_type)` — Implements test routed ocr keeps segmentation separate and preserves words. Receives: `monkeypatch, region_type`. Sends: `inferred or None`.
- L143 `def test_typhoon_still_reports_no_recognition_confidence_in_both_modes(monkeypatch)` — Implements test typhoon still reports no recognition confidence in both modes. Receives: `monkeypatch`. Sends: `inferred or None`.
- L162 `def test_google_preview_exposes_words_and_not_raw_provider_output(monkeypatch, mode)` — Implements test google preview exposes words and not raw provider output. Receives: `monkeypatch, mode`. Sends: `inferred or None`.
- L182 `def test_google_service_failure_retains_warning_and_no_false_measurement(monkeypatch)` — Implements test google service failure retains warning and no false measurement. Receives: `monkeypatch`. Sends: `inferred or None`.
- L196 `def authenticated_ingestion_request(monkeypatch)` — Implements authenticated ingestion request. Receives: `monkeypatch`. Sends: `inferred or None`.

### [`backend/tests/test_document_ingestion_google_transport.py`](../../backend/tests/test_document_ingestion_google_transport.py)

Purpose: Verifies document ingestion google transport behavior in the backend regression suite.

- L25 `def test_official_request_uses_adc_document_detection_image_bytes_and_timeouts(monkeypatch)` — Implements test official request uses adc document detection image bytes and timeouts. Receives: `monkeypatch`. Sends: `inferred or None`.
- L77 `def test_transport_and_auth_errors_are_mapped_without_leaking_details(monkeypatch, error, expected)` — Implements test transport and auth errors are mapped without leaking details. Receives: `monkeypatch, error, expected`. Sends: `inferred or None`.
- L87 `def test_network_work_runs_off_event_loop(monkeypatch)` — Implements test network work runs off event loop. Receives: `monkeypatch`. Sends: `inferred or None`.
- L92 `def post(image_bytes)` — Implements post. Receives: `image_bytes`. Sends: `inferred or None`.
- L99 `async def run()` — Executes run. Receives: `not applicable`. Sends: `inferred or None`.
- L110 `def test_coroutine_timeout_is_mapped(monkeypatch)` — Implements test coroutine timeout is mapped. Receives: `monkeypatch`. Sends: `inferred or None`.
- L113 `def delayed_post(image_bytes)` — Implements delayed post. Receives: `image_bytes`. Sends: `inferred or None`.
- L122 `def test_region_recognition_preserves_words_and_low_measurements_without_threshold(monkeypatch)` — Implements test region recognition preserves words and low measurements without threshold. Receives: `monkeypatch`. Sends: `inferred or None`.

### [`backend/tests/test_document_ingestion_routing.py`](../../backend/tests/test_document_ingestion_routing.py)

Purpose: Verifies document ingestion routing behavior in the backend regression suite.

- L38 `def _png_bytes() -> bytes` — Implements png bytes. Receives: `not applicable`. Sends: `bytes`.
- L44 `def _region(region_id: str, region_type: RegionType, bbox: tuple[int, int, int, int], contains_handwriting: bool | None=None, page_number: int=3) -> SegmentedRegion` — Implements region. Receives: `region_id: str, region_type: RegionType, bbox: tuple[int, int, int, int], contains_handwriting: bool | None=None, page_number: int=3`. Sends: `SegmentedRegion`.
- L61 `class StaticSegmenter` — Encapsulates staticsegmenter. Receives: `constructor arguments and class fields`. Sends: `StaticSegmenter`.
- L62 `def __init__(self, regions: list[SegmentedRegion]) -> None` — Implements init. Receives: `self, regions: list[SegmentedRegion]`. Sends: `None`.
- L65 `async def segment_page(self, page: RenderedPage) -> SegmentedPage` — Implements segment page. Receives: `self, page: RenderedPage`. Sends: `SegmentedPage`.
- L69 `class RecordingOCR` — Encapsulates recordingocr. Receives: `constructor arguments and class fields`. Sends: `RecordingOCR`.
- L70 `def __init__(self, generated: bool=False) -> None` — Implements init. Receives: `self, generated: bool=False`. Sends: `None`.
- L74 `async def recognize(self, region) -> RecognitionResult` — Implements recognize. Receives: `self, region`. Sends: `RecognitionResult`.
- L87 `class RecordingHTR` — Encapsulates recordinghtr. Receives: `constructor arguments and class fields`. Sends: `RecordingHTR`.
- L88 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L91 `async def recognize(self, region) -> RecognitionResult` — Implements recognize. Receives: `self, region`. Sends: `RecognitionResult`.
- L101 `class FailingRecognizer` — Encapsulates failingrecognizer. Receives: `constructor arguments and class fields`. Sends: `FailingRecognizer`.
- L102 `async def recognize(self, region) -> RecognitionResult` — Implements recognize. Receives: `self, region`. Sends: `RecognitionResult`.
- L106 `class UnifiedRecognizer` — Encapsulates unifiedrecognizer. Receives: `constructor arguments and class fields`. Sends: `UnifiedRecognizer`.
- L107 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L110 `async def recognize_page(self, page: RenderedPage) -> RecognizedPage` — Implements recognize page. Receives: `self, page: RenderedPage`. Sends: `RecognizedPage`.
- L115 `def _pipeline(regions: list[SegmentedRegion], ocr=None, htr=None, mixed_policy: str='unified', htr_enabled: bool=False) -> RegionRecognitionPipeline` — Implements pipeline. Receives: `regions: list[SegmentedRegion], ocr=None, htr=None, mixed_policy: str='unified', htr_enabled: bool=False`. Sends: `RegionRecognitionPipeline`.
- L130 `def test_router_selects_ocr_htr_and_mixed_fallback() -> None` — Implements test router selects ocr htr and mixed fallback. Receives: `not applicable`. Sends: `None`.
- L149 `def test_router_does_not_transcribe_figures_or_signatures() -> None` — Implements test router does not transcribe figures or signatures. Receives: `not applicable`. Sends: `None`.
- L158 `def test_figure_region_stays_non_authoritative_without_recognizer_call() -> None` — Implements test figure region stays non authoritative without recognizer call. Receives: `not applicable`. Sends: `None`.
- L174 `def test_routed_pipeline_preserves_reading_order_bbox_and_page_number() -> None` — Implements test routed pipeline preserves reading order bbox and page number. Receives: `not applicable`. Sends: `None`.
- L206 `def test_ocr_and_htr_failures_are_controlled_per_region() -> None` — Implements test ocr and htr failures are controlled per region. Receives: `not applicable`. Sends: `None`.
- L224 `def test_disabled_htr_preserves_handwriting_without_calling_provider() -> None` — Implements test disabled htr preserves handwriting without calling provider. Receives: `not applicable`. Sends: `None`.
- L243 `def test_unavailable_enabled_htr_does_not_interrupt_printed_region() -> None` — Implements test unavailable enabled htr does not interrupt printed region. Receives: `not applicable`. Sends: `None`.
- L263 `def test_unified_and_routed_modes_share_the_ingestion_service() -> None` — Implements test unified and routed modes share the ingestion service. Receives: `not applicable`. Sends: `None`.
- L284 `def test_figure_tags_are_separated_from_literal_transcription() -> None` — Implements test figure tags are separated from literal transcription. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_document_ingestion_segmentation.py`](../../backend/tests/test_document_ingestion_segmentation.py)

Purpose: Verifies document ingestion segmentation behavior in the backend regression suite.

- L13 `def _png_bytes() -> bytes` — Implements png bytes. Receives: `not applicable`. Sends: `bytes`.
- L19 `def test_whole_page_segmentation_assigns_deterministic_region_ids() -> None` — Implements test whole page segmentation assigns deterministic region ids. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_document_narrative_handoff.py`](../../backend/tests/test_document_narrative_handoff.py)

Purpose: Verifies document narrative handoff behavior in the backend regression suite.

- L20 `def document_source() -> dict[str, object]` — Implements document source. Receives: `not applicable`. Sends: `dict[str, object]`.
- L33 `def test_message_contract_accepts_one_document_source_and_rejects_two() -> None` — Implements test message contract accepts one document source and rejects two. Receives: `not applicable`. Sends: `None`.
- L48 `def test_document_source_participates_in_idempotency_without_changing_plain_messages() -> None` — Implements test document source participates in idempotency without changing plain messages. Receives: `not applicable`. Sends: `None`.
- L62 `def test_raw_evidence_keeps_text_authoritative_and_quality_metadata_separate() -> None` — Implements test raw evidence keeps text authoritative and quality metadata separate. Receives: `not applicable`. Sends: `None`.
- L89 `def test_analysis_and_mitre_prompts_receive_quality_as_non_evidence_context() -> None` — Implements test analysis and mitre prompts receive quality as non evidence context. Receives: `not applicable`. Sends: `None`.
- L125 `def test_internal_source_text_map_is_not_serialized_into_the_provider_context() -> None` — Implements test internal source text map is not serialized into the provider context. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_followup_contract_cleanup.py`](../../backend/tests/test_followup_contract_cleanup.py)

Purpose: Verifies followup contract cleanup behavior in the backend regression suite.

- L17 `def test_followup_decision_rejects_legacy_action_shape() -> None` — Implements test followup decision rejects legacy action shape. Receives: `not applicable`. Sends: `None`.
- L29 `def test_followup_decision_requires_selected_gap() -> None` — Implements test followup decision requires selected gap. Receives: `not applicable`. Sends: `None`.
- L41 `def test_followup_decision_attributes_are_clean() -> None` — Implements test followup decision attributes are clean. Receives: `not applicable`. Sends: `None`.
- L56 `def test_retired_followup_helpers_are_removed() -> None` — Implements test retired followup helpers are removed. Receives: `not applicable`. Sends: `None`.
- L65 `def test_retired_prompt_builder_helpers_are_removed() -> None` — Implements test retired prompt builder helpers are removed. Receives: `not applicable`. Sends: `None`.
- L71 `def test_gap_stage_invokes_analyzer_directly() -> None` — Implements test gap stage invokes analyzer directly. Receives: `not applicable`. Sends: `None`.
- L72 `class MockAnalyzer` — Encapsulates mockanalyzer. Receives: `constructor arguments and class fields`. Sends: `MockAnalyzer`.
- L73 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L76 `async def analyze(self, *, original_user_content: str, clarification_exchanges: list[ClarificationExchange], raw_evidence: str | None, analysis_answer: str | None, analysis_context: dict[str, object] | None, analysis_claims: list[dict[str, object]] | None) -> GapAnalysisResult` — Implements analyze. Receives: `self, *, original_user_content: str, clarification_exchanges: list[ClarificationExchange], raw_evidence: str | None, analysis_answer: str | None, analysis_context: dict[str, object] | None, analysis_claims: list[dict[str, object]] | None`. Sends: `GapAnalysisResult`.

### [`backend/tests/test_gap_assembly.py`](../../backend/tests/test_gap_assembly.py)

Purpose: Verifies gap assembly behavior in the backend regression suite.

- L12 `def claim(claim_id: str, text: str) -> dict[str, object]` — Implements claim. Receives: `claim_id: str, text: str`. Sends: `dict[str, object]`.
- L24 `def trace(*, claims: list[dict[str, object]] | None=None, with_mitre: bool=False) -> AnalysisTraceV3` — Implements trace. Receives: `*, claims: list[dict[str, object]] | None=None, with_mitre: bool=False`. Sends: `AnalysisTraceV3`.
- L56 `def gap(*, topic: str='Property identity', status: str='NOT_PROVIDED', affects: str='A-01 — suspect possession of the missing property', priority: str='medium', askable: bool=True) -> GapItem` — Implements gap. Receives: `*, topic: str='Property identity', status: str='NOT_PROVIDED', affects: str='A-01 — suspect possession of the missing property', priority: str='medium', askable: bool=True`. Sends: `GapItem`.
- L77 `def assemble(value: AnalysisTraceV3, gaps: list[GapItem]) -> AnalysisTraceV3` — Builds assemble. Receives: `value: AnalysisTraceV3, gaps: list[GapItem]`. Sends: `AnalysisTraceV3`.
- L86 `def test_gap_links_to_one_claim_by_stable_id() -> None` — Implements test gap links to one claim by stable id. Receives: `not applicable`. Sends: `None`.
- L92 `def test_one_gap_can_affect_multiple_claims() -> None` — Implements test one gap can affect multiple claims. Receives: `not applicable`. Sends: `None`.
- L103 `def test_free_text_affects_is_linked_conservatively() -> None` — Implements test free text affects is linked conservatively. Receives: `not applicable`. Sends: `None`.
- L117 `def test_case_level_gap_may_have_no_claim_link() -> None` — Implements test case level gap may have no claim link. Receives: `not applicable`. Sends: `None`.
- L131 `def test_gap_status_is_preserved(status: str, askable: bool) -> None` — Implements test gap status is preserved. Receives: `status: str, askable: bool`. Sends: `None`.
- L137 `def test_priority_order_controls_stable_gap_ids() -> None` — Implements test priority order controls stable gap ids. Receives: `not applicable`. Sends: `None`.
- L153 `def test_gap_assembly_preserves_analysis_and_provenance_bindings() -> None` — Implements test gap assembly preserves analysis and provenance bindings. Receives: `not applicable`. Sends: `None`.
- L162 `def test_unknown_direct_claim_reference_fails_without_persisting_empty_gaps() -> None` — Implements test unknown direct claim reference fails without persisting empty gaps. Receives: `not applicable`. Sends: `None`.
- L178 `def test_missing_gap_analysis_marks_v3_trace_unavailable() -> None` — Implements test missing gap analysis marks v3 trace unavailable. Receives: `not applicable`. Sends: `None`.
- L201 `def test_general_case_without_rag_or_mitre_validates(case_claim: str) -> None` — Implements test general case without rag or mitre validates. Receives: `case_claim: str`. Sends: `None`.
- L208 `def test_cyber_case_with_mitre_still_validates() -> None` — Implements test cyber case with mitre still validates. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_gap_claim_transport.py`](../../backend/tests/test_gap_claim_transport.py)

Purpose: Verifies gap claim transport behavior in the backend regression suite.

- L31 `def claim_payload(index: int) -> dict[str, object]` — Implements claim payload. Receives: `index: int`. Sends: `dict[str, object]`.
- L43 `def trace_with_64_claims() -> AnalysisTraceV3` — Implements trace with 64 claims. Receives: `not applicable`. Sends: `AnalysisTraceV3`.
- L66 `def test_dedicated_transport_preserves_all_64_claims_in_order() -> None` — Implements test dedicated transport preserves all 64 claims in order. Receives: `not applicable`. Sends: `None`.
- L79 `def test_gap_provider_payload_bypasses_generic_32_item_limiter(monkeypatch) -> None` — Implements test gap provider payload bypasses generic 32 item limiter. Receives: `monkeypatch`. Sends: `None`.
- L82 `async def fake_post(client, messages_url, request_payload, headers)` — Implements fake post. Receives: `client, messages_url, request_payload, headers`. Sends: `inferred or None`.
- L133 `def test_transport_bounds_text_without_dropping_claims() -> None` — Implements test transport bounds text without dropping claims. Receives: `not applicable`. Sends: `None`.
- L141 `def test_transport_rejects_claim_count_above_v3_contract() -> None` — Implements test transport rejects claim count above v3 contract. Receives: `not applicable`. Sends: `None`.
- L148 `def test_a64_exact_link_survives_gap_stage_assembly_and_serialization() -> None` — Implements test a64 exact link survives gap stage assembly and serialization. Receives: `not applicable`. Sends: `None`.
- L152 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L153 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L173 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L174 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L215 `def test_gap_failure_log_includes_source_run_id(caplog) -> None` — Implements test gap failure log includes source run id. Receives: `caplog`. Sends: `None`.
- L218 `class FailingAnalyzer` — Encapsulates failinganalyzer. Receives: `constructor arguments and class fields`. Sends: `FailingAnalyzer`.
- L219 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_general_case_analysis.py`](../../backend/tests/test_general_case_analysis.py)

Purpose: Verifies general case analysis behavior in the backend regression suite.

- L25 `def reported_claim(text: str, *, supporting: list[str] | None=None, contradicting: list[str] | None=None, status: str='reported') -> dict[str, object]` — Implements reported claim. Receives: `text: str, *, supporting: list[str] | None=None, contradicting: list[str] | None=None, status: str='reported'`. Sends: `dict[str, object]`.
- L43 `def provider_payload(claims: list[dict[str, object]], *, answer: str='Grounded case answer.', associations: list[dict[str, object]] | None=None) -> dict[str, object]` — Implements provider payload. Receives: `claims: list[dict[str, object]], *, answer: str='Grounded case answer.', associations: list[dict[str, object]] | None=None`. Sends: `dict[str, object]`.
- L58 `def response_for(payload: dict[str, object]) -> httpx.Response` — Implements response for. Receives: `payload: dict[str, object]`. Sends: `httpx.Response`.
- L65 `def parse(payload: dict[str, object], *, sources: set[str] | None=None, context: dict[str, object] | None=None, mode: str='case_overview')` — Parses parse. Receives: `payload: dict[str, object], *, sources: set[str] | None=None, context: dict[str, object] | None=None, mode: str='case_overview'`. Sends: `inferred or None`.
- L82 `def test_same_runtime_contract_handles_five_case_domains_without_required_mitre(domain: str, claim_text: str) -> None` — Implements test same runtime contract handles five case domains without required mitre. Receives: `domain: str, claim_text: str`. Sends: `None`.
- L96 `def test_property_case_preserves_conflicting_reported_sources() -> None` — Implements test property case preserves conflicting reported sources. Receives: `not applicable`. Sends: `None`.
- L110 `def test_analytical_inference_retains_sources_and_visible_reasoning() -> None` — Implements test analytical inference retains sources and visible reasoning. Receives: `not applicable`. Sends: `None`.
- L127 `def test_analytical_inference_without_authoritative_support_is_rejected() -> None` — Implements test analytical inference without authoritative support is rejected. Receives: `not applicable`. Sends: `None`.
- L142 `def test_missing_information_remains_not_established() -> None` — Implements test missing information remains not established. Receives: `not applicable`. Sends: `None`.
- L159 `def test_non_authoritative_sources_are_rejected(invalid_source: str) -> None` — Implements test non authoritative sources are rejected. Receives: `invalid_source: str`. Sends: `None`.
- L176 `def test_cyber_case_accepts_bound_optional_mitre_context() -> None` — Implements test cyber case accepts bound optional mitre context. Receives: `not applicable`. Sends: `None`.
- L200 `def mitre_association() -> dict[str, object]` — Implements mitre association. Receives: `not applicable`. Sends: `dict[str, object]`.
- L211 `def test_mitre_association_is_removed_without_admitted_rag() -> None` — Implements test mitre association is removed without admitted rag. Receives: `not applicable`. Sends: `None`.
- L225 `def test_mitre_association_outside_admitted_context_is_rejected() -> None` — Implements test mitre association outside admitted context is rejected. Receives: `not applicable`. Sends: `None`.
- L241 `def test_question_answer_mode_returns_direct_answer_with_v3_trace() -> None` — Implements test question answer mode returns direct answer with v3 trace. Receives: `not applicable`. Sends: `None`.
- L254 `def test_invalid_provider_structure_uses_safe_trace_failure() -> None` — Implements test invalid provider structure uses safe trace failure. Receives: `not applicable`. Sends: `None`.
- L265 `def test_service_requests_v3_schema_with_optional_external_context(monkeypatch) -> None` — Implements test service requests v3 schema with optional external context. Receives: `monkeypatch`. Sends: `None`.
- L268 `class Client` — Encapsulates client. Receives: `constructor arguments and class fields`. Sends: `Client`.
- L269 `async def post(self, url, *, headers, json)` — Implements post. Receives: `self, url, *, headers, json`. Sends: `inferred or None`.
- L304 `def test_claim_id_normalization_handles_variants() -> None` — Implements test claim id normalization handles variants. Receives: `not applicable`. Sends: `None`.
- L355 `def test_parse_strips_trailing_ocr_boilerplate() -> None` — Implements test parse strips trailing ocr boilerplate. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_main_case_analysis.py`](../../backend/tests/test_main_case_analysis.py)

Purpose: Verifies main case analysis behavior in the backend regression suite.

- L18 `def payload_from_prompt(prompt: str) -> dict[str, object]` — Implements payload from prompt. Receives: `prompt: str`. Sends: `dict[str, object]`.
- L23 `def test_analysis_prompt_uses_raw_evidence_and_separates_external_context() -> None` — Implements test analysis prompt uses raw evidence and separates external context. Receives: `not applicable`. Sends: `None`.
- L43 `def test_analysis_prompt_accepts_no_external_context() -> None` — Implements test analysis prompt accepts no external context. Receives: `not applicable`. Sends: `None`.
- L56 `def test_general_prompt_removes_forced_cyber_analysis_sections() -> None` — Implements test general prompt removes forced cyber analysis sections. Receives: `not applicable`. Sends: `None`.
- L68 `def test_prompt_preserves_epistemic_and_legal_boundaries() -> None` — Implements test prompt preserves epistemic and legal boundaries. Receives: `not applicable`. Sends: `None`.
- L81 `def test_question_answer_prompt_requires_a_direct_proportionate_answer() -> None` — Implements test question answer prompt requires a direct proportionate answer. Receives: `not applicable`. Sends: `None`.
- L87 `def test_question_mode_requires_a_question() -> None` — Implements test question mode requires a question. Receives: `not applicable`. Sends: `None`.
- L92 `def test_overview_rejects_a_question() -> None` — Implements test overview rejects a question. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_migration_chat_only_cleanup.py`](../../backend/tests/test_migration_chat_only_cleanup.py)

Purpose: Verifies migration chat only cleanup behavior in the backend regression suite.

- L8 `def test_migration_chain_is_clean_and_linear() -> None` — Implements test migration chain is clean and linear. Receives: `not applicable`. Sends: `None`.
- L72 `def test_baseline_declares_only_surviving_tables() -> None` — Implements test baseline declares only surviving tables. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_mitre_applicability_pipeline.py`](../../backend/tests/test_mitre_applicability_pipeline.py)

Purpose: Verifies mitre applicability pipeline behavior in the backend regression suite.

- L17 `def claimed(content: str, *, action: str='initial_analysis')` — Implements claimed. Receives: `content: str, *, action: str='initial_analysis'`. Sends: `inferred or None`.
- L39 `async def run_fresh(value, gate, rag_request)` — Executes fresh. Receives: `value, gate, rag_request`. Sends: `inferred or None`.
- L42 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L46 `async def followup_evaluator(**kwargs)` — Implements followup evaluator. Receives: `**kwargs`. Sends: `inferred or None`.
- L62 `def test_skip_avoids_rag_and_main_analysis_continues() -> None` — Implements test skip avoids rag and main analysis continues. Receives: `not applicable`. Sends: `None`.
- L66 `async def gate(**kwargs)` — Implements gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L69 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L82 `def test_retrieve_invokes_rag_once_before_main_analysis() -> None` — Implements test retrieve invokes rag once before main analysis. Receives: `not applicable`. Sends: `None`.
- L86 `async def gate(**kwargs)` — Implements gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L94 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L111 `def test_gate_failure_fails_closed_without_blocking_analysis() -> None` — Implements test gate failure fails closed without blocking analysis. Receives: `not applicable`. Sends: `None`.
- L115 `async def gate(**kwargs)` — Implements gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L118 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L130 `def test_rag_failure_after_retrieve_does_not_block_analysis() -> None` — Implements test rag failure after retrieve does not block analysis. Receives: `not applicable`. Sends: `None`.
- L133 `async def gate(**kwargs)` — Implements gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L141 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L153 `def test_ask_does_not_rerun_gate_or_rag() -> None` — Implements test ask does not rerun gate or rag. Receives: `not applicable`. Sends: `None`.
- L157 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L168 `def test_new_evidence_reevaluates_gate() -> None` — Implements test new evidence reevaluates gate. Receives: `not applicable`. Sends: `None`.
- L171 `async def gate(**kwargs)` — Implements gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L176 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L179 `async def scenario()` — Implements scenario. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_mitre_applicability_provider.py`](../../backend/tests/test_mitre_applicability_provider.py)

Purpose: Verifies mitre applicability provider behavior in the backend regression suite.

- L21 `def target() -> CoreLlmTarget` — Implements target. Receives: `not applicable`. Sends: `CoreLlmTarget`.
- L32 `def test_gate_uses_fixed_prompt_strict_schema_and_deterministic_options(monkeypatch) -> None` — Implements test gate uses fixed prompt strict schema and deterministic options. Receives: `monkeypatch`. Sends: `None`.
- L41 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.
- L73 `def test_malformed_provider_output_fails_closed(monkeypatch) -> None` — Implements test malformed provider output fails closed. Receives: `monkeypatch`. Sends: `None`.
- L76 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.
- L97 `def test_provider_error_fails_closed(monkeypatch) -> None` — Implements test provider error fails closed. Receives: `monkeypatch`. Sends: `None`.
- L100 `def handler(request: httpx.Request) -> httpx.Response` — Implements handler. Receives: `request: httpx.Request`. Sends: `httpx.Response`.

### [`backend/tests/test_mitre_applicability_validation.py`](../../backend/tests/test_mitre_applicability_validation.py)

Purpose: Verifies mitre applicability validation behavior in the backend regression suite.

- L81 `def test_semantic_fixture_contract(case_name: str, content: str, decision: str, trigger: str | None) -> None` — Implements test semantic fixture contract. Receives: `case_name: str, content: str, decision: str, trigger: str | None`. Sends: `None`.
- L98 `def test_mixed_sources_cite_only_the_cyber_source() -> None` — Implements test mixed sources cite only the cyber source. Receives: `not applicable`. Sends: `None`.
- L116 `def test_multi_message_behavior_can_cite_each_authoritative_source() -> None` — Implements test multi message behavior can cite each authoritative source. Receives: `not applicable`. Sends: `None`.
- L183 `def test_invalid_or_unattributable_output_fails_closed(payload: object) -> None` — Implements test invalid or unattributable output fails closed. Receives: `payload: object`. Sends: `None`.
- L192 `def test_trigger_must_be_an_exact_source_span() -> None` — Implements test trigger must be an exact source span. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_model_registry.py`](../../backend/tests/test_model_registry.py)

Purpose: Unit tests for the OpenRouter model registry and alias resolver.

- L13 `def test_default_model()` — Implements test default model. Receives: `not applicable`. Sends: `inferred or None`.
- L42 `def test_curated_aliases_resolution(alias: str, expected_canonical_id: str)` — Implements test curated aliases resolution. Receives: `alias: str, expected_canonical_id: str`. Sends: `inferred or None`.
- L48 `def test_custom_model_passthrough()` — Implements test custom model passthrough. Receives: `not applicable`. Sends: `inferred or None`.
- L54 `def test_list_and_table_formatting()` — Implements test list and table formatting. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_optional_rag_pipeline.py`](../../backend/tests/test_optional_rag_pipeline.py)

Purpose: Verifies optional rag pipeline behavior in the backend regression suite.

- L25 `def claimed(case_text: str)` — Implements claimed. Receives: `case_text: str`. Sends: `inferred or None`.
- L42 `def result_for(value, *, retrieval_context_id=None, cyber=False)` — Implements result for. Receives: `value, *, retrieval_context_id=None, cyber=False`. Sends: `inferred or None`.
- L83 `async def run_overview(value, rag_request, *, cyber=False)` — Executes overview. Receives: `value, rag_request, *, cyber=False`. Sends: `inferred or None`.
- L86 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L97 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L98 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L103 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L104 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L107 `async def applicability_gate(**kwargs)` — Implements applicability gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L127 `def test_theft_analysis_completes_when_rag_is_unavailable() -> None` — Implements test theft analysis completes when rag is unavailable. Receives: `not applicable`. Sends: `None`.
- L130 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L151 `def test_fraud_analysis_completes_when_rag_has_no_usable_context() -> None` — Implements test fraud analysis completes when rag has no usable context. Receives: `not applicable`. Sends: `None`.
- L154 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L169 `def test_cyber_analysis_preserves_successful_rag_and_mitre_binding() -> None` — Implements test cyber analysis preserves successful rag and mitre binding. Receives: `not applicable`. Sends: `None`.
- L172 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L195 `class Transaction` — Encapsulates transaction. Receives: `constructor arguments and class fields`. Sends: `Transaction`.
- L196 `async def __aenter__(self)` — Implements aenter. Receives: `self`. Sends: `inferred or None`.
- L199 `async def __aexit__(self, exc_type, exc, traceback)` — Implements aexit. Receives: `self, exc_type, exc, traceback`. Sends: `inferred or None`.
- L203 `class CompletionDb` — Encapsulates completiondb. Receives: `constructor arguments and class fields`. Sends: `CompletionDb`.
- L204 `def __init__(self)` — Implements init. Receives: `self`. Sends: `inferred or None`.
- L207 `def begin(self)` — Implements begin. Receives: `self`. Sends: `inferred or None`.
- L210 `def add(self, value)` — Implements add. Receives: `self, value`. Sends: `inferred or None`.
- L213 `async def flush(self)` — Implements flush. Receives: `self`. Sends: `inferred or None`.
- L217 `def test_rag_failure_does_not_persist_a_fake_rag_context() -> None` — Implements test rag failure does not persist a fake rag context. Receives: `not applicable`. Sends: `None`.
- L220 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L228 `async def lock_thread(run_id)` — Implements lock thread. Receives: `run_id`. Sends: `inferred or None`.
- L231 `async def lock_run(run_id, worker_id)` — Implements lock run. Receives: `run_id, worker_id`. Sends: `inferred or None`.

### [`backend/tests/test_password_accounts.py`](../../backend/tests/test_password_accounts.py)

Purpose: Verifies password accounts behavior in the backend regression suite.

- L17 `def account_client(monkeypatch)` — Implements account client. Receives: `monkeypatch`. Sends: `inferred or None`.
- L31 `def user_record(verified=True)` — Implements user record. Receives: `verified=True`. Sends: `inferred or None`.
- L44 `def test_password_hash_salted_and_checked()` — Implements test password hash salted and checked. Receives: `not applicable`. Sends: `inferred or None`.
- L54 `def test_registration_rejects_invalid_input(account_client, email, password)` — Implements test registration rejects invalid input. Receives: `account_client, email, password`. Sends: `inferred or None`.
- L65 `def test_registration_creates_session_without_email_verification(account_client)` — Implements test registration creates session without email verification. Receives: `account_client`. Sends: `inferred or None`.
- L86 `def test_duplicate_registration_rolls_back_without_session(account_client)` — Implements test duplicate registration rolls back without session. Receives: `account_client`. Sends: `inferred or None`.
- L105 `def test_login_requires_matching_credentials_without_verification(account_client, verified, password, status)` — Implements test login requires matching credentials without verification. Receives: `account_client, verified, password, status`. Sends: `inferred or None`.
- L118 `def test_email_verification_endpoints_removed(account_client, path)` — Implements test email verification endpoints removed. Receives: `account_client, path`. Sends: `inferred or None`.
- L123 `def test_anonymous_chat_and_oauth_state_rejected(account_client)` — Implements test anonymous chat and oauth state rejected. Receives: `account_client`. Sends: `inferred or None`.
- L131 `def test_anonymous_document_preview_is_rejected()` — Implements test anonymous document preview is rejected. Receives: `not applicable`. Sends: `inferred or None`.
- L141 `def test_cross_origin_auth_request_is_rejected()` — Implements test cross origin auth request is rejected. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_raw_evidence_workflow.py`](../../backend/tests/test_raw_evidence_workflow.py)

Purpose: Verifies raw evidence workflow behavior in the backend regression suite.

- L10 `def message(ordinal: int, content: str, evidence_kind: str) -> ChatMessage` — Implements message. Receives: `ordinal: int, content: str, evidence_kind: str`. Sends: `ChatMessage`.
- L21 `def test_raw_evidence_is_chronological_and_excludes_questions() -> None` — Implements test raw evidence is chronological and excludes questions. Receives: `not applicable`. Sends: `None`.
- L40 `def test_first_message_and_post_answer_actions_have_explicit_evidence_kinds() -> None` — Implements test first message and post answer actions have explicit evidence kinds. Receives: `not applicable`. Sends: `None`.
- L55 `def test_answered_thread_requires_an_explicit_action() -> None` — Implements test answered thread requires an explicit action. Receives: `not applicable`. Sends: `None`.
- L62 `def test_clarification_answer_is_evidence() -> None` — Implements test clarification answer is evidence. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_refactor_boundaries.py`](../../backend/tests/test_refactor_boundaries.py)

Purpose: Verifies refactor boundaries behavior in the backend regression suite.

- L15 `def test_source_aliases_are_never_guessed(source)` — Implements test source aliases are never guessed. Receives: `source`. Sends: `inferred or None`.
- L25 `def test_missing_source_is_not_filled_for_single_document()` — Implements test missing source is not filled for single document. Receives: `not applicable`. Sends: `inferred or None`.
- L33 `def test_identifier_formatting_preserves_identity_and_input()` — Implements test identifier formatting preserves identity and input. Receives: `not applicable`. Sends: `inferred or None`.
- L44 `def test_malformed_report_snapshot_does_not_enter_legacy_reader(snapshot)` — Implements test malformed report snapshot does not enter legacy reader. Receives: `snapshot`. Sends: `inferred or None`.
- L51 `def test_snapshot_without_mitre_does_not_resurrect_section_mappings()` — Implements test snapshot without mitre does not resurrect section mappings. Receives: `not applicable`. Sends: `inferred or None`.
- L60 `def test_metadata_preserves_legacy_extensions_and_rejects_invalid_known_values()` — Implements test metadata preserves legacy extensions and rejects invalid known values. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_report_view_model_and_pdf.py`](../../backend/tests/test_report_view_model_and_pdf.py)

Purpose: Verifies report view model and pdf behavior in the backend regression suite.

- L17 `def make_realistic_report_read() -> tuple[ChatReportRead, str]` — Implements make realistic report read. Receives: `not applicable`. Sends: `tuple[ChatReportRead, str]`.
- L124 `def test_view_model_extracts_timeline_and_gaps_without_contradictions()` — Implements test view model extracts timeline and gaps without contradictions. Receives: `not applicable`. Sends: `inferred or None`.
- L165 `def test_report_view_model_finding_provenance_multi_source_and_fallback()` — Implements test report view model finding provenance multi source and fallback. Receives: `not applicable`. Sends: `inferred or None`.
- L233 `def test_pdf_generation_produces_valid_pdf_bytes()` — Implements test pdf generation produces valid pdf bytes. Receives: `not applicable`. Sends: `inferred or None`.
- L240 `def test_pdf_generation_splits_long_evidence_across_pages()` — Implements test pdf generation splits long evidence across pages. Receives: `not applicable`. Sends: `inferred or None`.
- L258 `def test_html_rendering_contains_standalone_sections()` — Implements test html rendering contains standalone sections. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_route_surface.py`](../../backend/tests/test_route_surface.py)

Purpose: Verifies route surface behavior in the backend regression suite.

- L10 `def _fastapi_app() -> FastAPI` — Implements fastapi app. Receives: `not applicable`. Sends: `FastAPI`.
- L17 `def test_health_chat_and_nested_report_api_routes_are_registered() -> None` — Implements test health chat and nested report api routes are registered. Receives: `not applicable`. Sends: `None`.
- L77 `def test_legacy_route_prefixes_return_not_found_without_startup() -> None` — Implements test legacy route prefixes return not found without startup. Receives: `not applicable`. Sends: `None`.
- L88 `def test_startup_fails_when_database_is_unavailable(monkeypatch) -> None` — Implements test startup fails when database is unavailable. Receives: `monkeypatch`. Sends: `None`.
- L91 `class _FailingConnection` — Encapsulates failingconnection. Receives: `constructor arguments and class fields`. Sends: `_FailingConnection`.
- L92 `async def __aenter__(self)` — Implements aenter. Receives: `self`. Sends: `inferred or None`.
- L95 `async def __aexit__(self, exc_type, exc, traceback)` — Implements aexit. Receives: `self, exc_type, exc, traceback`. Sends: `inferred or None`.
- L98 `class _FakeEngine` — Encapsulates fakeengine. Receives: `constructor arguments and class fields`. Sends: `_FakeEngine`.
- L99 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L102 `def connect(self) -> _FailingConnection` — Implements connect. Receives: `self`. Sends: `_FailingConnection`.
- L105 `async def dispose(self) -> None` — Implements dispose. Receives: `self`. Sends: `None`.
- L111 `async def exercise_lifespan() -> None` — Implements exercise lifespan. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_run_recovery_api.py`](../../backend/tests/test_run_recovery_api.py)

Purpose: Verifies run recovery api behavior in the backend regression suite.

- L16 `def test_interrupted_request_can_be_read_and_retried_through_http(monkeypatch)` — Implements test interrupted request can be read and retried through http. Receives: `monkeypatch`. Sends: `inferred or None`.
- L19 `async def record_dispatch(run_id)` — Persists dispatch. Receives: `run_id`. Sends: `inferred or None`.
- L24 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L27 `async def database()` — Implements database. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_run_recovery_postgres.py`](../../backend/tests/test_run_recovery_postgres.py)

Purpose: Verifies run recovery postgres behavior in the backend regression suite.

- L19 `async def expire_run(factory, run_id)` — Implements expire run. Receives: `factory, run_id`. Sends: `inferred or None`.
- L25 `def test_interruption_retry_is_atomic_and_preserves_evidence()` — Implements test interruption retry is atomic and preserves evidence. Receives: `not applicable`. Sends: `inferred or None`.
- L26 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L39 `async def retry()` — Implements retry. Receives: `not applicable`. Sends: `inferred or None`.
- L66 `def test_heartbeat_renewal_and_expired_owner_fencing()` — Implements test heartbeat renewal and expired owner fencing. Receives: `not applicable`. Sends: `inferred or None`.
- L67 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.
- L91 `def test_unclaimed_queue_is_recoverable_and_newer_messages_block_retry()` — Implements test unclaimed queue is recoverable and newer messages block retry. Receives: `not applicable`. Sends: `inferred or None`.
- L92 `async def exercise()` — Implements exercise. Receives: `not applicable`. Sends: `inferred or None`.

### [`backend/tests/test_source_citations.py`](../../backend/tests/test_source_citations.py)

Purpose: Verifies source citations behavior in the backend regression suite.

- L10 `def document_source(content: str) -> CaseNarrativeDocumentSource` — Implements document source. Receives: `content: str`. Sends: `CaseNarrativeDocumentSource`.
- L33 `def multi_page_source(pages: list[tuple[int, str]]) -> tuple[str, CaseNarrativeDocumentSource]` — Implements multi page source. Receives: `pages: list[tuple[int, str]]`. Sends: `tuple[str, CaseNarrativeDocumentSource]`.
- L65 `def claim(source_id: str, quote: str) -> AnalysisClaimV3` — Implements claim. Receives: `source_id: str, quote: str`. Sends: `AnalysisClaimV3`.
- L86 `def test_valid_quote_binds_to_validated_document_page() -> None` — Implements test valid quote binds to validated document page. Receives: `not applicable`. Sends: `None`.
- L104 `def test_narrative_only_quote_remains_message_level() -> None` — Implements test narrative only quote remains message level. Receives: `not applicable`. Sends: `None`.
- L116 `def test_invalid_quote_is_not_persisted_as_a_citation() -> None` — Implements test invalid quote is not persisted as a citation. Receives: `not applicable`. Sends: `None`.
- L125 `def test_edited_narrative_drops_stale_page_span() -> None` — Implements test edited narrative drops stale page span. Receives: `not applicable`. Sends: `None`.
- L131 `def test_edited_early_page_drops_later_page_spans() -> None` — Implements test edited early page drops later page spans. Receives: `not applicable`. Sends: `None`.
- L138 `def test_quote_spanning_pages_binds_all_touched_pages() -> None` — Implements test quote spanning pages binds all touched pages. Receives: `not applicable`. Sends: `None`.
- L154 `def test_quote_spanning_non_consecutive_pages_keeps_safe_page_list() -> None` — Implements test quote spanning non consecutive pages keeps safe page list. Receives: `not applicable`. Sends: `None`.
- L168 `def test_stale_page_hash_drops_document_locator() -> None` — Implements test stale page hash drops document locator. Receives: `not applicable`. Sends: `None`.
- L191 `def test_duplicate_quote_on_different_pages_does_not_guess_a_page() -> None` — Implements test duplicate quote on different pages does not guess a page. Receives: `not applicable`. Sends: `None`.
- L225 `def test_late_duplicate_quote_on_another_page_does_not_escape_ambiguity_limit() -> None` — Implements test late duplicate quote on another page does not escape ambiguity limit. Receives: `not applicable`. Sends: `None`.
- L242 `def test_document_page_response_includes_a_normalized_text_digest() -> None` — Implements test document page response includes a normalized text digest. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_stateful_clarification.py`](../../backend/tests/test_stateful_clarification.py)

Purpose: Verifies stateful clarification behavior in the backend regression suite.

- L25 `def item(topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, affects: str='A-01') -> GapItem` — Implements item. Receives: `topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, affects: str='A-01'`. Sends: `GapItem`.
- L44 `def canonical_gap(gap_id: str, topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, claims: list[str] | None=None) -> AnalysisGapV3` — Implements canonical gap. Receives: `gap_id: str, topic: str, *, status: str='NOT_PROVIDED', priority: str='high', askable: bool=True, claims: list[str] | None=None`. Sends: `AnalysisGapV3`.
- L65 `def exchange(topic: str, answer: str, *, gap_id: str='G-01') -> ClarificationExchange` — Implements exchange. Receives: `topic: str, answer: str, *, gap_id: str='G-01'`. Sends: `ClarificationExchange`.
- L93 `def test_gap_key_normalization_is_bounded_and_cross_revision(left: str, right: str) -> None` — Implements test gap key normalization is bounded and cross revision. Receives: `left: str, right: str`. Sends: `None`.
- L100 `def test_priority_claim_link_and_stable_order_select_next_gap() -> None` — Implements test priority claim link and stable order select next gap. Receives: `not applicable`. Sends: `None`.
- L114 `def test_no_gaps_unknown_low_or_unaskable_proceed_without_candidate() -> None` — Implements test no gaps unknown low or unaskable proceed without candidate. Receives: `not applicable`. Sends: `None`.
- L133 `def test_answered_gap_key_survives_gap_and_claim_ordinal_changes() -> None` — Implements test answered gap key survives gap and claim ordinal changes. Receives: `not applicable`. Sends: `None`.
- L150 `def test_unavailable_answer_transitions_missing_topic_to_explicit_unknown(answer: str) -> None` — Implements test unavailable answer transitions missing topic to explicit unknown. Receives: `answer: str`. Sends: `None`.
- L163 `def test_exhausted_ambiguous_or_conflicting_gap_preserves_status(status: str) -> None` — Implements test exhausted ambiguous or conflicting gap preserves status. Receives: `status: str`. Sends: `None`.
- L173 `def test_gap_stage_applies_short_answer_topic_context_once() -> None` — Implements test gap stage applies short answer topic context once. Receives: `not applicable`. Sends: `None`.
- L176 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L177 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L202 `def test_followup_round_limit_prevents_question_generation(monkeypatch) -> None` — Implements test followup round limit prevents question generation. Receives: `monkeypatch`. Sends: `None`.
- L205 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L206 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L211 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L212 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L238 `def test_one_question_contract_rejects_compound_questions() -> None` — Implements test one question contract rejects compound questions. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_stateful_clarification_characterization.py`](../../backend/tests/test_stateful_clarification_characterization.py)

Purpose: Verifies stateful clarification characterization behavior in the backend regression suite.

- L16 `def gap(topic: str, *, priority: str='high', status: str='NOT_PROVIDED') -> GapItem` — Implements gap. Receives: `topic: str, *, priority: str='high', status: str='NOT_PROVIDED'`. Sends: `GapItem`.
- L33 `class StaticAnalyzer` — Encapsulates staticanalyzer. Receives: `constructor arguments and class fields`. Sends: `StaticAnalyzer`.
- L34 `def __init__(self, gaps: list[GapItem])` — Implements init. Receives: `self, gaps: list[GapItem]`. Sends: `inferred or None`.
- L37 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L41 `class StaticPolicy` — Encapsulates staticpolicy. Receives: `constructor arguments and class fields`. Sends: `StaticPolicy`.
- L42 `def __init__(self, topic: str, question: str)` — Implements init. Receives: `self, topic: str, question: str`. Sends: `inferred or None`.
- L46 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L54 `def test_unavailable_answer_exhausts_only_its_topic() -> None` — Implements test unavailable answer exhausts only its topic. Receives: `not applicable`. Sends: `None`.
- L88 `def test_same_topic_is_not_reasked_with_different_wording() -> None` — Implements test same topic is not reasked with different wording. Receives: `not applicable`. Sends: `None`.
- L114 `def test_clarification_chain_retains_structural_gap_context() -> None` — Implements test clarification chain retains structural gap context. Receives: `not applicable`. Sends: `None`.
- L170 `def test_asked_question_metadata_carries_gap_identity() -> None` — Implements test asked question metadata carries gap identity. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_stateful_clarification_decisions.py`](../../backend/tests/test_stateful_clarification_decisions.py)

Purpose: Verifies stateful clarification decisions behavior in the backend regression suite.

- L16 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L17 `def __init__(self, gaps: list[GapItem])` — Implements init. Receives: `self, gaps: list[GapItem]`. Sends: `inferred or None`.
- L20 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L24 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L25 `def __init__(self, topic: str, question: str)` — Implements init. Receives: `self, topic: str, question: str`. Sends: `inferred or None`.
- L30 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L39 `def gap(topic: str, status: str) -> GapItem` — Implements gap. Receives: `topic: str, status: str`. Sends: `GapItem`.
- L51 `def test_no_gaps_proceeds_without_question_generation() -> None` — Implements test no gaps proceeds without question generation. Receives: `not applicable`. Sends: `None`.
- L86 `def test_ambiguous_and_conflicting_gaps_allow_one_neutral_question(status: str, question: str, reason_code: str) -> None` — Implements test ambiguous and conflicting gaps allow one neutral question. Receives: `status: str, question: str, reason_code: str`. Sends: `None`.
- L109 `def test_resolved_gap_disappearance_does_not_keep_old_task_active() -> None` — Implements test resolved gap disappearance does not keep old task active. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_stateful_clarification_domains.py`](../../backend/tests/test_stateful_clarification_domains.py)

Purpose: Verifies stateful clarification domains behavior in the backend regression suite.

- L24 `def case_value(content: str)` — Implements case value. Receives: `content: str`. Sends: `inferred or None`.
- L42 `def analysis(value, retrieval_id: str | None=None) -> CaseAnalysisResult` — Implements analysis. Receives: `value, retrieval_id: str | None=None`. Sends: `CaseAnalysisResult`.
- L65 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L66 `def __init__(self, topic: str)` — Implements init. Receives: `self, topic: str`. Sends: `inferred or None`.
- L70 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L89 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L90 `def __init__(self, topic: str)` — Implements init. Receives: `self, topic: str`. Sends: `inferred or None`.
- L94 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L103 `async def skip_gate(**kwargs)` — Implements skip gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L117 `def test_general_case_domains_select_canonical_gap_without_mitre(case_text: str, topic: str) -> None` — Implements test general case domains select canonical gap without mitre. Receives: `case_text: str, topic: str`. Sends: `None`.
- L125 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L129 `async def no_rag(query: str)` — Implements no rag. Receives: `query: str`. Sends: `inferred or None`.
- L150 `def test_cyber_followup_does_not_depend_on_rag_availability(rag_mode: str) -> None` — Implements test cyber followup does not depend on rag availability. Receives: `rag_mode: str`. Sends: `None`.
- L155 `async def retrieve_gate(**kwargs)` — Implements retrieve gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L163 `async def rag_request(query: str)` — Implements rag request. Receives: `query: str`. Sends: `inferred or None`.
- L173 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_stateful_clarification_metadata.py`](../../backend/tests/test_stateful_clarification_metadata.py)

Purpose: Verifies stateful clarification metadata behavior in the backend regression suite.

- L12 `def test_raw_evidence_hash_ignores_workflow_context_and_assistant_question() -> None` — Implements test raw evidence hash ignores workflow context and assistant question. Receives: `not applicable`. Sends: `None`.
- L64 `def test_followup_position_copies_question_context_to_answer_metadata() -> None` — Implements test followup position copies question context to answer metadata. Receives: `not applicable`. Sends: `None`.
- L97 `class Scalars` — Encapsulates scalars. Receives: `constructor arguments and class fields`. Sends: `Scalars`.
- L98 `def all(self)` — Implements all. Receives: `self`. Sends: `inferred or None`.
- L101 `class Result` — Encapsulates result. Receives: `constructor arguments and class fields`. Sends: `Result`.
- L102 `def scalars(self)` — Implements scalars. Receives: `self`. Sends: `inferred or None`.
- L105 `class Database` — Encapsulates database. Receives: `constructor arguments and class fields`. Sends: `Database`.
- L106 `async def execute(self, statement)` — Executes execute. Receives: `self, statement`. Sends: `inferred or None`.
- L129 `def test_short_answer_context_is_structural_and_does_not_rewrite_user_content() -> None` — Implements test short answer context is structural and does not rewrite user content. Receives: `not applicable`. Sends: `None`.
- L153 `def test_mismatched_answer_context_cannot_override_asked_gap_topic() -> None` — Implements test mismatched answer context cannot override asked gap topic. Receives: `not applicable`. Sends: `None`.

### [`backend/tests/test_stateful_clarification_pipeline.py`](../../backend/tests/test_stateful_clarification_pipeline.py)

Purpose: Verifies stateful clarification pipeline behavior in the backend regression suite.

- L22 `def claimed(content: str, *, exchanges: tuple[ClarificationExchange, ...]=())` — Implements claimed. Receives: `content: str, *, exchanges: tuple[ClarificationExchange, ...]=()`. Sends: `inferred or None`.
- L47 `def analysis(value, retrieval_context_id: str | None=None) -> CaseAnalysisResult` — Implements analysis. Receives: `value, retrieval_context_id: str | None=None`. Sends: `CaseAnalysisResult`.
- L72 `def gap(topic: str, *, priority: str='high') -> GapItem` — Implements gap. Receives: `topic: str, *, priority: str='high'`. Sends: `GapItem`.
- L84 `async def skip_gate(**kwargs)` — Implements skip gate. Receives: `**kwargs`. Sends: `inferred or None`.
- L88 `class Analyzer` — Encapsulates analyzer. Receives: `constructor arguments and class fields`. Sends: `Analyzer`.
- L89 `def __init__(self, gaps: list[GapItem])` — Implements init. Receives: `self, gaps: list[GapItem]`. Sends: `inferred or None`.
- L93 `async def analyze(self, **kwargs)` — Implements analyze. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L98 `class Policy` — Encapsulates policy. Receives: `constructor arguments and class fields`. Sends: `Policy`.
- L99 `def __init__(self, topic: str, question: str)` — Implements init. Receives: `self, topic: str, question: str`. Sends: `inferred or None`.
- L104 `async def decide(self, **kwargs)` — Implements decide. Receives: `self, **kwargs`. Sends: `inferred or None`.
- L115 `def test_valid_v3_pipeline_uses_one_gap_call_and_one_question_call() -> None` — Implements test valid v3 pipeline uses one gap call and one question call. Receives: `not applicable`. Sends: `None`.
- L124 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L129 `async def no_rag(query: str)` — Implements no rag. Receives: `query: str`. Sends: `inferred or None`.
- L159 `def test_invalid_main_trace_never_runs_gap_or_followup_provider() -> None` — Implements test invalid main trace never runs gap or followup provider. Receives: `not applicable`. Sends: `None`.
- L164 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.
- L189 `def test_short_unknown_reruns_analysis_and_gap_once_then_selects_next_topic() -> None` — Implements test short unknown reruns analysis and gap once then selects next topic. Receives: `not applicable`. Sends: `None`.
- L207 `async def analysis_request(**kwargs)` — Implements analysis request. Receives: `**kwargs`. Sends: `inferred or None`.

### [`backend/tests/test_structured_output.py`](../../backend/tests/test_structured_output.py)

Purpose: Verifies structured output behavior in the backend regression suite.

- L10 `def test_report_schema_is_provider_compatible() -> None` — Implements test report schema is provider compatible. Receives: `not applicable`. Sends: `None`.
- L17 `def test_analysis_trace_v2_provider_schema_is_retired() -> None` — Implements test analysis trace v2 provider schema is retired. Receives: `not applicable`. Sends: `None`.
- L22 `def test_analysis_trace_v3_provider_schema_exposes_grounded_claim_roles() -> None` — Implements test analysis trace v3 provider schema exposes grounded claim roles. Receives: `not applicable`. Sends: `None`.

## Research And Evaluation Workspace

### [`deliverables/cybercase-report-followup-gap-study/scripts/validate_cases.py`](../../deliverables/cybercase-report-followup-gap-study/scripts/validate_cases.py)

Purpose: Validate CyberCase evaluation JSON files against schema and semantic invariants.

- L26 `def _json_path(parts: Iterable[Any]) -> str` — Implements json path. Receives: `parts: Iterable[Any]`. Sends: `str`.
- L33 `def _duplicates(values: Iterable[str]) -> set[str]` — Implements duplicates. Receives: `values: Iterable[str]`. Sends: `set[str]`.
- L38 `def _state_map(claim: dict[str, Any]) -> tuple[dict[str, str], set[str]]` — Implements state map. Receives: `claim: dict[str, Any]`. Sends: `tuple[dict[str, str], set[str]]`.
- L51 `def schema_errors(document: Any, schema: dict[str, Any]) -> list[str]` — Implements schema errors. Receives: `document: Any, schema: dict[str, Any]`. Sends: `list[str]`.
- L54 `def leaf_errors(error: Any) -> Iterable[Any]` — Implements leaf errors. Receives: `error: Any`. Sends: `Iterable[Any]`.
- L73 `def semantic_errors(document: Any) -> list[str]` — Return cross-field errors that JSON Schema cannot express. Receives: `document: Any`. Sends: `list[str]`.
- L178 `def check_refs(values: Any, allowed: set[str], path: str, ref_name: str) -> None` — Validates refs. Receives: `values: Any, allowed: set[str], path: str, ref_name: str`. Sends: `None`.
- L524 `def validate_document(document: Any, schema: dict[str, Any]) -> list[str]` — Validate one already-loaded document; useful for tests and mutation checks. Receives: `document: Any, schema: dict[str, Any]`. Sends: `list[str]`.
- L530 `def _expand_paths(arguments: list[str]) -> list[Path]` — Implements expand paths. Receives: `arguments: list[str]`. Sends: `list[Path]`.
- L538 `def _set_claim_state(document: dict[str, Any], claim_id: str, variant: str, state: str) -> None` — Updates claim state. Receives: `document: dict[str, Any], claim_id: str, variant: str, state: str`. Sends: `None`.
- L551 `def run_self_test(schema: dict[str, Any]) -> int` — Run permanent valid-fixture and negative-mutation checks. Receives: `schema: dict[str, Any]`. Sends: `int`.
- L663 `def main(argv: list[str] | None=None) -> int` — Implements main. Receives: `argv: list[str] | None=None`. Sends: `int`.

### [`evaluation/analysis_pilot/__init__.py`](../../evaluation/analysis_pilot/__init__.py)

Purpose: Analysis-isolation evaluation pilot package: RAW_DIRECT vs EXTRACTED_STATE.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`evaluation/analysis_pilot/config.py`](../../evaluation/analysis_pilot/config.py)

Purpose: Configuration for the analysis-isolation evaluation pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`evaluation/analysis_pilot/dataset.py`](../../evaluation/analysis_pilot/dataset.py)

Purpose: Dataset loader and deterministic stratified sampling for the pilot.

- L12 `def load_all_cases(path: Path=DATASET_PATH) -> list[dict[str, Any]]` — Load all cases from the semantic verification JSONL file. Receives: `path: Path=DATASET_PATH`. Sends: `list[dict[str, Any]]`.
- L26 `def select_stratified_pilot_cases(cases: list[dict[str, Any]] | None=None, count: int=10) -> list[dict[str, Any]]` — Select stratified cases across scenarios and languages deterministically. Receives: `cases: list[dict[str, Any]] | None=None, count: int=10`. Sends: `list[dict[str, Any]]`.

### [`evaluation/analysis_pilot/generator.py`](../../evaluation/analysis_pilot/generator.py)

Purpose: Analysis generator for RAW_DIRECT and EXTRACTED_STATE conditions.

- L43 `async def generate_analysis(*, case_info_text: str, condition: str, case: dict[str, Any], model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE, max_output_tokens: int=ANALYSIS_MAX_OUTPUT_TOKENS) -> GenerationRecord` — Run the analysis generation LLM call with strict structured output. Receives: `*, case_info_text: str, condition: str, case: dict[str, Any], model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE, max_output_tokens: int=ANALYSIS_MAX_OUTPUT_TOKENS`. Sends: `GenerationRecord`.
- L201 `async def run_raw_direct_condition(case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE) -> GenerationRecord` — Condition A: RAW_DIRECT. Receives: `case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE`. Sends: `GenerationRecord`.
- L218 `async def run_extracted_state_condition(case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE) -> tuple[GenerationRecord, ExtractionLogRecord]` — Condition B: EXTRACTED_STATE. Receives: `case: dict[str, Any], *, model: str=DEFAULT_ANALYSIS_MODEL, temperature: float=ANALYSIS_TEMPERATURE`. Sends: `tuple[GenerationRecord, ExtractionLogRecord]`.

### [`evaluation/analysis_pilot/judge.py`](../../evaluation/analysis_pilot/judge.py)

Purpose: Single-probe binary LLM judge for evaluation probes.

- L31 `async def judge_single_probe(*, analysis_output: CaseAnalysisOutput | None, probe: dict[str, Any], case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE) -> ProbeJudgmentRecord` — Evaluate whether a generated case analysis semantically asserts/entails a single probe claim. Receives: `*, analysis_output: CaseAnalysisOutput | None, probe: dict[str, Any], case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE`. Sends: `ProbeJudgmentRecord`.
- L168 `async def judge_all_case_probes(*, analysis_output: CaseAnalysisOutput | None, case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE, concurrency: int=4) -> list[ProbeJudgmentRecord]` — Evaluate all verification pair probes for a single case under a given condition. Receives: `*, analysis_output: CaseAnalysisOutput | None, case: dict[str, Any], condition: str, model: str=DEFAULT_JUDGE_MODEL, temperature: float=JUDGE_TEMPERATURE, concurrency: int=4`. Sends: `list[ProbeJudgmentRecord]`.
- L181 `async def _eval_one(probe: dict[str, Any]) -> ProbeJudgmentRecord` — Implements eval one. Receives: `probe: dict[str, Any]`. Sends: `ProbeJudgmentRecord`.

### [`evaluation/analysis_pilot/metrics.py`](../../evaluation/analysis_pilot/metrics.py)

Purpose: Metric computations for Supported Probe Coverage, Epistemic Violations, and Factual Errors.

- L13 `def compute_case_metrics(judgments: list[ProbeJudgmentRecord]) -> dict[str, Any]` — Compute supported probe coverage, epistemic violation rates, and factual error rates for a single case. Receives: `judgments: list[ProbeJudgmentRecord]`. Sends: `dict[str, Any]`.
- L81 `def compute_aggregate_metrics(case_metrics_list: list[dict[str, Any]]) -> dict[str, Any]` — Compute macro-averages and breakdown across all cases for a condition. Receives: `case_metrics_list: list[dict[str, Any]]`. Sends: `dict[str, Any]`.

### [`evaluation/analysis_pilot/prompts.py`](../../evaluation/analysis_pilot/prompts.py)

Purpose: Unified prompts for analysis generation and single-probe binary judging.

- L46 `def get_prompt_hash(system_prompt: str, user_content: str) -> str` — Return SHA-256 hash of the full prompt content for provenance tracking. Receives: `system_prompt: str, user_content: str`. Sends: `str`.

### [`evaluation/analysis_pilot/runner.py`](../../evaluation/analysis_pilot/runner.py)

Purpose: Main evaluation pilot orchestrator and CLI entrypoint.

- L58 `def write_jsonl(path: Path, records: list[Any]) -> None` — Write list of Pydantic models or dicts to JSONL file. Receives: `path: Path, records: list[Any]`. Sends: `None`.
- L70 `def generate_summary_markdown(raw_agg: dict[str, Any], ext_agg: dict[str, Any], case_results: list[dict[str, Any]], model_name: str, judge_model: str, selected_cases: list[dict[str, Any]]) -> str` — Format markdown summary table and per-case results. Receives: `raw_agg: dict[str, Any], ext_agg: dict[str, Any], case_results: list[dict[str, Any]], model_name: str, judge_model: str, selected_cases: list[dict[str, Any]]`. Sends: `str`.
- L107 `def _fmt_ep(ep_dict: dict[str, Any], key: str) -> str` — Implements fmt ep. Receives: `ep_dict: dict[str, Any], key: str`. Sends: `str`.
- L167 `async def run_single_case(case: dict[str, Any], *, model: str, judge_model: str, output_dir: Path) -> dict[str, Any]` — Execute both conditions and evaluate probes for a single case. Receives: `case: dict[str, Any], *, model: str, judge_model: str, output_dir: Path`. Sends: `dict[str, Any]`.
- L236 `async def run_pipeline(*, sanity_check: bool=False, model: str=DEFAULT_ANALYSIS_MODEL, judge_model: str=DEFAULT_JUDGE_MODEL, case_count: int=10, output_dir: Path=DEFAULT_OUTPUT_DIR) -> None` — Main pipeline execution orchestrator. Receives: `*, sanity_check: bool=False, model: str=DEFAULT_ANALYSIS_MODEL, judge_model: str=DEFAULT_JUDGE_MODEL, case_count: int=10, output_dir: Path=DEFAULT_OUTPUT_DIR`. Sends: `None`.
- L390 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`evaluation/analysis_pilot/schemas.py`](../../evaluation/analysis_pilot/schemas.py)

Purpose: Data schemas for analysis outputs, extraction logs, probe evaluations, and metrics.

- L18 `class Finding(BaseModel)` — A distinct analytical finding with an associated epistemic status. Receives: `constructor arguments and class fields`. Sends: `Finding`.
- L36 `class CaseAnalysisOutput(BaseModel)` — Structured evaluation output schema for case analysis generation. Receives: `constructor arguments and class fields`. Sends: `CaseAnalysisOutput`.
- L51 `class JudgeResponse(BaseModel)` — Structured output schema for the binary probe judge. Receives: `constructor arguments and class fields`. Sends: `JudgeResponse`.
- L65 `class GenerationRecord(BaseModel)` — Full machine-readable log of an analysis generation call. Receives: `constructor arguments and class fields`. Sends: `GenerationRecord`.
- L87 `class ExtractionLogRecord(BaseModel)` — Machine-readable record of production extraction step. Receives: `constructor arguments and class fields`. Sends: `ExtractionLogRecord`.
- L105 `class ProbeJudgmentRecord(BaseModel)` — Machine-readable log of an individual probe evaluation. Receives: `constructor arguments and class fields`. Sends: `ProbeJudgmentRecord`.

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

- L14 `def _common_data_arguments(parser: argparse.ArgumentParser) -> None` — Implements common data arguments. Receives: `parser: argparse.ArgumentParser`. Sends: `None`.
- L20 `def build_parser() -> argparse.ArgumentParser` — Builds parser. Receives: `not applicable`. Sends: `argparse.ArgumentParser`.
- L44 `def main(argv: list[str] | None=None) -> None` — Implements main. Receives: `argv: list[str] | None=None`. Sends: `None`.

### [`experiments/context_refinement/compressor.py`](../../experiments/context_refinement/compressor.py)

Purpose: Owns compressor behavior for the research and evaluation workspace.

- L12 `class CompressorFailure(RuntimeError)` — Encapsulates compressorfailure. Receives: `constructor arguments and class fields`. Sends: `CompressorFailure`.
- L16 `class LLMLingua2Refiner` — Encapsulates llmlingua2refiner. Receives: `constructor arguments and class fields`. Sends: `LLMLingua2Refiner`.
- L19 `def __init__(self, model_name: str=DEFAULT_COMPRESSOR_MODEL, compression_rate: float=DEFAULT_COMPRESSION_RATE, device_map: str='cpu') -> None` — Implements init. Receives: `self, model_name: str=DEFAULT_COMPRESSOR_MODEL, compression_rate: float=DEFAULT_COMPRESSION_RATE, device_map: str='cpu'`. Sends: `None`.
- L53 `def refine(self, context: str) -> RefinedContext` — Implements refine. Receives: `self, context: str`. Sends: `RefinedContext`.
- L77 `def _as_int(value: Any) -> int | None` — Implements as int. Receives: `value: Any`. Sends: `int | None`.

### [`experiments/context_refinement/contracts.py`](../../experiments/context_refinement/contracts.py)

Purpose: Owns contracts behavior for the research and evaluation workspace.

- L8 `class RefinedContext` — Encapsulates refinedcontext. Receives: `constructor arguments and class fields`. Sends: `RefinedContext`.
- L15 `class ContextRefiner(Protocol)` — Encapsulates contextrefiner. Receives: `constructor arguments and class fields`. Sends: `ContextRefiner`.
- L19 `def refine(self, context: str) -> RefinedContext` — Implements refine. Receives: `self, context: str`. Sends: `RefinedContext`.

### [`experiments/context_refinement/dataset.py`](../../experiments/context_refinement/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

- L23 `def sha256_file(path: Path) -> str` — Implements sha256 file. Receives: `path: Path`. Sends: `str`.
- L31 `def _selection_ids(path: Path) -> list[str]` — Implements selection ids. Receives: `path: Path`. Sends: `list[str]`.
- L39 `def _row_language(row: dict[str, Any]) -> str` — Implements row language. Receives: `row: dict[str, Any]`. Sends: `str`.
- L43 `def load_reused_subset(benchmark_path: Path, selection_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]` — Retrieves reused subset. Receives: `benchmark_path: Path, selection_path: Path`. Sends: `tuple[list[dict[str, Any]], dict[str, Any]]`.
- L85 `def gold_text(row: dict[str, Any]) -> str` — Implements gold text. Receives: `row: dict[str, Any]`. Sends: `str`.

### [`experiments/context_refinement/evaluation.py`](../../experiments/context_refinement/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

- L10 `def _ratio(numerator: int, denominator: int) -> float` — Implements ratio. Receives: `numerator: int, denominator: int`. Sends: `float`.
- L14 `def evaluate_pairs(rows: list[dict[str, Any]], raw_contexts: dict[str, dict[str, Any]], refined_contexts: dict[str, dict[str, Any]], predictions: dict[tuple[str, str], dict[str, Any]], sbert_model: Any) -> list[dict[str, Any]]` — Implements evaluate pairs. Receives: `rows: list[dict[str, Any]], raw_contexts: dict[str, dict[str, Any]], refined_contexts: dict[str, dict[str, Any]], predictions: dict[tuple[str, str], dict[str, Any]], sbert_model: Any`. Sends: `list[dict[str, Any]]`.

### [`experiments/context_refinement/llm_client.py`](../../experiments/context_refinement/llm_client.py)

Purpose: Owns llm client behavior for the research and evaluation workspace.

- L17 `class OpenRouterPilotClient` — Encapsulates openrouterpilotclient. Receives: `constructor arguments and class fields`. Sends: `OpenRouterPilotClient`.
- L22 `def __init__(self, api_key_env: str='OPENROUTER_API_KEY', base_url: str=DEFAULT_BASE_URL, timeout: float=120.0, max_attempts: int=5, backoff_base: float=1.0) -> None` — Implements init. Receives: `self, api_key_env: str='OPENROUTER_API_KEY', base_url: str=DEFAULT_BASE_URL, timeout: float=120.0, max_attempts: int=5, backoff_base: float=1.0`. Sends: `None`.
- L42 `def __enter__(self) -> 'OpenRouterPilotClient'` — Implements enter. Receives: `self`. Sends: `'OpenRouterPilotClient'`.
- L56 `def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None` — Implements exit. Receives: `self, exc_type: Any, exc_value: Any, traceback: Any`. Sends: `None`.
- L61 `def predict(self, prompt: str, sample_id: str, condition: str) -> dict[str, Any]` — Implements predict. Receives: `self, prompt: str, sample_id: str, condition: str`. Sends: `dict[str, Any]`.

### [`experiments/context_refinement/metrics.py`](../../experiments/context_refinement/metrics.py)

Purpose: Owns metrics behavior for the research and evaluation workspace.

- L6 `def load_sbert_model(model_name: str, device: str) -> Any` — Retrieves sbert model. Receives: `model_name: str, device: str`. Sends: `Any`.
- L14 `def score_condition(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], condition: str, sbert_model: Any) -> dict[str, dict[str, float]]` — Implements score condition. Receives: `rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], condition: str, sbert_model: Any`. Sends: `dict[str, dict[str, float]]`.

### [`experiments/context_refinement/prompting.py`](../../experiments/context_refinement/prompting.py)

Purpose: Owns prompting behavior for the research and evaluation workspace.

- L8 `def build_condition_prompt(row: dict[str, Any], context: str) -> str` — Builds condition prompt. Receives: `row: dict[str, Any], context: str`. Sends: `str`.
- L14 `def prompt_template_parts(row: dict[str, Any], raw_context: str, refined_context: str) -> tuple[str, str, str, str]` — Implements prompt template parts. Receives: `row: dict[str, Any], raw_context: str, refined_context: str`. Sends: `tuple[str, str, str, str]`.
- L26 `def validate_context_only_prompt_change(row: dict[str, Any], raw_context: str, refined_context: str) -> None` — Validates context only prompt change. Receives: `row: dict[str, Any], raw_context: str, refined_context: str`. Sends: `None`.

### [`experiments/context_refinement/protected_spans.py`](../../experiments/context_refinement/protected_spans.py)

Purpose: Owns protected spans behavior for the research and evaluation workspace.

- L27 `def extract_protected_spans(text: str) -> list[dict[str, Any]]` — Extracts protected spans. Receives: `text: str`. Sends: `list[dict[str, Any]]`.
- L41 `def compare_protected_spans(raw_context: str, refined_context: str) -> dict[str, Any]` — Implements compare protected spans. Receives: `raw_context: str, refined_context: str`. Sends: `dict[str, Any]`.

### [`experiments/context_refinement/reporting.py`](../../experiments/context_refinement/reporting.py)

Purpose: Owns reporting behavior for the research and evaluation workspace.

- L9 `def _percentile(values: list[float], percentile: float) -> float` — Implements percentile. Receives: `values: list[float], percentile: float`. Sends: `float`.
- L20 `def _metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements metric stats. Receives: `records: list[dict[str, Any]], condition: str`. Sends: `dict[str, Any]`.
- L30 `def _group_metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements group metric stats. Receives: `records: list[dict[str, Any]], condition: str`. Sends: `dict[str, Any]`.
- L37 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary. Receives: `records: list[dict[str, Any]], config: dict[str, Any]`. Sends: `dict[str, Any]`.
- L85 `def _sum_span_types(records: list[dict[str, Any]], field: str) -> dict[str, int]` — Implements sum span types. Receives: `records: list[dict[str, Any]], field: str`. Sends: `dict[str, int]`.
- L93 `def _ranked_examples(deltas: list[dict[str, Any]], group: str) -> list[dict[str, Any]]` — Implements ranked examples. Receives: `deltas: list[dict[str, Any]], group: str`. Sends: `list[dict[str, Any]]`.
- L104 `def render_markdown(summary: dict[str, Any]) -> str` — Renders markdown. Receives: `summary: dict[str, Any]`. Sends: `str`.

### [`experiments/context_refinement/reproducibility.py`](../../experiments/context_refinement/reproducibility.py)

Purpose: Owns reproducibility behavior for the research and evaluation workspace.

- L11 `def set_deterministic_seed(seed: int) -> dict[str, Any]` — Updates deterministic seed. Receives: `seed: int`. Sends: `dict[str, Any]`.
- L30 `def runtime_device_report() -> dict[str, Any]` — Implements runtime device report. Receives: `not applicable`. Sends: `dict[str, Any]`.

### [`experiments/context_refinement/runner.py`](../../experiments/context_refinement/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L29 `def _raw_context_record(row: dict[str, Any]) -> dict[str, Any]` — Implements raw context record. Receives: `row: dict[str, Any]`. Sends: `dict[str, Any]`.
- L42 `def _refined_context_record(row: dict[str, Any], result: Any, refiner_config: dict[str, Any]) -> dict[str, Any]` — Implements refined context record. Receives: `row: dict[str, Any], result: Any, refiner_config: dict[str, Any]`. Sends: `dict[str, Any]`.
- L62 `def _ensure_raw_contexts(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]` — Implements ensure raw contexts. Receives: `rows: list[dict[str, Any]], path: Path`. Sends: `dict[str, dict[str, Any]]`.
- L76 `def _ensure_refined_contexts(rows: list[dict[str, Any]], path: Path, refiner: LLMLingua2Refiner) -> dict[str, dict[str, Any]]` — Implements ensure refined contexts. Receives: `rows: list[dict[str, Any]], path: Path, refiner: LLMLingua2Refiner`. Sends: `dict[str, dict[str, Any]]`.
- L98 `def _prediction_record(row: dict[str, Any], condition: str, context: str, prompt: str, response: dict[str, Any]) -> dict[str, Any]` — Implements prediction record. Receives: `row: dict[str, Any], condition: str, context: str, prompt: str, response: dict[str, Any]`. Sends: `dict[str, Any]`.
- L119 `def _ensure_predictions(rows: list[dict[str, Any]], condition: str, contexts: dict[str, dict[str, Any]], prediction_path: Path, client: OpenRouterPilotClient, existing: dict[tuple[str, str], dict[str, Any]]) -> None` — Implements ensure predictions. Receives: `rows: list[dict[str, Any]], condition: str, contexts: dict[str, dict[str, Any]], prediction_path: Path, client: OpenRouterPilotClient, existing: dict[tuple[str, str], dict[str, Any]]`. Sends: `None`.
- L145 `def _run_config(args: Any, dataset_manifest: dict[str, Any], runtime: dict[str, Any], seed_report: dict[str, Any]) -> dict[str, Any]` — Executes config. Receives: `args: Any, dataset_manifest: dict[str, Any], runtime: dict[str, Any], seed_report: dict[str, Any]`. Sends: `dict[str, Any]`.
- L188 `def _write_report(output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], sbert_model_name: str, sbert_device: str) -> None` — Implements write report. Receives: `output_dir: Path, rows: list[dict[str, Any]], config: dict[str, Any], sbert_model_name: str, sbert_device: str`. Sends: `None`.
- L203 `def run_experiment(args: Any) -> None` — Executes experiment. Receives: `args: Any`. Sends: `None`.
- L243 `def report_existing(args: Any) -> None` — Implements report existing. Receives: `args: Any`. Sends: `None`.

### [`experiments/context_refinement/storage.py`](../../experiments/context_refinement/storage.py)

Purpose: Owns storage behavior for the research and evaluation workspace.

- L9 `def read_jsonl(path: Path) -> list[dict[str, Any]]` — Retrieves jsonl. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L24 `def index_records(path: Path, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]` — Implements index records. Receives: `path: Path, key_fields: tuple[str, ...]`. Sends: `dict[tuple[str, ...], dict[str, Any]]`.
- L34 `def append_jsonl(path: Path, record: dict[str, Any]) -> None` — Implements append jsonl. Receives: `path: Path, record: dict[str, Any]`. Sends: `None`.
- L42 `def write_json(path: Path, value: Any) -> None` — Implements write json. Receives: `path: Path, value: Any`. Sends: `None`.
- L47 `def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None` — Implements write jsonl. Receives: `path: Path, records: Iterable[dict[str, Any]]`. Sends: `None`.
- L58 `def write_or_validate_json(path: Path, value: Any) -> None` — Implements write or validate json. Receives: `path: Path, value: Any`. Sends: `None`.

### [`experiments/context_refinement/tests/__init__.py`](../../experiments/context_refinement/tests/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/context_refinement/tests/test_dataset_and_storage.py`](../../experiments/context_refinement/tests/test_dataset_and_storage.py)

Purpose: Verifies dataset and storage behavior in the research and evaluation workspace.

- L11 `class DatasetAndStorageTests(unittest.TestCase)` — Encapsulates datasetandstoragetests. Receives: `constructor arguments and class fields`. Sends: `DatasetAndStorageTests`.
- L12 `def test_existing_selection_is_reused_then_filtered(self) -> None` — Implements test existing selection is reused then filtered. Receives: `self`. Sends: `None`.
- L41 `def test_jsonl_index_rejects_duplicate_keys(self) -> None` — Implements test jsonl index rejects duplicate keys. Receives: `self`. Sends: `None`.

### [`experiments/context_refinement/tests/test_prompt_and_spans.py`](../../experiments/context_refinement/tests/test_prompt_and_spans.py)

Purpose: Verifies prompt and spans behavior in the research and evaluation workspace.

- L12 `class PromptAndSpanTests(unittest.TestCase)` — Encapsulates promptandspantests. Receives: `constructor arguments and class fields`. Sends: `PromptAndSpanTests`.
- L13 `def test_prompt_changes_only_context(self) -> None` — Implements test prompt changes only context. Receives: `self`. Sends: `None`.
- L28 `def test_protected_span_diagnostics_are_explicit(self) -> None` — Implements test protected span diagnostics are explicit. Receives: `self`. Sends: `None`.

### [`experiments/ctinexus_extraction_benchmark/__init__.py`](../../experiments/ctinexus_extraction_benchmark/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/__main__.py`](../../experiments/ctinexus_extraction_benchmark/__main__.py)

Purpose: Owns main behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/cache.py`](../../experiments/ctinexus_extraction_benchmark/cache.py)

Purpose: Owns cache behavior for the research and evaluation workspace.

- L11 `def load_jsonl_cache(path: Path) -> dict[str, ExtractorPrediction]` — Retrieves jsonl cache. Receives: `path: Path`. Sends: `dict[str, ExtractorPrediction]`.
- L26 `def cache_matches(record: ExtractorPrediction, *, condition: str, doc_id: str, narrative_sha256: str, contract: dict[str, Any]) -> bool` — Implements cache matches. Receives: `record: ExtractorPrediction, *, condition: str, doc_id: str, narrative_sha256: str, contract: dict[str, Any]`. Sends: `bool`.
- L46 `def append_jsonl(path: Path, record: ExtractorPrediction) -> None` — Implements append jsonl. Receives: `path: Path, record: ExtractorPrediction`. Sends: `None`.
- L55 `def write_json(path: Path, payload: Any) -> None` — Implements write json. Receives: `path: Path, payload: Any`. Sends: `None`.

### [`experiments/ctinexus_extraction_benchmark/constants.py`](../../experiments/ctinexus_extraction_benchmark/constants.py)

Purpose: Owns constants behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/ctinexus_extraction_benchmark/dataset.py`](../../experiments/ctinexus_extraction_benchmark/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

- L18 `class GoldEntity` — Encapsulates goldentity. Receives: `constructor arguments and class fields`. Sends: `GoldEntity`.
- L24 `class GoldRelation` — Encapsulates goldrelation. Receives: `constructor arguments and class fields`. Sends: `GoldRelation`.
- L31 `class CTINexusCase` — Encapsulates ctinexuscase. Receives: `constructor arguments and class fields`. Sends: `CTINexusCase`.
- L38 `def sha256_text(value: str) -> str` — Implements sha256 text. Receives: `value: str`. Sends: `str`.
- L42 `def _raw_entities(raw: dict[str, Any]) -> list[GoldEntity]` — Implements raw entities. Receives: `raw: dict[str, Any]`. Sends: `list[GoldEntity]`.
- L54 `def _raw_relations(raw: dict[str, Any]) -> list[GoldRelation]` — Implements raw relations. Receives: `raw: dict[str, Any]`. Sends: `list[GoldRelation]`.
- L70 `def _load_raw_document(path: Path) -> dict[str, Any]` — Retrieves raw document. Receives: `path: Path`. Sends: `dict[str, Any]`.
- L77 `def load_ctinexus_cases(dataset_dir: str | Path) -> list[CTINexusCase]` — Retrieves ctinexus cases. Receives: `dataset_dir: str | Path`. Sends: `list[CTINexusCase]`.
- L94 `def dataset_manifest(cases: list[CTINexusCase], dataset_dir: str | Path) -> dict[str, Any]` — Implements dataset manifest. Receives: `cases: list[CTINexusCase], dataset_dir: str | Path`. Sends: `dict[str, Any]`.

### [`experiments/ctinexus_extraction_benchmark/evaluation.py`](../../experiments/ctinexus_extraction_benchmark/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

- L16 `def _stats(values: list[float]) -> dict[str, float | int | None]` — Implements stats. Receives: `values: list[float]`. Sends: `dict[str, float | int | None]`.
- L31 `def _coverage(predictions: Iterable[ExtractorPrediction]) -> dict[str, object]` — Implements coverage. Receives: `predictions: Iterable[ExtractorPrediction]`. Sends: `dict[str, object]`.
- L48 `def _latency(predictions: Iterable[ExtractorPrediction], condition: str) -> dict[str, object]` — Implements latency. Receives: `predictions: Iterable[ExtractorPrediction], condition: str`. Sends: `dict[str, object]`.
- L71 `def _example(doc_id: str, category: str, values: object) -> dict[str, object]` — Implements example. Receives: `doc_id: str, category: str, values: object`. Sends: `dict[str, object]`.
- L75 `def _error_examples(cases: list[CTINexusCase], evaluations: dict[str, DocumentEvaluation], predictions: dict[str, ExtractorPrediction]) -> dict[str, list[dict[str, object]]]` — Implements error examples. Receives: `cases: list[CTINexusCase], evaluations: dict[str, DocumentEvaluation], predictions: dict[str, ExtractorPrediction]`. Sends: `dict[str, list[dict[str, object]]]`.
- L128 `def evaluate_condition(cases: list[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str) -> tuple[dict[str, object], list[dict[str, object]]]` — Implements evaluate condition. Receives: `cases: list[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str`. Sends: `tuple[dict[str, object], list[dict[str, object]]]`.
- L148 `def combined_error_examples(cases: list[CTINexusCase], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], e1_predictions: dict[str, ExtractorPrediction], e2_predictions: dict[str, ExtractorPrediction]) -> dict[str, list[dict[str, object]]]` — Implements combined error examples. Receives: `cases: list[CTINexusCase], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], e1_predictions: dict[str, ExtractorPrediction], e2_predictions: dict[str, ExtractorPrediction]`. Sends: `dict[str, list[dict[str, object]]]`.

### [`experiments/ctinexus_extraction_benchmark/gliner.py`](../../experiments/ctinexus_extraction_benchmark/gliner.py)

Purpose: Owns gliner behavior for the research and evaluation workspace.

- L19 `def resolve_device(requested: str) -> str` — Implements resolve device. Receives: `requested: str`. Sends: `str`.
- L27 `def _confidence_values(items: list[TypedEntityPrediction], relations: list[TypedRelationPrediction]) -> list[float]` — Implements confidence values. Receives: `items: list[TypedEntityPrediction], relations: list[TypedRelationPrediction]`. Sends: `list[float]`.
- L33 `def _distribution(values: list[float]) -> dict[str, float | int | None]` — Implements distribution. Receives: `values: list[float]`. Sends: `dict[str, float | int | None]`.
- L48 `def _field_value(value: Any) -> Any` — Implements field value. Receives: `value: Any`. Sends: `Any`.
- L54 `class CtinexusGlinerExtractor` — Encapsulates ctinexusglinerextractor. Receives: `constructor arguments and class fields`. Sends: `CtinexusGlinerExtractor`.
- L55 `def __init__(self, *, model_name: str=GLINER_MODEL, device: str='auto', threshold: float=GLINER_THRESHOLD) -> None` — Implements init. Receives: `self, *, model_name: str=GLINER_MODEL, device: str='auto', threshold: float=GLINER_THRESHOLD`. Sends: `None`.
- L72 `def _ground(self, source: str, value: Any) -> dict[str, Any] | None` — Implements ground. Receives: `self, source: str, value: Any`. Sends: `dict[str, Any] | None`.
- L75 `def _extract_entities(self, source: str) -> tuple[list[TypedEntityPrediction], list[dict[str, Any]]]` — Extracts entities. Receives: `self, source: str`. Sends: `tuple[list[TypedEntityPrediction], list[dict[str, Any]]]`.
- L113 `def _extract_relations(self, source: str) -> tuple[list[TypedRelationPrediction], list[dict[str, Any]]]` — Extracts relations. Receives: `self, source: str`. Sends: `tuple[list[TypedRelationPrediction], list[dict[str, Any]]]`.
- L152 `def extract(self, case: CTINexusCase)` — Extracts extract. Receives: `self, case: CTINexusCase`. Sends: `inferred or None`.

### [`experiments/ctinexus_extraction_benchmark/production.py`](../../experiments/ctinexus_extraction_benchmark/production.py)

Purpose: Owns production behavior for the research and evaluation workspace.

- L23 `def _api_call_count(result: Any, serialized_input_length: int) -> int` — Implements api call count. Receives: `result: Any, serialized_input_length: int`. Sends: `int`.
- L36 `async def extract_production(case: CTINexusCase, model: str=PRODUCTION_MODEL)` — Extracts production. Receives: `case: CTINexusCase, model: str=PRODUCTION_MODEL`. Sends: `inferred or None`.

### [`experiments/ctinexus_extraction_benchmark/projection.py`](../../experiments/ctinexus_extraction_benchmark/projection.py)

Purpose: Owns projection behavior for the research and evaluation workspace.

- L16 `def _dedupe(values: Iterable[str]) -> list[str]` — Implements dedupe. Receives: `values: Iterable[str]`. Sends: `list[str]`.
- L20 `def _prediction(*, condition: str, case: CTINexusCase, model: str, graph: PredictedGraph, typed_entities: list[TypedEntityPrediction], typed_relations: list[TypedRelationPrediction], diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements prediction. Receives: `*, condition: str, case: CTINexusCase, model: str, graph: PredictedGraph, typed_entities: list[TypedEntityPrediction], typed_relations: list[TypedRelationPrediction], diagnostics: dict[str, Any], contract: dict[str, Any]`. Sends: `ExtractorPrediction`.
- L45 `def production_prediction(case: CTINexusCase, extraction: Any, *, model: str, status: str, failure_code: str | None, failure_message: str | None, latency_ms: float, input_tokens: int | None, output_tokens: int | None, diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements production prediction. Receives: `case: CTINexusCase, extraction: Any, *, model: str, status: str, failure_code: str | None, failure_message: str | None, latency_ms: float, input_tokens: int | None, output_tokens: int | None, diagnostics: dict[str, Any], contract: dict[str, Any]`. Sends: `ExtractorPrediction`.
- L115 `def gliner_prediction(case: CTINexusCase, *, model: str, entities: list[TypedEntityPrediction], relations: list[TypedRelationPrediction], latency_ms: float, diagnostics: dict[str, Any], contract: dict[str, Any]) -> ExtractorPrediction` — Implements gliner prediction. Receives: `case: CTINexusCase, *, model: str, entities: list[TypedEntityPrediction], relations: list[TypedRelationPrediction], latency_ms: float, diagnostics: dict[str, Any], contract: dict[str, Any]`. Sends: `ExtractorPrediction`.
- L144 `def _dedupe_triplets(relations: list[TypedRelationPrediction]) -> list[tuple[str, str, str]]` — Implements dedupe triplets. Receives: `relations: list[TypedRelationPrediction]`. Sends: `list[tuple[str, str, str]]`.
- L148 `def _dedupe_edges(relations: list[TypedRelationPrediction]) -> list[tuple[str, str]]` — Implements dedupe edges. Receives: `relations: list[TypedRelationPrediction]`. Sends: `list[tuple[str, str]]`.

### [`experiments/ctinexus_extraction_benchmark/report.py`](../../experiments/ctinexus_extraction_benchmark/report.py)

Purpose: Owns report behavior for the research and evaluation workspace.

- L10 `def _metric(summary: dict[str, Any], block: str, field: str) -> float` — Implements metric. Receives: `summary: dict[str, Any], block: str, field: str`. Sends: `float`.
- L14 `def _comparison_rows(e1: dict[str, Any], e2: dict[str, Any]) -> list[tuple[str, str, str, str]]` — Implements comparison rows. Receives: `e1: dict[str, Any], e2: dict[str, Any]`. Sends: `list[tuple[str, str, str, str]]`.
- L34 `def _markdown_table(headers: list[str], rows: list[list[str]]) -> str` — Implements markdown table. Receives: `headers: list[str], rows: list[list[str]]`. Sends: `str`.
- L41 `def _category_table(condition: str, rows: list[dict[str, Any]], key: str) -> str` — Implements category table. Receives: `condition: str, rows: list[dict[str, Any]], key: str`. Sends: `str`.
- L50 `def _summary_payload(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> dict[str, Any]` — Implements summary payload. Receives: `manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]`. Sends: `dict[str, Any]`.
- L68 `def _markdown(manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]) -> str` — Implements markdown. Receives: `manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], errors: dict[str, Any]`. Sends: `str`.
- L152 `def write_report(output_dir: Path, manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], errors: dict[str, Any]) -> dict[str, Any]` — Implements write report. Receives: `output_dir: Path, manifest: dict[str, Any], config: dict[str, Any], e1: dict[str, Any], e2: dict[str, Any], e1_rows: list[dict[str, object]], e2_rows: list[dict[str, object]], errors: dict[str, Any]`. Sends: `dict[str, Any]`.

### [`experiments/ctinexus_extraction_benchmark/runner.py`](../../experiments/ctinexus_extraction_benchmark/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L38 `def _contracts(config: dict[str, Any]) -> dict[str, dict[str, Any]]` — Implements contracts. Receives: `config: dict[str, Any]`. Sends: `dict[str, dict[str, Any]]`.
- L54 `def _config(output_dir: Path, dataset_dir: Path, gliner_device: str) -> dict[str, Any]` — Implements config. Receives: `output_dir: Path, dataset_dir: Path, gliner_device: str`. Sends: `dict[str, Any]`.
- L84 `def _verify_config(output_dir: Path, config: dict[str, Any]) -> None` — Validates config. Receives: `output_dir: Path, config: dict[str, Any]`. Sends: `None`.
- L100 `def _offline_e1(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction` — Implements offline e1. Receives: `case: CTINexusCase, config: dict[str, Any]`. Sends: `ExtractorPrediction`.
- L116 `def _offline_e2(case: CTINexusCase, config: dict[str, Any]) -> ExtractorPrediction` — Implements offline e2. Receives: `case: CTINexusCase, config: dict[str, Any]`. Sends: `ExtractorPrediction`.
- L133 `async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]` — Executes benchmark. Receives: `args: argparse.Namespace`. Sends: `dict[str, Any]`.
- L190 `def _confidence_summary(predictions: dict[str, ExtractorPrediction]) -> dict[str, object]` — Implements confidence summary. Receives: `predictions: dict[str, ExtractorPrediction]`. Sends: `dict[str, object]`.
- L197 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L206 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`experiments/ctinexus_extraction_benchmark/runtime.py`](../../experiments/ctinexus_extraction_benchmark/runtime.py)

Purpose: Owns runtime behavior for the research and evaluation workspace.

- L12 `def prepare_runtime() -> None` — Implements prepare runtime. Receives: `not applicable`. Sends: `None`.

### [`experiments/ctinexus_extraction_benchmark/schemas.py`](../../experiments/ctinexus_extraction_benchmark/schemas.py)

Purpose: Owns schemas behavior for the research and evaluation workspace.

- L10 `class TypedEntityPrediction(BaseModel)` — Encapsulates typedentityprediction. Receives: `constructor arguments and class fields`. Sends: `TypedEntityPrediction`.
- L20 `class TypedRelationPrediction(BaseModel)` — Encapsulates typedrelationprediction. Receives: `constructor arguments and class fields`. Sends: `TypedRelationPrediction`.
- L35 `class ExtractorPrediction(BaseModel)` — Encapsulates extractorprediction. Receives: `constructor arguments and class fields`. Sends: `ExtractorPrediction`.

### [`experiments/ctinexus_extraction_benchmark/type_mapping.py`](../../experiments/ctinexus_extraction_benchmark/type_mapping.py)

Purpose: Owns type mapping behavior for the research and evaluation workspace.

- L33 `def _key(value: str) -> str` — Implements key. Receives: `value: str`. Sends: `str`.
- L37 `def map_production_entity_type(value: str) -> str | None` — Transforms production entity type. Receives: `value: str`. Sends: `str | None`.

### [`experiments/ctinexus_extraction_benchmark/typed_metrics.py`](../../experiments/ctinexus_extraction_benchmark/typed_metrics.py)

Purpose: Owns typed metrics behavior for the research and evaluation workspace.

- L15 `def _mapped_type(condition: str, value: str) -> str | None` — Implements mapped type. Receives: `condition: str, value: str`. Sends: `str | None`.
- L21 `def _sets_for_entity_type(case: CTINexusCase, prediction: ExtractorPrediction, condition: str)` — Implements sets for entity type. Receives: `case: CTINexusCase, prediction: ExtractorPrediction, condition: str`. Sends: `inferred or None`.
- L36 `def entity_type_metrics(cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str) -> tuple[list[dict[str, object]], dict[str, int]]` — Implements entity type metrics. Receives: `cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction], condition: str`. Sends: `tuple[list[dict[str, object]], dict[str, int]]`.
- L69 `def relation_type_metrics(cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction]) -> list[dict[str, object]]` — Implements relation type metrics. Receives: `cases: Iterable[CTINexusCase], predictions: dict[str, ExtractorPrediction]`. Sends: `list[dict[str, object]]`.

### [`experiments/followup_pilot/__init__.py`](../../experiments/followup_pilot/__init__.py)

Purpose: One-case pilot comparing no follow-up with adaptive clarification.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/followup_pilot/evaluator.py`](../../experiments/followup_pilot/evaluator.py)

Purpose: Blind, interactive manual evaluator for two pilot result files.

- L43 `class ShuffleLike(Protocol)` — Encapsulates shufflelike. Receives: `constructor arguments and class fields`. Sends: `ShuffleLike`.
- L44 `def shuffle(self, values: list[ExperimentResult]) -> None` — Implements shuffle. Receives: `self, values: list[ExperimentResult]`. Sends: `None`.
- L47 `def utc_now() -> datetime` — Implements utc now. Receives: `not applicable`. Sends: `datetime`.
- L51 `def load_result(path: Path) -> ExperimentResult` — Retrieves result. Receives: `path: Path`. Sends: `ExperimentResult`.
- L55 `def exact_duplicate_question_count(result: ExperimentResult) -> int` — Implements exact duplicate question count. Receives: `result: ExperimentResult`. Sends: `int`.
- L60 `def recovered_hidden_fields(result: ExperimentResult) -> set[str]` — Implements recovered hidden fields. Receives: `result: ExperimentResult`. Sends: `set[str]`.
- L70 `def calculate_metrics(*, case: PilotCase, result: ExperimentResult, field_scores: dict[str, FieldRating]) -> SystemMetrics` — Implements calculate metrics. Receives: `*, case: PilotCase, result: ExperimentResult, field_scores: dict[str, FieldRating]`. Sends: `SystemMetrics`.
- L98 `def _prompt_rating(*, system_label: str, field: str, input_fn: InputCallable, output_fn: OutputCallable) -> FieldRating` — Implements prompt rating. Receives: `*, system_label: str, field: str, input_fn: InputCallable, output_fn: OutputCallable`. Sends: `FieldRating`.
- L115 `def conduct_blind_evaluation(*, case: PilotCase, results: Sequence[ExperimentResult], input_fn: InputCallable=input, output_fn: OutputCallable=print, rng: ShuffleLike | None=None) -> EvaluationResult` — Implements conduct blind evaluation. Receives: `*, case: PilotCase, results: Sequence[ExperimentResult], input_fn: InputCallable=input, output_fn: OutputCallable=print, rng: ShuffleLike | None=None`. Sends: `EvaluationResult`.
- L185 `def save_evaluation(evaluation: EvaluationResult, path: Path) -> Path` — Persists evaluation. Receives: `evaluation: EvaluationResult, path: Path`. Sends: `Path`.
- L194 `def build_argument_parser() -> argparse.ArgumentParser` — Builds argument parser. Receives: `not applicable`. Sends: `argparse.ArgumentParser`.
- L202 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`experiments/followup_pilot/runner.py`](../../experiments/followup_pilot/runner.py)

Purpose: Terminal runner for the bounded follow-up pilot.

- L52 `class FollowUpPolicyLike(Protocol)` — Encapsulates followuppolicylike. Receives: `constructor arguments and class fields`. Sends: `FollowUpPolicyLike`.
- L53 `async def decide(self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]) -> FollowUpDecision` — Implements decide. Receives: `self, *, original_user_content: str, clarification_exchanges: Sequence[ClarificationExchange]`. Sends: `FollowUpDecision`.
- L62 `class HumanAnswer` — Encapsulates humananswer. Receives: `constructor arguments and class fields`. Sends: `HumanAnswer`.
- L71 `def utc_now() -> datetime` — Implements utc now. Receives: `not applicable`. Sends: `datetime`.
- L75 `def load_case(path: Path) -> PilotCase` — Retrieves case. Receives: `path: Path`. Sends: `PilotCase`.
- L79 `def build_initial_query(case: PilotCase) -> str` — Build the one frozen initial query shared by both conditions. Receives: `case: PilotCase`. Sends: `str`.
- L88 `def _normalize_question(question: str) -> str` — Normalizes question. Receives: `question: str`. Sends: `str`.
- L92 `async def _timed_rag_call(*, query: str, round_number: int, rag_call: RagCallable) -> tuple[QueryResponse, RagCallRecord]` — Implements timed rag call. Receives: `*, query: str, round_number: int, rag_call: RagCallable`. Sends: `tuple[QueryResponse, RagCallRecord]`.
- L111 `def _interactive_answer_provider(*, input_fn: InputCallable, output_fn: OutputCallable) -> AnswerProvider` — Implements interactive answer provider. Receives: `*, input_fn: InputCallable, output_fn: OutputCallable`. Sends: `AnswerProvider`.
- L116 `def provide(case: PilotCase, round_number: int, question: str) -> HumanAnswer` — Implements provide. Receives: `case: PilotCase, round_number: int, question: str`. Sends: `HumanAnswer`.
- L155 `def print_answer_sheet(case: PilotCase, output_fn: OutputCallable=print) -> None` — Implements print answer sheet. Receives: `case: PilotCase, output_fn: OutputCallable=print`. Sends: `None`.
- L162 `async def _build_result(*, case: PilotCase, method: Method, policy_position: str, policy_calls: int, started_at: datetime, total_started: float, questions: list[QuestionRecord], current_query: str, latest_response: QueryResponse, stopped_by: str, failure_reason: str | None, rag_calls: list[RagCallRecord], experiment_id: str | None, rag_model: str, followup_model: str) -> ExperimentResult` — Builds result. Receives: `*, case: PilotCase, method: Method, policy_position: str, policy_calls: int, started_at: datetime, total_started: float, questions: list[QuestionRecord], current_query: str, latest_response: QueryResponse, stopped_by: str, failure_reason: str | None, rag_calls: list[RagCallRecord], experiment_id: str | None, rag_model: str, followup_model: str`. Sends: `ExperimentResult`.
- L204 `def _get_answer_provider(*, case: PilotCase, answer_provider: AnswerProvider | None, input_fn: InputCallable, output_fn: OutputCallable) -> AnswerProvider` — Retrieves answer provider. Receives: `*, case: PilotCase, answer_provider: AnswerProvider | None, input_fn: InputCallable, output_fn: OutputCallable`. Sends: `AnswerProvider`.
- L217 `async def _decide(policy: FollowUpPolicyLike, *, original_user_content: str, exchanges: Sequence[ClarificationExchange]) -> FollowUpDecision` — Implements decide. Receives: `policy: FollowUpPolicyLike, *, original_user_content: str, exchanges: Sequence[ClarificationExchange]`. Sends: `FollowUpDecision`.
- L230 `def _record_answer(*, case: PilotCase, answer_provider: AnswerProvider, round_number: int, question: str, questions: list[QuestionRecord], exchanges: list[ClarificationExchange]) -> str` — Persists answer. Receives: `*, case: PilotCase, answer_provider: AnswerProvider, round_number: int, question: str, questions: list[QuestionRecord], exchanges: list[ClarificationExchange]`. Sends: `str`.
- L262 `async def run_no_followup(case: PilotCase, *, rag_call: RagCallable=request_rag, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model) -> ExperimentResult` — Executes no followup. Receives: `case: PilotCase, *, rag_call: RagCallable=request_rag, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model`. Sends: `ExperimentResult`.
- L297 `async def _run_post_rag_adaptive(case: PilotCase, *, method: Method, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes post rag adaptive. Receives: `case: PilotCase, *, method: Method, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS`. Sends: `ExperimentResult`.
- L396 `async def run_post_rag_adaptive(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes post rag adaptive. Receives: `case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS`. Sends: `ExperimentResult`.
- L424 `async def run_adaptive_followup(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Backward-compatible name for the historical post-RAG baseline. Receives: `case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS`. Sends: `ExperimentResult`.
- L453 `async def run_pre_rag_adaptive(case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS) -> ExperimentResult` — Executes pre rag adaptive. Receives: `case: PilotCase, *, rag_call: RagCallable=request_rag, policy: FollowUpPolicyLike | None=None, answer_provider: AnswerProvider | None=None, input_fn: InputCallable=input, output_fn: OutputCallable=print, experiment_id: str | None=None, rag_model: str='existing-rag-service', followup_model: str=settings.chat_followup_policy_model, max_rounds: int=MAX_FOLLOWUP_ROUNDS`. Sends: `ExperimentResult`.
- L566 `def save_result(result: ExperimentResult, results_dir: Path=DEFAULT_RESULTS_DIR) -> Path` — Persists result. Receives: `result: ExperimentResult, results_dir: Path=DEFAULT_RESULTS_DIR`. Sends: `Path`.
- L582 `async def run_method(case: PilotCase, method: Method, **kwargs: object) -> ExperimentResult` — Executes method. Receives: `case: PilotCase, method: Method, **kwargs: object`. Sends: `ExperimentResult`.
- L601 `def build_argument_parser() -> argparse.ArgumentParser` — Builds argument parser. Receives: `not applicable`. Sends: `argparse.ArgumentParser`.
- L618 `async def _run_cli(args: argparse.Namespace) -> list[Path]` — Executes cli. Receives: `args: argparse.Namespace`. Sends: `list[Path]`.
- L640 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`experiments/followup_pilot/schemas.py`](../../experiments/followup_pilot/schemas.py)

Purpose: Strict, serializable contracts for the follow-up pilot.

- L47 `class StrictModel(BaseModel)` — Encapsulates strictmodel. Receives: `constructor arguments and class fields`. Sends: `StrictModel`.
- L51 `class PilotCase(StrictModel)` — Encapsulates pilotcase. Receives: `constructor arguments and class fields`. Sends: `PilotCase`.
- L61 `def validate_case_contract(self) -> 'PilotCase'` — Validates case contract. Receives: `self`. Sends: `'PilotCase'`.
- L73 `class QuestionRecord(StrictModel)` — Encapsulates questionrecord. Receives: `constructor arguments and class fields`. Sends: `QuestionRecord`.
- L81 `def requested_fields_are_unique(self) -> 'QuestionRecord'` — Implements requested fields are unique. Receives: `self`. Sends: `'QuestionRecord'`.
- L87 `class RagCallRecord(StrictModel)` — Encapsulates ragcallrecord. Receives: `constructor arguments and class fields`. Sends: `RagCallRecord`.
- L94 `class ExperimentResult(StrictModel)` — Encapsulates experimentresult. Receives: `constructor arguments and class fields`. Sends: `ExperimentResult`.
- L117 `def backfill_legacy_metadata(self) -> 'ExperimentResult'` — Implements backfill legacy metadata. Receives: `self`. Sends: `'ExperimentResult'`.
- L126 `class SystemMetrics(StrictModel)` — Encapsulates systemmetrics. Receives: `constructor arguments and class fields`. Sends: `SystemMetrics`.
- L136 `class SystemEvaluation(StrictModel)` — Encapsulates systemevaluation. Receives: `constructor arguments and class fields`. Sends: `SystemEvaluation`.
- L142 `class EvaluationResult(StrictModel)` — Encapsulates evaluationresult. Receives: `constructor arguments and class fields`. Sends: `EvaluationResult`.

### [`experiments/followup_pilot/tests/__init__.py`](../../experiments/followup_pilot/tests/__init__.py)

Purpose: Offline tests for the follow-up pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/followup_pilot/tests/test_runner.py`](../../experiments/followup_pilot/tests/test_runner.py)

Purpose: Verifies runner behavior in the research and evaluation workspace.

- L49 `class FakeRag` — Encapsulates fakerag. Receives: `constructor arguments and class fields`. Sends: `FakeRag`.
- L50 `def __init__(self, answers: list[str], events: list[str] | None=None) -> None` — Implements init. Receives: `self, answers: list[str], events: list[str] | None=None`. Sends: `None`.
- L62 `async def __call__(self, query: str) -> QueryResponse` — Implements call. Receives: `self, query: str`. Sends: `QueryResponse`.
- L70 `class FakePolicy` — Encapsulates fakepolicy. Receives: `constructor arguments and class fields`. Sends: `FakePolicy`.
- L71 `def __init__(self, outcomes: list[FollowUpDecision | Exception], events: list[str] | None=None) -> None` — Implements init. Receives: `self, outcomes: list[FollowUpDecision | Exception], events: list[str] | None=None`. Sends: `None`.
- L80 `async def decide(self, *, original_user_content: str, clarification_exchanges: object) -> FollowUpDecision` — Implements decide. Receives: `self, *, original_user_content: str, clarification_exchanges: object`. Sends: `FollowUpDecision`.
- L100 `class FixedRng` — Encapsulates fixedrng. Receives: `constructor arguments and class fields`. Sends: `FixedRng`.
- L101 `def shuffle(self, values: list[ExperimentResult]) -> None` — Implements shuffle. Receives: `self, values: list[ExperimentResult]`. Sends: `None`.
- L105 `def answer_provider(answers: list[HumanAnswer])` — Implements answer provider. Receives: `answers: list[HumanAnswer]`. Sends: `inferred or None`.
- L108 `def provide(case, round_number, question)` — Implements provide. Receives: `case, round_number, question`. Sends: `inferred or None`.
- L117 `def result_for(method: str, *, analysis: str, questions: list[QuestionRecord] | None=None) -> ExperimentResult` — Implements result for. Receives: `method: str, *, analysis: str, questions: list[QuestionRecord] | None=None`. Sends: `ExperimentResult`.
- L151 `class RunnerTests(unittest.IsolatedAsyncioTestCase)` — Encapsulates runnertests. Receives: `constructor arguments and class fields`. Sends: `RunnerTests`.
- L152 `def setUp(self) -> None` — Implements setup. Receives: `self`. Sends: `None`.
- L155 `async def test_no_followup_calls_rag_once_and_never_needs_policy(self) -> None` — Implements test no followup calls rag once and never needs policy. Receives: `self`. Sends: `None`.
- L166 `async def test_adaptive_rebuilds_query_and_preserves_exchange_order(self) -> None` — Implements test adaptive rebuilds query and preserves exchange order. Receives: `self`. Sends: `None`.
- L210 `async def test_adaptive_stops_immediately_when_policy_answers(self) -> None` — Implements test adaptive stops immediately when policy answers. Receives: `self`. Sends: `None`.
- L225 `async def test_adaptive_stops_after_three_answered_rounds(self) -> None` — Implements test adaptive stops after three answered rounds. Receives: `self`. Sends: `None`.
- L250 `async def test_policy_exception_fails_open_to_latest_rag_answer(self) -> None` — Implements test policy exception fails open to latest rag answer. Receives: `self`. Sends: `None`.
- L266 `async def test_pre_rag_asks_before_any_rag_call(self) -> None` — Implements test pre rag asks before any rag call. Receives: `self`. Sends: `None`.
- L297 `async def test_insufficient_case_asks_for_material_fact_before_rag(self) -> None` — Implements test insufficient case asks for material fact before rag. Receives: `self`. Sends: `None`.
- L338 `async def test_sufficient_case_proceeds_to_rag_without_followup(self) -> None` — Implements test sufficient case proceeds to rag without followup. Receives: `self`. Sends: `None`.
- L361 `async def test_pre_rag_max_rounds_calls_rag_after_the_last_answer(self) -> None` — Implements test pre rag max rounds calls rag after the last answer. Receives: `self`. Sends: `None`.
- L388 `async def test_pre_rag_policy_failure_fails_open_to_one_rag_call(self) -> None` — Implements test pre rag policy failure fails open to one rag call. Receives: `self`. Sends: `None`.
- L405 `async def test_post_rag_baseline_keeps_rag_before_policy(self) -> None` — Implements test post rag baseline keeps rag before policy. Receives: `self`. Sends: `None`.
- L426 `def test_historical_result_files_remain_loadable(self) -> None` — Implements test historical result files remain loadable. Receives: `self`. Sends: `None`.
- L439 `async def test_result_file_contains_required_metadata(self) -> None` — Implements test result file contains required metadata. Receives: `self`. Sends: `None`.
- L454 `class EvaluatorTests(unittest.TestCase)` — Encapsulates evaluatortests. Receives: `constructor arguments and class fields`. Sends: `EvaluatorTests`.
- L455 `def setUp(self) -> None` — Implements setup. Receives: `self`. Sends: `None`.
- L458 `def test_completeness_and_manual_metrics_are_calculated(self) -> None` — Implements test completeness and manual metrics are calculated. Receives: `self`. Sends: `None`.
- L490 `def test_unknown_fallback_does_not_count_as_recovery(self) -> None` — Implements test unknown fallback does not count as recovery. Receives: `self`. Sends: `None`.
- L513 `def test_evaluator_hides_mapping_until_all_scores_are_collected(self) -> None` — Implements test evaluator hides mapping until all scores are collected. Receives: `self`. Sends: `None`.
- L517 `def fake_input(prompt: str) -> str` — Implements fake input. Receives: `prompt: str`. Sends: `str`.
- L546 `def test_fixture_hides_exactly_two_recoverable_fields(self) -> None` — Implements test fixture hides exactly two recoverable fields. Receives: `self`. Sends: `None`.

### [`experiments/representation_analysis/__init__.py`](../../experiments/representation_analysis/__init__.py)

Purpose: Isolated SEvenLLM representation analysis experiment.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/__main__.py`](../../experiments/representation_analysis/__main__.py)

Purpose: Owns main behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/analysis.py`](../../experiments/representation_analysis/analysis.py)

Purpose: Owns analysis behavior for the research and evaluation workspace.

- L12 `def analysis_record(row: dict[str, Any], condition: str, context: str, response: dict[str, Any], reused_from: str | None=None) -> dict[str, Any]` — Implements analysis record. Receives: `row: dict[str, Any], condition: str, context: str, response: dict[str, Any], reused_from: str | None=None`. Sends: `dict[str, Any]`.
- L21 `def validated_b0_cache(path: Path, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]` — Implements validated b0 cache. Receives: `path: Path, rows: list[dict[str, Any]]`. Sends: `dict[str, dict[str, Any]]`.
- L39 `def validate_shared_prompt(row: dict[str, Any], context: str) -> None` — Validates shared prompt. Receives: `row: dict[str, Any], context: str`. Sends: `None`.

### [`experiments/representation_analysis/b3.py`](../../experiments/representation_analysis/b3.py)

Purpose: Owns b3 behavior for the research and evaluation workspace.

- L26 `def build_augmented_context(raw: str, events: str) -> str` — Builds augmented context. Receives: `raw: str, events: str`. Sends: `str`.
- L31 `def validate_sources(rows: list[dict[str, Any]], source_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]` — Validates sources. Receives: `rows: list[dict[str, Any]], source_dir: Path`. Sends: `tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]`.
- L46 `def metric_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements metric stats. Receives: `records: list[dict[str, Any]], condition: str`. Sends: `dict[str, Any]`.
- L50 `def paired_stats(records: list[dict[str, Any]], left: str, right: str, metric: str) -> dict[str, Any]` — Implements paired stats. Receives: `records: list[dict[str, Any]], left: str, right: str, metric: str`. Sends: `dict[str, Any]`.
- L55 `def build_results(rows: list[dict[str, Any]], b0: dict[str, dict[str, Any]], b2: dict[str, dict[str, Any]], b3: dict[str, dict[str, Any]], source_dir: Path, model: Any) -> list[dict[str, Any]]` — Builds results. Receives: `rows: list[dict[str, Any]], b0: dict[str, dict[str, Any]], b2: dict[str, dict[str, Any]], b3: dict[str, dict[str, Any]], source_dir: Path, model: Any`. Sends: `list[dict[str, Any]]`.
- L66 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary. Receives: `records: list[dict[str, Any]], config: dict[str, Any]`. Sends: `dict[str, Any]`.
- L73 `def render_report(summary: dict[str, Any]) -> str` — Renders report. Receives: `summary: dict[str, Any]`. Sends: `str`.
- L85 `def run(args: Any) -> None` — Executes run. Receives: `args: Any`. Sends: `None`.
- L101 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`experiments/representation_analysis/cli.py`](../../experiments/representation_analysis/cli.py)

Purpose: Owns cli behavior for the research and evaluation workspace.

- L14 `def build_parser() -> argparse.ArgumentParser` — Builds parser. Receives: `not applicable`. Sends: `argparse.ArgumentParser`.
- L34 `def main(argv: list[str] | None=None) -> None` — Implements main. Receives: `argv: list[str] | None=None`. Sends: `None`.

### [`experiments/representation_analysis/constants.py`](../../experiments/representation_analysis/constants.py)

Purpose: Owns constants behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/dataset.py`](../../experiments/representation_analysis/dataset.py)

Purpose: Owns dataset behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/diagnostics.py`](../../experiments/representation_analysis/diagnostics.py)

Purpose: Owns diagnostics behavior for the research and evaluation workspace.

- L20 `def detect_source_strings(text: str) -> dict[str, list[str]]` — Implements detect source strings. Receives: `text: str`. Sends: `dict[str, list[str]]`.
- L24 `def retention_diagnostics(source: str, representation: str) -> dict[str, Any]` — Implements retention diagnostics. Receives: `source: str, representation: str`. Sends: `dict[str, Any]`.
- L34 `def case_state_surface_values(case_state: dict[str, Any]) -> list[str]` — Implements case state surface values. Receives: `case_state: dict[str, Any]`. Sends: `list[str]`.
- L37 `def visit(value: Any, key: str='') -> None` — Implements visit. Receives: `value: Any, key: str=''`. Sends: `None`.
- L50 `def possible_unsupported_surface_values(source: str, case_state: dict[str, Any]) -> list[str]` — Implements possible unsupported surface values. Receives: `source: str, case_state: dict[str, Any]`. Sends: `list[str]`.

### [`experiments/representation_analysis/gliner_adapter.py`](../../experiments/representation_analysis/gliner_adapter.py)

Purpose: Owns gliner adapter behavior for the research and evaluation workspace.

- L10 `class GlinerEventExtractor` — Encapsulates glinereventextractor. Receives: `constructor arguments and class fields`. Sends: `GlinerEventExtractor`.
- L11 `def __init__(self, model_name: str, device: str, threshold: float=0.5, model: Any=None) -> None` — Implements init. Receives: `self, model_name: str, device: str, threshold: float=0.5, model: Any=None`. Sends: `None`.
- L20 `def extract(self, source: str) -> dict[str, Any]` — Extracts extract. Receives: `self, source: str`. Sends: `dict[str, Any]`.
- L36 `def _ground_events(self, source: str, raw_events: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements ground events. Receives: `self, source: str, raw_events: Any`. Sends: `tuple[list[dict[str, Any]], list[dict[str, Any]]]`.
- L59 `def _ground_value(source: str, value: Any) -> dict[str, Any] | None` — Implements ground value. Receives: `source: str, value: Any`. Sends: `dict[str, Any] | None`.

### [`experiments/representation_analysis/production_extraction.py`](../../experiments/representation_analysis/production_extraction.py)

Purpose: Owns production extraction behavior for the research and evaluation workspace.

- L10 `def production_extraction_contract() -> dict[str, Any]` — Implements production extraction contract. Receives: `not applicable`. Sends: `dict[str, Any]`.
- L21 `async def extract_case_state(sample_id: str, source: str) -> dict[str, Any]` — Extracts case state. Receives: `sample_id: str, source: str`. Sends: `dict[str, Any]`.

### [`experiments/representation_analysis/prompting.py`](../../experiments/representation_analysis/prompting.py)

Purpose: Owns prompting behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/reporting.py`](../../experiments/representation_analysis/reporting.py)

Purpose: Owns reporting behavior for the research and evaluation workspace.

- L10 `def build_summary(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]` — Builds summary. Receives: `records: list[dict[str, Any]], config: dict[str, Any]`. Sends: `dict[str, Any]`.
- L11 `def stats(selected: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements stats. Receives: `selected: list[dict[str, Any]], condition: str`. Sends: `dict[str, Any]`.
- L34 `def failure_examples(records: list[dict[str, Any]]) -> dict[str, Any]` — Implements failure examples. Receives: `records: list[dict[str, Any]]`. Sends: `dict[str, Any]`.
- L36 `def item(record: dict[str, Any], condition: str) -> dict[str, Any]` — Implements item. Receives: `record: dict[str, Any], condition: str`. Sends: `dict[str, Any]`.
- L47 `def size_stats(records: list[dict[str, Any]], condition: str) -> dict[str, Any]` — Implements size stats. Receives: `records: list[dict[str, Any]], condition: str`. Sends: `dict[str, Any]`.
- L52 `def render_markdown(summary: dict[str, Any]) -> str` — Renders markdown. Receives: `summary: dict[str, Any]`. Sends: `str`.

### [`experiments/representation_analysis/runner.py`](../../experiments/representation_analysis/runner.py)

Purpose: Owns runner behavior for the research and evaluation workspace.

- L26 `def run_config(args: Any, manifest: dict[str, Any]) -> dict[str, Any]` — Executes config. Receives: `args: Any, manifest: dict[str, Any]`. Sends: `dict[str, Any]`.
- L38 `async def ensure_b1(rows: list[dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]` — Implements ensure b1. Receives: `rows: list[dict[str, Any]], path: Path`. Sends: `dict[str, dict[str, Any]]`.
- L54 `def ensure_b2(rows: list[dict[str, Any]], path: Path, args: Any) -> dict[str, dict[str, Any]]` — Implements ensure b2. Receives: `rows: list[dict[str, Any]], path: Path, args: Any`. Sends: `dict[str, dict[str, Any]]`.
- L68 `def ensure_analysis(rows: list[dict[str, Any]], condition: str, contexts: dict[str, str], path: Path, args: Any, cache: dict[str, dict[str, Any]] | None=None) -> dict[str, dict[str, Any]]` — Implements ensure analysis. Receives: `rows: list[dict[str, Any]], condition: str, contexts: dict[str, str], path: Path, args: Any, cache: dict[str, dict[str, Any]] | None=None`. Sends: `dict[str, dict[str, Any]]`.
- L88 `def assemble(rows: list[dict[str, Any]], analyses: dict[str, dict[str, dict[str, Any]]], extractions: dict[str, dict[str, dict[str, Any]]], model: Any) -> list[dict[str, Any]]` — Builds assemble. Receives: `rows: list[dict[str, Any]], analyses: dict[str, dict[str, dict[str, Any]]], extractions: dict[str, dict[str, dict[str, Any]]], model: Any`. Sends: `list[dict[str, Any]]`.
- L107 `def run_experiment(args: Any) -> None` — Executes experiment. Receives: `args: Any`. Sends: `None`.

### [`experiments/representation_analysis/serializers.py`](../../experiments/representation_analysis/serializers.py)

Purpose: Owns serializers behavior for the research and evaluation workspace.

- L10 `def serialize_case_state(value: dict[str, Any]) -> str` — Serializes case state. Receives: `value: dict[str, Any]`. Sends: `str`.
- L14 `def serialize_events(events: list[dict[str, Any]]) -> str` — Serializes events. Receives: `events: list[dict[str, Any]]`. Sends: `str`.
- L23 `def estimate_tokens(text: str) -> int` — Implements estimate tokens. Receives: `text: str`. Sends: `int`.

### [`experiments/representation_analysis/storage.py`](../../experiments/representation_analysis/storage.py)

Purpose: Owns storage behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/tests/__init__.py`](../../experiments/representation_analysis/tests/__init__.py)

Purpose: Defines the public package surface for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/representation_analysis/tests/test_b3.py`](../../experiments/representation_analysis/tests/test_b3.py)

Purpose: Verifies b3 behavior in the research and evaluation workspace.

- L8 `class B3ContextTests(unittest.TestCase)` — Encapsulates b3contexttests. Receives: `constructor arguments and class fields`. Sends: `B3ContextTests`.
- L9 `def test_raw_and_events_are_preserved_verbatim(self)` — Implements test raw and events are preserved verbatim. Receives: `self`. Sends: `inferred or None`.
- L17 `def test_empty_extraction_is_explicit(self)` — Implements test empty extraction is explicit. Receives: `self`. Sends: `inferred or None`.

### [`experiments/representation_analysis/tests/test_contracts.py`](../../experiments/representation_analysis/tests/test_contracts.py)

Purpose: Verifies contracts behavior in the research and evaluation workspace.

- L10 `class FakeGliner` — Encapsulates fakegliner. Receives: `constructor arguments and class fields`. Sends: `FakeGliner`.
- L11 `def extract_json(self, source, schema, **kwargs)` — Extracts json. Receives: `self, source, schema, **kwargs`. Sends: `inferred or None`.
- L15 `class ContractTests(unittest.TestCase)` — Encapsulates contracttests. Receives: `constructor arguments and class fields`. Sends: `ContractTests`.
- L16 `def test_gliner_keeps_only_exact_source_spans(self)` — Implements test gliner keeps only exact source spans. Receives: `self`. Sends: `inferred or None`.
- L24 `def test_retention_and_case_state_diagnostics(self)` — Implements test retention and case state diagnostics. Receives: `self`. Sends: `inferred or None`.

### [`experiments/semantic_verification/__init__.py`](../../experiments/semantic_verification/__init__.py)

Purpose: Offline-only synthetic semantic verification fixture construction.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/__main__.py`](../../experiments/semantic_verification/__main__.py)

Purpose: CLI entrypoint for the isolated offline benchmark.

- L20 `def _parser()` — Implements parser. Receives: `not applicable`. Sends: `inferred or None`.
- L37 `def main(argv=None)` — Implements main. Receives: `argv=None`. Sends: `inferred or None`.

### [`experiments/semantic_verification/constants.py`](../../experiments/semantic_verification/constants.py)

Purpose: Constants shared by the isolated offline benchmark package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/generator.py`](../../experiments/semantic_verification/generator.py)

Purpose: Gold-first deterministic construction of the bilingual benchmark.

- L18 `def _entity(case_id, suffix, entity_type, name)` — Implements entity. Receives: `case_id, suffix, entity_type, name`. Sends: `inferred or None`.
- L22 `def _relationship(case_id, number, subject, predicate, target, timestamp=None, certainty='reported', negated=False)` — Implements relationship. Receives: `case_id, number, subject, predicate, target, timestamp=None, certainty='reported', negated=False`. Sends: `inferred or None`.
- L31 `def _timeline(case_id, number, event_type, actor, predicate, target, timestamp, certainty='reported')` — Implements timeline. Receives: `case_id, number, event_type, actor, predicate, target, timestamp, certainty='reported'`. Sends: `inferred or None`.
- L41 `def _timestamps(case_number)` — Implements timestamps. Receives: `case_number`. Sends: `inferred or None`.
- L52 `def _gold(case_id, case_number, language, scenario)` — Implements gold. Receives: `case_id, case_number, language, scenario`. Sends: `inferred or None`.
- L109 `def _propositions(case_id, layout_index, facts_by_slot, language, gold_facts)` — Implements propositions. Receives: `case_id, layout_index, facts_by_slot, language, gold_facts`. Sends: `inferred or None`.
- L121 `def _negative_sources(error_type, facts_by_slot)` — Implements negative sources. Receives: `error_type, facts_by_slot`. Sends: `inferred or None`.
- L131 `def _pairs(case_id, case_number, language, gold_facts, facts)` — Implements pairs. Receives: `case_id, case_number, language, gold_facts, facts`. Sends: `inferred or None`.
- L153 `def generate_cases(case_count=DEFAULT_CASE_COUNT, seed=DEFAULT_SEED)` — Generates cases. Receives: `case_count=DEFAULT_CASE_COUNT, seed=DEFAULT_SEED`. Sends: `inferred or None`.
- L175 `def write_jsonl(cases, path)` — Implements write jsonl. Receives: `cases, path`. Sends: `inferred or None`.

### [`experiments/semantic_verification/rendering.py`](../../experiments/semantic_verification/rendering.py)

Purpose: Deterministic bilingual renderers and semantic corruption operators.

- L33 `def entity_map(gold_facts)` — Implements entity map. Receives: `gold_facts`. Sends: `inferred or None`.
- L37 `def semantic_signature(fact)` — Implements semantic signature. Receives: `fact`. Sends: `inferred or None`.
- L47 `def fact_edge(fact)` — Implements fact edge. Receives: `fact`. Sends: `inferred or None`.
- L53 `def _timestamp_text(timestamp, language)` — Implements timestamp text. Receives: `timestamp, language`. Sends: `inferred or None`.
- L59 `def render_fact(fact, language, gold_facts, sentence=True)` — Renders fact. Receives: `fact, language, gold_facts, sentence=True`. Sends: `inferred or None`.
- L79 `def render_proposition(proposition, facts_by_id, language, gold_facts)` — Renders proposition. Receives: `proposition, facts_by_id, language, gold_facts`. Sends: `inferred or None`.
- L98 `def normalized_claim(text)` — Implements normalized claim. Receives: `text`. Sends: `inferred or None`.
- L102 `def _alternate_entity(entity_id, gold_facts)` — Implements alternate entity. Receives: `entity_id, gold_facts`. Sends: `inferred or None`.
- L111 `def _shift_timestamp(value)` — Implements shift timestamp. Receives: `value`. Sends: `inferred or None`.
- L118 `def corrupt_fact(source_fact, error_type, gold_facts)` — Implements corrupt fact. Receives: `source_fact, error_type, gold_facts`. Sends: `inferred or None`.
- L143 `def render_corruption(source_facts, error_type, language, gold_facts)` — Renders corruption. Receives: `source_facts, error_type, language, gold_facts`. Sends: `inferred or None`.

### [`experiments/semantic_verification/reporting.py`](../../experiments/semantic_verification/reporting.py)

Purpose: Deterministic report writing for benchmark construction results.

- L7 `def summary_markdown(summary)` — Implements summary markdown. Receives: `summary`. Sends: `inferred or None`.
- L52 `def write_summary_reports(summary, json_path, markdown_path)` — Implements write summary reports. Receives: `summary, json_path, markdown_path`. Sends: `inferred or None`.

### [`experiments/semantic_verification/tests/__init__.py`](../../experiments/semantic_verification/tests/__init__.py)

Purpose: Focused tests for the offline fixture construction package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`experiments/semantic_verification/tests/test_benchmark.py`](../../experiments/semantic_verification/tests/test_benchmark.py)

Purpose: Offline integrity and tamper tests for the proposition-backed benchmark.

- L19 `def _validate_rows(rows, strict=False)` — Validates rows. Receives: `rows, strict=False`. Sends: `inferred or None`.
- L26 `class SemanticVerificationTests(unittest.TestCase)` — Encapsulates semanticverificationtests. Receives: `constructor arguments and class fields`. Sends: `SemanticVerificationTests`.
- L27 `def test_exact_counts_diversity_and_coverage(self)` — Implements test exact counts diversity and coverage. Receives: `self`. Sends: `inferred or None`.
- L45 `def test_repeatability_including_reports(self)` — Implements test repeatability including reports. Receives: `self`. Sends: `inferred or None`.
- L58 `def test_claims_have_no_label_markers(self)` — Implements test claims have no label markers. Receives: `self`. Sends: `inferred or None`.
- L64 `def test_narrative_tamper_is_rejected(self)` — Implements test narrative tamper is rejected. Receives: `self`. Sends: `inferred or None`.
- L71 `def test_absent_entity_and_timestamp_are_rejected(self)` — Implements test absent entity and timestamp are rejected. Receives: `self`. Sends: `inferred or None`.
- L89 `def test_positive_and_trivial_negative_tamper_are_rejected(self)` — Implements test positive and trivial negative tamper are rejected. Receives: `self`. Sends: `inferred or None`.
- L105 `def test_timeline_edge_without_relationship_is_rejected(self)` — Implements test timeline edge without relationship is rejected. Receives: `self`. Sends: `inferred or None`.
- L112 `def test_malformed_blank_and_duplicate_json_are_rejected(self)` — Implements test malformed blank and duplicate json are rejected. Receives: `self`. Sends: `inferred or None`.
- L126 `def test_import_and_network_isolation(self)` — Implements test import and network isolation. Receives: `self`. Sends: `inferred or None`.

### [`experiments/semantic_verification/validator.py`](../../experiments/semantic_verification/validator.py)

Purpose: Strict construction validator for the synthetic JSONL fixture.

- L11 `class _DuplicateKeyError(ValueError)` — Encapsulates duplicatekeyerror. Receives: `constructor arguments and class fields`. Sends: `_DuplicateKeyError`.
- L15 `def _reject_duplicate_keys(pairs)` — Implements reject duplicate keys. Receives: `pairs`. Sends: `inferred or None`.
- L24 `def _reject_non_finite(value)` — Implements reject non finite. Receives: `value`. Sends: `inferred or None`.
- L28 `def _record(failures, message)` — Persists record. Receives: `failures, message`. Sends: `inferred or None`.
- L33 `def _sentence_count(narrative)` — Implements sentence count. Receives: `narrative`. Sends: `inferred or None`.
- L37 `def _parse_dataset(path, failures)` — Parses dataset. Receives: `path, failures`. Sends: `inferred or None`.
- L60 `def _fact_entities(fact)` — Implements fact entities. Receives: `fact`. Sends: `inferred or None`.
- L66 `def validate_dataset(path, strict=True)` — Validates dataset. Receives: `path, strict=True`. Sends: `inferred or None`.

### [`research/attribute_first_pilot/__init__.py`](../../research/attribute_first_pilot/__init__.py)

Purpose: Attribute-First Reasoning Research Pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/attribute_first_pilot/contracts.py`](../../research/attribute_first_pilot/contracts.py)

Purpose: Domain contracts, schemas, and enums for the Attribute-First Reasoning Pilot.

- L10 `class AnswerabilityEnum(str, Enum)` — Encapsulates answerabilityenum. Receives: `constructor arguments and class fields`. Sends: `AnswerabilityEnum`.
- L16 `class QuestionTypeEnum(str, Enum)` — Encapsulates questiontypeenum. Receives: `constructor arguments and class fields`. Sends: `QuestionTypeEnum`.
- L25 `class EpistemicStateEnum(str, Enum)` — Encapsulates epistemicstateenum. Receives: `constructor arguments and class fields`. Sends: `EpistemicStateEnum`.
- L31 `class ConditionEnum(str, Enum)` — Encapsulates conditionenum. Receives: `constructor arguments and class fields`. Sends: `ConditionEnum`.
- L39 `class SentenceEvidence(BaseModel)` — A numbered sentence unit in the cybersecurity case context. Receives: `constructor arguments and class fields`. Sends: `SentenceEvidence`.
- L45 `class AttributeContract(BaseModel)` — The concise intermediate context-analysis attribute representation. Receives: `constructor arguments and class fields`. Sends: `AttributeContract`.
- L69 `class EvaluationNotes(BaseModel)` — Ground truth analytical notes for manual or deterministic verification. Receives: `constructor arguments and class fields`. Sends: `EvaluationNotes`.
- L76 `class BenchmarkItem(BaseModel)` — Single benchmark instance. Receives: `constructor arguments and class fields`. Sends: `BenchmarkItem`.
- L86 `def formatted_context(self) -> str` — Format sentences with bracketed sentence IDs. Receives: `self`. Sends: `str`.
- L91 `class BenchmarkSuite(BaseModel)` — Full benchmark suite containing all instances. Receives: `constructor arguments and class fields`. Sends: `BenchmarkSuite`.
- L98 `class ModelCallUsage(BaseModel)` — Token usage metadata for a single LLM invocation. Receives: `constructor arguments and class fields`. Sends: `ModelCallUsage`.
- L105 `class GenerationResult(BaseModel)` — Result of an answer generation call. Receives: `constructor arguments and class fields`. Sends: `GenerationResult`.
- L115 `class AttributePredictionResult(BaseModel)` — Result of an attribute prediction call. Receives: `constructor arguments and class fields`. Sends: `AttributePredictionResult`.
- L125 `class ItemRunResult(BaseModel)` — Full experimental execution records for a single benchmark item across all 3 conditions. Receives: `constructor arguments and class fields`. Sends: `ItemRunResult`.
- L138 `class PilotRunOutput(BaseModel)` — Complete serialized experiment run output. Receives: `constructor arguments and class fields`. Sends: `PilotRunOutput`.

### [`research/attribute_first_pilot/evaluator.py`](../../research/attribute_first_pilot/evaluator.py)

Purpose: Evaluation and metrics module for the Attribute-First Reasoning Research Pilot.

- L30 `def calculate_macro_f1(gold: list[str], pred: list[str], labels: list[str]) -> float` — Calculate macro-averaged F1 score over discrete categories. Receives: `gold: list[str], pred: list[str], labels: list[str]`. Sends: `float`.
- L60 `def calculate_evidence_metrics(gold_sets: list[set[str]], pred_sets: list[set[str]]) -> tuple[float, float, float]` — Calculate mean precision, recall, and F1 for relevant evidence sentence selection. Receives: `gold_sets: list[set[str]], pred_sets: list[set[str]]`. Sends: `tuple[float, float, float]`.
- L104 `class AttributeEvaluationReport` — Encapsulates attributeevaluationreport. Receives: `constructor arguments and class fields`. Sends: `AttributeEvaluationReport`.
- L123 `def evaluate_attributes(run_output: PilotRunOutput) -> AttributeEvaluationReport` — Evaluate predicted attributes against gold attributes. Receives: `run_output: PilotRunOutput`. Sends: `AttributeEvaluationReport`.
- L278 `class EfficiencyReport` — Encapsulates efficiencyreport. Receives: `constructor arguments and class fields`. Sends: `EfficiencyReport`.
- L289 `def evaluate_efficiency(run_output: PilotRunOutput) -> EfficiencyReport` — Evaluate latency and token usage across conditions. Receives: `run_output: PilotRunOutput`. Sends: `EfficiencyReport`.
- L328 `def load_manual_scores(csv_path: Path) -> dict[str, dict[str, float]]` — Parse manual scores from CSV file if filled. Receives: `csv_path: Path`. Sends: `dict[str, dict[str, float]]`.
- L371 `def generate_markdown_report(run_output: PilotRunOutput, attr_report: AttributeEvaluationReport, eff_report: EfficiencyReport, manual_scores: dict[str, dict[str, float]] | None=None) -> str` — Generate Markdown evaluation summary. Receives: `run_output: PilotRunOutput, attr_report: AttributeEvaluationReport, eff_report: EfficiencyReport, manual_scores: dict[str, dict[str, float]] | None=None`. Sends: `str`.
- L477 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/attribute_first_pilot/llm_judge.py`](../../research/attribute_first_pilot/llm_judge.py)

Purpose: LLM Judge for scoring B0, A1, and A2 downstream answers.

- L34 `class JudgeScore(BaseModel)` — Encapsulates judgescore. Receives: `constructor arguments and class fields`. Sends: `JudgeScore`.
- L93 `async def judge_single_answer(client: httpx.AsyncClient, model: str, api_key: str, context: str, question: str, expected_behavior: str, required_points: list[str], forbidden_points: list[str], candidate_answer: str, base_url: str='https://openrouter.ai/api/v1') -> JudgeScore` — Judge a single candidate answer. Receives: `client: httpx.AsyncClient, model: str, api_key: str, context: str, question: str, expected_behavior: str, required_points: list[str], forbidden_points: list[str], candidate_answer: str, base_url: str='https://openrouter.ai/api/v1'`. Sends: `JudgeScore`.
- L148 `async def run_judge_pipeline(results_path: Path, benchmark_path: Path, output_csv_path: Path, judge_model: str=DEFAULT_JUDGE_MODEL) -> None` — Run LLM judge across all items for B0, A1, and A2. Receives: `results_path: Path, benchmark_path: Path, output_csv_path: Path, judge_model: str=DEFAULT_JUDGE_MODEL`. Sends: `None`.
- L252 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/attribute_first_pilot/prompts.py`](../../research/attribute_first_pilot/prompts.py)

Purpose: Prompts and prompt builders for the Attribute-First Reasoning Pilot.

- L109 `def build_attribute_prediction_messages(context: str, question: str) -> list[dict[str, str]]` — Build messages payload for attribute prediction. Receives: `context: str, question: str`. Sends: `list[dict[str, str]]`.
- L117 `def build_direct_baseline_messages(context: str, question: str) -> list[dict[str, str]]` — Build messages payload for direct zero-shot baseline (B0). Receives: `context: str, question: str`. Sends: `list[dict[str, str]]`.
- L125 `def build_attribute_first_messages(context: str, question: str, attributes: AttributeContract | dict) -> list[dict[str, str]]` — Build messages payload for attribute-first generation (A1 and A2). Receives: `context: str, question: str, attributes: AttributeContract | dict`. Sends: `list[dict[str, str]]`.

### [`research/attribute_first_pilot/provider.py`](../../research/attribute_first_pilot/provider.py)

Purpose: LLM Provider wrapper for the Attribute-First Reasoning Pilot.

- L30 `def get_api_key() -> str` — Retrieve the OpenRouter API key from environment variables or .env. Receives: `not applicable`. Sends: `str`.
- L53 `def clean_json_text(text: str) -> str` — Strip markdown code fences and whitespace from model JSON output. Receives: `text: str`. Sends: `str`.
- L66 `class AttributePredictionError(Exception)` — Raised when the model output fails strict attribute JSON validation. Receives: `constructor arguments and class fields`. Sends: `AttributePredictionError`.
- L68 `def __init__(self, message: str, raw_text: str)` — Implements init. Receives: `self, message: str, raw_text: str`. Sends: `inferred or None`.
- L73 `class PilotLlmProvider` — OpenRouter provider for the pilot experiment. Receives: `constructor arguments and class fields`. Sends: `PilotLlmProvider`.
- L76 `def __init__(self, model: str=DEFAULT_MODEL, api_key: str | None=None, base_url: str=DEFAULT_OPENROUTER_BASE_URL, timeout: float=60.0, temperature: float=0.0, dry_run: bool=False)` — Implements init. Receives: `self, model: str=DEFAULT_MODEL, api_key: str | None=None, base_url: str=DEFAULT_OPENROUTER_BASE_URL, timeout: float=60.0, temperature: float=0.0, dry_run: bool=False`. Sends: `inferred or None`.
- L97 `async def _call_chat_completions(self, messages: list[dict[str, str]], max_tokens: int=1024, response_format: dict[str, str] | None=None) -> tuple[str, float, ModelCallUsage]` — Execute chat completion and track latency + usage. Receives: `self, messages: list[dict[str, str]], max_tokens: int=1024, response_format: dict[str, str] | None=None`. Sends: `tuple[str, float, ModelCallUsage]`.
- L162 `async def generate_answer(self, messages: list[dict[str, str]], max_tokens: int=1024) -> GenerationResult` — Generate text answer for direct or attribute-first condition. Receives: `self, messages: list[dict[str, str]], max_tokens: int=1024`. Sends: `GenerationResult`.
- L188 `async def predict_attributes(self, messages: list[dict[str, str]], max_tokens: int=512) -> AttributePredictionResult` — Predict structured attributes with strict validation. Receives: `self, messages: list[dict[str, str]], max_tokens: int=512`. Sends: `AttributePredictionResult`.

### [`research/attribute_first_pilot/runner.py`](../../research/attribute_first_pilot/runner.py)

Purpose: CLI Runner for the Attribute-First Reasoning Research Pilot.

- L35 `def load_benchmark(path: Path) -> BenchmarkSuite` — Load and validate benchmark suite. Receives: `path: Path`. Sends: `BenchmarkSuite`.
- L43 `def export_manual_scoring_template(run_output: PilotRunOutput, csv_path: Path) -> None` — Export blank manual scoring CSV template with blind/comparative answer rows. Receives: `run_output: PilotRunOutput, csv_path: Path`. Sends: `None`.
- L104 `async def run_single_item(item: BenchmarkItem, provider: PilotLlmProvider) -> ItemRunResult` — Run B0, A1 (step 1 & 2), and A2 for a single benchmark item. Receives: `item: BenchmarkItem, provider: PilotLlmProvider`. Sends: `ItemRunResult`.
- L155 `async def run_pilot(benchmark_path: Path=DEFAULT_BENCHMARK_PATH, results_dir: Path=DEFAULT_RESULTS_DIR, model: str=DEFAULT_MODEL, temperature: float=0.0, limit: int | None=None, dry_run: bool=False) -> Path` — Execute the full pilot pipeline and write results. Receives: `benchmark_path: Path=DEFAULT_BENCHMARK_PATH, results_dir: Path=DEFAULT_RESULTS_DIR, model: str=DEFAULT_MODEL, temperature: float=0.0, limit: int | None=None, dry_run: bool=False`. Sends: `Path`.
- L221 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/attribute_first_pilot/tests/__init__.py`](../../research/attribute_first_pilot/tests/__init__.py)

Purpose: Unit tests for the Attribute-First Reasoning Pilot.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/attribute_first_pilot/tests/test_pilot.py`](../../research/attribute_first_pilot/tests/test_pilot.py)

Purpose: Unit tests for the Attribute-First Reasoning Pilot components.

- L44 `def test_attribute_contract_valid()` — Test standard validation of AttributeContract. Receives: `not applicable`. Sends: `inferred or None`.
- L60 `def test_attribute_contract_invalid_enum()` — Test that invalid enums raise ValidationError. Receives: `not applicable`. Sends: `inferred or None`.
- L70 `def test_clean_json_text()` — Test stripping markdown code fences. Receives: `not applicable`. Sends: `inferred or None`.
- L77 `def test_benchmark_json_integrity()` — Validate all items in benchmark.json match the Pydantic schema. Receives: `not applicable`. Sends: `inferred or None`.
- L97 `def test_prompt_builders()` — Test that prompt builder functions construct the expected message structure. Receives: `not applicable`. Sends: `inferred or None`.
- L127 `def test_macro_f1_calculation()` — Test macro F1 calculation. Receives: `not applicable`. Sends: `inferred or None`.
- L136 `def test_evidence_metrics_calculation()` — Test evidence precision/recall/F1 calculation. Receives: `not applicable`. Sends: `inferred or None`.
- L146 `def test_runner_mock_single_item(tmp_path)` — Test executing a mock item through PilotLlmProvider dry_run. Receives: `tmp_path`. Sends: `inferred or None`.
- L177 `def test_evaluator_report_generation()` — Test evaluating mock run output and generating report. Receives: `not applicable`. Sends: `inferred or None`.

### [`research/diagnostic/run_no_rag_diagnostic.py`](../../research/diagnostic/run_no_rag_diagnostic.py)

Purpose: Run the Main Case Analysis diagnostic with RAG explicitly skipped.

- L92 `class AtomicClaim(BaseModel)` — Encapsulates atomicclaim. Receives: `constructor arguments and class fields`. Sends: `AtomicClaim`.
- L100 `class AtomicClaimsResponse(BaseModel)` — Encapsulates atomicclaimsresponse. Receives: `constructor arguments and class fields`. Sends: `AtomicClaimsResponse`.
- L106 `class ClaimAuditResponse(BaseModel)` — Encapsulates claimauditresponse. Receives: `constructor arguments and class fields`. Sends: `ClaimAuditResponse`.
- L117 `class ClaimAuditBatchResponse(BaseModel)` — Encapsulates claimauditbatchresponse. Receives: `constructor arguments and class fields`. Sends: `ClaimAuditBatchResponse`.
- L123 `class CoverageItem(BaseModel)` — Encapsulates coverageitem. Receives: `constructor arguments and class fields`. Sends: `CoverageItem`.
- L131 `class CoverageResponse(BaseModel)` — Encapsulates coverageresponse. Receives: `constructor arguments and class fields`. Sends: `CoverageResponse`.
- L141 `class StructuredCallResult` — Encapsulates structuredcallresult. Receives: `constructor arguments and class fields`. Sends: `StructuredCallResult`.
- L150 `def _json(value: object) -> str` — Implements json. Receives: `value: object`. Sends: `str`.
- L154 `def _compact_json(value: object) -> str` — Implements compact json. Receives: `value: object`. Sends: `str`.
- L158 `def _extract_text(payload: object) -> str` — Extracts text. Receives: `payload: object`. Sends: `str`.
- L177 `def _clean_json_text(value: str) -> str` — Normalizes json text. Receives: `value: str`. Sends: `str`.
- L184 `def _usage_value(usage: object, names: tuple[str, ...]) -> int | None` — Implements usage value. Receives: `usage: object, names: tuple[str, ...]`. Sends: `int | None`.
- L194 `async def _structured_call(*, model: str, system_prompt: str, user_prompt: str, output_model: type[T], max_tokens: int, timeout_seconds: float=RESEARCH_TIMEOUT_SECONDS) -> StructuredCallResult` — Implements structured call. Receives: `*, model: str, system_prompt: str, user_prompt: str, output_model: type[T], max_tokens: int, timeout_seconds: float=RESEARCH_TIMEOUT_SECONDS`. Sends: `StructuredCallResult`.
- L318 `def _claim_prompt(analysis_text: str) -> str` — Implements claim prompt. Receives: `analysis_text: str`. Sends: `str`.
- L327 `def _decompose_claims_deterministically(analysis_text: str) -> list[AtomicClaim]` — Split only generated text into auditable sentence-level claims. Receives: `analysis_text: str`. Sends: `list[AtomicClaim]`.
- L364 `def _audit_prompt(*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object]) -> str` — Implements audit prompt. Receives: `*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object]`. Sends: `str`.
- L382 `def _audit_batch_prompt(*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object]) -> str` — Implements audit batch prompt. Receives: `*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object]`. Sends: `str`.
- L400 `def _coverage_prompt(analysis_text: str, observations: list[str]) -> str` — Implements coverage prompt. Receives: `analysis_text: str, observations: list[str]`. Sends: `str`.
- L416 `def _empty_analysis_context() -> dict[str, object]` — Implements empty analysis context. Receives: `not applicable`. Sends: `dict[str, object]`.
- L420 `def _allowed_evidence_ids(case_state: dict[str, object]) -> set[str]` — Implements allowed evidence ids. Receives: `case_state: dict[str, object]`. Sends: `set[str]`.
- L431 `def _sanitize_audit(audit: ClaimAuditResponse, *, allowed_evidence_ids: set[str]) -> tuple[ClaimAuditResponse, list[str]]` — Normalizes audit. Receives: `audit: ClaimAuditResponse, *, allowed_evidence_ids: set[str]`. Sends: `tuple[ClaimAuditResponse, list[str]]`.
- L459 `def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None` — Implements write jsonl. Receives: `path: Path, records: list[dict[str, object]]`. Sends: `None`.
- L467 `def _read_cases(path: Path) -> list[dict[str, object]]` — Retrieves cases. Receives: `path: Path`. Sends: `list[dict[str, object]]`.
- L481 `def _read_jsonl_records(path: Path) -> list[dict[str, object]]` — Retrieves jsonl records. Receives: `path: Path`. Sends: `list[dict[str, object]]`.
- L493 `def _case_state_for(case: dict[str, object]) -> dict[str, object]` — Implements case state for. Receives: `case: dict[str, object]`. Sends: `dict[str, object]`.
- L501 `async def _run_claim_extraction(analysis_text: str, *, model: str) -> StructuredCallResult` — Executes claim extraction. Receives: `analysis_text: str, *, model: str`. Sends: `StructuredCallResult`.
- L515 `async def _run_one_audit(*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object], model: str) -> tuple[ClaimAuditResponse | None, StructuredCallResult, list[str]]` — Executes one audit. Receives: `*, claim: AtomicClaim, case_state: dict[str, object], analysis_context: dict[str, object], model: str`. Sends: `tuple[ClaimAuditResponse | None, StructuredCallResult, list[str]]`.
- L547 `async def _run_audits(*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object], model: str) -> list[dict[str, object]]` — Executes audits. Receives: `*, claims: list[AtomicClaim], case_state: dict[str, object], analysis_context: dict[str, object], model: str`. Sends: `list[dict[str, object]]`.
- L601 `async def _run_coverage(*, analysis_text: str, observations: list[str], model: str) -> tuple[list[dict[str, object]], StructuredCallResult]` — Executes coverage. Receives: `*, analysis_text: str, observations: list[str], model: str`. Sends: `tuple[list[dict[str, object]], StructuredCallResult]`.
- L674 `def _evidence_lookup(case_state: dict[str, object]) -> dict[str, str]` — Implements evidence lookup. Receives: `case_state: dict[str, object]`. Sends: `dict[str, str]`.
- L685 `def _percent(count: int, denominator: int) -> float` — Implements percent. Receives: `count: int, denominator: int`. Sends: `float`.
- L689 `def _aggregate(*, cases: list[dict[str, object]], analysis_records: list[dict[str, object]], claim_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], coverage_records: list[dict[str, object]], main_model: str, claim_model: str, judge_a_model: str, judge_b_model: str, second_judge_requested: bool) -> dict[str, object]` — Implements aggregate. Receives: `*, cases: list[dict[str, object]], analysis_records: list[dict[str, object]], claim_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], coverage_records: list[dict[str, object]], main_model: str, claim_model: str, judge_a_model: str, judge_b_model: str, second_judge_requested: bool`. Sends: `dict[str, object]`.
- L900 `def _report(*, summary: dict[str, object], analysis_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], cases_by_id: dict[str, dict[str, object]]) -> str` — Implements report. Receives: `*, summary: dict[str, object], analysis_records: list[dict[str, object]], audit_a_records: list[dict[str, object]], audit_b_records: list[dict[str, object]], cases_by_id: dict[str, dict[str, object]]`. Sends: `str`.
- L1068 `async def run(args: argparse.Namespace) -> int` — Executes run. Receives: `args: argparse.Namespace`. Sends: `int`.
- L1420 `def _parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.

### [`research/render_sample_report.py`](../../research/render_sample_report.py)

Purpose: Render sample CyberCase incident reports in both Thai and English (HTML & PDF).

- L21 `def build_sample_report() -> ChatReportRead` — Builds sample report. Receives: `not applicable`. Sends: `ChatReportRead`.
- L143 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/__init__.py`](../../research/sevenllm_preflight/__init__.py)

Purpose: SEvenLLM tokenizer and protocol preflight utilities.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/b2_config.py`](../../research/sevenllm_preflight/b2_config.py)

Purpose: Owns b2 config behavior for the research and evaluation workspace.

- L95 `def default_fixed_selection_path() -> Path` — Implements default fixed selection path. Receives: `not applicable`. Sends: `Path`.
- L99 `def training_defaults() -> dict[str, object]` — Implements training defaults. Receives: `not applicable`. Sends: `dict[str, object]`.

### [`research/sevenllm_preflight/b2_leakage.py`](../../research/sevenllm_preflight/b2_leakage.py)

Purpose: Owns b2 leakage behavior for the research and evaluation workspace.

- L10 `def load_fixed_benchmark_ids(path: Path) -> list[str]` — Retrieves fixed benchmark ids. Receives: `path: Path`. Sends: `list[str]`.
- L21 `def benchmark_reference(rows: list[dict[str, Any]], fixed_ids: list[str]) -> dict[str, Any]` — Implements benchmark reference. Receives: `rows: list[dict[str, Any]], fixed_ids: list[str]`. Sends: `dict[str, Any]`.
- L43 `def _overlap_details(examples: list[dict[str, Any]], reference: dict[str, Any]) -> dict[str, Any]` — Implements overlap details. Receives: `examples: list[dict[str, Any]], reference: dict[str, Any]`. Sends: `dict[str, Any]`.
- L69 `def check_leakage(splits: dict[str, list[dict[str, Any]]], benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]) -> dict[str, Any]` — Validates leakage. Receives: `splits: dict[str, list[dict[str, Any]]], benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]`. Sends: `dict[str, Any]`.

### [`research/sevenllm_preflight/b2_metrics.py`](../../research/sevenllm_preflight/b2_metrics.py)

Purpose: Owns b2 metrics behavior for the research and evaluation workspace.

- L13 `def prediction_text(record: dict[str, Any]) -> str` — Implements prediction text. Receives: `record: dict[str, Any]`. Sends: `str`.
- L20 `def parse_json_prediction(raw: str) -> Any | None` — Parses json prediction. Receives: `raw: str`. Sends: `Any | None`.
- L34 `def flatten_values(value: Any) -> list[str]` — Implements flatten values. Receives: `value: Any`. Sends: `list[str]`.
- L42 `def extraction_scores(gold: Any, prediction: Any | None) -> tuple[float, float, float]` — Implements extraction scores. Receives: `gold: Any, prediction: Any | None`. Sends: `tuple[float, float, float]`.
- L57 `def rouge_l(gold: str, prediction: str) -> float` — Implements rouge l. Receives: `gold: str, prediction: str`. Sends: `float`.
- L63 `def mean(records: list[dict[str, Any]], field: str) -> float` — Implements mean. Receives: `records: list[dict[str, Any]], field: str`. Sends: `float`.
- L67 `def grouped_mean(records: list[dict[str, Any]], group_field: str, metric_field: str) -> dict[str, float]` — Implements grouped mean. Receives: `records: list[dict[str, Any]], group_field: str, metric_field: str`. Sends: `dict[str, float]`.
- L74 `def score_rows(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]` — Implements score rows. Receives: `rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]`. Sends: `dict[str, Any]`.

### [`research/sevenllm_preflight/b2_preflight.py`](../../research/sevenllm_preflight/b2_preflight.py)

Purpose: Owns b2 preflight behavior for the research and evaluation workspace.

- L36 `def file_sha256(path: Path) -> str` — Implements file sha256. Receives: `path: Path`. Sends: `str`.
- L44 `def tokenize_lengths(tokenizer: Any, input_text: str, target_text: str) -> tuple[int, int]` — Implements tokenize lengths. Receives: `tokenizer: Any, input_text: str, target_text: str`. Sends: `tuple[int, int]`.
- L50 `def measure_examples(examples: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]` — Implements measure examples. Receives: `examples: list[dict[str, Any]], tokenizer: Any`. Sends: `list[dict[str, Any]]`.
- L58 `def length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]` — Implements length summary. Receives: `rows: list[dict[str, Any]], field: str, threshold: int`. Sends: `dict[str, Any]`.
- L82 `def category_length_summary(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]` — Implements category length summary. Receives: `rows: list[dict[str, Any]], field: str, threshold: int`. Sends: `dict[str, Any]`.
- L89 `def tokenizer_metadata(tokenizer: Any, tokenizer_source: str) -> dict[str, Any]` — Implements tokenizer metadata. Receives: `tokenizer: Any, tokenizer_source: str`. Sends: `dict[str, Any]`.
- L104 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L118 `def build_manifest(args: argparse.Namespace, filtered: list[dict[str, Any]], train: list[dict[str, Any]], validation: list[dict[str, Any]], invalid: list[dict[str, Any]], leakage: dict[str, Any], tokenizer: dict[str, Any], hard_blockers: list[str], train_path: Path, validation_path: Path) -> dict[str, Any]` — Builds manifest. Receives: `args: argparse.Namespace, filtered: list[dict[str, Any]], train: list[dict[str, Any]], validation: list[dict[str, Any]], invalid: list[dict[str, Any]], leakage: dict[str, Any], tokenizer: dict[str, Any], hard_blockers: list[str], train_path: Path, validation_path: Path`. Sends: `dict[str, Any]`.
- L224 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/b2_records.py`](../../research/sevenllm_preflight/b2_records.py)

Purpose: Owns b2 records behavior for the research and evaluation workspace.

- L16 `def load_data_file(path: Path) -> list[dict[str, Any]]` — Retrieves data file. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L31 `def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None` — Implements write jsonl. Receives: `path: Path, rows: Iterable[dict[str, Any]]`. Sends: `None`.
- L39 `def _json_text(value: Any) -> str` — Implements json text. Receives: `value: Any`. Sends: `str`.
- L45 `def instruction_text(row: dict[str, Any]) -> str` — Implements instruction text. Receives: `row: dict[str, Any]`. Sends: `str`.
- L62 `def language_for(row: dict[str, Any]) -> str` — Implements language for. Receives: `row: dict[str, Any]`. Sends: `str`.
- L81 `def source_id_for(row: dict[str, Any]) -> str | None` — Implements source id for. Receives: `row: dict[str, Any]`. Sends: `str | None`.
- L89 `def output_text(row: dict[str, Any]) -> str` — Implements output text. Receives: `row: dict[str, Any]`. Sends: `str`.
- L99 `def prompt_fingerprint(row: dict[str, Any]) -> str` — Implements prompt fingerprint. Receives: `row: dict[str, Any]`. Sends: `str`.
- L108 `def example_fingerprint(row: dict[str, Any]) -> str` — Implements example fingerprint. Receives: `row: dict[str, Any]`. Sends: `str`.
- L118 `def _fingerprint(payload: dict[str, str]) -> str` — Implements fingerprint. Receives: `payload: dict[str, str]`. Sends: `str`.
- L123 `def build_input_text(row: dict[str, Any]) -> str` — Builds input text. Receives: `row: dict[str, Any]`. Sends: `str`.
- L133 `def build_example(row: dict[str, Any], source_line: int) -> dict[str, Any]` — Builds example. Receives: `row: dict[str, Any], source_line: int`. Sends: `dict[str, Any]`.
- L154 `def filter_english_training_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements filter english training rows. Receives: `rows: list[dict[str, Any]]`. Sends: `tuple[list[dict[str, Any]], list[dict[str, Any]]]`.
- L167 `def benchmark_id_for(row: dict[str, Any]) -> str` — Implements benchmark id for. Receives: `row: dict[str, Any]`. Sends: `str`.

### [`research/sevenllm_preflight/b2_split.py`](../../research/sevenllm_preflight/b2_split.py)

Purpose: Owns b2 split behavior for the research and evaluation workspace.

- L10 `def split_examples(examples: list[dict[str, Any]], validation_ratio: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` — Implements split examples. Receives: `examples: list[dict[str, Any]], validation_ratio: float, seed: int`. Sends: `tuple[list[dict[str, Any]], list[dict[str, Any]]]`.
- L30 `def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]` — Implements category counts. Receives: `rows: list[dict[str, Any]]`. Sends: `dict[str, int]`.

### [`research/sevenllm_preflight/b2_training.py`](../../research/sevenllm_preflight/b2_training.py)

Purpose: Owns b2 training behavior for the research and evaluation workspace.

- L42 `def file_sha256(path: Path) -> str` — Implements file sha256. Receives: `path: Path`. Sends: `str`.
- L49 `def load_preflight_manifest(path: Path) -> dict[str, Any]` — Retrieves preflight manifest. Receives: `path: Path`. Sends: `dict[str, Any]`.
- L77 `def select_precision() -> dict[str, Any]` — Extracts precision. Receives: `not applicable`. Sends: `dict[str, Any]`.
- L91 `def seed_runtime(seed: int) -> None` — Implements seed runtime. Receives: `seed: int`. Sends: `None`.
- L100 `def tokenized_dataset(path: Path, tokenizer: Any, split_name: str) -> Any` — Implements tokenized dataset. Receives: `path: Path, tokenizer: Any, split_name: str`. Sends: `Any`.
- L103 `def encode(batch: dict[str, list[str]]) -> dict[str, Any]` — Serializes encode. Receives: `batch: dict[str, list[str]]`. Sends: `dict[str, Any]`.
- L120 `def latest_checkpoint(output_dir: Path) -> Path` — Implements latest checkpoint. Receives: `output_dir: Path`. Sends: `Path`.
- L129 `def warmup_steps_for(dataset_size: int, args: Any) -> int` — Implements warmup steps for. Receives: `dataset_size: int, args: Any`. Sends: `int`.
- L136 `def build_training_arguments(output_dir: Path, precision: dict[str, Any], args: Any, dataset_size: int, seed: int) -> Seq2SeqTrainingArguments` — Builds training arguments. Receives: `output_dir: Path, precision: dict[str, Any], args: Any, dataset_size: int, seed: int`. Sends: `Seq2SeqTrainingArguments`.
- L184 `def build_run_config(manifest_path: Path, output_dir: Path, precision: dict[str, Any], args: Any, resume_from_checkpoint: Path | None, warmup_steps: int, model_revision: str, seed: int) -> dict[str, Any]` — Builds run config. Receives: `manifest_path: Path, output_dir: Path, precision: dict[str, Any], args: Any, resume_from_checkpoint: Path | None, warmup_steps: int, model_revision: str, seed: int`. Sends: `dict[str, Any]`.
- L224 `def run_training(args: Any) -> dict[str, Any]` — Executes training. Receives: `args: Any`. Sends: `dict[str, Any]`.

### [`research/sevenllm_preflight/evaluate_b2_benchmark.py`](../../research/sevenllm_preflight/evaluate_b2_benchmark.py)

Purpose: Owns evaluate b2 benchmark behavior for the research and evaluation workspace.

- L31 `def file_sha256(path: Path) -> str` — Implements file sha256. Receives: `path: Path`. Sends: `str`.
- L39 `def fixed_rows(benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]) -> list[dict[str, Any]]` — Implements fixed rows. Receives: `benchmark_rows: list[dict[str, Any]], fixed_ids: list[str]`. Sends: `list[dict[str, Any]]`.
- L60 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L71 `def choose_device(value: str) -> torch.device` — Implements choose device. Receives: `value: str`. Sends: `torch.device`.
- L79 `def predict(rows: list[dict[str, Any]], model: Any, tokenizer: Any, device: torch.device, batch_size: int) -> list[dict[str, Any]]` — Implements predict. Receives: `rows: list[dict[str, Any]], model: Any, tokenizer: Any, device: torch.device, batch_size: int`. Sends: `list[dict[str, Any]]`.
- L117 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/evaluation.py`](../../research/sevenllm_preflight/evaluation.py)

Purpose: Owns evaluation behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/models.py`](../../research/sevenllm_preflight/models.py)

Purpose: Owns models behavior for the research and evaluation workspace.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`research/sevenllm_preflight/protocol.py`](../../research/sevenllm_preflight/protocol.py)

Purpose: Owns protocol behavior for the research and evaluation workspace.

- L48 `def language_for(row: dict[str, Any]) -> str` — Implements language for. Receives: `row: dict[str, Any]`. Sends: `str`.
- L52 `def format_for(row: dict[str, Any]) -> str` — Implements format for. Receives: `row: dict[str, Any]`. Sends: `str`.
- L61 `def instruction_text(row: dict[str, Any]) -> str` — Implements instruction text. Receives: `row: dict[str, Any]`. Sends: `str`.
- L71 `def _build_input(row: dict[str, Any], include_choice_marker: bool) -> str` — Builds input. Receives: `row: dict[str, Any], include_choice_marker: bool`. Sends: `str`.
- L82 `def build_mt5_input(row: dict[str, Any]) -> str` — Builds mt5 input. Receives: `row: dict[str, Any]`. Sends: `str`.
- L86 `def build_b0_prompt(row: dict[str, Any]) -> str` — Builds b0 prompt. Receives: `row: dict[str, Any]`. Sends: `str`.
- L100 `def normalize_choice_output(raw: str) -> str | None` — Normalizes choice output. Receives: `raw: str`. Sends: `str | None`.
- L108 `def gold_output_text(row: dict[str, Any]) -> str` — Implements gold output text. Receives: `row: dict[str, Any]`. Sends: `str`.
- L115 `def metadata_for(row: dict[str, Any]) -> dict[str, Any]` — Implements metadata for. Receives: `row: dict[str, Any]`. Sends: `dict[str, Any]`.

### [`research/sevenllm_preflight/run_openrouter_b0.py`](../../research/sevenllm_preflight/run_openrouter_b0.py)

Purpose: Owns run openrouter b0 behavior for the research and evaluation workspace.

- L30 `class RequestFailure(RuntimeError)` — Encapsulates requestfailure. Receives: `constructor arguments and class fields`. Sends: `RequestFailure`.
- L31 `def __init__(self, message: str, metadata: dict[str, Any]) -> None` — Implements init. Receives: `self, message: str, metadata: dict[str, Any]`. Sends: `None`.
- L36 `def utc_now() -> str` — Implements utc now. Receives: `not applicable`. Sends: `str`.
- L40 `def completed_ids(path: Path) -> set[str]` — Implements completed ids. Receives: `path: Path`. Sends: `set[str]`.
- L57 `def retry_delay(response: httpx.Response | None, attempt: int, base: float) -> float` — Implements retry delay. Receives: `response: httpx.Response | None, attempt: int, base: float`. Sends: `float`.
- L68 `def response_error(response: httpx.Response) -> str` — Implements response error. Receives: `response: httpx.Response`. Sends: `str`.
- L77 `def request_prediction(client: httpx.Client, prompt: str, sample_id: str, max_attempts: int, backoff_base: float) -> tuple[str, str, str, dict[str, Any]]` — Implements request prediction. Receives: `client: httpx.Client, prompt: str, sample_id: str, max_attempts: int, backoff_base: float`. Sends: `tuple[str, str, str, dict[str, Any]]`.
- L144 `def normalized_prediction(row: dict[str, Any], raw: str) -> str | None` — Implements normalized prediction. Receives: `row: dict[str, Any], raw: str`. Sends: `str | None`.
- L150 `def base_record(row: dict[str, Any], base_url: str, key_env: str) -> dict[str, Any]` — Implements base record. Receives: `row: dict[str, Any], base_url: str, key_env: str`. Sends: `dict[str, Any]`.
- L169 `def write_record(handle: Any, record: dict[str, Any]) -> None` — Implements write record. Receives: `handle: Any, record: dict[str, Any]`. Sends: `None`.
- L175 `def seed_records(path: Path | None, selected_ids: set[str]) -> dict[str, dict[str, Any]]` — Implements seed records. Receives: `path: Path | None, selected_ids: set[str]`. Sends: `dict[str, dict[str, Any]]`.
- L183 `def run(args: argparse.Namespace) -> None` — Executes run. Receives: `args: argparse.Namespace`. Sends: `None`.
- L226 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L243 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/run_pilot.py`](../../research/sevenllm_preflight/run_pilot.py)

Purpose: Owns run pilot behavior for the research and evaluation workspace.

- L20 `def load_rows(path: Path) -> list[dict[str, Any]]` — Retrieves rows. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L25 `def english_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]` — Implements english rows. Receives: `rows: list[dict[str, Any]]`. Sends: `list[dict[str, Any]]`.
- L34 `def tokenized_input(tokenizer: Any, prompt: str) -> dict[str, torch.Tensor]` — Implements tokenized input. Receives: `tokenizer: Any, prompt: str`. Sends: `dict[str, torch.Tensor]`.
- L43 `def load_model(model_dir: Path, device: torch.device) -> tuple[Any, Any]` — Retrieves model. Receives: `model_dir: Path, device: torch.device`. Sends: `tuple[Any, Any]`.
- L51 `def generate_prediction(tokenizer: Any, model: Any, row: dict[str, Any], device: torch.device) -> tuple[str, str, int]` — Generates prediction. Receives: `tokenizer: Any, model: Any, row: dict[str, Any], device: torch.device`. Sends: `tuple[str, str, int]`.
- L67 `def write_predictions(rows: list[dict[str, Any]], model_dir: Path, output_path: Path, device: torch.device) -> None` — Implements write predictions. Receives: `rows: list[dict[str, Any]], model_dir: Path, output_path: Path, device: torch.device`. Sends: `None`.
- L93 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L102 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/run_preflight.py`](../../research/sevenllm_preflight/run_preflight.py)

Purpose: Owns run preflight behavior for the research and evaluation workspace.

- L33 `def load_rows(path: Path) -> list[dict[str, Any]]` — Retrieves rows. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L38 `def load_json(path: Path) -> dict[str, Any]` — Retrieves json. Receives: `path: Path`. Sends: `dict[str, Any]`.
- L43 `def token_count(tokenizer: Any, text: str, add_eos: bool=True) -> int` — Implements token count. Receives: `tokenizer: Any, text: str, add_eos: bool=True`. Sends: `int`.
- L47 `def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]` — Validates rows. Receives: `rows: list[dict[str, Any]]`. Sends: `dict[str, Any]`.
- L77 `def build_records(rows: list[dict[str, Any]], tokenizer: Any) -> list[dict[str, Any]]` — Builds records. Receives: `rows: list[dict[str, Any]], tokenizer: Any`. Sends: `list[dict[str, Any]]`.
- L100 `def truncation_analysis(records: list[dict[str, Any]], limit: int) -> dict[str, Any]` — Implements truncation analysis. Receives: `records: list[dict[str, Any]], limit: int`. Sends: `dict[str, Any]`.
- L122 `def longest_records(records: list[dict[str, Any]], limit: int=20) -> list[dict[str, Any]]` — Implements longest records. Receives: `records: list[dict[str, Any]], limit: int=20`. Sends: `list[dict[str, Any]]`.
- L128 `def build_manifest(args: argparse.Namespace, tokenizer: dict[str, Any], config: dict[str, Any], validation: dict[str, Any], records: list[dict[str, Any]], input_stats: dict[str, Any], output_stats: dict[str, Any], truncation: dict[str, Any]) -> dict[str, Any]` — Builds manifest. Receives: `args: argparse.Namespace, tokenizer: dict[str, Any], config: dict[str, Any], validation: dict[str, Any], records: list[dict[str, Any]], input_stats: dict[str, Any], output_stats: dict[str, Any], truncation: dict[str, Any]`. Sends: `dict[str, Any]`.
- L190 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L201 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/score_pilot.py`](../../research/sevenllm_preflight/score_pilot.py)

Purpose: Owns score pilot behavior for the research and evaluation workspace.

- L17 `def predictions_by_id(path: Path, expected_ids: set[str], limit: int | None=None, restrict_to_ids: bool=False) -> dict[str, dict[str, Any]]` — Implements predictions by id. Receives: `path: Path, expected_ids: set[str], limit: int | None=None, restrict_to_ids: bool=False`. Sends: `dict[str, dict[str, Any]]`.
- L35 `def prediction_text(record: dict[str, Any]) -> str` — Implements prediction text. Receives: `record: dict[str, Any]`. Sends: `str`.
- L45 `def flatten_values(value: Any) -> list[str]` — Implements flatten values. Receives: `value: Any`. Sends: `list[str]`.
- L58 `def extraction_f1(gold: Any, prediction: Any) -> tuple[float, float, float]` — Implements extraction f1. Receives: `gold: Any, prediction: Any`. Sends: `tuple[float, float, float]`.
- L68 `def parse_json_prediction(raw: str) -> Any | None` — Parses json prediction. Receives: `raw: str`. Sends: `Any | None`.
- L82 `def rouge_l(gold: str, prediction: str) -> float` — Implements rouge l. Receives: `gold: str, prediction: str`. Sends: `float`.
- L88 `def english_sentences(text: str) -> list[str]` — Implements english sentences. Receives: `text: str`. Sends: `list[str]`.
- L92 `def sbert_records(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], model: SentenceTransformer) -> list[dict[str, Any]]` — Implements sbert records. Receives: `rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], model: SentenceTransformer`. Sends: `list[dict[str, Any]]`.
- L116 `def group_mean(records: list[dict[str, Any]], key: str, metric: str) -> dict[str, float]` — Implements group mean. Receives: `records: list[dict[str, Any]], key: str, metric: str`. Sends: `dict[str, float]`.
- L123 `def metric_mean(records: list[dict[str, Any]], metric: str) -> float` — Implements metric mean. Receives: `records: list[dict[str, Any]], metric: str`. Sends: `float`.
- L127 `def model_identity(predictions: dict[str, dict[str, Any]]) -> dict[str, Any]` — Implements model identity. Receives: `predictions: dict[str, dict[str, Any]]`. Sends: `dict[str, Any]`.
- L145 `def score_model(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], sbert_model: SentenceTransformer | None=None) -> dict[str, Any]` — Implements score model. Receives: `rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], sbert_model: SentenceTransformer | None=None`. Sends: `dict[str, Any]`.
- L192 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L205 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/selection.py`](../../research/sevenllm_preflight/selection.py)

Purpose: Owns selection behavior for the research and evaluation workspace.

- L10 `def load_jsonl(path: Path) -> list[dict[str, Any]]` — Retrieves jsonl. Receives: `path: Path`. Sends: `list[dict[str, Any]]`.
- L15 `def parse_category_counts(values: list[str]) -> dict[str, int] | None` — Parses category counts. Receives: `values: list[str]`. Sends: `dict[str, int] | None`.
- L35 `def selected_english(rows: list[dict[str, Any]], limit: int | None=None, category_counts: dict[str, int] | None=None) -> list[dict[str, Any]]` — Implements selected english. Receives: `rows: list[dict[str, Any]], limit: int | None=None, category_counts: dict[str, int] | None=None`. Sends: `list[dict[str, Any]]`.
- L58 `def selection_manifest(rows: list[dict[str, Any]], category_counts: dict[str, int] | None) -> dict[str, Any]` — Implements selection manifest. Receives: `rows: list[dict[str, Any]], category_counts: dict[str, int] | None`. Sends: `dict[str, Any]`.

### [`research/sevenllm_preflight/statistics.py`](../../research/sevenllm_preflight/statistics.py)

Purpose: Owns statistics behavior for the research and evaluation workspace.

- L8 `def percentile(values: list[int], probability: float) -> float` — Implements percentile. Receives: `values: list[int], probability: float`. Sends: `float`.
- L21 `def distribution(values: Iterable[int], thresholds: Iterable[int]) -> dict[str, object]` — Implements distribution. Receives: `values: Iterable[int], thresholds: Iterable[int]`. Sends: `dict[str, object]`.
- L45 `def grouped_distributions(records: list[dict[str, object]], field: str, thresholds: Iterable[int]) -> dict[str, dict[str, object]]` — Implements grouped distributions. Receives: `records: list[dict[str, object]], field: str, thresholds: Iterable[int]`. Sends: `dict[str, dict[str, object]]`.
- L53 `def grouped_output_distributions(records: list[dict[str, object]], field: str) -> dict[str, dict[str, object]]` — Implements grouped output distributions. Receives: `records: list[dict[str, object]], field: str`. Sends: `dict[str, dict[str, object]]`.

### [`research/sevenllm_preflight/tests/test_b2_contract.py`](../../research/sevenllm_preflight/tests/test_b2_contract.py)

Purpose: Verifies b2 contract behavior in the research and evaluation workspace.

- L11 `def row(category: str, source_line: int, language: str='en') -> dict[str, object]` — Implements row. Receives: `category: str, source_line: int, language: str='en'`. Sends: `dict[str, object]`.
- L22 `def test_b2_input_and_target_exclude_thought() -> None` — Implements test b2 input and target exclude thought. Receives: `not applicable`. Sends: `None`.
- L33 `def test_filter_keeps_exact_categories_and_english_only() -> None` — Implements test filter keeps exact categories and english only. Receives: `not applicable`. Sends: `None`.
- L45 `def test_split_is_deterministic_and_category_stratified() -> None` — Implements test split is deterministic and category stratified. Receives: `not applicable`. Sends: `None`.
- L63 `def test_fixed_selection_matches_existing_manifest() -> None` — Implements test fixed selection matches existing manifest. Receives: `not applicable`. Sends: `None`.
- L68 `def test_leakage_check_fails_on_prompt_overlap() -> None` — Implements test leakage check fails on prompt overlap. Receives: `not applicable`. Sends: `None`.

### [`research/sevenllm_preflight/train_b2.py`](../../research/sevenllm_preflight/train_b2.py)

Purpose: Owns train b2 behavior for the research and evaluation workspace.

- L15 `def parse_args() -> argparse.Namespace` — Parses args. Receives: `not applicable`. Sends: `argparse.Namespace`.
- L28 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

## Frontend Application

### [`frontend/src/app/case/[threadId]/[view]/page.tsx`](../../frontend/src/app/case/[threadId]/[view]/page.tsx)

Purpose: Implements the Next.js page entry for the `case/[threadId]/[view]` route segment.

- L1 `function CaseWorkspaceViewPage()` — Renders or constructs caseworkspaceviewpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/case/[threadId]/page.tsx`](../../frontend/src/app/case/[threadId]/page.tsx)

Purpose: Implements the Next.js page entry for the `case/[threadId]` route segment.

- L1 `function ThreadCasePage()` — Renders or constructs threadcasepage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/case/layout.tsx`](../../frontend/src/app/case/layout.tsx)

Purpose: Implements the Next.js layout entry for the `case` route segment.

- L5 `interface CaseLayoutProps` — Defines the structural contract for caselayoutprops. Receives: `not applicable`. Sends: `type declaration`.
- L9 `function CaseLayout({ children }: CaseLayoutProps)` — Renders or constructs caselayout. Receives: `{ children }: CaseLayoutProps`. Sends: `inferred or void`.

### [`frontend/src/app/case/page.tsx`](../../frontend/src/app/case/page.tsx)

Purpose: Implements the Next.js page entry for the `case` route segment.

- L1 `function CasePage()` — Renders or constructs casepage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/chat/page.tsx`](../../frontend/src/app/chat/[threadId]/chat/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/chat` route segment.

- L3 `interface PageProps` — Defines the structural contract for pageprops. Receives: `not applicable`. Sends: `type declaration`.
- L7 `function ThreadSpecificChatPage({ params }: PageProps)` — Renders or constructs threadspecificchatpage. Receives: `{ params }: PageProps`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/intake/page.tsx`](../../frontend/src/app/chat/[threadId]/intake/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/intake` route segment.

- L1 `function ThreadIntakePage()` — Renders or constructs threadintakepage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/materials/page.tsx`](../../frontend/src/app/chat/[threadId]/materials/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/materials` route segment.

- L1 `function ThreadMaterialsPage()` — Renders or constructs threadmaterialspage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/overview/page.tsx`](../../frontend/src/app/chat/[threadId]/overview/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/overview` route segment.

- L1 `function ThreadOverviewPage()` — Renders or constructs threadoverviewpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/page.tsx`](../../frontend/src/app/chat/[threadId]/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]` route segment.

- L1 `function ThreadChatPage()` — Renders or constructs threadchatpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/report/page.tsx`](../../frontend/src/app/chat/[threadId]/report/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/report` route segment.

- L1 `function ThreadReportPage()` — Renders or constructs threadreportpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/[threadId]/technical-context/page.tsx`](../../frontend/src/app/chat/[threadId]/technical-context/page.tsx)

Purpose: Implements the Next.js page entry for the `chat/[threadId]/technical-context` route segment.

- L1 `function ThreadTechnicalContextPage()` — Renders or constructs threadtechnicalcontextpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/chat/layout.tsx`](../../frontend/src/app/chat/layout.tsx)

Purpose: Implements the Next.js layout entry for the `chat` route segment.

- L7 `interface ChatLayoutProps` — Defines the structural contract for chatlayoutprops. Receives: `not applicable`. Sends: `type declaration`.
- L11 `function ChatLayout({ children }: ChatLayoutProps)` — Renders or constructs chatlayout. Receives: `{ children }: ChatLayoutProps`. Sends: `inferred or void`.

### [`frontend/src/app/chat/page.tsx`](../../frontend/src/app/chat/page.tsx)

Purpose: Implements the Next.js page entry for the `chat` route segment.

- L1 `function ChatPage()` — Renders or constructs chatpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx)

Purpose: Implements the Next.js layout entry for the `frontend/src/app` route segment.

- L28 `function RootLayout({ children, }: Readonly<{ children: React.ReactNode; }>)` — Renders or constructs rootlayout. Receives: `{ children, }: Readonly<{ children: React.ReactNode; }>`. Sends: `inferred or void`.

### [`frontend/src/app/login/page.tsx`](../../frontend/src/app/login/page.tsx)

Purpose: Implements the Next.js page entry for the `login` route segment.

- L3 `function LoginPage()` — Renders or constructs loginpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx)

Purpose: Implements the Next.js page entry for the `frontend/src/app` route segment.

- L5 `function Home()` — Renders or constructs home. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/app/providers.tsx`](../../frontend/src/app/providers.tsx)

Purpose: Implements the Next.js providers entry for the `frontend/src/app` route segment.

- L7 `function Providers({ children }: { children: ReactNode })` — Renders or constructs providers. Receives: `{ children }: { children: ReactNode }`. Sends: `inferred or void`.

### [`frontend/src/app/register/page.tsx`](../../frontend/src/app/register/page.tsx)

Purpose: Implements the Next.js page entry for the `register` route segment.

- L3 `function RegisterPage()` — Renders or constructs registerpage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/auth/AccountForm.tsx`](../../frontend/src/components/auth/AccountForm.tsx)

Purpose: Renders and coordinates the accountform user-interface component.

- L8 `function AccountForm({ register = false }: { register?: boolean })` — Renders or constructs accountform. Receives: `{ register = false }: { register?: boolean }`. Sends: `inferred or void`.
- L28 `getRedirectTarget(userId: string): string` — Implements getredirecttarget. Receives: `userId: string`. Sends: `string`.
- L51 `function submit(event: FormEvent<HTMLFormElement>)` — Implements submit. Receives: `event: FormEvent<HTMLFormElement>`. Sends: `inferred or void`.
- L79 `handleOAuthClick(provider: "google" | "github")` — Implements handleoauthclick. Receives: `provider: "google" | "github"`. Sends: `inferred or void`.

### [`frontend/src/components/auth/AccountGate.tsx`](../../frontend/src/components/auth/AccountGate.tsx)

Purpose: Renders and coordinates the accountgate user-interface component.

- L7 `function AccountGate({ children }: { children: ReactNode })` — Renders or constructs accountgate. Receives: `{ children }: { children: ReactNode }`. Sends: `inferred or void`.

### [`frontend/src/components/ChatWorkspace.tsx`](../../frontend/src/components/ChatWorkspace.tsx)

Purpose: Renders and coordinates the chatworkspace user-interface component.

- L23 `function ChatWorkspace()` — Renders or constructs chatworkspace. Receives: `not applicable`. Sends: `inferred or void`.
- L240 `function caseRunStatus(caseRecord: CaseRead | null): "queued" | "running" | "failed" | null` — Implements caserunstatus. Receives: `caseRecord: CaseRead | null`. Sends: `"queued" | "running" | "failed" | null`.
- L245 `function nativeThreadStatus(caseRecord: CaseRead | null, runStatus: string | null)` — Implements nativethreadstatus. Receives: `caseRecord: CaseRead | null, runStatus: string | null`. Sends: `inferred or void`.
- L251 `function caseRunPhase(status: string | null, hasResult: boolean): RunPhase` — Implements caserunphase. Receives: `status: string | null, hasResult: boolean`. Sends: `RunPhase`.

### [`frontend/src/components/ChatWorkspaceLayout.tsx`](../../frontend/src/components/ChatWorkspaceLayout.tsx)

Purpose: Renders and coordinates the chatworkspacelayout user-interface component.

- L17 `function ChatWorkspaceLayout({ activeCase, activeCaseId, chatThreadId, caseFirstMode = false, activeView, activeWorkspaceView, cases, casesLoading, casesError, creatingCase, deletingCaseId, phase, threadStatus, queryErro` — Renders or constructs chatworkspacelayout. Receives: `{ activeCase, activeCaseId, chatThreadId, caseFirstMode = false, activeView, activeWorkspaceView, cases, casesLoading, casesError, creatingCase, deletingCaseId, phase, threadStatus, queryError, input, postAnswerAction, v`. Sends: `inferred or void`.
- L72 `handleOpenChat()` — Implements handleopenchat. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/common/CaseRequiredState.tsx`](../../frontend/src/components/common/CaseRequiredState.tsx)

Purpose: Renders and coordinates the caserequiredstate user-interface component.

- L3 `interface EmptyStateCaseRequiredProps` — Defines the structural contract for emptystatecaserequiredprops. Receives: `not applicable`. Sends: `type declaration`.
- L10 `function EmptyStateCaseRequired({ title, subtitle, description, onOpenIntake, }: EmptyStateCaseRequiredProps)` — Renders or constructs emptystatecaserequired. Receives: `{ title, subtitle, description, onOpenIntake, }: EmptyStateCaseRequiredProps`. Sends: `inferred or void`.
- L40 `function EmptyChatIntakeNotice({ onOpenIntake }: { onOpenIntake: () => void })` — Renders or constructs emptychatintakenotice. Receives: `{ onOpenIntake }: { onOpenIntake: () => void }`. Sends: `inferred or void`.

### [`frontend/src/components/common/CyberCaseLogo.tsx`](../../frontend/src/components/common/CyberCaseLogo.tsx)

Purpose: Renders and coordinates the cybercaselogo user-interface component.

- L3 `function CyberCaseLogo({ size = 32 }: { size?: number })` — Renders or constructs cybercaselogo. Receives: `{ size = 32 }: { size?: number }`. Sends: `inferred or void`.

### [`frontend/src/components/common/DeleteDialog.tsx`](../../frontend/src/components/common/DeleteDialog.tsx)

Purpose: Renders and coordinates the deletedialog user-interface component.

- L6 `interface ConfirmDialogProps` — Defines the structural contract for confirmdialogprops. Receives: `not applicable`. Sends: `type declaration`.
- L19 `function ConfirmDialog({ isOpen, title, description, confirmLabel, confirmLoadingLabel, isProcessing = false, onCancel, onConfirm, titleId = "confirm-dialog-title", descriptionId = "confirm-dialog-description", }: Confir` — Renders or constructs confirmdialog. Receives: `{ isOpen, title, description, confirmLabel, confirmLoadingLabel, isProcessing = false, onCancel, onConfirm, titleId = "confirm-dialog-title", descriptionId = "confirm-dialog-description", }: ConfirmDialogProps`. Sends: `inferred or void`.
- L97 `interface DeleteCaseDialogProps` — Defines the structural contract for deletecasedialogprops. Receives: `not applicable`. Sends: `type declaration`.
- L104 `function DeleteCaseDialog({ caseRecord, isDeleting, onCancel, onConfirm, }: DeleteCaseDialogProps)` — Renders or constructs deletecasedialog. Receives: `{ caseRecord, isDeleting, onCancel, onConfirm, }: DeleteCaseDialogProps`. Sends: `inferred or void`.
- L126 `interface SignOutDialogProps` — Defines the structural contract for signoutdialogprops. Receives: `not applicable`. Sends: `type declaration`.
- L133 `function SignOutDialog({ isOpen, isSigningOut = false, onCancel, onConfirm, }: SignOutDialogProps)` — Renders or constructs signoutdialog. Receives: `{ isOpen, isSigningOut = false, onCancel, onConfirm, }: SignOutDialogProps`. Sends: `inferred or void`.

### [`frontend/src/components/common/icons.tsx`](../../frontend/src/components/common/icons.tsx)

Purpose: Renders and coordinates the icons user-interface component.

- L3 `type IconName` — Defines the type contract for iconname. Receives: `not applicable`. Sends: `type declaration`.
- L117 `interface IconProps` — Defines the structural contract for iconprops. Receives: `not applicable`. Sends: `type declaration`.
- L121 `function Icon({ name, ...props }: IconProps)` — Renders or constructs icon. Receives: `{ name, ...props }: IconProps`. Sends: `inferred or void`.

### [`frontend/src/components/common/MeaningfulErrorModal.tsx`](../../frontend/src/components/common/MeaningfulErrorModal.tsx)

Purpose: Renders and coordinates the meaningfulerrormodal user-interface component.

- L7 `interface MeaningfulErrorModalProps` — Defines the structural contract for meaningfulerrormodalprops. Receives: `not applicable`. Sends: `type declaration`.
- L14 `function MeaningfulErrorModal({ isOpen, error, onClose, onRetry, }: MeaningfulErrorModalProps)` — Renders or constructs meaningfulerrormodal. Receives: `{ isOpen, error, onClose, onRetry, }: MeaningfulErrorModalProps`. Sends: `inferred or void`.
- L29 `handleKeyDown(event: KeyboardEvent)` — Implements handlekeydown. Receives: `event: KeyboardEvent`. Sends: `inferred or void`.
- L87 `handleBackdropClick(event: React.MouseEvent<HTMLDivElement>)` — Implements handlebackdropclick. Receives: `event: React.MouseEvent<HTMLDivElement>`. Sends: `inferred or void`.

### [`frontend/src/components/common/SignOutDialog.tsx`](../../frontend/src/components/common/SignOutDialog.tsx)

Purpose: Renders and coordinates the signoutdialog user-interface component.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/components/common/StatusPill.tsx`](../../frontend/src/components/common/StatusPill.tsx)

Purpose: Renders and coordinates the statuspill user-interface component.

- L3 `type StatusPillTone` — Defines the type contract for statuspilltone. Receives: `not applicable`. Sends: `type declaration`.
- L11 `interface StatusPillProps` — Defines the structural contract for statuspillprops. Receives: `not applicable`. Sends: `type declaration`.
- L26 `function StatusPill({ children, tone = "neutral", className = "", }: StatusPillProps)` — Renders or constructs statuspill. Receives: `{ children, tone = "neutral", className = "", }: StatusPillProps`. Sends: `inferred or void`.

### [`frontend/src/components/common/types.ts`](../../frontend/src/components/common/types.ts)

Purpose: Renders and coordinates the types user-interface component.

- L1 `type RunPhase` — Defines the type contract for runphase. Receives: `not applicable`. Sends: `type declaration`.
- L9 `type WorkspaceView` — Defines the type contract for workspaceview. Receives: `not applicable`. Sends: `type declaration`.
- L16 `type WorkspaceRouteView` — Defines the type contract for workspacerouteview. Receives: `not applicable`. Sends: `type declaration`.
- L18 `function workspaceViewForRoute(view: WorkspaceRouteView): WorkspaceView` — Implements workspaceviewforroute. Receives: `view: WorkspaceRouteView`. Sends: `WorkspaceView`.

### [`frontend/src/components/common/UserProfileMenu.tsx`](../../frontend/src/components/common/UserProfileMenu.tsx)

Purpose: Renders and coordinates the userprofilemenu user-interface component.

- L8 `function UserProfileMenu()` — Renders or constructs userprofilemenu. Receives: `not applicable`. Sends: `inferred or void`.
- L13 `handleSignOut()` — Implements handlesignout. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/common/WorkspaceSectionHeader.tsx`](../../frontend/src/components/common/WorkspaceSectionHeader.tsx)

Purpose: Renders and coordinates the workspacesectionheader user-interface component.

- L3 `interface WorkspaceSectionHeaderProps` — Defines the structural contract for workspacesectionheaderprops. Receives: `not applicable`. Sends: `type declaration`.
- L11 `function WorkspaceSectionHeader({ eyebrow, title, description, headingId, aside, }: WorkspaceSectionHeaderProps)` — Renders or constructs workspacesectionheader. Receives: `{ eyebrow, title, description, headingId, aside, }: WorkspaceSectionHeaderProps`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/AnalysisEvidenceReferences.tsx`](../../frontend/src/components/conversation/AnalysisEvidenceReferences.tsx)

Purpose: Renders and coordinates the analysisevidencereferences user-interface component.

- L10 `interface AnalysisEvidenceReferencesProps` — Defines the structural contract for analysisevidencereferencesprops. Receives: `not applicable`. Sends: `type declaration`.
- L15 `function AnalysisEvidenceReferences({ analysisMessage, messages, }: AnalysisEvidenceReferencesProps)` — Renders or constructs analysisevidencereferences. Receives: `{ analysisMessage, messages, }: AnalysisEvidenceReferencesProps`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/ChatMessageMarkdown.tsx`](../../frontend/src/components/conversation/ChatMessageMarkdown.tsx)

Purpose: Renders and coordinates the chatmessagemarkdown user-interface component.

- L6 `interface ChatMessageMarkdownProps` — Defines the structural contract for chatmessagemarkdownprops. Receives: `not applicable`. Sends: `type declaration`.
- L10 `function ChatMessageMarkdown({ content }: ChatMessageMarkdownProps)` — Renders or constructs chatmessagemarkdown. Receives: `{ content }: ChatMessageMarkdownProps`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/ChatPanel.tsx`](../../frontend/src/components/conversation/ChatPanel.tsx)

Purpose: Renders and coordinates the chatpanel user-interface component.

- L11 `interface ChatPanelProps` — Defines the structural contract for chatpanelprops. Receives: `not applicable`. Sends: `type declaration`.
- L22 `function ChatPanel({ messages, input, threadStatus, phase, onInputChange, onSubmit, }: ChatPanelProps)` — Renders or constructs chatpanel. Receives: `{ messages, input, threadStatus, phase, onInputChange, onSubmit, }: ChatPanelProps`. Sends: `inferred or void`.
- L61 `interface ChatComposerProps` — Defines the structural contract for chatcomposerprops. Receives: `not applicable`. Sends: `type declaration`.
- L68 `function ChatComposer({ input, isSubmitting, onInputChange, onSubmit, }: ChatComposerProps)` — Renders or constructs chatcomposer. Receives: `{ input, isSubmitting, onInputChange, onSubmit, }: ChatComposerProps`. Sends: `inferred or void`.
- L84 `handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>)` — Implements handlekeydown. Receives: `event: KeyboardEvent<HTMLTextAreaElement>`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/ChatTranscript.tsx`](../../frontend/src/components/conversation/ChatTranscript.tsx)

Purpose: Renders and coordinates the chattranscript user-interface component.

- L16 `interface ChatTranscriptProps` — Defines the structural contract for chattranscriptprops. Receives: `not applicable`. Sends: `type declaration`.
- L21 `function ChatTranscript({ messages, isProcessing }: ChatTranscriptProps)` — Renders or constructs chattranscript. Receives: `{ messages, isProcessing }: ChatTranscriptProps`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/FollowUpActionCard.tsx`](../../frontend/src/components/conversation/FollowUpActionCard.tsx)

Purpose: Renders and coordinates the followupactioncard user-interface component.

- L5 `function FollowUpActionCard({ detail, }: { detail: ChatFollowUpGapDetail; })` — Renders or constructs followupactioncard. Receives: `{ detail, }: { detail: ChatFollowUpGapDetail; }`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/MitreCandidatePanel.tsx`](../../frontend/src/components/conversation/MitreCandidatePanel.tsx)

Purpose: Renders and coordinates the mitrecandidatepanel user-interface component.

- L3 `interface MitreCandidatePanelProps` — Defines the structural contract for mitrecandidatepanelprops. Receives: `not applicable`. Sends: `type declaration`.
- L7 `function MitreCandidatePanel({ candidates, }: MitreCandidatePanelProps)` — Renders or constructs mitrecandidatepanel. Receives: `{ candidates, }: MitreCandidatePanelProps`. Sends: `inferred or void`.

### [`frontend/src/components/conversation/WorkspaceChatPanel.tsx`](../../frontend/src/components/conversation/WorkspaceChatPanel.tsx)

Purpose: Renders and coordinates the workspacechatpanel user-interface component.

- L17 `interface WorkspaceChatPanelProps` — Defines the structural contract for workspacechatpanelprops. Receives: `not applicable`. Sends: `type declaration`.
- L32 `function WorkspaceChatPanel({ isOpen, phase, messages, visibleMessages, threadStatus, input, postAnswerAction, onViewChange, onInputChange, onPostAnswerActionChange, onSubmit, onToggleChat, }: WorkspaceChatPanelProps)` — Renders or constructs workspacechatpanel. Receives: `{ isOpen, phase, messages, visibleMessages, threadStatus, input, postAnswerAction, onViewChange, onInputChange, onPostAnswerActionChange, onSubmit, onToggleChat, }: WorkspaceChatPanelProps`. Sends: `inferred or void`.
- L52 `checkMobile()` — Implements checkmobile. Receives: `not applicable`. Sends: `inferred or void`.
- L66 `handleMouseMove(event: MouseEvent)` — Implements handlemousemove. Receives: `event: MouseEvent`. Sends: `inferred or void`.
- L73 `handleMouseUp()` — Implements handlemouseup. Receives: `not applicable`. Sends: `inferred or void`.
- L82 `handleToggleExpand()` — Implements handletoggleexpand. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/evidence/EvidenceCitationChip.tsx`](../../frontend/src/components/evidence/EvidenceCitationChip.tsx)

Purpose: Renders and coordinates the evidencecitationchip user-interface component.

- L6 `interface EvidenceCitationChipProps` — Defines the structural contract for evidencecitationchipprops. Receives: `not applicable`. Sends: `type declaration`.
- L21 `function EvidenceCitationChip({ sourceRef, sourceKey, isActive, showDocumentName = false, citationRole, onSelect, onNavigateToSource, }: EvidenceCitationChipProps)` — Renders or constructs evidencecitationchip. Receives: `{ sourceRef, sourceKey, isActive, showDocumentName = false, citationRole, onSelect, onNavigateToSource, }: EvidenceCitationChipProps`. Sends: `inferred or void`.

### [`frontend/src/components/evidence/HighlightedEvidenceText.tsx`](../../frontend/src/components/evidence/HighlightedEvidenceText.tsx)

Purpose: Renders and coordinates the highlightedevidencetext user-interface component.

- L3 `interface HighlightedEvidenceTextProps` — Defines the structural contract for highlightedevidencetextprops. Receives: `not applicable`. Sends: `type declaration`.
- L8 `function HighlightedEvidenceText({ content, exactQuote, }: HighlightedEvidenceTextProps)` — Renders or constructs highlightedevidencetext. Receives: `{ content, exactQuote, }: HighlightedEvidenceTextProps`. Sends: `inferred or void`.

### [`frontend/src/components/evidence/SourceEvidenceContent.tsx`](../../frontend/src/components/evidence/SourceEvidenceContent.tsx)

Purpose: Renders and coordinates the sourceevidencecontent user-interface component.

- L4 `function SourceEvidenceContent({ sourceRef }: { sourceRef: SourceMessageRef })` — Renders or constructs sourceevidencecontent. Receives: `{ sourceRef }: { sourceRef: SourceMessageRef }`. Sends: `inferred or void`.

### [`frontend/src/components/home/HomePage.tsx`](../../frontend/src/components/home/HomePage.tsx)

Purpose: Renders and coordinates the homepage user-interface component.

- L10 `function HomePage()` — Renders or constructs homepage. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/home/HomeSections.tsx`](../../frontend/src/components/home/HomeSections.tsx)

Purpose: Renders and coordinates the homesections user-interface component.

- L8 `type HomePillarVisual` — Defines the type contract for homepillarvisual. Receives: `not applicable`. Sends: `type declaration`.
- L10 `interface HomePillar` — Defines the structural contract for homepillar. Receives: `not applicable`. Sends: `type declaration`.
- L59 `function HomeMiniVisual({ type }: { type: HomePillarVisual })` — Renders or constructs homeminivisual. Receives: `{ type }: { type: HomePillarVisual }`. Sends: `inferred or void`.
- L115 `function HomeNavigation()` — Renders or constructs homenavigation. Receives: `not applicable`. Sends: `inferred or void`.
- L153 `function handleClickOutside(event: MouseEvent)` — Implements handleclickoutside. Receives: `event: MouseEvent`. Sends: `inferred or void`.
- L166 `handleLogout()` — Implements handlelogout. Receives: `not applicable`. Sends: `inferred or void`.
- L325 `function HomeHero()` — Renders or constructs homehero. Receives: `not applicable`. Sends: `inferred or void`.
- L397 `function HomePlatform()` — Renders or constructs homeplatform. Receives: `not applicable`. Sends: `inferred or void`.
- L447 `function HomeWorkflow()` — Renders or constructs homeworkflow. Receives: `not applicable`. Sends: `inferred or void`.
- L512 `function HomeIntelligence()` — Renders or constructs homeintelligence. Receives: `not applicable`. Sends: `inferred or void`.
- L552 `function HomeFooter()` — Renders or constructs homefooter. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/intake/CaseFirstIntakeView.tsx`](../../frontend/src/components/intake/CaseFirstIntakeView.tsx)

Purpose: Renders and coordinates the casefirstintakeview user-interface component.

- L15 `interface CaseFirstIntakeViewProps` — Defines the structural contract for casefirstintakeviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L33 `function CaseFirstIntakeView({ caseId, documents, evidence, analysisResult, run, isSubmitting, error, isUploadingDocument, admittingExtractionId, onSubmitCase, onUploadDocument, onAdmitExtraction, onOpenOverview, onOpenC` — Renders or constructs casefirstintakeview. Receives: `{ caseId, documents, evidence, analysisResult, run, isSubmitting, error, isUploadingDocument, admittingExtractionId, onSubmitCase, onUploadDocument, onAdmitExtraction, onOpenOverview, onOpenChat, onOpenMaterials, }: Case`. Sends: `inferred or void`.
- L67 `handleSubmit(event: FormEvent<HTMLFormElement>)` — Implements handlesubmit. Receives: `event: FormEvent<HTMLFormElement>`. Sends: `inferred or void`.
- L154 `function sourceLabel(kind: string): string` — Implements sourcelabel. Receives: `kind: string`. Sends: `string`.

### [`frontend/src/components/intake/CaseIntakeFiles.tsx`](../../frontend/src/components/intake/CaseIntakeFiles.tsx)

Purpose: Renders and coordinates the caseintakefiles user-interface component.

- L4 `function CaseIntakeFiles({ materials, selectedId, onSelect, children, onOpenMaterials }: { materials: IntakeMaterial[]; selectedId: string | null; onSelect: (material: IntakeMaterial) => void; children: ReactNode; onOpen` — Renders or constructs caseintakefiles. Receives: `{ materials, selectedId, onSelect, children, onOpenMaterials }: { materials: IntakeMaterial[]; selectedId: string | null; onSelect: (material: IntakeMaterial) => void; children: ReactNode; onOpenMaterials?: () => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/intake/CaseIntakeView.tsx`](../../frontend/src/components/intake/CaseIntakeView.tsx)

Purpose: Renders and coordinates the caseintakeview user-interface component.

- L20 `interface CaseIntakeViewProps` — Defines the structural contract for caseintakeviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L42 `function CaseIntakeView(props: CaseIntakeViewProps)` — Renders or constructs caseintakeview. Receives: `props: CaseIntakeViewProps`. Sends: `inferred or void`.
- L68 `function CaseIntakeContent({ caseKey, threadId, threadStatus, isSubmitting, error, onSubmitCase, messages = [], onOpenOverview, onOpenChat, onOpenMaterials, }: CaseIntakeViewProps & { caseKey: string })` — Renders or constructs caseintakecontent. Receives: `{ caseKey, threadId, threadStatus, isSubmitting, error, onSubmitCase, messages = [], onOpenOverview, onOpenChat, onOpenMaterials, }: CaseIntakeViewProps & { caseKey: string }`. Sends: `inferred or void`.
- L95 `handleSubmit(event: FormEvent<HTMLFormElement>)` — Implements handlesubmit. Receives: `event: FormEvent<HTMLFormElement>`. Sends: `inferred or void`.
- L105 `useDocument(draft: CaseNarrativeDraft)` — Implements usedocument. Receives: `draft: CaseNarrativeDraft`. Sends: `inferred or void`.
- L182 `function ExistingCaseRecord({ message, text, filename }: { message?: PersistedChatMessage; text?: string; filename?: string; })` — Renders or constructs existingcaserecord. Receives: `{ message, text, filename }: { message?: PersistedChatMessage; text?: string; filename?: string; }`. Sends: `inferred or void`.
- L199 `function ExtractedCaseSummary({ overview, sourceCount, onReview }: { overview: CaseOverviewData; sourceCount: number; onReview?: () => void; })` — Renders or constructs extractedcasesummary. Receives: `{ overview, sourceCount, onReview }: { overview: CaseOverviewData; sourceCount: number; onReview?: () => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/intake/CaseNarrativeSourceNotice.tsx`](../../frontend/src/components/intake/CaseNarrativeSourceNotice.tsx)

Purpose: Renders and coordinates the casenarrativesourcenotice user-interface component.

- L3 `function confidenceLabel(source: CaseNarrativeDocumentSource): string` — Implements confidencelabel. Receives: `source: CaseNarrativeDocumentSource`. Sends: `string`.
- L13 `function CaseNarrativeSourceNotice({ source, onRemove, }: { source: CaseNarrativeDocumentSource; onRemove: () => void; })` — Renders or constructs casenarrativesourcenotice. Receives: `{ source, onRemove, }: { source: CaseNarrativeDocumentSource; onRemove: () => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/intake/DocumentIngestionPreview.tsx`](../../frontend/src/components/intake/DocumentIngestionPreview.tsx)

Purpose: Renders and coordinates the documentingestionpreview user-interface component.

- L16 `interface DocumentIngestionPreviewProps` — Defines the structural contract for documentingestionpreviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L23 `function DocumentIngestionPreview({ caseKey = "draft", disabled = false, showResult = true, onUseAsNarrative, }: DocumentIngestionPreviewProps = {})` — Renders or constructs documentingestionpreview. Receives: `{ caseKey = "draft", disabled = false, showResult = true, onUseAsNarrative, }: DocumentIngestionPreviewProps = {}`. Sends: `inferred or void`.
- L46 `processDocument()` — Implements processdocument. Receives: `not applicable`. Sends: `inferred or void`.
- L69 `handleClear()` — Implements handleclear. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/components/intake/DocumentIngestionResult.tsx`](../../frontend/src/components/intake/DocumentIngestionResult.tsx)

Purpose: Renders and coordinates the documentingestionresult user-interface component.

- L5 `function DocumentIngestionResult({ result, onUseAsNarrative }: { result: IngestedDocumentPreview; onUseAsNarrative?: (draft: CaseNarrativeDraft) => void; })` — Renders or constructs documentingestionresult. Receives: `{ result, onUseAsNarrative }: { result: IngestedDocumentPreview; onUseAsNarrative?: (draft: CaseNarrativeDraft) => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/intake/ExtractedTextPreview.tsx`](../../frontend/src/components/intake/ExtractedTextPreview.tsx)

Purpose: Renders and coordinates the extractedtextpreview user-interface component.

- L7 `type ContentMode` — Defines the type contract for contentmode. Receives: `not applicable`. Sends: `type declaration`.
- L9 `function ExtractedTextPreview({ text, label, onEdit }: { text: string; label: string; onEdit?: (text: string) => void; })` — Renders or constructs extractedtextpreview. Receives: `{ text, label, onEdit }: { text: string; label: string; onEdit?: (text: string) => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/intake/IntakeNarrativeForm.tsx`](../../frontend/src/components/intake/IntakeNarrativeForm.tsx)

Purpose: Renders and coordinates the intakenarrativeform user-interface component.

- L8 `function IntakeNarrativeForm({ title, description, draft, result, disabled, sourceLinked, onTitle, onDescription, onUseDocument, onRemoveSource, onSubmit }: { title: string; description: string; draft: CaseNarrativeDraft` — Renders or constructs intakenarrativeform. Receives: `{ title, description, draft, result, disabled, sourceLinked, onTitle, onDescription, onUseDocument, onRemoveSource, onSubmit }: { title: string; description: string; draft: CaseNarrativeDraft | null; result: IngestedDocu`. Sends: `inferred or void`.

### [`frontend/src/components/layout/WorkspaceHeader.tsx`](../../frontend/src/components/layout/WorkspaceHeader.tsx)

Purpose: Renders and coordinates the workspaceheader user-interface component.

- L12 `interface WorkspaceHeaderProps` — Defines the structural contract for workspaceheaderprops. Receives: `not applicable`. Sends: `type declaration`.
- L37 `function WorkspaceHeader({ activeCase, activeCaseId, activeView, cases, creatingCase, deletingCaseId, phase, onViewChange, onSelectCase, onNewCase, onRequestDelete, isChatOpen = true, onToggleChat, }: WorkspaceHeaderProp` — Renders or constructs workspaceheader. Receives: `{ activeCase, activeCaseId, activeView, cases, creatingCase, deletingCaseId, phase, onViewChange, onSelectCase, onNewCase, onRequestDelete, isChatOpen = true, onToggleChat, }: WorkspaceHeaderProps`. Sends: `inferred or void`.

### [`frontend/src/components/layout/WorkspaceSidebar.tsx`](../../frontend/src/components/layout/WorkspaceSidebar.tsx)

Purpose: Renders and coordinates the workspacesidebar user-interface component.

- L14 `interface WorkspaceNavigationProps` — Defines the structural contract for workspacenavigationprops. Receives: `not applicable`. Sends: `type declaration`.
- L52 `function WorkspaceSidebar({ cases, activeCaseId, casesLoading, casesError, onSelectCase, onNewCase, onRequestDelete, deletingCaseId, activeView, onViewChange, }: WorkspaceNavigationProps)` — Renders or constructs workspacesidebar. Receives: `{ cases, activeCaseId, casesLoading, casesError, onSelectCase, onNewCase, onRequestDelete, deletingCaseId, activeView, onViewChange, }: WorkspaceNavigationProps`. Sends: `inferred or void`.
- L186 `function NavigationGroup({ label, tabs, activeView, onViewChange, }: { label: string; tabs: Array<{ view: WorkspaceView; icon: IconName }>; activeView: WorkspaceView; onViewChange: (view: WorkspaceView) => void; })` — Renders or constructs navigationgroup. Receives: `{ label, tabs, activeView, onViewChange, }: { label: string; tabs: Array<{ view: WorkspaceView; icon: IconName }>; activeView: WorkspaceView; onViewChange: (view: WorkspaceView) => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/materials/CaseMaterialsView.tsx`](../../frontend/src/components/materials/CaseMaterialsView.tsx)

Purpose: Renders and coordinates the casematerialsview user-interface component.

- L10 `interface CaseMaterialsViewProps` — Defines the structural contract for casematerialsviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L22 `function MaterialRow({ item, onOpenChat, }: { item: CaseMaterialItem; onOpenChat?: () => void; })` — Renders or constructs materialrow. Receives: `{ item, onOpenChat, }: { item: CaseMaterialItem; onOpenChat?: () => void; }`. Sends: `inferred or void`.
- L73 `function CaseMaterialsView({ messages, nativeDocuments, nativeEvidence, isUploadingDocument = false, admittingExtractionId = null, onUploadDocument, onAdmitExtraction, onOpenChat, onOpenIntake, }: CaseMaterialsViewProps)` — Renders or constructs casematerialsview. Receives: `{ messages, nativeDocuments, nativeEvidence, isUploadingDocument = false, admittingExtractionId = null, onUploadDocument, onAdmitExtraction, onOpenChat, onOpenIntake, }: CaseMaterialsViewProps`. Sends: `inferred or void`.

### [`frontend/src/components/materials/CaseNativeMaterialsView.tsx`](../../frontend/src/components/materials/CaseNativeMaterialsView.tsx)

Purpose: Renders and coordinates the casenativematerialsview user-interface component.

- L8 `interface CaseNativeMaterialsViewProps` — Defines the structural contract for casenativematerialsviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L19 `function CaseNativeMaterialsView({ documents, evidence, isUploading, admittingExtractionId, onUploadDocument, onAdmitExtraction, onOpenChat, onOpenIntake, }: CaseNativeMaterialsViewProps)` — Renders or constructs casenativematerialsview. Receives: `{ documents, evidence, isUploading, admittingExtractionId, onUploadDocument, onAdmitExtraction, onOpenChat, onOpenIntake, }: CaseNativeMaterialsViewProps`. Sends: `inferred or void`.
- L127 `function EvidenceSourceRow({ source, onOpenChat }: { source: EvidenceSourceRead; onOpenChat?: () => void })` — Renders or constructs evidencesourcerow. Receives: `{ source, onOpenChat }: { source: EvidenceSourceRead; onOpenChat?: () => void }`. Sends: `inferred or void`.
- L149 `function EmptyMaterials({ onOpenIntake }: { onOpenIntake?: () => void })` — Renders or constructs emptymaterials. Receives: `{ onOpenIntake }: { onOpenIntake?: () => void }`. Sends: `inferred or void`.
- L159 `function sourceLabel(kind: string): string` — Implements sourcelabel. Receives: `kind: string`. Sends: `string`.
- L166 `function formatBytes(bytes: number): string` — Implements formatbytes. Receives: `bytes: number`. Sends: `string`.
- L172 `function formatDate(value: string): string` — Implements formatdate. Receives: `value: string`. Sends: `string`.

### [`frontend/src/components/overview/CaseFindingsSection.tsx`](../../frontend/src/components/overview/CaseFindingsSection.tsx)

Purpose: Renders and coordinates the casefindingssection user-interface component.

- L17 `interface FindingSourceActions` — Defines the structural contract for findingsourceactions. Receives: `not applicable`. Sends: `type declaration`.
- L26 `function FindingRow({ finding, ...sourceActions }: FindingSourceActions & { finding: CaseFinding })` — Renders or constructs findingrow. Receives: `{ finding, ...sourceActions }: FindingSourceActions & { finding: CaseFinding }`. Sends: `inferred or void`.
- L58 `function SourceGroup({ sources, findingId, role, onSelectSource, onNavigateToSource, activeSourceKey }: FindingSourceActions & { sources: SourceMessageRef[]; findingId: string; role: "supporting" | "conflicting"; })` — Renders or constructs sourcegroup. Receives: `{ sources, findingId, role, onSelectSource, onNavigateToSource, activeSourceKey }: FindingSourceActions & { sources: SourceMessageRef[]; findingId: string; role: "supporting" | "conflicting"; }`. Sends: `inferred or void`.
- L75 `function CaseFindingsSection({ findings, ...sourceActions }: FindingSourceActions & { findings: CaseFinding[]; })` — Renders or constructs casefindingssection. Receives: `{ findings, ...sourceActions }: FindingSourceActions & { findings: CaseFinding[]; }`. Sends: `inferred or void`.

### [`frontend/src/components/overview/CaseOverviewHeader.tsx`](../../frontend/src/components/overview/CaseOverviewHeader.tsx)

Purpose: Renders and coordinates the caseoverviewheader user-interface component.

- L10 `interface CaseOverviewHeaderProps` — Defines the structural contract for caseoverviewheaderprops. Receives: `not applicable`. Sends: `type declaration`.
- L19 `function CaseOverviewHeader({ threadId, threadTitle, threadStatus, onOpenChat, onOpenReport, onOpenMaterials, }: CaseOverviewHeaderProps)` — Renders or constructs caseoverviewheader. Receives: `{ threadId, threadTitle, threadStatus, onOpenChat, onOpenReport, onOpenMaterials, }: CaseOverviewHeaderProps`. Sends: `inferred or void`.

### [`frontend/src/components/overview/CaseOverviewView.tsx`](../../frontend/src/components/overview/CaseOverviewView.tsx)

Purpose: Renders and coordinates the caseoverviewview user-interface component.

- L17 `function OverviewSummarySection({ summary }: { summary: string })` — Renders or constructs overviewsummarysection. Receives: `{ summary }: { summary: string }`. Sends: `inferred or void`.
- L29 `interface CaseOverviewViewProps` — Defines the structural contract for caseoverviewviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L47 `function CaseOverviewView({ threadId, threadTitle, threadStatus, messages, onOpenChat, onOpenReport, onOpenIntake, onOpenMaterials, onOpenTechnicalContext, onNavigateToSource, nativeAnalysisResult, nativeEvidenceSnapshot` — Renders or constructs caseoverviewview. Receives: `{ threadId, threadTitle, threadStatus, messages, onOpenChat, onOpenReport, onOpenIntake, onOpenMaterials, onOpenTechnicalContext, onNavigateToSource, nativeAnalysisResult, nativeEvidenceSnapshot, nativeRunStatus, nativeA`. Sends: `inferred or void`.
- L127 `handleSelectSource(sourceRef: SourceMessageRef, anchorElement: HTMLElement, sourceKey: string, citationRole?: "supporting" | "conflicting")` — Implements handleselectsource. Receives: `sourceRef: SourceMessageRef, anchorElement: HTMLElement, sourceKey: string, citationRole?: "supporting" | "conflicting"`. Sends: `inferred or void`.
- L207 `interface OverviewStateProps` — Defines the structural contract for overviewstateprops. Receives: `not applicable`. Sends: `type declaration`.
- L217 `function OverviewState({ eyebrow, title, description, actionLabel, onAction, actionIcon, processing, }: OverviewStateProps)` — Renders or constructs overviewstate. Receives: `{ eyebrow, title, description, actionLabel, onAction, actionIcon, processing, }: OverviewStateProps`. Sends: `inferred or void`.

### [`frontend/src/components/overview/MitreExplainedSimply.tsx`](../../frontend/src/components/overview/MitreExplainedSimply.tsx)

Purpose: Renders and coordinates the mitreexplainedsimply user-interface component.

- L7 `interface MitreExplainedSimplyProps` — Defines the structural contract for mitreexplainedsimplyprops. Receives: `not applicable`. Sends: `type declaration`.
- L13 `function MitreExplainedSimply({ techniques, status, onOpenTechnicalContext, }: MitreExplainedSimplyProps)` — Renders or constructs mitreexplainedsimply. Receives: `{ techniques, status, onOpenTechnicalContext, }: MitreExplainedSimplyProps`. Sends: `inferred or void`.
- L70 `function TechnicalContextNotice({ status, }: { status: "unavailable" | "no_matches"; })` — Renders or constructs technicalcontextnotice. Receives: `{ status, }: { status: "unavailable" | "no_matches"; }`. Sends: `inferred or void`.

### [`frontend/src/components/overview/OpenQuestionsSection.tsx`](../../frontend/src/components/overview/OpenQuestionsSection.tsx)

Purpose: Renders and coordinates the openquestionssection user-interface component.

- L8 `function OpenQuestionsSection({ gaps, onOpenChat }: { gaps: CaseGap[]; onOpenChat?: () => void; })` — Renders or constructs openquestionssection. Receives: `{ gaps, onOpenChat }: { gaps: CaseGap[]; onOpenChat?: () => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/overview/OverviewStatusRail.tsx`](../../frontend/src/components/overview/OverviewStatusRail.tsx)

Purpose: Renders and coordinates the overviewstatusrail user-interface component.

- L5 `function OverviewStatusRail({ messages, overview, nativeAnalysisResult, nativeEvidenceSnapshot, nativeRunStatus, }: { messages: PersistedChatMessage[]; overview: CaseOverviewData; nativeAnalysisResult?: CaseAnalysisResul` — Renders or constructs overviewstatusrail. Receives: `{ messages, overview, nativeAnalysisResult, nativeEvidenceSnapshot, nativeRunStatus, }: { messages: PersistedChatMessage[]; overview: CaseOverviewData; nativeAnalysisResult?: CaseAnalysisResultRead | null; nativeEvidence`. Sends: `inferred or void`.
- L57 `function NativeOverviewStatusRail({ overview, result, snapshot, runStatus, }: { overview: CaseOverviewData; result: CaseAnalysisResultRead | null; snapshot: CaseEvidenceSnapshotRead | null; runStatus: CaseRunRead["status` — Renders or constructs nativeoverviewstatusrail. Receives: `{ overview, result, snapshot, runStatus, }: { overview: CaseOverviewData; result: CaseAnalysisResultRead | null; snapshot: CaseEvidenceSnapshotRead | null; runStatus: CaseRunRead["status"] | null; }`. Sends: `inferred or void`.

### [`frontend/src/components/overview/SourceEvidenceDrawer.tsx`](../../frontend/src/components/overview/SourceEvidenceDrawer.tsx)

Purpose: Renders and coordinates the sourceevidencedrawer user-interface component.

- L9 `function SourceEvidenceDrawer({ sourceRef, anchorElement, citationRole, onClose, onNavigateToSource }: { sourceRef: SourceMessageRef; anchorElement: HTMLElement; citationRole?: "supporting" | "conflicting"; onClose: () =` — Renders or constructs sourceevidencedrawer. Receives: `{ sourceRef, anchorElement, citationRole, onClose, onNavigateToSource }: { sourceRef: SourceMessageRef; anchorElement: HTMLElement; citationRole?: "supporting" | "conflicting"; onClose: () => void; onNavigateToSource?: (`. Sends: `inferred or void`.

### [`frontend/src/components/overview/SourceEvidencePopover.tsx`](../../frontend/src/components/overview/SourceEvidencePopover.tsx)

Purpose: Renders and coordinates the sourceevidencepopover user-interface component.

- L10 `interface SourceEvidencePopoverProps` — Defines the structural contract for sourceevidencepopoverprops. Receives: `not applicable`. Sends: `type declaration`.
- L18 `function SourceEvidencePopover({ sourceRef, anchorElement, onClose, onNavigateToSource, citationRole, }: SourceEvidencePopoverProps)` — Renders or constructs sourceevidencepopover. Receives: `{ sourceRef, anchorElement, onClose, onNavigateToSource, citationRole, }: SourceEvidencePopoverProps`. Sends: `inferred or void`.
- L40 `updatePosition()` — Implements updateposition. Receives: `not applicable`. Sends: `inferred or void`.
- L82 `handleKeyDown(event: KeyboardEvent)` — Implements handlekeydown. Receives: `event: KeyboardEvent`. Sends: `inferred or void`.
- L89 `handlePointerDown(event: PointerEvent | MouseEvent)` — Implements handlepointerdown. Receives: `event: PointerEvent | MouseEvent`. Sends: `inferred or void`.

### [`frontend/src/components/report/CaseReportView.tsx`](../../frontend/src/components/report/CaseReportView.tsx)

Purpose: Renders and coordinates the casereportview user-interface component.

- L20 `interface CaseReportViewProps` — Defines the structural contract for casereportviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L29 `function CaseReportView({ caseId, caseTitle, analysisResult, runStatus, onOpenChat, onOpenOverview }: CaseReportViewProps)` — Renders or constructs casereportview. Receives: `{ caseId, caseTitle, analysisResult, runStatus, onOpenChat, onOpenOverview }: CaseReportViewProps`. Sends: `inferred or void`.
- L58 `handleGenerate()` — Implements handlegenerate. Receives: `not applicable`. Sends: `inferred or void`.
- L65 `handleRetry()` — Implements handleretry. Receives: `not applicable`. Sends: `inferred or void`.
- L102 `function reportRequestKey(): string` — Implements reportrequestkey. Receives: `not applicable`. Sends: `string`.
- L107 `function downloadPdf(blob: Blob, versionNumber: number): void` — Implements downloadpdf. Receives: `blob: Blob, versionNumber: number`. Sends: `void`.

### [`frontend/src/components/report/ChatReportView.tsx`](../../frontend/src/components/report/ChatReportView.tsx)

Purpose: Renders and coordinates the chatreportview user-interface component.

- L23 `interface ChatReportViewProps` — Defines the structural contract for chatreportviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L33 `function ChatReportView({ threadId, threadTitle, threadStatus, hasMessages, hasCompletedAnalysis, onOpenChat, onOpenOverview, }: ChatReportViewProps)` — Renders or constructs chatreportview. Receives: `{ threadId, threadTitle, threadStatus, hasMessages, hasCompletedAnalysis, onOpenChat, onOpenOverview, }: ChatReportViewProps`. Sends: `inferred or void`.
- L115 `handleClearReportError()` — Implements handleclearreporterror. Receives: `not applicable`. Sends: `inferred or void`.
- L120 `handleRetryReport()` — Implements handleretryreport. Receives: `not applicable`. Sends: `inferred or void`.
- L146 `handleGenerate()` — Implements handlegenerate. Receives: `not applicable`. Sends: `inferred or void`.
- L164 `handleDownloadPdf(report: ChatReportRead)` — Implements handledownloadpdf. Receives: `report: ChatReportRead`. Sends: `inferred or void`.
- L271 `function reportRequestKey(): string` — Implements reportrequestkey. Receives: `not applicable`. Sends: `string`.
- L278 `function downloadPdf(blob: Blob, versionNumber: number): void` — Implements downloadpdf. Receives: `blob: Blob, versionNumber: number`. Sends: `void`.

### [`frontend/src/components/report/PersistedReportCard.tsx`](../../frontend/src/components/report/PersistedReportCard.tsx)

Purpose: Renders and coordinates the persistedreportcard user-interface component.

- L13 `interface PersistedReportCardProps` — Defines the structural contract for persistedreportcardprops. Receives: `not applicable`. Sends: `type declaration`.
- L22 `function PersistedReportCard({ report, threadId, caseId, threadTitle, isDownloading, onDownloadPdf, }: PersistedReportCardProps)` — Renders or constructs persistedreportcard. Receives: `{ report, threadId, caseId, threadTitle, isDownloading, onDownloadPdf, }: PersistedReportCardProps`. Sends: `inferred or void`.
- L83 `function ReportPdfViewer({ threadId, caseId, reportId, title, }: { threadId?: string; caseId?: string; reportId: string; title: string; })` — Renders or constructs reportpdfviewer. Receives: `{ threadId, caseId, reportId, title, }: { threadId?: string; caseId?: string; reportId: string; title: string; }`. Sends: `inferred or void`.
- L207 `function ReportFailure({ report }: { report: ChatReportRead })` — Renders or constructs reportfailure. Receives: `{ report }: { report: ChatReportRead }`. Sends: `inferred or void`.

### [`frontend/src/components/report/ReportEmptyState.tsx`](../../frontend/src/components/report/ReportEmptyState.tsx)

Purpose: Renders and coordinates the reportemptystate user-interface component.

- L1 `interface ReportEmptyStateProps` — Defines the structural contract for reportemptystateprops. Receives: `not applicable`. Sends: `type declaration`.
- L5 `function ReportEmptyState({ onReturn }: ReportEmptyStateProps)` — Renders or constructs reportemptystate. Receives: `{ onReturn }: ReportEmptyStateProps`. Sends: `inferred or void`.

### [`frontend/src/components/report/ReportHistory.tsx`](../../frontend/src/components/report/ReportHistory.tsx)

Purpose: Renders and coordinates the reporthistory user-interface component.

- L4 `interface ReportVersionSelectorProps` — Defines the structural contract for reportversionselectorprops. Receives: `not applicable`. Sends: `type declaration`.
- L10 `function ReportVersionSelector({ reports, selectedReportId, onSelect, }: ReportVersionSelectorProps)` — Renders or constructs reportversionselector. Receives: `{ reports, selectedReportId, onSelect, }: ReportVersionSelectorProps`. Sends: `inferred or void`.
- L46 `function NoSavedReport({ canGenerate, isGenerating, onGenerate, onOpenOverview, }: { canGenerate: boolean; isGenerating: boolean; onGenerate: () => void; onOpenOverview?: () => void; })` — Renders or constructs nosavedreport. Receives: `{ canGenerate, isGenerating, onGenerate, onOpenOverview, }: { canGenerate: boolean; isGenerating: boolean; onGenerate: () => void; onOpenOverview?: () => void; }`. Sends: `inferred or void`.

### [`frontend/src/components/technical/TechnicalContextView.tsx`](../../frontend/src/components/technical/TechnicalContextView.tsx)

Purpose: Renders and coordinates the technicalcontextview user-interface component.

- L10 `interface TechnicalContextViewProps` — Defines the structural contract for technicalcontextviewprops. Receives: `not applicable`. Sends: `type declaration`.
- L16 `function TechnicalItem({ item, onSelectSource, activeSourceKey, }: { item: TechnicalContextCard; onSelectSource: (source: SourceMessageRef, element: HTMLElement, key: string) => void; activeSourceKey: string | null; })` — Renders or constructs technicalitem. Receives: `{ item, onSelectSource, activeSourceKey, }: { item: TechnicalContextCard; onSelectSource: (source: SourceMessageRef, element: HTMLElement, key: string) => void; activeSourceKey: string | null; }`. Sends: `inferred or void`.
- L99 `function TechnicalContextView({ messages, onOpenIntake, onNavigateToSource, }: TechnicalContextViewProps)` — Renders or constructs technicalcontextview. Receives: `{ messages, onOpenIntake, onNavigateToSource, }: TechnicalContextViewProps`. Sends: `inferred or void`.
- L111 `handleSelectSource(source: SourceMessageRef, element: HTMLElement, key: string)` — Implements handleselectsource. Receives: `source: SourceMessageRef, element: HTMLElement, key: string`. Sends: `inferred or void`.
- L121 `handleClosePopover()` — Implements handleclosepopover. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/features/chat/routing/chat-route.ts`](../../frontend/src/features/chat/routing/chat-route.ts)

Purpose: Owns chat route behavior for the frontend application.

- L3 `interface ChatRouteState` — Defines the structural contract for chatroutestate. Receives: `not applicable`. Sends: `type declaration`.
- L8 `function decodeCaseId(segment: string): string` — Implements decodecaseid. Receives: `segment: string`. Sends: `string`.
- L16 `function chatRouteState(pathname: string): ChatRouteState` — Implements chatroutestate. Receives: `pathname: string`. Sends: `ChatRouteState`.
- L38 `function casePath(caseId: string, view: WorkspaceRouteView): string` — Implements casepath. Receives: `caseId: string, view: WorkspaceRouteView`. Sends: `string`.

### [`frontend/src/features/chat/runs/chat-polling.ts`](../../frontend/src/features/chat/runs/chat-polling.ts)

Purpose: Owns chat polling behavior for the frontend application.

- L5 `function waitForNextChatPoll(signal: AbortSignal): Promise<void>` — Implements waitfornextchatpoll. Receives: `signal: AbortSignal`. Sends: `Promise<void>`.
- L11 `finish()` — Implements finish. Receives: `not applicable`. Sends: `inferred or void`.
- L21 `function isChatRequestCanceled(signal: AbortSignal, error: unknown): boolean` — Implements ischatrequestcanceled. Receives: `signal: AbortSignal, error: unknown`. Sends: `boolean`.
- L28 `interface ChatPollingOptions` — Defines the structural contract for chatpollingoptions. Receives: `not applicable`. Sends: `type declaration`.
- L37 `function pollChatThreadUntilSettled({ threadId, runId, signal, isCurrent, readThread, applyThreadDetail, }: ChatPollingOptions): Promise<ChatThreadDetail | null>` — Implements pollchatthreaduntilsettled. Receives: `{ threadId, runId, signal, isCurrent, readThread, applyThreadDetail, }: ChatPollingOptions`. Sends: `Promise<ChatThreadDetail | null>`.

### [`frontend/src/features/chat/runs/use-chat-submission.ts`](../../frontend/src/features/chat/runs/use-chat-submission.ts)

Purpose: Owns use chat submission behavior for the frontend application.

- L14 `interface UseChatSubmissionOptions` — Defines the structural contract for usechatsubmissionoptions. Receives: `not applicable`. Sends: `type declaration`.
- L25 `function useChatSubmission({ session, cases, upsertCase, createCase, ensureChat, updateCase, router, casePath, }: UseChatSubmissionOptions)` — Implements usechatsubmission. Receives: `{ session, cases, upsertCase, createCase, ensureChat, updateCase, router, casePath, }: UseChatSubmissionOptions`. Sends: `inferred or void`.

### [`frontend/src/features/chat/workspace/chat-retry-request.ts`](../../frontend/src/features/chat/workspace/chat-retry-request.ts)

Purpose: Owns chat retry request behavior for the frontend application.

- L4 `function restoreInterruptedSubmission(detail: ChatThreadDetail): PendingChatSubmission | null` — Implements restoreinterruptedsubmission. Receives: `detail: ChatThreadDetail`. Sends: `PendingChatSubmission | null`.

### [`frontend/src/features/chat/workspace/chat-workspace-types.ts`](../../frontend/src/features/chat/workspace/chat-workspace-types.ts)

Purpose: Owns chat workspace types behavior for the frontend application.

- L22 `interface PendingChatSubmission` — Defines the structural contract for pendingchatsubmission. Receives: `not applicable`. Sends: `type declaration`.
- L33 `interface ChatWorkspaceLayoutProps` — Defines the structural contract for chatworkspacelayoutprops. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/features/chat/workspace/use-chat-draft.ts`](../../frontend/src/features/chat/workspace/use-chat-draft.ts)

Purpose: Owns use chat draft behavior for the frontend application.

- L15 `interface ChatDraftState` — Defines the structural contract for chatdraftstate. Receives: `not applicable`. Sends: `type declaration`.
- L28 `function phaseForThread(detail: ChatThreadDetail | undefined): RunPhase` — Implements phaseforthread. Receives: `detail: ChatThreadDetail | undefined`. Sends: `RunPhase`.
- L36 `function useChatDraft()` — Implements usechatdraft. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/features/chat/workspace/use-chat-thread-deletion.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-deletion.ts)

Purpose: Owns use chat thread deletion behavior for the frontend application.

- L9 `interface UseChatThreadDeletionOptions` — Defines the structural contract for usechatthreaddeletionoptions. Receives: `not applicable`. Sends: `type declaration`.
- L22 `function useChatThreadDeletion({ session, deleteCandidate, deletingCaseId, activeView, cases, activeCaseId = null, isChatOpen = true, deleteCase, router, setDeleteCandidate, }: UseChatThreadDeletionOptions)` — Implements usechatthreaddeletion. Receives: `{ session, deleteCandidate, deletingCaseId, activeView, cases, activeCaseId = null, isChatOpen = true, deleteCase, router, setDeleteCandidate, }: UseChatThreadDeletionOptions`. Sends: `inferred or void`.

### [`frontend/src/features/chat/workspace/use-chat-thread-selection.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-selection.ts)

Purpose: Owns use chat thread selection behavior for the frontend application.

- L13 `interface ChatSelection` — Defines the structural contract for chatselection. Receives: `not applicable`. Sends: `type declaration`.
- L18 `function readChatThreadDetail(threadId: string, signal: AbortSignal)` — Implements readchatthreaddetail. Receives: `threadId: string, signal: AbortSignal`. Sends: `inferred or void`.
- L23 `function useChatThreadSelection({ cacheUpsertThread, }: { cacheUpsertThread: (thread: ChatThreadRead) => void })` — Implements usechatthreadselection. Receives: `{ cacheUpsertThread, }: { cacheUpsertThread: (thread: ChatThreadRead) => void }`. Sends: `inferred or void`.
- L169 `type ChatSession` — Defines the type contract for chatsession. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/features/chat/workspace/use-workspace-submission-actions.ts`](../../frontend/src/features/chat/workspace/use-workspace-submission-actions.ts)

Purpose: Owns use workspace submission actions behavior for the frontend application.

- L11 `type SubmitContent` — Defines the type contract for submitcontent. Receives: `not applicable`. Sends: `type declaration`.
- L19 `interface WorkspaceSubmissionActionsOptions` — Defines the structural contract for workspacesubmissionactionsoptions. Receives: `not applicable`. Sends: `type declaration`.
- L28 `function useWorkspaceSubmissionActions({ session, displayFollowUp, router, submitContent, updateCase, setActiveView, }: WorkspaceSubmissionActionsOptions)` — Implements useworkspacesubmissionactions. Receives: `{ session, displayFollowUp, router, submitContent, updateCase, setActiveView, }: WorkspaceSubmissionActionsOptions`. Sends: `inferred or void`.

### [`frontend/src/hooks/use-account-state.ts`](../../frontend/src/hooks/use-account-state.ts)

Purpose: Owns use account state behavior for the frontend application.

- L6 `function useAccountState(key: string, initial: T)` — Implements useaccountstate. Receives: `key: string, initial: T`. Sends: `inferred or void`.

### [`frontend/src/hooks/use-auth.ts`](../../frontend/src/hooks/use-auth.ts)

Purpose: Owns use auth behavior for the frontend application.

- L18 `function useAuth()` — Implements useauth. Receives: `not applicable`. Sends: `inferred or void`.
- L43 `sync(event: StorageEvent)` — Implements sync. Receives: `event: StorageEvent`. Sends: `inferred or void`.
- L69 `loginWithOAuth(provider: "google" | "github")` — Implements loginwithoauth. Receives: `provider: "google" | "github"`. Sends: `inferred or void`.

### [`frontend/src/hooks/use-case-queries.ts`](../../frontend/src/hooks/use-case-queries.ts)

Purpose: Owns use case queries behavior for the frontend application.

- L40 `function sortCases(cases: CaseRead[]): CaseRead[]` — Implements sortcases. Receives: `cases: CaseRead[]`. Sends: `CaseRead[]`.
- L46 `function useCaseWorkspaceQueries(caseId: string | null)` — Implements usecaseworkspacequeries. Receives: `caseId: string | null`. Sends: `inferred or void`.
- L83 `function caseFromChatThread(thread: ChatThreadRead): CaseRead` — Implements casefromchatthread. Receives: `thread: ChatThreadRead`. Sends: `CaseRead`.
- L95 `function useCases()` — Implements usecases. Receives: `not applicable`. Sends: `inferred or void`.
- L103 `function useCaseMutations()` — Implements usecasemutations. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/hooks/use-case-run-polling.ts`](../../frontend/src/hooks/use-case-run-polling.ts)

Purpose: Owns use case run polling behavior for the frontend application.

- L9 `function useCaseRunPolling(caseId: string | null, runId: string | null | undefined, chatThreadId: string | null | undefined)` — Implements usecaserunpolling. Receives: `caseId: string | null, runId: string | null | undefined, chatThreadId: string | null | undefined`. Sends: `inferred or void`.

### [`frontend/src/hooks/use-case-workspace-actions.ts`](../../frontend/src/hooks/use-case-workspace-actions.ts)

Purpose: Owns use case workspace actions behavior for the frontend application.

- L21 `interface UseCaseWorkspaceActionsOptions` — Defines the structural contract for usecaseworkspaceactionsoptions. Receives: `not applicable`. Sends: `type declaration`.
- L33 `function useCaseWorkspaceActions({ activeCaseId, activeCase, isChatOpen, setIsChatOpen, session, upsertCase, updateCase, router, setActiveView, }: UseCaseWorkspaceActionsOptions)` — Implements usecaseworkspaceactions. Receives: `{ activeCaseId, activeCase, isChatOpen, setIsChatOpen, session, upsertCase, updateCase, router, setActiveView, }: UseCaseWorkspaceActionsOptions`. Sends: `inferred or void`.
- L164 `function createIdempotencyKey(): string` — Implements createidempotencykey. Receives: `not applicable`. Sends: `string`.

### [`frontend/src/hooks/use-chat-queries.ts`](../../frontend/src/hooks/use-chat-queries.ts)

Purpose: Owns use chat queries behavior for the frontend application.

- L25 `function sortThreads(threads: ChatThreadRead[]): ChatThreadRead[]` — Implements sortthreads. Receives: `threads: ChatThreadRead[]`. Sends: `ChatThreadRead[]`.
- L31 `function useChatThreads()` — Implements usechatthreads. Receives: `not applicable`. Sends: `inferred or void`.
- L39 `function useChatThreadMutations()` — Implements usechatthreadmutations. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/lib/account-storage.ts`](../../frontend/src/lib/account-storage.ts)

Purpose: Owns account storage behavior for the frontend application.

- L1 `function accountStorageKey(key: string): string` — Implements accountstoragekey. Receives: `key: string`. Sends: `string`.
- L6 `function readAccountValue(key: string): string | null` — Implements readaccountvalue. Receives: `key: string`. Sends: `string | null`.
- L11 `function writeAccountValue(key: string, value: string): void` — Implements writeaccountvalue. Receives: `key: string, value: string`. Sends: `void`.

### [`frontend/src/lib/analysis-citations.ts`](../../frontend/src/lib/analysis-citations.ts)

Purpose: Owns analysis citations behavior for the frontend application.

- L11 `interface AnalysisSourceReference` — Defines the structural contract for analysissourcereference. Receives: `not applicable`. Sends: `type declaration`.
- L16 `function sourceReferencesForAnalysisMessage(analysisMessage: PersistedChatMessage, messages: PersistedChatMessage[]): AnalysisSourceReference[]` — Implements sourcereferencesforanalysismessage. Receives: `analysisMessage: PersistedChatMessage, messages: PersistedChatMessage[]`. Sends: `AnalysisSourceReference[]`.

### [`frontend/src/lib/api-client.ts`](../../frontend/src/lib/api-client.ts)

Purpose: Owns api client behavior for the frontend application.

- L20 `function getApiBaseUrl(): string` — Implements getapibaseurl. Receives: `not applicable`. Sends: `string`.
- L42 `listChatThreads(signal?: AbortSignal): Promise<ChatThreadRead[]>` — Implements listchatthreads. Receives: `signal?: AbortSignal`. Sends: `Promise<ChatThreadRead[]>`.
- L51 `createChatThread(title: string = "New case", signal?: AbortSignal): Promise<ChatThreadRead>` — Implements createchatthread. Receives: `title: string = "New case", signal?: AbortSignal`. Sends: `Promise<ChatThreadRead>`.
- L63 `getChatThread(threadId: string, signal?: AbortSignal): Promise<ChatThreadDetail>` — Implements getchatthread. Receives: `threadId: string, signal?: AbortSignal`. Sends: `Promise<ChatThreadDetail>`.
- L74 `updateChatThread(threadId: string, title: string, signal?: AbortSignal): Promise<ChatThreadRead>` — Implements updatechatthread. Receives: `threadId: string, title: string, signal?: AbortSignal`. Sends: `Promise<ChatThreadRead>`.
- L87 `deleteChatThread(threadId: string, signal?: AbortSignal): Promise<void>` — Implements deletechatthread. Receives: `threadId: string, signal?: AbortSignal`. Sends: `Promise<void>`.
- L96 `createChatMessage(threadId: string, content: string, idempotencyKey: string, signal?: AbortSignal, action?: ChatMessageAction, documentSources?: CaseNarrativeDocumentSource[], responseLanguage: "thai" | "english" = "engl` — Implements createchatmessage. Receives: `threadId: string, content: string, idempotencyKey: string, signal?: AbortSignal, action?: ChatMessageAction, documentSources?: CaseNarrativeDocumentSource[], responseLanguage: "thai" | "english" = "english"`. Sends: `Promise<ChatMessageAccepted>`.
- L121 `getChatRun(threadId: string, runId: string, signal?: AbortSignal): Promise<ChatRun>` — Implements getchatrun. Receives: `threadId: string, runId: string, signal?: AbortSignal`. Sends: `Promise<ChatRun>`.
- L133 `listChatReports(threadId: string, signal?: AbortSignal): Promise<ChatReportRead[]>` — Implements listchatreports. Receives: `threadId: string, signal?: AbortSignal`. Sends: `Promise<ChatReportRead[]>`.
- L144 `getChatReport(threadId: string, reportId: string, signal?: AbortSignal): Promise<ChatReportRead>` — Implements getchatreport. Receives: `threadId: string, reportId: string, signal?: AbortSignal`. Sends: `Promise<ChatReportRead>`.
- L156 `downloadChatReportPdf(threadId: string, reportId: string, signal?: AbortSignal): Promise<Blob>` — Implements downloadchatreportpdf. Receives: `threadId: string, reportId: string, signal?: AbortSignal`. Sends: `Promise<Blob>`.
- L168 `generateChatReport(threadId: string, idempotencyKey?: string, signal?: AbortSignal): Promise<ChatReportRead>` — Implements generatechatreport. Receives: `threadId: string, idempotencyKey?: string, signal?: AbortSignal`. Sends: `Promise<ChatReportRead>`.
- L181 `function getApiErrorMessage(error: unknown, fallback: string): string` — Implements getapierrormessage. Receives: `error: unknown, fallback: string`. Sends: `string`.
- L216 `getSession(signal?: AbortSignal): Promise<UserProfile | null>` — Implements getsession. Receives: `signal?: AbortSignal`. Sends: `Promise<UserProfile | null>`.
- L226 `getCurrentUser(signal?: AbortSignal): Promise<UserProfile>` — Implements getcurrentuser. Receives: `signal?: AbortSignal`. Sends: `Promise<UserProfile>`.
- L236 `devLogin(payload: DevLoginPayload, signal?: AbortSignal): Promise<AuthTokenResponse>` — Implements devlogin. Receives: `payload: DevLoginPayload, signal?: AbortSignal`. Sends: `Promise<AuthTokenResponse>`.
- L248 `logout(signal?: AbortSignal): Promise<{ message: string }>` — Implements logout. Receives: `signal?: AbortSignal`. Sends: `Promise<{ message: string }>`.
- L259 `getOAuthLoginUrl(provider: "google" | "github"): string` — Implements getoauthloginurl. Receives: `provider: "google" | "github"`. Sends: `string`.

### [`frontend/src/lib/api-types.ts`](../../frontend/src/lib/api-types.ts)

Purpose: Owns api types behavior for the frontend application.

- L10 `type CaseRead` — Defines the type contract for caseread. Receives: `not applicable`. Sends: `type declaration`.
- L17 `type ChatRetryRequest` — Defines the type contract for chatretryrequest. Receives: `not applicable`. Sends: `type declaration`.
- L20 `type ChatThreadDetail` — Defines the type contract for chatthreaddetail. Receives: `not applicable`. Sends: `type declaration`.
- L24 `type ChatMessageRead` — Defines the type contract for chatmessageread. Receives: `not applicable`. Sends: `type declaration`.
- L25 `type ChatMessageAccepted` — Defines the type contract for chatmessageaccepted. Receives: `not applicable`. Sends: `type declaration`.
- L29 `type CaseChatMessageAccepted` — Defines the type contract for casechatmessageaccepted. Receives: `not applicable`. Sends: `type declaration`.
- L33 `type CaseNarrativeDocumentSource` — Defines the type contract for casenarrativedocumentsource. Receives: `not applicable`. Sends: `type declaration`.
- L35 `type PersistedChatMessage` — Defines the type contract for persistedchatmessage. Receives: `not applicable`. Sends: `type declaration`.
- L39 `type ChatRun` — Defines the type contract for chatrun. Receives: `not applicable`. Sends: `type declaration`.
- L40 `type ThreadStatus` — Defines the type contract for threadstatus. Receives: `not applicable`. Sends: `type declaration`.
- L41 `type RunStatus` — Defines the type contract for runstatus. Receives: `not applicable`. Sends: `type declaration`.
- L42 `type ChatMessageCreate` — Defines the type contract for chatmessagecreate. Receives: `not applicable`. Sends: `type declaration`.
- L45 `type ChatMessageAction` — Defines the type contract for chatmessageaction. Receives: `not applicable`. Sends: `type declaration`.
- L46 `type DocumentExtractionMethod` — Defines the type contract for documentextractionmethod. Receives: `not applicable`. Sends: `type declaration`.
- L47 `type DocumentVerificationStatus` — Defines the type contract for documentverificationstatus. Receives: `not applicable`. Sends: `type declaration`.
- L48 `type DocumentConfidenceStatus` — Defines the type contract for documentconfidencestatus. Receives: `not applicable`. Sends: `type declaration`.
- L50 `interface CaseIntakeSubmission` — Defines the structural contract for caseintakesubmission. Receives: `not applicable`. Sends: `type declaration`.
- L56 `type ChatReportSupportType` — Defines the type contract for chatreportsupporttype. Receives: `not applicable`. Sends: `type declaration`.
- L63 `interface ChatReportClaim` — Defines the structural contract for chatreportclaim. Receives: `not applicable`. Sends: `type declaration`.
- L73 `interface ChatReportSection` — Defines the structural contract for chatreportsection. Receives: `not applicable`. Sends: `type declaration`.
- L80 `interface ChatStructuredReport` — Defines the structural contract for chatstructuredreport. Receives: `not applicable`. Sends: `type declaration`.
- L89 `interface ChatReportRead` — Defines the structural contract for chatreportread. Receives: `not applicable`. Sends: `type declaration`.
- L135 `interface UserProfile` — Defines the structural contract for userprofile. Receives: `not applicable`. Sends: `type declaration`.
- L144 `interface AuthTokenResponse` — Defines the structural contract for authtokenresponse. Receives: `not applicable`. Sends: `type declaration`.
- L151 `interface DevLoginPayload` — Defines the structural contract for devloginpayload. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/api.ts`](../../frontend/src/lib/api.ts)

Purpose: Owns api behavior for the frontend application.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/lib/case-client.ts`](../../frontend/src/lib/case-client.ts)

Purpose: Owns case client behavior for the frontend application.

- L20 `listCases(signal?: AbortSignal): Promise<CaseRead[]>` — Implements listcases. Receives: `signal?: AbortSignal`. Sends: `Promise<CaseRead[]>`.
- L29 `createCase(title: string = "New case", signal?: AbortSignal): Promise<CaseRead>` — Implements createcase. Receives: `title: string = "New case", signal?: AbortSignal`. Sends: `Promise<CaseRead>`.
- L41 `getCase(caseId: string, signal?: AbortSignal): Promise<CaseRead>` — Implements getcase. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<CaseRead>`.
- L52 `updateCase(caseId: string, title: string, signal?: AbortSignal): Promise<CaseRead>` — Implements updatecase. Receives: `caseId: string, title: string, signal?: AbortSignal`. Sends: `Promise<CaseRead>`.
- L65 `deleteCase(caseId: string, signal?: AbortSignal): Promise<void>` — Implements deletecase. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<void>`.
- L74 `listCaseDocuments(caseId: string, signal?: AbortSignal): Promise<CaseDocumentRead[]>` — Implements listcasedocuments. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<CaseDocumentRead[]>`.
- L85 `listCaseEvidence(caseId: string, signal?: AbortSignal): Promise<EvidenceSourceRead[]>` — Implements listcaseevidence. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<EvidenceSourceRead[]>`.
- L96 `admitCaseEvidence(caseId: string, request: CaseEvidenceCreate, signal?: AbortSignal): Promise<EvidenceSourceRead>` — Implements admitcaseevidence. Receives: `caseId: string, request: CaseEvidenceCreate, signal?: AbortSignal`. Sends: `Promise<EvidenceSourceRead>`.
- L109 `uploadCaseDocument(caseId: string, file: File, signal?: AbortSignal): Promise<CaseDocumentRead>` — Implements uploadcasedocument. Receives: `caseId: string, file: File, signal?: AbortSignal`. Sends: `Promise<CaseDocumentRead>`.
- L124 `admitCaseDocument(caseId: string, documentId: string, extractionId: string, signal?: AbortSignal): Promise<EvidenceSourceRead>` — Implements admitcasedocument. Receives: `caseId: string, documentId: string, extractionId: string, signal?: AbortSignal`. Sends: `Promise<EvidenceSourceRead>`.
- L138 `startCaseAnalysis(caseId: string, request: CaseAnalysisCreate, signal?: AbortSignal): Promise<CaseAnalysisAccepted>` — Implements startcaseanalysis. Receives: `caseId: string, request: CaseAnalysisCreate, signal?: AbortSignal`. Sends: `Promise<CaseAnalysisAccepted>`.
- L151 `getCaseAnalysis(caseId: string, signal?: AbortSignal): Promise<CaseAnalysisResultRead | null>` — Implements getcaseanalysis. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<CaseAnalysisResultRead | null>`.
- L162 `getCaseRun(caseId: string, runId: string, signal?: AbortSignal): Promise<CaseRunRead>` — Implements getcaserun. Receives: `caseId: string, runId: string, signal?: AbortSignal`. Sends: `Promise<CaseRunRead>`.
- L174 `getCaseEvidenceSnapshot(caseId: string, snapshotId: string, signal?: AbortSignal): Promise<CaseEvidenceSnapshotRead>` — Implements getcaseevidencesnapshot. Receives: `caseId: string, snapshotId: string, signal?: AbortSignal`. Sends: `Promise<CaseEvidenceSnapshotRead>`.
- L186 `ensureCaseChat(caseId: string, signal?: AbortSignal): Promise<import("./api-types").ChatThreadRead>` — Implements ensurecasechat. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<import("./api-types").ChatThreadRead>`.
- L198 `listCaseClarifications(caseId: string, signal?: AbortSignal): Promise<CaseClarificationRead[]>` — Implements listcaseclarifications. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<CaseClarificationRead[]>`.
- L209 `answerCaseClarification(caseId: string, clarificationId: string, request: CaseClarificationAnswer, signal?: AbortSignal): Promise<CaseClarificationAccepted>` — Implements answercaseclarification. Receives: `caseId: string, clarificationId: string, request: CaseClarificationAnswer, signal?: AbortSignal`. Sends: `Promise<CaseClarificationAccepted>`.
- L223 `listCaseReports(caseId: string, signal?: AbortSignal): Promise<ChatReportRead[]>` — Implements listcasereports. Receives: `caseId: string, signal?: AbortSignal`. Sends: `Promise<ChatReportRead[]>`.
- L234 `generateCaseReport(caseId: string, request: CaseReportCreate, signal?: AbortSignal): Promise<ChatReportRead>` — Implements generatecasereport. Receives: `caseId: string, request: CaseReportCreate, signal?: AbortSignal`. Sends: `Promise<ChatReportRead>`.
- L247 `downloadCaseReportPdf(caseId: string, reportId: string, signal?: AbortSignal): Promise<Blob>` — Implements downloadcasereportpdf. Receives: `caseId: string, reportId: string, signal?: AbortSignal`. Sends: `Promise<Blob>`.

### [`frontend/src/lib/case-evidence.ts`](../../frontend/src/lib/case-evidence.ts)

Purpose: Owns case evidence behavior for the frontend application.

- L3 `type CaseEvidenceKind` — Defines the type contract for caseevidencekind. Receives: `not applicable`. Sends: `type declaration`.
- L8 `type EvidenceSourceType` — Defines the type contract for evidencesourcetype. Receives: `not applicable`. Sends: `type declaration`.
- L13 `type MaterialType` — Defines the type contract for materialtype. Receives: `not applicable`. Sends: `type declaration`.
- L18 `interface CaseEvidencePresentation` — Defines the structural contract for caseevidencepresentation. Receives: `not applicable`. Sends: `type declaration`.
- L29 `function getCaseEvidenceKind(message: PersistedChatMessage): CaseEvidenceKind | null` — Implements getcaseevidencekind. Receives: `message: PersistedChatMessage`. Sends: `CaseEvidenceKind | null`.
- L48 `function isCaseEvidenceMessage(message: PersistedChatMessage): boolean` — Implements iscaseevidencemessage. Receives: `message: PersistedChatMessage`. Sends: `boolean`.
- L54 `function getCaseEvidencePresentation(message: PersistedChatMessage): CaseEvidencePresentation | null` — Implements getcaseevidencepresentation. Receives: `message: PersistedChatMessage`. Sends: `CaseEvidencePresentation | null`.

### [`frontend/src/lib/case-intake-model.ts`](../../frontend/src/lib/case-intake-model.ts)

Purpose: Owns case intake model behavior for the frontend application.

- L5 `interface IntakeMaterial` — Defines the structural contract for intakematerial. Receives: `not applicable`. Sends: `type declaration`.
- L15 `function intakeMaterials(messages: PersistedChatMessage[], ingestion: DocumentIngestionState, draft?: CaseNarrativeDocumentSource): IntakeMaterial[]` — Implements intakematerials. Receives: `messages: PersistedChatMessage[], ingestion: DocumentIngestionState, draft?: CaseNarrativeDocumentSource`. Sends: `IntakeMaterial[]`.
- L60 `function intakeStatus({ ingestion, hasEvidence, hasAnalysis, isSubmitting, hasNarrative, hasUnreviewedMaterial, failed, }: { ingestion: DocumentIngestionState; hasEvidence: boolean; hasAnalysis: boolean; isSubmitting: bo` — Implements intakestatus. Receives: `{ ingestion, hasEvidence, hasAnalysis, isSubmitting, hasNarrative, hasUnreviewedMaterial, failed, }: { ingestion: DocumentIngestionState; hasEvidence: boolean; hasAnalysis: boolean; isSubmitting: boolean; hasNarrative: b`. Sends: `{ label: string; detail: string }`.

### [`frontend/src/lib/case-materials.ts`](../../frontend/src/lib/case-materials.ts)

Purpose: Owns case materials behavior for the frontend application.

- L9 `interface CaseMaterialItem` — Defines the structural contract for casematerialitem. Receives: `not applicable`. Sends: `type declaration`.
- L21 `interface CaseMaterialsData` — Defines the structural contract for casematerialsdata. Receives: `not applicable`. Sends: `type declaration`.
- L27 `function formatTimestamp(isoString: string, ordinal: number): string` — Implements formattimestamp. Receives: `isoString: string, ordinal: number`. Sends: `string`.
- L44 `function buildCaseMaterials(messages: PersistedChatMessage[]): CaseMaterialsData` — Implements buildcasematerials. Receives: `messages: PersistedChatMessage[]`. Sends: `CaseMaterialsData`.

### [`frontend/src/lib/case-narrative-document.ts`](../../frontend/src/lib/case-narrative-document.ts)

Purpose: Owns case narrative document behavior for the frontend application.

- L12 `interface CaseNarrativeDraft` — Defines the structural contract for casenarrativedraft. Receives: `not applicable`. Sends: `type declaration`.
- L18 `interface CaseNarrativeDraftPage` — Defines the structural contract for casenarrativedraftpage. Receives: `not applicable`. Sends: `type declaration`.
- L24 `function transcribedRegions(result: IngestedDocumentPreview): DocumentRegionPreview[]` — Implements transcribedregions. Receives: `result: IngestedDocumentPreview`. Sends: `DocumentRegionPreview[]`.
- L35 `function uniqueWarnings(result: IngestedDocumentPreview): string[]` — Implements uniquewarnings. Receives: `result: IngestedDocumentPreview`. Sends: `string[]`.
- L48 `function verificationStatus(regions: DocumentRegionPreview[], warnings: string[]): DocumentVerificationStatus` — Implements verificationstatus. Receives: `regions: DocumentRegionPreview[], warnings: string[]`. Sends: `DocumentVerificationStatus`.
- L71 `function confidence(regions: DocumentRegionPreview[]): { status: DocumentConfidenceStatus; minimum: number | null }` — Implements confidence. Receives: `regions: DocumentRegionPreview[]`. Sends: `{ status: DocumentConfidenceStatus; minimum: number | null }`.
- L96 `function buildCaseNarrativeDraft(result: IngestedDocumentPreview): CaseNarrativeDraft` — Implements buildcasenarrativedraft. Receives: `result: IngestedDocumentPreview`. Sends: `CaseNarrativeDraft`.
- L133 `function bindCaseNarrativeDocumentSource(draft: CaseNarrativeDraft, narrative: string): CaseNarrativeDocumentSource` — Implements bindcasenarrativedocumentsource. Receives: `draft: CaseNarrativeDraft, narrative: string`. Sends: `CaseNarrativeDocumentSource`.

### [`frontend/src/lib/case-overview-contracts.ts`](../../frontend/src/lib/case-overview-contracts.ts)

Purpose: Owns case overview contracts behavior for the frontend application.

- L3 `type ClaimType` — Defines the type contract for claimtype. Receives: `not applicable`. Sends: `type declaration`.
- L4 `type EpistemicStatus` — Defines the type contract for epistemicstatus. Receives: `not applicable`. Sends: `type declaration`.
- L11 `type GapStatus` — Defines the type contract for gapstatus. Receives: `not applicable`. Sends: `type declaration`.
- L16 `type GapPriority` — Defines the type contract for gappriority. Receives: `not applicable`. Sends: `type declaration`.
- L17 `type TechnicalContextStatus` — Defines the type contract for technicalcontextstatus. Receives: `not applicable`. Sends: `type declaration`.
- L23 `interface SourceMessageRef` — Defines the structural contract for sourcemessageref. Receives: `not applicable`. Sends: `type declaration`.
- L40 `interface EvidencePage` — Defines the structural contract for evidencepage. Receives: `not applicable`. Sends: `type declaration`.
- L46 `interface AnalysisEvidenceCitation` — Defines the structural contract for analysisevidencecitation. Receives: `not applicable`. Sends: `type declaration`.
- L54 `interface MitreTechniqueRef` — Defines the structural contract for mitretechniqueref. Receives: `not applicable`. Sends: `type declaration`.
- L61 `interface CaseFinding` — Defines the structural contract for casefinding. Receives: `not applicable`. Sends: `type declaration`.
- L72 `interface CaseGap` — Defines the structural contract for casegap. Receives: `not applicable`. Sends: `type declaration`.
- L83 `interface MitreExplainedCard` — Defines the structural contract for mitreexplainedcard. Receives: `not applicable`. Sends: `type declaration`.
- L92 `interface CaseOverviewData` — Defines the structural contract for caseoverviewdata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/case-overview-native-source.ts`](../../frontend/src/lib/case-overview-native-source.ts)

Purpose: Owns case overview native source behavior for the frontend application.

- L7 `interface NativeSnapshotSource` — Defines the structural contract for nativesnapshotsource. Receives: `not applicable`. Sends: `type declaration`.
- L18 `interface NativeCitation` — Defines the structural contract for nativecitation. Receives: `not applicable`. Sends: `type declaration`.
- L27 `interface NativePageBinding` — Defines the structural contract for nativepagebinding. Receives: `not applicable`. Sends: `type declaration`.
- L32 `function parseNativeSnapshot(snapshot: CaseEvidenceSnapshotRead): NativeSnapshotSource[]` — Implements parsenativesnapshot. Receives: `snapshot: CaseEvidenceSnapshotRead`. Sends: `NativeSnapshotSource[]`.
- L42 `function parseSnapshotSource(value: unknown): NativeSnapshotSource` — Implements parsesnapshotsource. Receives: `value: unknown`. Sends: `NativeSnapshotSource`.
- L66 `function parseNativeCitations(value: unknown, sourceIds: string[], sources: NativeSnapshotSource[]): NativeCitation[]` — Implements parsenativecitations. Receives: `value: unknown, sourceIds: string[], sources: NativeSnapshotSource[]`. Sends: `NativeCitation[]`.
- L100 `function sourceRefs(ids: string[], citations: NativeCitation[], sources: NativeSnapshotSource[]): SourceMessageRef[]` — Implements sourcerefs. Receives: `ids: string[], citations: NativeCitation[], sources: NativeSnapshotSource[]`. Sends: `SourceMessageRef[]`.
- L113 `function buildSourceRef(source: NativeSnapshotSource, citation: NativeCitation | null): SourceMessageRef` — Implements buildsourceref. Receives: `source: NativeSnapshotSource, citation: NativeCitation | null`. Sends: `SourceMessageRef`.
- L136 `function resolvePageBinding(source: NativeSnapshotSource, citation: NativeCitation): NativePageBinding | null` — Implements resolvepagebinding. Receives: `source: NativeSnapshotSource, citation: NativeCitation`. Sends: `NativePageBinding | null`.
- L168 `function sourceTypeFor(kind: string): SourceMessageRef["sourceType"]` — Implements sourcetypefor. Receives: `kind: string`. Sends: `SourceMessageRef["sourceType"]`.
- L175 `function sourceTypeLabel(type: SourceMessageRef["sourceType"]): string` — Implements sourcetypelabel. Receives: `type: SourceMessageRef["sourceType"]`. Sends: `string`.
- L181 `function quoteOccurrences(content: string, quote: string): number[]` — Implements quoteoccurrences. Receives: `content: string, quote: string`. Sends: `number[]`.
- L191 `function contextualExcerpt(content: string, exactQuote?: string): string` — Implements contextualexcerpt. Receives: `content: string, exactQuote?: string`. Sends: `string`.
- L200 `function sameNumbers(left: number[], right: number[]): boolean` — Implements samenumbers. Receives: `left: number[], right: number[]`. Sends: `boolean`.
- L204 `function isInteger(value: unknown): value is number` — Implements isinteger. Receives: `value: unknown`. Sends: `value is number`.
- L208 `function isPositiveInteger(value: unknown): value is number` — Implements ispositiveinteger. Receives: `value: unknown`. Sends: `value is number`.
- L212 `function canonicalJson(value: unknown): string` — Implements canonicaljson. Receives: `value: unknown`. Sends: `string`.

### [`frontend/src/lib/case-overview-native-trace.ts`](../../frontend/src/lib/case-overview-native-trace.ts)

Purpose: Owns case overview native trace behavior for the frontend application.

- L6 `interface NativeTraceClaim` — Defines the structural contract for nativetraceclaim. Receives: `not applicable`. Sends: `type declaration`.
- L18 `interface NativeTraceAssociation` — Defines the structural contract for nativetraceassociation. Receives: `not applicable`. Sends: `type declaration`.
- L25 `interface ParsedNativeTrace` — Defines the structural contract for parsednativetrace. Receives: `not applicable`. Sends: `type declaration`.
- L38 `function parseNativeTrace(result: CaseAnalysisResultRead, snapshot: CaseEvidenceSnapshotRead, sources: NativeSnapshotSource[]): ParsedNativeTrace` — Implements parsenativetrace. Receives: `result: CaseAnalysisResultRead, snapshot: CaseEvidenceSnapshotRead, sources: NativeSnapshotSource[]`. Sends: `ParsedNativeTrace`.
- L62 `function parseClaim(value: unknown, sources: NativeSnapshotSource[]): NativeTraceClaim` — Implements parseclaim. Receives: `value: unknown, sources: NativeSnapshotSource[]`. Sends: `NativeTraceClaim`.
- L86 `function parseGap(value: unknown): CaseGap` — Implements parsegap. Receives: `value: unknown`. Sends: `CaseGap`.
- L99 `function parseAssociation(value: unknown): NativeTraceAssociation` — Implements parseassociation. Receives: `value: unknown`. Sends: `NativeTraceAssociation`.
- L109 `function invalidSummary(): string` — Implements invalidsummary. Receives: `not applicable`. Sends: `string`.

### [`frontend/src/lib/case-overview-native.ts`](../../frontend/src/lib/case-overview-native.ts)

Purpose: Owns case overview native behavior for the frontend application.

- L7 `function buildNativeCaseOverview(result: CaseAnalysisResultRead | null, snapshot: CaseEvidenceSnapshotRead | null, runStatus: string | null): CaseOverviewData` — Implements buildnativecaseoverview. Receives: `result: CaseAnalysisResultRead | null, snapshot: CaseEvidenceSnapshotRead | null, runStatus: string | null`. Sends: `CaseOverviewData`.
- L36 `function emptyNativeOverview(isProcessing: boolean): CaseOverviewData` — Implements emptynativeoverview. Receives: `isProcessing: boolean`. Sends: `CaseOverviewData`.
- L50 `function unavailableNativeOverview(isProcessing: boolean, reason: string): CaseOverviewData` — Implements unavailablenativeoverview. Receives: `isProcessing: boolean, reason: string`. Sends: `CaseOverviewData`.
- L54 `function toFinding(claim: NativeTraceClaim, associations: NativeTraceAssociation[], sources: NativeSnapshotSource[]): CaseFinding` — Implements tofinding. Receives: `claim: NativeTraceClaim, associations: NativeTraceAssociation[], sources: NativeSnapshotSource[]`. Sends: `CaseFinding`.
- L76 `function buildMitreCards(associations: NativeTraceAssociation[], findings: CaseFinding[]): MitreExplainedCard[]` — Implements buildmitrecards. Receives: `associations: NativeTraceAssociation[], findings: CaseFinding[]`. Sends: `MitreExplainedCard[]`.
- L88 `function technicalContextStatus(associations: NativeTraceAssociation[], retrievalContextId: string | null, result: CaseAnalysisResultRead): TechnicalContextStatus` — Implements technicalcontextstatus. Receives: `associations: NativeTraceAssociation[], retrievalContextId: string | null, result: CaseAnalysisResultRead`. Sends: `TechnicalContextStatus`.

### [`frontend/src/lib/case-overview-parsing.ts`](../../frontend/src/lib/case-overview-parsing.ts)

Purpose: Owns case overview parsing behavior for the frontend application.

- L12 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord. Receives: `value: unknown`. Sends: `Record<string, unknown> | null`.
- L18 `function asArray(value: unknown): unknown[]` — Implements asarray. Receives: `value: unknown`. Sends: `unknown[]`.
- L22 `function asString(value: unknown): string` — Implements asstring. Receives: `value: unknown`. Sends: `string`.
- L26 `function asStringArray(value: unknown): string[]` — Implements asstringarray. Receives: `value: unknown`. Sends: `string[]`.
- L30 `interface ParsedAssociation` — Defines the structural contract for parsedassociation. Receives: `not applicable`. Sends: `type declaration`.
- L36 `interface ParsedMitreTableRow` — Defines the structural contract for parsedmitretablerow. Receives: `not applicable`. Sends: `type declaration`.
- L41 `function parseAssociations(value: unknown): ParsedAssociation[]` — Implements parseassociations. Receives: `value: unknown`. Sends: `ParsedAssociation[]`.
- L55 `function parseMitreTable(value: unknown): Map<string, ParsedMitreTableRow>` — Implements parsemitretable. Receives: `value: unknown`. Sends: `Map<string, ParsedMitreTableRow>`.
- L70 `function techniquesForClaim(claimId: string, associations: ParsedAssociation[], table: Map<string, ParsedMitreTableRow>): MitreTechniqueRef[]` — Implements techniquesforclaim. Receives: `claimId: string, associations: ParsedAssociation[], table: Map<string, ParsedMitreTableRow>`. Sends: `MitreTechniqueRef[]`.
- L88 `function buildMitreCards(associations: ParsedAssociation[], table: Map<string, ParsedMitreTableRow>, claimTextById: Map<string, string>): MitreExplainedCard[]` — Implements buildmitrecards. Receives: `associations: ParsedAssociation[], table: Map<string, ParsedMitreTableRow>, claimTextById: Map<string, string>`. Sends: `MitreExplainedCard[]`.

### [`frontend/src/lib/case-overview-v3.ts`](../../frontend/src/lib/case-overview-v3.ts)

Purpose: Owns case overview v3 behavior for the frontend application.

- L42 `function isV3CaseOverviewMessage(message: PersistedChatMessage): boolean` — Implements isv3caseoverviewmessage. Receives: `message: PersistedChatMessage`. Sends: `boolean`.
- L54 `function buildV3CaseOverview(message: PersistedChatMessage, messages: PersistedChatMessage[], isProcessing: boolean): CaseOverviewData` — Implements buildv3caseoverview. Receives: `message: PersistedChatMessage, messages: PersistedChatMessage[], isProcessing: boolean`. Sends: `CaseOverviewData`.
- L80 `function parseFindings(value: unknown, messages: PersistedChatMessage[], associations: ReturnType<typeof parseAssociations>, mitreTable: ReturnType<typeof parseMitreTable>): CaseFinding[]` — Implements parsefindings. Receives: `value: unknown, messages: PersistedChatMessage[], associations: ReturnType<typeof parseAssociations>, mitreTable: ReturnType<typeof parseMitreTable>`. Sends: `CaseFinding[]`.
- L117 `function parseGaps(value: unknown): CaseGap[]` — Implements parsegaps. Receives: `value: unknown`. Sends: `CaseGap[]`.
- L147 `function resolveTechnicalContextStatus(message: PersistedChatMessage, associationCount: number): TechnicalContextStatus` — Implements resolvetechnicalcontextstatus. Receives: `message: PersistedChatMessage, associationCount: number`. Sends: `TechnicalContextStatus`.

### [`frontend/src/lib/case-overview.ts`](../../frontend/src/lib/case-overview.ts)

Purpose: Owns case overview behavior for the frontend application.

- L42 `function groupCaseFindings(findings: CaseFinding[])` — Implements groupcasefindings. Receives: `findings: CaseFinding[]`. Sends: `inferred or void`.
- L53 `function caseOverviewMetadata(messages: PersistedChatMessage[], overview: CaseOverviewData)` — Implements caseoverviewmetadata. Receives: `messages: PersistedChatMessage[], overview: CaseOverviewData`. Sends: `inferred or void`.
- L79 `function analysisRecord(message: PersistedChatMessage)` — Implements analysisrecord. Receives: `message: PersistedChatMessage`. Sends: `inferred or void`.
- L85 `function isCandidateAnalysisMessage(message: PersistedChatMessage): boolean` — Implements iscandidateanalysismessage. Receives: `message: PersistedChatMessage`. Sends: `boolean`.
- L101 `function buildCaseOverview(messages: PersistedChatMessage[], threadStatus?: ThreadStatus | null): CaseOverviewData` — Implements buildcaseoverview. Receives: `messages: PersistedChatMessage[], threadStatus?: ThreadStatus | null`. Sends: `CaseOverviewData`.

### [`frontend/src/lib/chat-followup.ts`](../../frontend/src/lib/chat-followup.ts)

Purpose: Owns chat followup behavior for the frontend application.

- L7 `interface ChatFollowUpEntry` — Defines the structural contract for chatfollowupentry. Receives: `not applicable`. Sends: `type declaration`.
- L12 `interface ActiveChatFollowUp` — Defines the structural contract for activechatfollowup. Receives: `not applicable`. Sends: `type declaration`.
- L18 `interface ChatFollowUpGapDetail` — Defines the structural contract for chatfollowupgapdetail. Receives: `not applicable`. Sends: `type declaration`.
- L32 `interface FollowUpMetadata` — Defines the structural contract for followupmetadata. Receives: `not applicable`. Sends: `type declaration`.
- L37 `function followUpMetadata(message: PersistedChatMessage): FollowUpMetadata | null` — Implements followupmetadata. Receives: `message: PersistedChatMessage`. Sends: `FollowUpMetadata | null`.
- L64 `function isRecord(value: unknown): value is Record<string, unknown>` — Implements isrecord. Receives: `value: unknown`. Sends: `value is Record<string, unknown>`.
- L68 `function isNonEmptyString(value: unknown): value is string` — Implements isnonemptystring. Receives: `value: unknown`. Sends: `value is string`.
- L72 `function isGapStatus(value: unknown): value is ChatFollowUpGapDetail["status"]` — Implements isgapstatus. Receives: `value: unknown`. Sends: `value is ChatFollowUpGapDetail["status"]`.
- L83 `function isGapPriority(value: unknown): value is ChatFollowUpGapDetail["priority"]` — Implements isgappriority. Receives: `value: unknown`. Sends: `value is ChatFollowUpGapDetail["priority"]`.
- L89 `function followUpGapDetailForMessage(message: PersistedChatMessage): ChatFollowUpGapDetail | null` — Implements followupgapdetailformessage. Receives: `message: PersistedChatMessage`. Sends: `ChatFollowUpGapDetail | null`.
- L120 `function orderedMessages(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements orderedmessages. Receives: `persistedMessages: PersistedChatMessage[]`. Sends: `PersistedChatMessage[]`.
- L128 `function latestUserAnswerBetween(persistedMessages: PersistedChatMessage[], questionOrdinal: number, nextAssistantOrdinal?: number): PersistedChatMessage | null` — Implements latestuseranswerbetween. Receives: `persistedMessages: PersistedChatMessage[], questionOrdinal: number, nextAssistantOrdinal?: number`. Sends: `PersistedChatMessage | null`.
- L143 `function activeChatFollowUpForThread(persistedMessages: PersistedChatMessage[], status: ThreadStatus | null): ActiveChatFollowUp | null` — Implements activechatfollowupforthread. Receives: `persistedMessages: PersistedChatMessage[], status: ThreadStatus | null`. Sends: `ActiveChatFollowUp | null`.
- L206 `function filterSupersededClarificationAnswers(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements filtersupersededclarificationanswers. Receives: `persistedMessages: PersistedChatMessage[]`. Sends: `PersistedChatMessage[]`.
- L243 `function chatTranscriptMessages(persistedMessages: PersistedChatMessage[]): PersistedChatMessage[]` — Implements chattranscriptmessages. Receives: `persistedMessages: PersistedChatMessage[]`. Sends: `PersistedChatMessage[]`.
- L249 `function persistedRequestOrdinal(detail: ChatThreadDetail, lastKnownMessageOrdinal: number, content: string): number | undefined` — Implements persistedrequestordinal. Receives: `detail: ChatThreadDetail, lastKnownMessageOrdinal: number, content: string`. Sends: `number | undefined`.
- L262 `function hasCompletedAssistantOutput(detail: ChatThreadDetail, requestOrdinal: number): boolean` — Implements hascompletedassistantoutput. Receives: `detail: ChatThreadDetail, requestOrdinal: number`. Sends: `boolean`.

### [`frontend/src/lib/document-ingestion-store.ts`](../../frontend/src/lib/document-ingestion-store.ts)

Purpose: Owns document ingestion store behavior for the frontend application.

- L11 `interface DocumentIngestionState` — Defines the structural contract for documentingestionstate. Receives: `not applicable`. Sends: `type declaration`.
- L33 `function getStorageKey(caseKey: string): string` — Implements getstoragekey. Receives: `caseKey: string`. Sends: `string`.
- L38 `function loadInitialState(caseKey: string): DocumentIngestionState` — Implements loadinitialstate. Receives: `caseKey: string`. Sends: `DocumentIngestionState`.
- L63 `function saveToLocalStorage(caseKey: string, state: DocumentIngestionState)` — Implements savetolocalstorage. Receives: `caseKey: string, state: DocumentIngestionState`. Sends: `inferred or void`.
- L93 `function notify(caseKey: string)` — Implements notify. Receives: `caseKey: string`. Sends: `inferred or void`.
- L100 `function getDocumentIngestionSnapshot(caseKey: string = "draft"): DocumentIngestionState` — Implements getdocumentingestionsnapshot. Receives: `caseKey: string = "draft"`. Sends: `DocumentIngestionState`.
- L105 `function getServerSnapshot(): DocumentIngestionState` — Implements getserversnapshot. Receives: `not applicable`. Sends: `DocumentIngestionState`.
- L109 `function subscribeDocumentIngestion(listener: () => void): () => void` — Implements subscribedocumentingestion. Receives: `listener: () => void`. Sends: `() => void`.
- L116 `function hydrateDocumentIngestionStore(caseKey: string = "draft")` — Implements hydratedocumentingestionstore. Receives: `caseKey: string = "draft"`. Sends: `inferred or void`.
- L133 `function setDocumentIngestionFile(file: File | null, caseKey: string = "draft")` — Implements setdocumentingestionfile. Receives: `file: File | null, caseKey: string = "draft"`. Sends: `inferred or void`.
- L153 `function setDocumentIngestionMode(mode: DocumentIngestionMode, caseKey: string = "draft")` — Implements setdocumentingestionmode. Receives: `mode: DocumentIngestionMode, caseKey: string = "draft"`. Sends: `inferred or void`.
- L171 `function setDocumentIngestionProcessing(isProcessing: boolean, caseKey: string = "draft")` — Implements setdocumentingestionprocessing. Receives: `isProcessing: boolean, caseKey: string = "draft"`. Sends: `inferred or void`.
- L184 `function setDocumentIngestionResult(result: IngestedDocumentPreview | null, caseKey: string = "draft")` — Implements setdocumentingestionresult. Receives: `result: IngestedDocumentPreview | null, caseKey: string = "draft"`. Sends: `inferred or void`.
- L198 `function setDocumentIngestionError(error: string | null, caseKey: string = "draft")` — Implements setdocumentingestionerror. Receives: `error: string | null, caseKey: string = "draft"`. Sends: `inferred or void`.
- L211 `function resetDocumentIngestionState(caseKey?: string)` — Implements resetdocumentingestionstate. Receives: `caseKey?: string`. Sends: `inferred or void`.
- L249 `function useDocumentIngestion(caseKey: string = "draft")` — Implements usedocumentingestion. Receives: `caseKey: string = "draft"`. Sends: `inferred or void`.

### [`frontend/src/lib/document-ingestion.ts`](../../frontend/src/lib/document-ingestion.ts)

Purpose: Owns document ingestion behavior for the frontend application.

- L6 `type DocumentIngestionMode` — Defines the type contract for documentingestionmode. Receives: `not applicable`. Sends: `type declaration`.
- L8 `interface DocumentBoundingBox` — Defines the structural contract for documentboundingbox. Receives: `not applicable`. Sends: `type declaration`.
- L15 `interface DocumentRecognitionCandidate` — Defines the structural contract for documentrecognitioncandidate. Receives: `not applicable`. Sends: `type declaration`.
- L25 `interface DocumentGeneratedContent` — Defines the structural contract for documentgeneratedcontent. Receives: `not applicable`. Sends: `type declaration`.
- L31 `interface OCRWord` — Defines the structural contract for ocrword. Receives: `not applicable`. Sends: `type declaration`.
- L37 `interface DocumentRegionPreview` — Defines the structural contract for documentregionpreview. Receives: `not applicable`. Sends: `type declaration`.
- L57 `interface DocumentRoutingSummary` — Defines the structural contract for documentroutingsummary. Receives: `not applicable`. Sends: `type declaration`.
- L66 `interface DocumentPagePreview` — Defines the structural contract for documentpagepreview. Receives: `not applicable`. Sends: `type declaration`.
- L74 `interface IngestedDocumentPreview` — Defines the structural contract for ingesteddocumentpreview. Receives: `not applicable`. Sends: `type declaration`.
- L85 `interface PreviewDocumentIngestionOptions` — Defines the structural contract for previewdocumentingestionoptions. Receives: `not applicable`. Sends: `type declaration`.
- L91 `function generateOcrIdempotencyKey(caseKey: string, file: File, mode: DocumentIngestionMode): string` — Implements generateocridempotencykey. Receives: `caseKey: string, file: File, mode: DocumentIngestionMode`. Sends: `string`.
- L100 `function previewDocumentIngestion(file: File, mode: DocumentIngestionMode, optionsOrSignal?: AbortSignal | PreviewDocumentIngestionOptions): Promise<IngestedDocumentPreview>` — Implements previewdocumentingestion. Receives: `file: File, mode: DocumentIngestionMode, optionsOrSignal?: AbortSignal | PreviewDocumentIngestionOptions`. Sends: `Promise<IngestedDocumentPreview>`.

### [`frontend/src/lib/evidence-citation.ts`](../../frontend/src/lib/evidence-citation.ts)

Purpose: Owns evidence citation behavior for the frontend application.

- L10 `interface PageSpan` — Defines the structural contract for pagespan. Receives: `not applicable`. Sends: `type declaration`.
- L16 `function mapSourceMessageIds(sourceIds: string[], messages: PersistedChatMessage[], citations: AnalysisEvidenceCitation[] = []): SourceMessageRef[]` — Implements mapsourcemessageids. Receives: `sourceIds: string[], messages: PersistedChatMessage[], citations: AnalysisEvidenceCitation[] = []`. Sends: `SourceMessageRef[]`.
- L43 `function parseEvidenceCitations(value: unknown): AnalysisEvidenceCitation[]` — Implements parseevidencecitations. Receives: `value: unknown`. Sends: `AnalysisEvidenceCitation[]`.
- L64 `function formatPageReference(pageNumbers: number[]): string` — Implements formatpagereference. Receives: `pageNumbers: number[]`. Sends: `string`.
- L69 `function formatEvidenceCitationText(sourceRef: Pick<SourceMessageRef, "label" | "pageNumbers" | "sourceType" | "isNativeEvidence">): string` — Implements formatevidencecitationtext. Receives: `sourceRef: Pick<SourceMessageRef, "label" | "pageNumbers" | "sourceType" | "isNativeEvidence">`. Sends: `string`.
- L80 `function buildSourceMessageRef(message: PersistedChatMessage, citation: AnalysisEvidenceCitation | null): SourceMessageRef` — Implements buildsourcemessageref. Receives: `message: PersistedChatMessage, citation: AnalysisEvidenceCitation | null`. Sends: `SourceMessageRef`.
- L127 `function resolvePageCitation(message: PersistedChatMessage, citation: AnalysisEvidenceCitation): EvidencePage[] | null` — Implements resolvepagecitation. Receives: `message: PersistedChatMessage, citation: AnalysisEvidenceCitation`. Sends: `EvidencePage[] | null`.
- L178 `function validPageSpans(document: Record<string, unknown>, content: string): PageSpan[]` — Implements validpagespans. Receives: `document: Record<string, unknown>, content: string`. Sends: `PageSpan[]`.
- L200 `function quoteOccurrences(content: string, quote: string): number[]` — Implements quoteoccurrences. Receives: `content: string, quote: string`. Sends: `number[]`.
- L210 `function contextualExcerpt(content: string, exactQuote?: string): string` — Implements contextualexcerpt. Receives: `content: string, exactQuote?: string`. Sends: `string`.
- L219 `function formatPageList(pageNumbers: number[]): string` — Implements formatpagelist. Receives: `pageNumbers: number[]`. Sends: `string`.
- L228 `function sameNumbers(left: number[], right: number[]): boolean` — Implements samenumbers. Receives: `left: number[], right: number[]`. Sends: `boolean`.
- L232 `function isSortedUnique(values: number[]): boolean` — Implements issortedunique. Receives: `values: number[]`. Sends: `boolean`.
- L238 `function isInteger(value: unknown): value is number` — Implements isinteger. Receives: `value: unknown`. Sends: `value is number`.
- L242 `function isPositiveInteger(value: unknown): value is number` — Implements ispositiveinteger. Receives: `value: unknown`. Sends: `value is number`.
- L246 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord. Receives: `value: unknown`. Sends: `Record<string, unknown> | null`.
- L252 `function asArray(value: unknown): unknown[]` — Implements asarray. Receives: `value: unknown`. Sends: `unknown[]`.
- L256 `function asString(value: unknown): string` — Implements asstring. Receives: `value: unknown`. Sends: `string`.

### [`frontend/src/lib/generated/AdmitExtractionRequest.ts`](../../frontend/src/lib/generated/AdmitExtractionRequest.ts)

Purpose: Owns admitextractionrequest behavior for the frontend application.

- L1 `type AdmitExtractionRequest` — Defines the type contract for admitextractionrequest. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseAnalysisAccepted.ts`](../../frontend/src/lib/generated/CaseAnalysisAccepted.ts)

Purpose: Owns caseanalysisaccepted behavior for the frontend application.

- L3 `type CaseAnalysisAccepted` — Defines the type contract for caseanalysisaccepted. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseAnalysisCreate.ts`](../../frontend/src/lib/generated/CaseAnalysisCreate.ts)

Purpose: Owns caseanalysiscreate behavior for the frontend application.

- L1 `type CaseAnalysisCreate` — Defines the type contract for caseanalysiscreate. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseAnalysisResultRead.ts`](../../frontend/src/lib/generated/CaseAnalysisResultRead.ts)

Purpose: Owns caseanalysisresultread behavior for the frontend application.

- L1 `type CaseAnalysisResultRead` — Defines the type contract for caseanalysisresultread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseChatMessageAccepted.ts`](../../frontend/src/lib/generated/CaseChatMessageAccepted.ts)

Purpose: Owns casechatmessageaccepted behavior for the frontend application.

- L4 `type CaseChatMessageAccepted` — Defines the type contract for casechatmessageaccepted. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseClarificationAccepted.ts`](../../frontend/src/lib/generated/CaseClarificationAccepted.ts)

Purpose: Owns caseclarificationaccepted behavior for the frontend application.

- L4 `type CaseClarificationAccepted` — Defines the type contract for caseclarificationaccepted. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseClarificationAnswer.ts`](../../frontend/src/lib/generated/CaseClarificationAnswer.ts)

Purpose: Owns caseclarificationanswer behavior for the frontend application.

- L1 `type CaseClarificationAnswer` — Defines the type contract for caseclarificationanswer. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseClarificationRead.ts`](../../frontend/src/lib/generated/CaseClarificationRead.ts)

Purpose: Owns caseclarificationread behavior for the frontend application.

- L1 `type CaseClarificationRead` — Defines the type contract for caseclarificationread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseDocumentRead.ts`](../../frontend/src/lib/generated/CaseDocumentRead.ts)

Purpose: Owns casedocumentread behavior for the frontend application.

- L3 `type CaseDocumentRead` — Defines the type contract for casedocumentread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseEvidenceCreate.ts`](../../frontend/src/lib/generated/CaseEvidenceCreate.ts)

Purpose: Owns caseevidencecreate behavior for the frontend application.

- L1 `type CaseEvidenceCreate` — Defines the type contract for caseevidencecreate. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseEvidenceSnapshotRead.ts`](../../frontend/src/lib/generated/CaseEvidenceSnapshotRead.ts)

Purpose: Owns caseevidencesnapshotread behavior for the frontend application.

- L1 `type CaseEvidenceSnapshotRead` — Defines the type contract for caseevidencesnapshotread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseNarrativeDocumentPageSpan.ts`](../../frontend/src/lib/generated/CaseNarrativeDocumentPageSpan.ts)

Purpose: Owns casenarrativedocumentpagespan behavior for the frontend application.

- L1 `type CaseNarrativeDocumentPageSpan` — Defines the type contract for casenarrativedocumentpagespan. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseNarrativeDocumentSource.ts`](../../frontend/src/lib/generated/CaseNarrativeDocumentSource.ts)

Purpose: Owns casenarrativedocumentsource behavior for the frontend application.

- L3 `type CaseNarrativeDocumentSource` — Defines the type contract for casenarrativedocumentsource. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseRead.ts`](../../frontend/src/lib/generated/CaseRead.ts)

Purpose: Owns caseread behavior for the frontend application.

- L1 `type CaseRead` — Defines the type contract for caseread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseReportCreate.ts`](../../frontend/src/lib/generated/CaseReportCreate.ts)

Purpose: Owns casereportcreate behavior for the frontend application.

- L1 `type CaseReportCreate` — Defines the type contract for casereportcreate. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/CaseRunRead.ts`](../../frontend/src/lib/generated/CaseRunRead.ts)

Purpose: Owns caserunread behavior for the frontend application.

- L1 `type CaseRunRead` — Defines the type contract for caserunread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatActionMetadata.ts`](../../frontend/src/lib/generated/ChatActionMetadata.ts)

Purpose: Owns chatactionmetadata behavior for the frontend application.

- L1 `type ChatActionMetadata` — Defines the type contract for chatactionmetadata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatMessageAccepted.ts`](../../frontend/src/lib/generated/ChatMessageAccepted.ts)

Purpose: Owns chatmessageaccepted behavior for the frontend application.

- L4 `type ChatMessageAccepted` — Defines the type contract for chatmessageaccepted. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatMessageCreate.ts`](../../frontend/src/lib/generated/ChatMessageCreate.ts)

Purpose: Owns chatmessagecreate behavior for the frontend application.

- L3 `type ChatMessageCreate` — Defines the type contract for chatmessagecreate. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatMessageRead.ts`](../../frontend/src/lib/generated/ChatMessageRead.ts)

Purpose: Owns chatmessageread behavior for the frontend application.

- L3 `type ChatMessageRead` — Defines the type contract for chatmessageread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatReportRead.ts`](../../frontend/src/lib/generated/ChatReportRead.ts)

Purpose: Owns chatreportread behavior for the frontend application.

- L3 `type ChatReportRead` — Defines the type contract for chatreportread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatRetryRequest.ts`](../../frontend/src/lib/generated/ChatRetryRequest.ts)

Purpose: Owns chatretryrequest behavior for the frontend application.

- L3 `type ChatRetryRequest` — Defines the type contract for chatretryrequest. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatRunRead.ts`](../../frontend/src/lib/generated/ChatRunRead.ts)

Purpose: Owns chatrunread behavior for the frontend application.

- L1 `type ChatRunRead` — Defines the type contract for chatrunread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatThreadDetail.ts`](../../frontend/src/lib/generated/ChatThreadDetail.ts)

Purpose: Owns chatthreaddetail behavior for the frontend application.

- L4 `type ChatThreadDetail` — Defines the type contract for chatthreaddetail. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ChatThreadRead.ts`](../../frontend/src/lib/generated/ChatThreadRead.ts)

Purpose: Owns chatthreadread behavior for the frontend application.

- L1 `type ChatThreadRead` — Defines the type contract for chatthreadread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/DocumentExtractionRead.ts`](../../frontend/src/lib/generated/DocumentExtractionRead.ts)

Purpose: Owns documentextractionread behavior for the frontend application.

- L1 `type DocumentExtractionRead` — Defines the type contract for documentextractionread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/DocumentSourceMetadata.ts`](../../frontend/src/lib/generated/DocumentSourceMetadata.ts)

Purpose: Owns documentsourcemetadata behavior for the frontend application.

- L3 `type DocumentSourceMetadata` — Defines the type contract for documentsourcemetadata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/EvidenceRevisionRead.ts`](../../frontend/src/lib/generated/EvidenceRevisionRead.ts)

Purpose: Owns evidencerevisionread behavior for the frontend application.

- L1 `type EvidenceRevisionRead` — Defines the type contract for evidencerevisionread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/EvidenceSourceRead.ts`](../../frontend/src/lib/generated/EvidenceSourceRead.ts)

Purpose: Owns evidencesourceread behavior for the frontend application.

- L3 `type EvidenceSourceRead` — Defines the type contract for evidencesourceread. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/FollowUpMetadata.ts`](../../frontend/src/lib/generated/FollowUpMetadata.ts)

Purpose: Owns followupmetadata behavior for the frontend application.

- L1 `type FollowUpMetadata` — Defines the type contract for followupmetadata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/MessageMetadata.ts`](../../frontend/src/lib/generated/MessageMetadata.ts)

Purpose: Owns messagemetadata behavior for the frontend application.

- L6 `type MessageMetadata` — Defines the type contract for messagemetadata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/RagAttemptMetadata.ts`](../../frontend/src/lib/generated/RagAttemptMetadata.ts)

Purpose: Owns ragattemptmetadata behavior for the frontend application.

- L1 `type RagAttemptMetadata` — Defines the type contract for ragattemptmetadata. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ReportClaim.ts`](../../frontend/src/lib/generated/ReportClaim.ts)

Purpose: Owns reportclaim behavior for the frontend application.

- L1 `type ReportClaim` — Defines the type contract for reportclaim. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/ReportSection.ts`](../../frontend/src/lib/generated/ReportSection.ts)

Purpose: Owns reportsection behavior for the frontend application.

- L1 `type ReportSection` — Defines the type contract for reportsection. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/generated/StructuredReport.ts`](../../frontend/src/lib/generated/StructuredReport.ts)

Purpose: Owns structuredreport behavior for the frontend application.

- L4 `type StructuredReport` — Defines the type contract for structuredreport. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/intake-readable-text.ts`](../../frontend/src/lib/intake-readable-text.ts)

Purpose: Owns intake readable text behavior for the frontend application.

- L5 `function intakeReadableText(source: string): string` — Implements intakereadabletext. Receives: `source: string`. Sends: `string`.

### [`frontend/src/lib/mitre-candidate.ts`](../../frontend/src/lib/mitre-candidate.ts)

Purpose: Owns mitre candidate behavior for the frontend application.

- L3 `interface MitreLinkedClaimView` — Defines the structural contract for mitrelinkedclaimview. Receives: `not applicable`. Sends: `type declaration`.
- L16 `interface MitreCandidateView` — Defines the structural contract for mitrecandidateview. Receives: `not applicable`. Sends: `type declaration`.
- L38 `function mitreCandidatesForMessage(message: PersistedChatMessage): MitreCandidateView[] | null` — Implements mitrecandidatesformessage. Receives: `message: PersistedChatMessage`. Sends: `MitreCandidateView[] | null`.
- L87 `function parseClaims(value: unknown): Map<string, MitreLinkedClaimView> | null` — Implements parseclaims. Receives: `value: unknown`. Sends: `Map<string, MitreLinkedClaimView> | null`.
- L120 `function admittedMitreRows(rows: unknown[]): Map<string, string>` — Implements admittedmitrerows. Receives: `rows: unknown[]`. Sends: `Map<string, string>`.
- L136 `function isValidatedTrace(trace: Record<string, unknown> | null): trace is Record<string, unknown>` — Implements isvalidatedtrace. Receives: `trace: Record<string, unknown> | null`. Sends: `trace is Record<string, unknown>`.
- L150 `function hasOnlyAssociationKeys(value: Record<string, unknown>): boolean` — Implements hasonlyassociationkeys. Receives: `value: Record<string, unknown>`. Sends: `boolean`.
- L162 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord. Receives: `value: unknown`. Sends: `Record<string, unknown> | null`.
- L168 `function asArray(value: unknown): unknown[] | null` — Implements asarray. Receives: `value: unknown`. Sends: `unknown[] | null`.
- L172 `function requiredString(value: unknown): string | null` — Implements requiredstring. Receives: `value: unknown`. Sends: `string | null`.
- L176 `function stringArray(value: unknown): string[] | null` — Implements stringarray. Receives: `value: unknown`. Sends: `string[] | null`.

### [`frontend/src/lib/sha256.ts`](../../frontend/src/lib/sha256.ts)

Purpose: Owns sha256 behavior for the frontend application.

- L25 `function rotateRight(value: number, amount: number): number` — Implements rotateright. Receives: `value: number, amount: number`. Sends: `number`.
- L29 `function sha256Hex(value: string): string` — Implements sha256hex. Receives: `value: string`. Sends: `string`.

### [`frontend/src/lib/technical-context.ts`](../../frontend/src/lib/technical-context.ts)

Purpose: Owns technical context behavior for the frontend application.

- L5 `interface TechnicalContextCard` — Defines the structural contract for technicalcontextcard. Receives: `not applicable`. Sends: `type declaration`.
- L16 `interface TechnicalContextData` — Defines the structural contract for technicalcontextdata. Receives: `not applicable`. Sends: `type declaration`.
- L22 `function asRecord(value: unknown): Record<string, unknown> | null` — Implements asrecord. Receives: `value: unknown`. Sends: `Record<string, unknown> | null`.
- L28 `function asArray(value: unknown): unknown[] | null` — Implements asarray. Receives: `value: unknown`. Sends: `unknown[] | null`.
- L32 `function asString(value: unknown): string` — Implements asstring. Receives: `value: unknown`. Sends: `string`.
- L36 `function extractShortPlainMeaning(description: string): string` — Implements extractshortplainmeaning. Receives: `description: string`. Sends: `string`.
- L46 `function resolveCaseRelevance(reason: string): string` — Implements resolvecaserelevance. Receives: `reason: string`. Sends: `string`.
- L58 `function mapSourceMessageIds(sourceIds: string[], allMessages: PersistedChatMessage[]): SourceMessageRef[]` — Implements mapsourcemessageids. Receives: `sourceIds: string[], allMessages: PersistedChatMessage[]`. Sends: `SourceMessageRef[]`.
- L98 `function buildTechnicalContext(messages: PersistedChatMessage[]): TechnicalContextData` — Implements buildtechnicalcontext. Receives: `messages: PersistedChatMessage[]`. Sends: `TechnicalContextData`.
- L132 `interface MitreTableRow` — Defines the structural contract for mitretablerow. Receives: `not applicable`. Sends: `type declaration`.

### [`frontend/src/lib/user-facing-error.ts`](../../frontend/src/lib/user-facing-error.ts)

Purpose: Owns user facing error behavior for the frontend application.

- L3 `type ErrorCategory` — Defines the type contract for errorcategory. Receives: `not applicable`. Sends: `type declaration`.
- L11 `interface UserFacingError` — Defines the structural contract for userfacingerror. Receives: `not applicable`. Sends: `type declaration`.
- L49 `function isTimeoutString(str: string): boolean` — Implements istimeoutstring. Receives: `str: string`. Sends: `boolean`.
- L53 `function isNetworkString(str: string): boolean` — Implements isnetworkstring. Receives: `str: string`. Sends: `boolean`.
- L61 `function isRateLimitString(str: string): boolean` — Implements isratelimitstring. Receives: `str: string`. Sends: `boolean`.
- L65 `function isServerErrorString(str: string): boolean` — Implements isservererrorstring. Receives: `str: string`. Sends: `boolean`.
- L71 `function toUserFacingError(rawError: unknown, options?: { isUncertain?: boolean; actionLabel?: string; }): UserFacingError` — Implements touserfacingerror. Receives: `rawError: unknown, options?: { isUncertain?: boolean; actionLabel?: string; }`. Sends: `UserFacingError`.

## Frontend Regression Suite

### [`frontend/src/test/components/chat/AnalysisEvidenceReferences.test.tsx`](../../frontend/src/test/components/chat/AnalysisEvidenceReferences.test.tsx)

Purpose: Verifies analysisevidencereferences test behavior in the frontend regression suite.

- L7 `function message(id: string, role: "user" | "assistant", content: string, metadata: Record<string, unknown>): PersistedChatMessage` — Implements message. Receives: `id: string, role: "user" | "assistant", content: string, metadata: Record<string, unknown>`. Sends: `PersistedChatMessage`.
- L121 `function citation(exactQuote: string, sourceMessageId: string, documentId: string, filename: string, pageNumber: number)` — Implements citation. Receives: `exactQuote: string, sourceMessageId: string, documentId: string, filename: string, pageNumber: number`. Sends: `inferred or void`.

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

### [`frontend/src/test/components/common/UserProfileMenu.test.tsx`](../../frontend/src/test/components/common/UserProfileMenu.test.tsx)

Purpose: Verifies userprofilemenu test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/home/HomePage.test.tsx`](../../frontend/src/test/components/home/HomePage.test.tsx)

Purpose: Verifies homepage test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/CaseIntakeFiles.test.tsx`](../../frontend/src/test/components/intake/CaseIntakeFiles.test.tsx)

Purpose: Verifies caseintakefiles test behavior in the frontend regression suite.

- L19 `function chooseDocument(filename: string)` — Implements choosedocument. Receives: `filename: string`. Sends: `inferred or void`.
- L25 `function filesPanel()` — Implements filespanel. Receives: `not applicable`. Sends: `inferred or void`.
- L29 `function evidenceMessage(id: string, evidenceKind: PersistedChatMessage["metadata_json"]["evidence_kind"], documentSources: NonNullable<PersistedChatMessage["metadata_json"]["document_sources"]>, role: PersistedChatMessa` — Implements evidencemessage. Receives: `id: string, evidenceKind: PersistedChatMessage["metadata_json"]["evidence_kind"], documentSources: NonNullable<PersistedChatMessage["metadata_json"]["document_sources"]>, role: PersistedChatMessage["role"] = "user"`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/components/intake/CaseIntakeView.test.tsx`](../../frontend/src/test/components/intake/CaseIntakeView.test.tsx)

Purpose: Verifies caseintakeview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/DocumentIngestionPreview.test.tsx`](../../frontend/src/test/components/intake/DocumentIngestionPreview.test.tsx)

Purpose: Verifies documentingestionpreview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/ExtractedTextPreview.test.tsx`](../../frontend/src/test/components/intake/ExtractedTextPreview.test.tsx)

Purpose: Verifies extractedtextpreview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/intake/IntakePreparation.test.tsx`](../../frontend/src/test/components/intake/IntakePreparation.test.tsx)

Purpose: Verifies intakepreparation test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/layout/WorkspaceSidebar.test.tsx`](../../frontend/src/test/components/layout/WorkspaceSidebar.test.tsx)

Purpose: Verifies workspacesidebar test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/materials/CaseMaterialsView.test.tsx`](../../frontend/src/test/components/materials/CaseMaterialsView.test.tsx)

Purpose: Verifies casematerialsview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/overview/CaseFindingsSection.test.tsx`](../../frontend/src/test/components/overview/CaseFindingsSection.test.tsx)

Purpose: Verifies casefindingssection test behavior in the frontend regression suite.

- L7 `function finding(id: string, claimType: ClaimType = "reported", epistemicStatus: EpistemicStatus = "reported"): CaseFinding` — Implements finding. Receives: `id: string, claimType: ClaimType = "reported", epistemicStatus: EpistemicStatus = "reported"`. Sends: `CaseFinding`.

### [`frontend/src/test/components/overview/CaseOverviewView.test.tsx`](../../frontend/src/test/components/overview/CaseOverviewView.test.tsx)

Purpose: Verifies caseoverviewview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/overview/mock-native-dialog.ts`](../../frontend/src/test/components/overview/mock-native-dialog.ts)

Purpose: Verifies mock native dialog behavior in the frontend regression suite.

- L3 `function mockNativeDialog()` — Implements mocknativedialog. Receives: `not applicable`. Sends: `inferred or void`.
- L8 `value(this: HTMLDialogElement)` — Implements value. Receives: `this: HTMLDialogElement`. Sends: `inferred or void`.
- L12 `value(this: HTMLDialogElement)` — Implements value. Receives: `this: HTMLDialogElement`. Sends: `inferred or void`.

### [`frontend/src/test/components/overview/overview-fixtures.ts`](../../frontend/src/test/components/overview/overview-fixtures.ts)

Purpose: Verifies overview fixtures behavior in the frontend regression suite.

- L3 `function sourceMessage(id: string, ordinal: number, content: string): PersistedChatMessage` — Implements sourcemessage. Receives: `id: string, ordinal: number, content: string`. Sends: `PersistedChatMessage`.
- L18 `function analysisMessage(cyber = true): PersistedChatMessage` — Implements analysismessage. Receives: `cyber = true`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/components/overview/OverviewMetadata.test.tsx`](../../frontend/src/test/components/overview/OverviewMetadata.test.tsx)

Purpose: Verifies overviewmetadata test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/components/overview/SourceEvidencePopover.test.tsx`](../../frontend/src/test/components/overview/SourceEvidencePopover.test.tsx)

Purpose: Verifies sourceevidencepopover test behavior in the frontend regression suite.

- L111 `function Harness()` — Renders or constructs harness. Receives: `not applicable`. Sends: `inferred or void`.

### [`frontend/src/test/components/report/ChatReportView.test.tsx`](../../frontend/src/test/components/report/ChatReportView.test.tsx)

Purpose: Verifies chatreportview test behavior in the frontend regression suite.

- L7 `function sampleReport(): api.ChatReportRead` — Implements samplereport. Receives: `not applicable`. Sends: `api.ChatReportRead`.

### [`frontend/src/test/components/report/PersistedReportCard.test.tsx`](../../frontend/src/test/components/report/PersistedReportCard.test.tsx)

Purpose: Verifies persistedreportcard test behavior in the frontend regression suite.

- L9 `function sampleReport(): ChatReportRead` — Implements samplereport. Receives: `not applicable`. Sends: `ChatReportRead`.

### [`frontend/src/test/components/technical/TechnicalContextView.test.tsx`](../../frontend/src/test/components/technical/TechnicalContextView.test.tsx)

Purpose: Verifies technicalcontextview test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/account-draft-persistence.test.tsx`](../../frontend/src/test/features/chat/account-draft-persistence.test.tsx)

Purpose: Verifies account draft persistence test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-interrupted-retry.test.tsx`](../../frontend/src/test/features/chat/chat-interrupted-retry.test.tsx)

Purpose: Verifies chat interrupted retry test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-polling.test.ts`](../../frontend/src/test/features/chat/chat-polling.test.ts)

Purpose: Verifies chat polling test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-route.test.ts`](../../frontend/src/test/features/chat/chat-route.test.ts)

Purpose: Verifies chat route test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-session-selection.test.tsx`](../../frontend/src/test/features/chat/chat-session-selection.test.tsx)

Purpose: Verifies chat session selection test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-session-test-support.tsx`](../../frontend/src/test/features/chat/chat-session-test-support.tsx)

Purpose: Verifies chat session support behavior in the frontend regression suite.

- L10 `function message(threadId: string, ordinal: number, role: "user" | "assistant", content: string = role): PersistedChatMessage` — Implements message. Receives: `threadId: string, ordinal: number, role: "user" | "assistant", content: string = role`. Sends: `PersistedChatMessage`.
- L17 `function thread(id = "a", status: ThreadStatus = "idle", messages: PersistedChatMessage[] = []): ChatThreadDetail` — Implements thread. Receives: `id = "a", status: ThreadStatus = "idle", messages: PersistedChatMessage[] = []`. Sends: `ChatThreadDetail`.
- L24 `function caseRecord(id = "a", status: ThreadStatus = "idle"): CaseRead` — Implements caserecord. Receives: `id = "a", status: ThreadStatus = "idle"`. Sends: `CaseRead`.
- L35 `function accepted(request: PersistedChatMessage): ChatMessageAccepted` — Implements accepted. Receives: `request: PersistedChatMessage`. Sends: `ChatMessageAccepted`.
- L46 `function deferred()` — Implements deferred. Receives: `not applicable`. Sends: `inferred or void`.
- L53 `function renderSession()` — Implements rendersession. Receives: `not applicable`. Sends: `inferred or void`.
- L61 `wrapper({ children }: { children: ReactNode })` — Implements wrapper. Receives: `{ children }: { children: ReactNode }`. Sends: `inferred or void`.
- L79 `function tick(milliseconds = 0)` — Implements tick. Receives: `milliseconds = 0`. Sends: `inferred or void`.

### [`frontend/src/test/features/chat/chat-submission-retry.test.tsx`](../../frontend/src/test/features/chat/chat-submission-retry.test.tsx)

Purpose: Verifies chat submission retry test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/features/chat/chat-thread-deletion.test.tsx`](../../frontend/src/test/features/chat/chat-thread-deletion.test.tsx)

Purpose: Verifies chat thread deletion test behavior in the frontend regression suite.

- L16 `function renderDeletion(deleteThread: (id: string) => Promise<void>)` — Implements renderdeletion. Receives: `deleteThread: (id: string) => Promise<void>`. Sends: `inferred or void`.
- L20 `wrapper({ children }: { children: ReactNode })` — Implements wrapper. Receives: `{ children }: { children: ReactNode }`. Sends: `inferred or void`.

### [`frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx`](../../frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx)

Purpose: Verifies chatworkspaceintake test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/analysis-retirement.test.ts`](../../frontend/src/test/lib/analysis-retirement.test.ts)

Purpose: Verifies analysis retirement test behavior in the frontend regression suite.

- L5 `function record(ordinal: number, metadata: Record<string, unknown>): PersistedChatMessage` — Persists record. Receives: `ordinal: number, metadata: Record<string, unknown>`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/lib/case-evidence.test.ts`](../../frontend/src/test/lib/case-evidence.test.ts)

Purpose: Verifies case evidence test behavior in the frontend regression suite.

- L9 `function makeUserMessage(ordinal: number, metadata: Record<string, unknown> = {}, content = "Test content"): PersistedChatMessage` — Implements makeusermessage. Receives: `ordinal: number, metadata: Record<string, unknown> = {}, content = "Test content"`. Sends: `PersistedChatMessage`.
- L26 `function makeAssistantMessage(ordinal: number, metadata: Record<string, unknown> = {}, content = "Assistant response"): PersistedChatMessage` — Implements makeassistantmessage. Receives: `ordinal: number, metadata: Record<string, unknown> = {}, content = "Assistant response"`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/lib/case-materials.test.ts`](../../frontend/src/test/lib/case-materials.test.ts)

Purpose: Verifies case materials test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/case-narrative-document.test.ts`](../../frontend/src/test/lib/case-narrative-document.test.ts)

Purpose: Verifies case narrative document test behavior in the frontend regression suite.

- L9 `function nativeDocument(): IngestedDocumentPreview` — Implements nativedocument. Receives: `not applicable`. Sends: `IngestedDocumentPreview`.

### [`frontend/src/test/lib/case-overview-native.test.ts`](../../frontend/src/test/lib/case-overview-native.test.ts)

Purpose: Verifies case overview native test behavior in the frontend regression suite.

- L11 `function fixture(): { result: CaseAnalysisResultRead; snapshot: CaseEvidenceSnapshotRead }` — Implements fixture. Receives: `not applicable`. Sends: `{ result: CaseAnalysisResultRead; snapshot: CaseEvidenceSnapshotRead }`.

### [`frontend/src/test/lib/case-overview.test.ts`](../../frontend/src/test/lib/case-overview.test.ts)

Purpose: Verifies case overview test behavior in the frontend regression suite.

- L6 `function message(id: string, ordinal: number, role: "user" | "assistant", content: string, metadata_json: Record<string, unknown>): PersistedChatMessage` — Implements message. Receives: `id: string, ordinal: number, role: "user" | "assistant", content: string, metadata_json: Record<string, unknown>`. Sends: `PersistedChatMessage`.
- L25 `function v3Trace(overrides: Record<string, unknown> = {}): Record<string, unknown>` — Implements v3trace. Receives: `overrides: Record<string, unknown> = {}`. Sends: `Record<string, unknown>`.

### [`frontend/src/test/lib/chat-followup.test.ts`](../../frontend/src/test/lib/chat-followup.test.ts)

Purpose: Verifies chat followup test behavior in the frontend regression suite.

- L11 `function message(ordinal: number, role: PersistedChatMessage["role"], content: string, metadata_json: Record<string, unknown> = {}): PersistedChatMessage` — Implements message. Receives: `ordinal: number, role: PersistedChatMessage["role"], content: string, metadata_json: Record<string, unknown> = {}`. Sends: `PersistedChatMessage`.
- L29 `function clarification(ordinal: number, content: string, round: number): PersistedChatMessage` — Implements clarification. Receives: `ordinal: number, content: string, round: number`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/lib/evidence-citation.test.ts`](../../frontend/src/test/lib/evidence-citation.test.ts)

Purpose: Verifies evidence citation test behavior in the frontend regression suite.

- L10 `function message(content: string, documentSources: Record<string, unknown>[] = []): PersistedChatMessage` — Implements message. Receives: `content: string, documentSources: Record<string, unknown>[] = []`. Sends: `PersistedChatMessage`.
- L29 `function documentForPages(pages: Array<[number, string]>): Record<string, unknown>` — Implements documentforpages. Receives: `pages: Array<[number, string]>`. Sends: `Record<string, unknown>`.
- L49 `function citation(exactQuote: string, pageNumbers: number[])` — Implements citation. Receives: `exactQuote: string, pageNumbers: number[]`. Sends: `inferred or void`.

### [`frontend/src/test/lib/mitre-candidate.test.ts`](../../frontend/src/test/lib/mitre-candidate.test.ts)

Purpose: Verifies mitre candidate test behavior in the frontend regression suite.

- L6 `function message(metadataOverrides: Record<string, unknown> = {}): PersistedChatMessage` — Implements message. Receives: `metadataOverrides: Record<string, unknown> = {}`. Sends: `PersistedChatMessage`.

### [`frontend/src/test/lib/technical-context.test.ts`](../../frontend/src/test/lib/technical-context.test.ts)

Purpose: Verifies technical context test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/lib/user-facing-error.test.ts`](../../frontend/src/test/lib/user-facing-error.test.ts)

Purpose: Verifies user facing error test behavior in the frontend regression suite.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`frontend/src/test/setup.ts`](../../frontend/src/test/setup.ts)

Purpose: Verifies setup behavior in the frontend regression suite.

- L3 `class MockResizeObserver` — Encapsulates mockresizeobserver. Receives: `constructor arguments and class fields`. Sends: `MockResizeObserver`.
- L4 `observe()` — Implements observe. Receives: `not applicable`. Sends: `inferred or void`.
- L5 `unobserve()` — Implements unobserve. Receives: `not applicable`. Sends: `inferred or void`.
- L6 `disconnect()` — Implements disconnect. Receives: `not applicable`. Sends: `inferred or void`.
- L15 `get()` — Retrieves get. Receives: `not applicable`. Sends: `inferred or void`.
- L21 `get()` — Retrieves get. Receives: `not applicable`. Sends: `inferred or void`.
- L27 `get()` — Retrieves get. Receives: `not applicable`. Sends: `inferred or void`.
- L33 `get()` — Retrieves get. Receives: `not applicable`. Sends: `inferred or void`.

## Graphrag Runtime And Evaluation Package

### [`rag_service/app/main.py`](../../rag_service/app/main.py)

Purpose: Owns main behavior for the GraphRAG runtime and evaluation package.

- L16 `async def lifespan(app: FastAPI)` — Startup / shutdown lifecycle. Receives: `app: FastAPI`. Sends: `inferred or None`.

### [`rag_service/app/RAG/__init__.py`](../../rag_service/app/RAG/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/__init__.py`](../../rag_service/app/RAG/GraphRAG/__init__.py)

Purpose: MITRE ATT&CK GraphRAG Pipeline ================================ Hybrid Graph + Vector DB RAG with Cross-Lingual (Thai ↔ English) support.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/config.py`](../../rag_service/app/RAG/GraphRAG/config.py)

Purpose: Central Configuration for MITRE ATT&CK GraphRAG.

- L46 `def _resolve_device() -> str` — Implements resolve device. Receives: `not applicable`. Sends: `str`.
- L110 `def validate_core_llm_provider(value: str) -> str` — Validates core llm provider. Receives: `value: str`. Sends: `str`.
- L313 `def sep(title='')` — Print a separator line for console output. Receives: `title=''`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/docs/make_retrieval_ranking_report.py`](../../rag_service/app/RAG/GraphRAG/docs/make_retrieval_ranking_report.py)

Purpose: Build the Thai progress report PDF for the real-CTI evaluation work.

- L55 `def P(t, s='body')` — Renders or constructs p. Receives: `t, s='body'`. Sends: `inferred or None`.
- L59 `def code(lines)` — Implements code. Receives: `lines`. Sends: `inferred or None`.
- L63 `def table(rows, widths, header=True, aligns=None)` — Implements table. Receives: `rows, widths, header=True, aligns=None`. Sends: `inferred or None`.
- L89 `def chrome(canvas, doc)` — Implements chrome. Receives: `canvas, doc`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/__init__.py)

Purpose: RAG Evaluation Framework ========================= Modular evaluation for retriever quality, generation quality (RAGAS), and end-to-end GraphRAG pipeline performance.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/attack_id_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/attack_id_metrics.py)

Purpose: ATT&CK ID-Based Generation Metrics ==================================== Deterministic metrics for scoring generated answers against gold ATT&CK technique IDs — TRAM/CTIBench-style correctness scoring, plus guard metrics for the Thai output contract.

- L53 `def extract_attack_ids(text: str) -> set[str]` — All MITRE ATT&CK IDs (any entity kind) in the text, uppercased. Receives: `text: str`. Sends: `set[str]`.
- L58 `def extract_technique_ids(text: str) -> set[str]` — Technique IDs only (T####/T####.###), excluding tactics (TA####). Receives: `text: str`. Sends: `set[str]`.
- L66 `def extract_technique_names(text: str, alias_map: dict[str, str]) -> set[str]` — Technique IDs whose canonical name/alias appears in the text. Receives: `text: str, alias_map: dict[str, str]`. Sends: `set[str]`.
- L88 `def extract_all_techniques(text: str, alias_map: Optional[dict[str, str]]=None) -> set[str]` — Union of ID-cited and name-cited techniques in the answer. Receives: `text: str, alias_map: Optional[dict[str, str]]=None`. Sends: `set[str]`.
- L100 `def _base_technique(attack_id: str) -> str` — T1566.002 -> T1566; T1566 -> T1566. Receives: `attack_id: str`. Sends: `str`.
- L105 `def technique_set_score(predicted: set[str], gold: set[str]) -> dict` — Soft precision/recall/F1 between predicted and gold technique IDs. Receives: `predicted: set[str], gold: set[str]`. Sends: `dict`.
- L160 `def tactic_level_score(predicted: set[str], gold: set[str], technique_to_tactics: dict[str, list[str]]) -> dict` — Set precision/recall/F1 at the tactic level (coarser credit). Receives: `predicted: set[str], gold: set[str], technique_to_tactics: dict[str, list[str]]`. Sends: `dict`.
- L171 `def tactics_of(ids: set[str]) -> set[str]` — Implements tactics of. Receives: `ids: set[str]`. Sends: `set[str]`.
- L206 `def thai_char_ratio(text: str) -> float` — Thai letters / (Thai + Latin letters). Receives: `text: str`. Sends: `float`.
- L220 `def structure_compliance(text: str, required_headings: list[str]) -> dict` — Which required section headings appear in the answer (case-insensitive). Receives: `text: str, required_headings: list[str]`. Sends: `dict`.
- L232 `def id_survival(source_text: str, translated_text: str) -> dict` — Technique IDs preserved across the translation stage. Receives: `source_text: str, translated_text: str`. Sends: `dict`.

### [`rag_service/app/RAG/GraphRAG/evaluation/build_deprecated_blocklist.py`](../../rag_service/app/RAG/GraphRAG/evaluation/build_deprecated_blocklist.py)

Purpose: Build Deprecated/Revoked ATT&CK ID Blocklist ============================================== The Neo4j graph does not store `revoked` / `x_mitre_deprecated` flags (ingestion drops them), so deprecated techniques like T1064 (Scripting) look identical to live ones and leak into sampled kill-chains.

- L36 `def latest_bundle(domain_dir: Path) -> Path | None` — Newest versioned bundle in a domain folder (e.g. Receives: `domain_dir: Path`. Sends: `Path | None`.
- L50 `def attack_id_of(obj: dict) -> str | None` — Implements attack id of. Receives: `obj: dict`. Sends: `str | None`.
- L57 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/crosslingual_benchmark.py`](../../rag_service/app/RAG/GraphRAG/evaluation/crosslingual_benchmark.py)

Purpose: Cross-Lingual Retrieval Benchmark ================================== Compares three retrieval configurations for Thai queries against the English-only MITRE ATT&CK knowledge base: 1.

- L62 `def load_cache(path: Path) -> dict[str, str]` — Retrieves cache. Receives: `path: Path`. Sends: `dict[str, str]`.
- L69 `def save_cache(cache: dict[str, str], path: Path) -> None` — Persists cache. Receives: `cache: dict[str, str], path: Path`. Sends: `None`.
- L74 `def translate_all(samples: list[EvalSample], cache_path: Path, use_local: bool) -> dict[str, str]` — Translate every query once, reusing/extending the on-disk cache. Receives: `samples: list[EvalSample], cache_path: Path, use_local: bool`. Sends: `dict[str, str]`.
- L113 `class RetrievalBackend` — Shared retrieval stack: one embed model, one reranker, one Qdrant client. Receives: `constructor arguments and class fields`. Sends: `RetrievalBackend`.
- L122 `def __init__(self, with_graph: bool, top_k: int)` — Implements init. Receives: `self, with_graph: bool, top_k: int`. Sends: `inferred or None`.
- L146 `def close(self) -> None` — Implements close. Receives: `self`. Sends: `None`.
- L150 `def retrieve_ids(self, queries: list[str]) -> list[str]` — Implements retrieve ids. Receives: `self, queries: list[str]`. Sends: `list[str]`.
- L155 `def _retrieve_vector_rerank(self, queries: list[str]) -> list[str]` — Implements retrieve vector rerank. Receives: `self, queries: list[str]`. Sends: `list[str]`.
- L165 `def _retrieve_hybrid(self, queries: list[str]) -> list[str]` — Implements retrieve hybrid. Receives: `self, queries: list[str]`. Sends: `list[str]`.
- L190 `def print_comparison(results: list[RetrieverEvalResult]) -> None` — Implements print comparison. Receives: `results: list[RetrieverEvalResult]`. Sends: `None`.
- L227 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.
- L267 `class Tee` — Encapsulates tee. Receives: `constructor arguments and class fields`. Sends: `Tee`.
- L268 `def write(self, data)` — Implements write. Receives: `self, data`. Sends: `inferred or None`.
- L272 `def flush(self)` — Implements flush. Receives: `self`. Sends: `inferred or None`.
- L296 `def trag_fn(query: str) -> list[str]` — Implements trag fn. Receives: `query: str`. Sends: `list[str]`.
- L299 `def thai_direct_fn(query: str) -> list[str]` — Implements thai direct fn. Receives: `query: str`. Sends: `list[str]`.
- L302 `def dual_fn(query: str) -> list[str]` — Implements dual fn. Receives: `query: str`. Sends: `list[str]`.

### [`rag_service/app/RAG/GraphRAG/evaluation/crosslingual_generation_benchmark.py`](../../rag_service/app/RAG/GraphRAG/evaluation/crosslingual_generation_benchmark.py)

Purpose: Cross-Lingual Generation Benchmark ==================================== Compares 5 generation-path variants over FROZEN retrieval contexts, so score differences are attributable to the generation stage only.

- L113 `def load_samples(dataset_path: Path, max_samples: int=0) -> list[dict]` — Thai incident samples with gold IDs (the benchmark's unit of work). Receives: `dataset_path: Path, max_samples: int=0`. Sends: `list[dict]`.
- L143 `def phase_retrieve(samples: list[dict], use_local: bool=False) -> None` — Retrieve ONCE per sample, mirroring the production agent path (_node_retrieve): Thai incident -> decomposer -> native-language sub-queries -> retrieve_multi_quota -> build_context(15/8). Receives: `samples: list[dict], use_local: bool=False`. Sends: `None`.
- L282 `def _invoke(llm, system: str, user: str) -> tuple[str, dict]` — One LLM call -> (text, {input_tokens, output_tokens}). Receives: `llm, system: str, user: str`. Sends: `tuple[str, dict]`.
- L299 `def _sum_usage(*usages: dict) -> dict` — Implements sum usage. Receives: `*usages: dict`. Sends: `dict`.
- L306 `def run_variant(variant: str, ctx: dict, reasoning_llm, cheap_llm) -> dict` — Execute one variant over a cached context. Receives: `variant: str, ctx: dict, reasoning_llm, cheap_llm`. Sends: `dict`.
- L377 `def phase_generate(variants: list[str], reasoning_model: str, cheap_model: str, max_samples: int=0) -> None` — Implements phase generate. Receives: `variants: list[str], reasoning_model: str, cheap_model: str, max_samples: int=0`. Sends: `None`.
- L406 `def make_llm(model: str)` — Implements make llm. Receives: `model: str`. Sends: `inferred or None`.
- L466 `def _bootstrap_ci(deltas: list[float], n_boot: int=10000, seed: int=42) -> tuple[float, float]` — 95% bootstrap CI of the mean of paired deltas. Receives: `deltas: list[float], n_boot: int=10000, seed: int=42`. Sends: `tuple[float, float]`.
- L479 `def _wilcoxon_p(deltas: list[float]) -> float | None` — Two-sided Wilcoxon signed-rank p-value (scipy if available). Receives: `deltas: list[float]`. Sends: `float | None`.
- L491 `def score_row(row: dict, sample: dict, lookup: dict) -> dict` — All deterministic metrics for one (sample, variant) generation. Receives: `row: dict, sample: dict, lookup: dict`. Sends: `dict`.
- L535 `def phase_score(dataset_path: Path) -> None` — Implements phase score. Receives: `dataset_path: Path`. Sends: `None`.
- L615 `def phase_score_retrieval(dataset_path: Path, k_values: tuple[int, ...]=(5, 10, 15, 20)) -> None` — Step-coverage@k of the production retrieval path, per cue_type. Receives: `dataset_path: Path, k_values: tuple[int, ...]=(5, 10, 15, 20)`. Sends: `None`.
- L648 `def mean(vals: list[float]) -> float` — Implements mean. Receives: `vals: list[float]`. Sends: `float`.
- L700 `def _shim_rag_result(raw: dict)` — Rebuild a GraphRAGResult look-alike from cached mapping_raw so the REAL production build_mitre_table runs offline — no logic duplication. Receives: `raw: dict`. Sends: `inferred or None`.
- L726 `def _is_technique_label(label: str) -> bool` — Determines technique label. Receives: `label: str`. Sends: `bool`.
- L730 `def _technique_ids_from_rows(rows) -> set[str]` — Implements technique ids from rows. Receives: `rows`. Sends: `set[str]`.
- L737 `def _raw_retrieval_technique_ids(raw: dict) -> set[str]` — The no-filter baseline: every technique ID retrieval dragged in. Receives: `raw: dict`. Sends: `set[str]`.
- L751 `def phase_score_mapping(dataset_path: Path, thresholds: list[float]) -> None` — Implements phase score mapping. Receives: `dataset_path: Path, thresholds: list[float]`. Sends: `None`.
- L798 `def _mean(dicts: list[dict], key: str) -> float` — Implements mean. Receives: `dicts: list[dict], key: str`. Sends: `float`.
- L869 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/__init__.py)

Purpose: Embedding-model A/B experiment (thesis section 5.1).

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/arms.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/arms.py)

Purpose: The three retrieval arms of the embedding-model comparison.

- L58 `def make_client() -> QdrantClient` — Implements make client. Receives: `not applicable`. Sends: `QdrantClient`.
- L66 `def load_bge()` — Retrieves bge. Receives: `not applicable`. Sends: `inferred or None`.
- L72 `def load_e5()` — Retrieves e5. Receives: `not applicable`. Sends: `inferred or None`.
- L83 `class Hit` — Encapsulates hit. Receives: `constructor arguments and class fields`. Sends: `Hit`.
- L89 `class _ArmBase` — Shared search topology. Receives: `constructor arguments and class fields`. Sends: `_ArmBase`.
- L95 `def __init__(self, client: Optional[QdrantClient]=None)` — Implements init. Receives: `self, client: Optional[QdrantClient]=None`. Sends: `inferred or None`.
- L99 `def _query_collection(self, collection: str, query: str, top_k: int, qdrant_filter: Optional[Filter]) -> list[Hit]` — Implements query collection. Receives: `self, collection: str, query: str, top_k: int, qdrant_filter: Optional[Filter]`. Sends: `list[Hit]`.
- L105 `def _normalize(hits: list[Hit]) -> None` — Normalizes normalize. Receives: `hits: list[Hit]`. Sends: `None`.
- L115 `def search_entities(self, query: str, top_k: int) -> list[Hit]` — Implements search entities. Receives: `self, query: str, top_k: int`. Sends: `list[Hit]`.
- L123 `def search_relationships(self, query: str, top_k: int) -> list[Hit]` — Implements search relationships. Receives: `self, query: str, top_k: int`. Sends: `list[Hit]`.
- L126 `def search_all(self, query: str, top_k: int=VECTOR_TOP_K) -> list[Hit]` — Implements search all. Receives: `self, query: str, top_k: int=VECTOR_TOP_K`. Sends: `list[Hit]`.
- L135 `def retrieve_ids(self, query: str, top_k: int=VECTOR_TOP_K) -> list[str]` — Implements retrieve ids. Receives: `self, query: str, top_k: int=VECTOR_TOP_K`. Sends: `list[str]`.
- L139 `def _parse(points) -> list[Hit]` — Parses parse. Receives: `points`. Sends: `list[Hit]`.
- L151 `class BgeHybridArm(_ArmBase)` — Arm A — the deployed stack: BGE-M3 dense + sparse, Qdrant native RRF. Receives: `constructor arguments and class fields`. Sends: `BgeHybridArm`.
- L159 `def __init__(self, model, client=None)` — Implements init. Receives: `self, model, client=None`. Sends: `inferred or None`.
- L163 `def _encode(self, query: str)` — Serializes encode. Receives: `self, query: str`. Sends: `inferred or None`.
- L174 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection. Receives: `self, collection, query, top_k, qdrant_filter`. Sends: `inferred or None`.
- L191 `class BgeDenseArm(_ArmBase)` — Arm B — BGE-M3 with the sparse component removed. Receives: `constructor arguments and class fields`. Sends: `BgeDenseArm`.
- L203 `def __init__(self, model, client=None)` — Implements init. Receives: `self, model, client=None`. Sends: `inferred or None`.
- L207 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection. Receives: `self, collection, query, top_k, qdrant_filter`. Sends: `inferred or None`.
- L222 `class E5DenseArm(_ArmBase)` — Arm C — multilingual-e5-large, dense only (the model has no sparse head). Receives: `constructor arguments and class fields`. Sends: `E5DenseArm`.
- L230 `def __init__(self, model, client=None)` — Implements init. Receives: `self, model, client=None`. Sends: `inferred or None`.
- L234 `def _query_collection(self, collection, query, top_k, qdrant_filter)` — Implements query collection. Receives: `self, collection, query, top_k, qdrant_filter`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/ingest_e5.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/ingest_e5.py)

Purpose: Re-embed the ATT&CK corpus with multilingual-e5-large into its own Qdrant collections, so arm C can be compared against the BGE-M3 arms.

- L55 `def _client() -> QdrantClient` — Implements client. Receives: `not applicable`. Sends: `QdrantClient`.
- L65 `def _init_collection(client: QdrantClient, name: str) -> None` — Dense-only collection. Receives: `client: QdrantClient, name: str`. Sends: `None`.
- L78 `def _entity_docs(entities) -> tuple[list[str], list[str], list[dict]]` — Identical text/payload construction to VectorLoader.load_entities. Receives: `entities`. Sends: `tuple[list[str], list[str], list[dict]]`.
- L100 `def _relationship_docs(relationships) -> tuple[list[str], list[str], list[dict]]` — Identical text/payload construction to VectorLoader.load_relationships. Receives: `relationships`. Sends: `tuple[list[str], list[str], list[dict]]`.
- L122 `def _load(client, model, collection: str, ids, docs, metas, label: str) -> int` — Retrieves load. Receives: `client, model, collection: str, ids, docs, metas, label: str`. Sends: `int`.
- L168 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/embed_ab/run_ab.py`](../../rag_service/app/RAG/GraphRAG/evaluation/embed_ab/run_ab.py)

Purpose: Run the embedding-model A/B/C comparison and write a report.

- L57 `def _pair_key(s: EvalSample) -> tuple` — Thai variants copy their source sample's gold IDs verbatim, so (category, gold set) identifies a translation pair. Receives: `s: EvalSample`. Sends: `tuple`.
- L63 `def build_pairs(samples: list[EvalSample], max_pairs: int, seed: int=42)` — Return [(th_sample, en_sample)], stratified across categories. Receives: `samples: list[EvalSample], max_pairs: int, seed: int=42`. Sends: `inferred or None`.
- L101 `def gold_coverage(client, pairs, collections_pair) -> dict` — What fraction of gold STIX IDs actually exist as points in the corpus? Gold comes from Neo4j; the vector corpus drops entities/relationships that have no description. Receives: `client, pairs, collections_pair`. Sends: `dict`.
- L127 `def run_arm(arm, pairs, lang_label: str) -> dict` — Executes arm. Receives: `arm, pairs, lang_label: str`. Sends: `dict`.
- L143 `def _fmt(v) -> str` — Implements fmt. Receives: `v`. Sends: `str`.
- L147 `def write_report(rows: list[dict], coverage: dict, out_dir: Path, meta: dict) -> Path` — Implements write report. Receives: `rows: list[dict], coverage: dict, out_dir: Path, meta: dict`. Sends: `Path`.
- L199 `def main() -> int` — Implements main. Receives: `not applicable`. Sends: `int`.

### [`rag_service/app/RAG/GraphRAG/evaluation/eval_runner.py`](../../rag_service/app/RAG/GraphRAG/evaluation/eval_runner.py)

Purpose: Evaluation Runner ================== CLI orchestrator for RAG evaluation.

- L47 `def _make_vector_retriever_fn(embed_model=None)` — Create a retriever function for vector-only search. Receives: `embed_model=None`. Sends: `inferred or None`.
- L53 `def fn(query: str) -> list[str]` — Implements fn. Receives: `query: str`. Sends: `list[str]`.
- L60 `def _make_graph_retriever_fn()` — Create a retriever function for graph-only search (requires STIX IDs as seed). Receives: `not applicable`. Sends: `inferred or None`.
- L71 `def fn(query: str) -> list[str]` — Implements fn. Receives: `query: str`. Sends: `list[str]`.
- L127 `def _subtechnique_parent_map() -> dict[str, str]` — sub-technique stix_id -> parent technique stix_id. Receives: `not applicable`. Sends: `dict[str, str]`.
- L167 `def _normalise_to_parent(fn, parent_map: dict[str, str])` — Wrap a retriever fn so its ids are parent-granular, like the gold. Receives: `fn, parent_map: dict[str, str]`. Sends: `inferred or None`.
- L178 `def wrapped(query: str) -> list[str]` — Implements wrapped. Receives: `query: str`. Sends: `list[str]`.
- L191 `def _collect_hybrid_ids(result) -> list[str]` — Flatten a GraphRAGResult into an ordered, deduped STIX-id list (vector hits first, then each subgraph's center node + neighbors). Receives: `result`. Sends: `list[str]`.
- L211 `def _make_hybrid_retriever_fn(embed_model=None)` — Create a retriever function for hybrid (Vector + Graph) search — single-query baseline (no decomposition). Receives: `embed_model=None`. Sends: `inferred or None`.
- L218 `def fn(query: str) -> list[str]` — Implements fn. Receives: `query: str`. Sends: `list[str]`.
- L225 `def _make_hybrid_quota_retriever_fn(embed_model=None, use_local: bool=False)` — Hybrid retriever with query decomposition + per-query quota — mirrors the production agent path (``_node_retrieve``). Receives: `embed_model=None, use_local: bool=False`. Sends: `inferred or None`.
- L244 `def fn(query: str) -> list[str]` — Implements fn. Receives: `query: str`. Sends: `list[str]`.
- L268 `def _make_generation_fn(embed_model=None)` — Create a generation function wrapping GraphRAGAgent — the served path. Receives: `embed_model=None`. Sends: `inferred or None`.
- L287 `def fn(query: str) -> tuple[str, list[str]]` — Returns (answer, list_of_context_chunks). Receives: `query: str`. Sends: `tuple[str, list[str]]`.
- L312 `class _ArmSkipped(Exception)` — Raised to skip an arm the caller did not select in --arms. Receives: `constructor arguments and class fields`. Sends: `_ArmSkipped`.
- L316 `class EvalRunner` — Orchestrates the full evaluation pipeline. Receives: `constructor arguments and class fields`. Sends: `EvalRunner`.
- L324 `def __init__(self, dataset_path: str, mode: str='full', use_local: bool=False, max_samples: int=0, arms: tuple[str, ...] | None=None, k_values: list[int] | None=None)` — Implements init. Receives: `self, dataset_path: str, mode: str='full', use_local: bool=False, max_samples: int=0, arms: tuple[str, ...] | None=None, k_values: list[int] | None=None`. Sends: `inferred or None`.
- L356 `def _get_embed_model(self)` — Lazy-load and share the embedding model. Receives: `self`. Sends: `inferred or None`.
- L366 `def run(self) -> dict` — Execute evaluation and return results dict. Receives: `self`. Sends: `dict`.
- L386 `def _run_retriever_eval(self) -> list[RetrieverEvalResult]` — Run retriever benchmarks on all 3 retriever modes. Receives: `self`. Sends: `list[RetrieverEvalResult]`.
- L486 `def _run_generation_eval(self) -> GenerationEvalResult` — Run generation evaluation. Receives: `self`. Sends: `GenerationEvalResult`.
- L502 `def _print_comparison(self, results: list[RetrieverEvalResult]) -> None` — Print a side-by-side comparison table. Receives: `self, results: list[RetrieverEvalResult]`. Sends: `None`.
- L550 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.
- L612 `class Tee` — Encapsulates tee. Receives: `constructor arguments and class fields`. Sends: `Tee`.
- L613 `def write(self, data)` — Implements write. Receives: `self, data`. Sends: `inferred or None`.
- L617 `def flush(self)` — Implements flush. Receives: `self`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/export_alias_tables.py`](../../rag_service/app/RAG/GraphRAG/evaluation/export_alias_tables.py)

Purpose: Export Alias / Tactic Lookup Tables from Neo4j ================================================ One-off export for attack_id_metrics.py: - alias_map : lowercased technique name -> attack_id, used by extract_technique_names() to credit answers that name a technique without citing its ID - technique_to_tactics : attack_id -> tactic shortnames, used by tactic_level_score() Output: evaluation/data/attack_lookup.json Usage: cd rag_service/app/RAG/GraphRAG python -m evaluation.export_alias_tables.

- L49 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/generate_eval_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/generate_eval_dataset.py)

Purpose: Neo4j-Grounded Evaluation Dataset Generator ============================================= Generates a validated evaluation dataset by querying Neo4j directly, eliminating manual ground-truth labeling errors.

- L59 `class GeneratedSample` — A single generated evaluation sample. Receives: `constructor arguments and class fields`. Sends: `GeneratedSample`.
- L82 `def to_dict(self) -> dict` — Transforms dict. Receives: `self`. Sends: `dict`.
- L100 `class Neo4jGroundTruthBuilder` — Connects to Neo4j and runs Cypher queries for ground truth extraction. Receives: `constructor arguments and class fields`. Sends: `Neo4jGroundTruthBuilder`.
- L103 `def __init__(self)` — Implements init. Receives: `self`. Sends: `inferred or None`.
- L107 `def close(self)` — Implements close. Receives: `self`. Sends: `inferred or None`.
- L110 `def run_query(self, cypher: str, params: dict | None=None) -> list[dict]` — Execute a Cypher query and return results as list of dicts. Receives: `self, cypher: str, params: dict | None=None`. Sends: `list[dict]`.
- L118 `def get_top_techniques(self, limit: int=15) -> list[dict]` — Find techniques with the most relationships (well-connected nodes). Receives: `self, limit: int=15`. Sends: `list[dict]`.
- L130 `def get_top_groups(self, limit: int=12) -> list[dict]` — Find groups with the most USES relationships. Receives: `self, limit: int=12`. Sends: `list[dict]`.
- L141 `def get_top_software(self, limit: int=12) -> list[dict]` — Find software with the most USES relationships. Receives: `self, limit: int=12`. Sends: `list[dict]`.
- L153 `def get_all_tactics(self) -> list[dict]` — Get all tactics. Receives: `self`. Sends: `list[dict]`.
- L162 `def get_groups_with_campaigns(self, limit: int=8) -> list[dict]` — Find groups that have campaigns attributed to them. Receives: `self, limit: int=8`. Sends: `list[dict]`.
- L174 `def get_techniques_with_detection(self, limit: int=10) -> list[dict]` — Find techniques that have DataComponent detection links. Receives: `self, limit: int=10`. Sends: `list[dict]`.
- L187 `def get_techniques_by_attack_ids(self, attack_ids: list[str]) -> dict[str, str]` — Return {attack_id: stix_id} for the given ATT&CK IDs (techniques + subtechniques). Receives: `self, attack_ids: list[str]`. Sends: `dict[str, str]`.
- L211 `class QueryTemplateRegistry` — Defines evaluation query templates that map to Cypher traversal patterns. Receives: `constructor arguments and class fields`. Sends: `QueryTemplateRegistry`.
- L214 `def __init__(self, neo4j: Neo4jGroundTruthBuilder)` — Implements init. Receives: `self, neo4j: Neo4jGroundTruthBuilder`. Sends: `inferred or None`.
- L219 `def generate_mitigation_lookup(self, technique: dict) -> GeneratedSample | None` — 'What mitigations exist for [technique]?' → MITIGATES relationship. Receives: `self, technique: dict`. Sends: `GeneratedSample | None`.
- L269 `def generate_technique_lookup(self, technique: dict) -> GeneratedSample | None` — 'What is [technique] ([ATT&CK ID])?' → node + subtechniques + description. Receives: `self, technique: dict`. Sends: `GeneratedSample | None`.
- L315 `def generate_group_software(self, group: dict) -> GeneratedSample | None` — 'What tools and malware does [group] use?' → USES→Software. Receives: `self, group: dict`. Sends: `GeneratedSample | None`.
- L361 `def generate_group_techniques(self, group: dict) -> GeneratedSample | None` — 'What techniques does [group] use?' → USES→Technique. Receives: `self, group: dict`. Sends: `GeneratedSample | None`.
- L397 `def generate_tactic_techniques(self, tactic: dict) -> GeneratedSample | None` — 'What are all [tactic] techniques?' → IN_TACTIC relationship. Receives: `self, tactic: dict`. Sends: `GeneratedSample | None`.
- L431 `def generate_software_techniques(self, software: dict) -> GeneratedSample | None` — 'What techniques does [software] use?' → USES→Technique. Receives: `self, software: dict`. Sends: `GeneratedSample | None`.
- L466 `def generate_technique_detection(self, technique: dict) -> GeneratedSample | None` — 'How can I detect [technique]?' → DETECTS relationship. Receives: `self, technique: dict`. Sends: `GeneratedSample | None`.
- L509 `def generate_technique_groups(self, technique: dict) -> GeneratedSample | None` — 'What groups use [technique]?' → Group-USES→Technique. Receives: `self, technique: dict`. Sends: `GeneratedSample | None`.
- L543 `def generate_campaign_attribution(self, group: dict) -> GeneratedSample | None` — 'What campaigns are attributed to [group]?' → ATTRIBUTED_TO relationship. Receives: `self, group: dict`. Sends: `GeneratedSample | None`.
- L606 `def _make_thai_variant(sample: GeneratedSample, seed_node: dict) -> GeneratedSample | None` — Create a Thai-language variant of an English sample. Receives: `sample: GeneratedSample, seed_node: dict`. Sends: `GeneratedSample | None`.
- L1185 `class IncidentScenarioGenerator` — Generates incident-style evaluation samples grounded in Neo4j STIX IDs. Receives: `constructor arguments and class fields`. Sends: `IncidentScenarioGenerator`.
- L1188 `def __init__(self, neo4j: Neo4jGroundTruthBuilder)` — Implements init. Receives: `self, neo4j: Neo4jGroundTruthBuilder`. Sends: `inferred or None`.
- L1191 `def generate(self) -> list[GeneratedSample]` — Build all incident samples, looking up STIX IDs from Neo4j. Receives: `self`. Sends: `list[GeneratedSample]`.
- L1257 `class DatasetGenerator` — Iterates query templates × seed nodes to generate evaluation samples. Receives: `constructor arguments and class fields`. Sends: `DatasetGenerator`.
- L1260 `def __init__(self, neo4j: Neo4jGroundTruthBuilder, thai_ratio: float=0.2)` — Implements init. Receives: `self, neo4j: Neo4jGroundTruthBuilder, thai_ratio: float=0.2`. Sends: `inferred or None`.
- L1265 `def generate(self) -> list[GeneratedSample]` — Generate the full evaluation dataset. Receives: `self`. Sends: `list[GeneratedSample]`.
- L1270 `def _add(sample: GeneratedSample | None, seed: dict | None=None) -> None` — Add sample if valid and not duplicate. Receives: `sample: GeneratedSample | None, seed: dict | None=None`. Sends: `None`.
- L1439 `class ValidationResult` — Result of dataset validation. Receives: `constructor arguments and class fields`. Sends: `ValidationResult`.
- L1446 `def summary(self) -> str` — Implements summary. Receives: `self`. Sends: `str`.
- L1483 `class DatasetValidator` — Validates the generated dataset for consistency and completeness. Receives: `constructor arguments and class fields`. Sends: `DatasetValidator`.
- L1486 `def __init__(self, min_samples: int=50, min_categories: int=8)` — Implements init. Receives: `self, min_samples: int=50, min_categories: int=8`. Sends: `inferred or None`.
- L1490 `def validate(self, samples: list[GeneratedSample]) -> ValidationResult` — Run all validation checks. Receives: `self, samples: list[GeneratedSample]`. Sends: `ValidationResult`.
- L1604 `def save_dataset(samples: list[GeneratedSample], output_path: Path) -> None` — Save the generated dataset as JSON. Receives: `samples: list[GeneratedSample], output_path: Path`. Sends: `None`.
- L1616 `def load_dataset_for_validation(path: Path) -> list[GeneratedSample]` — Load an existing dataset JSON for validation. Receives: `path: Path`. Sends: `list[GeneratedSample]`.
- L1641 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/generation_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/generation_metrics.py)

Purpose: Generation (Answer) Evaluation Metrics ======================================== Evaluates the quality of LLM-generated answers using: 1.

- L31 `def _tokenize(text: str) -> list[str]` — Simple whitespace + lowercase tokenizer. Receives: `text: str`. Sends: `list[str]`.
- L36 `def token_f1(prediction: str, reference: str) -> dict[str, float]` — Token-level Precision, Recall, F1 between prediction and reference. Receives: `prediction: str, reference: str`. Sends: `dict[str, float]`.
- L55 `def rouge_l(prediction: str, reference: str) -> float` — ROUGE-L score (longest common subsequence). Receives: `prediction: str, reference: str`. Sends: `float`.
- L87 `def _try_ragas_evaluate(questions: list[str], answers: list[str], contexts: list[list[str]], reference_answers: list[str] | None=None, use_local: bool=False) -> dict[str, list[float]] | None` — Attempt RAGAS evaluation. Receives: `questions: list[str], answers: list[str], contexts: list[list[str]], reference_answers: list[str] | None=None, use_local: bool=False`. Sends: `dict[str, list[float]] | None`.
- L206 `def _try_bertscore(predictions: list[str], references: list[str]) -> list[float] | None` — Attempt BERTScore. Receives: `predictions: list[str], references: list[str]`. Sends: `list[float] | None`.
- L234 `class GenerationEvalResult` — Aggregated generation evaluation results. Receives: `constructor arguments and class fields`. Sends: `GenerationEvalResult`.
- L256 `def to_table(self) -> str` — Format results as a printable table. Receives: `self`. Sends: `str`.
- L294 `def evaluate_generation(query_fn: Callable[[str], tuple[str, list[str]]], samples: list[EvalSample], use_local: bool=False) -> GenerationEvalResult` — Run generation evaluation across all samples. Receives: `query_fn: Callable[[str], tuple[str, list[str]]], samples: list[EvalSample], use_local: bool=False`. Sends: `GenerationEvalResult`.
- L382 `def _safe_mean(key)` — Implements safe mean. Receives: `key`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/ground_truth.py`](../../rag_service/app/RAG/GraphRAG/evaluation/ground_truth.py)

Purpose: Ground Truth Dataset ===================== Data model and I/O for evaluation datasets.

- L21 `class EvalSample` — A single evaluation sample. Receives: `constructor arguments and class fields`. Sends: `EvalSample`.
- L42 `def has_reference_answer(self) -> bool` — Determines reference answer. Receives: `self`. Sends: `bool`.
- L45 `def has_attack_steps(self) -> bool` — Determines attack steps. Receives: `self`. Sends: `bool`.
- L49 `def load_ground_truth(path: str | Path) -> list[EvalSample]` — Load evaluation samples from a JSON file. Receives: `path: str | Path`. Sends: `list[EvalSample]`.
- L96 `def save_ground_truth(samples: list[EvalSample], path: str | Path) -> None` — Save evaluation samples to a JSON file. Receives: `samples: list[EvalSample], path: str | Path`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/make_incident_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/make_incident_dataset.py)

Purpose: Incident Dataset Builder (semi-automated) ========================================== Builds chronological Thai case-file incident samples for the eval dataset: 1.

- L52 `def load_deprecated_blocklist() -> set[str]` — Deprecated/revoked ATT&CK IDs to exclude from chains. Receives: `not applicable`. Sends: `set[str]`.
- L120 `def _tactic_order(tactic: str) -> int` — Implements tactic order. Receives: `tactic: str`. Sends: `int`.
- L127 `def sample_kill_chains(neo4j: Neo4jGroundTruthBuilder, num_chains: int, rng: random.Random, min_steps: int=3, max_steps: int=6, blocked_ids: set[str] | None=None, source: str='group') -> list[dict]` — Sample up to num_chains kill-chains from a Group or a real Campaign. Receives: `neo4j: Neo4jGroundTruthBuilder, num_chains: int, rng: random.Random, min_steps: int=3, max_steps: int=6, blocked_ids: set[str] | None=None, source: str='group'`. Sends: `list[dict]`.
- L281 `def _parse_json_reply(text: str) -> dict` — Parses json reply. Receives: `text: str`. Sends: `dict`.
- L287 `def draft_narrative(llm, chain: dict) -> dict | None` — One LLM call -> {narrative_th, narrative_en, cues}. Receives: `llm, chain: dict`. Sends: `dict | None`.
- L333 `def _entry_from_stored(sid: str, stored: dict, id_to_name: dict[str, str]) -> dict` — Rebuild a review entry from a previously drafted sample (--resume). Receives: `sid: str, stored: dict, id_to_name: dict[str, str]`. Sends: `dict`.
- L362 `def build_sample(idx: int, chain: dict, draft: dict) -> tuple[GeneratedSample, list[str]]` — Assemble a GeneratedSample; returns (sample, review_flags). Receives: `idx: int, chain: dict, draft: dict`. Sends: `tuple[GeneratedSample, list[str]]`.
- L405 `def write_review_md(path: Path, entries: list[dict]) -> None` — Implements write review md. Receives: `path: Path, entries: list[dict]`. Sends: `None`.
- L439 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/__init__.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/__init__.py)

Purpose: Real-CTI evaluation tier.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/build_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/build_dataset.py)

Purpose: Select the real-CTI chain set ============================== Merges the CTID and CISA chain pools into one balanced selection of N chains — the input to Thai case-file drafting, not yet an eval dataset.

- L49 `def _load(path: Path) -> list[dict]` — Retrieves load. Receives: `path: Path`. Sends: `list[dict]`.
- L55 `def _bucket_key(chain: dict) -> str` — The document a chain came from — the unit diversity is spread over. Receives: `chain: dict`. Sends: `str`.
- L60 `def round_robin(chains: list[dict], want: int, rng: random.Random) -> list[dict]` — Take up to `want` chains, cycling over source documents. Receives: `chains: list[dict], want: int, rng: random.Random`. Sends: `list[dict]`.
- L85 `def select(num: int, seed: int, ctid_share: float) -> tuple[list[dict], dict]` — Extracts select. Receives: `num: int, seed: int, ctid_share: float`. Sends: `tuple[list[dict], dict]`.
- L111 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/cisa_loader.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/cisa_loader.py)

Purpose: CISA advisories -> attack chains ================================= Turns the CISA TTP Articles Data Set (see fetch_cisa.py) into chains with the same shape ctid_loader.py produces.

- L91 `def load_lookups() -> tuple[dict[str, list[str]], dict[str, list[str]]]` — Return (attack_id -> tactics, attack_id -> known names/aliases). Receives: `not applicable`. Sends: `tuple[dict[str, list[str]], dict[str, list[str]]]`.
- L100 `def is_observable(attack_id: str, raw_id: str, tactics: dict[str, list[str]]) -> bool` — False when every tactic the technique belongs to is unobservable. Receives: `attack_id: str, raw_id: str, tactics: dict[str, list[str]]`. Sends: `bool`.
- L113 `def extract_technical_details(raw_text: str) -> str` — Extracts technical details. Receives: `raw_text: str`. Sends: `str`.
- L122 `def clean_cue(sentence: str) -> str` — Strip ATT&CK tags and CISA's numeric citations from a cue. Receives: `sentence: str`. Sends: `str`.
- L133 `def parse_advisory(record: dict, tactics: dict[str, list[str]]) -> tuple[str, list[dict]]` — Return (advisory_id, ordered steps) for one advisory record. Receives: `record: dict, tactics: dict[str, list[str]]`. Sends: `tuple[str, list[dict]]`.
- L176 `def order_by_kill_chain(steps: list[dict]) -> list[dict]` — Reorder an advisory's steps into kill-chain phase order. Receives: `steps: list[dict]`. Sends: `list[dict]`.
- L187 `def key(item: tuple[int, dict]) -> tuple[int, int]` — Implements key. Receives: `item: tuple[int, dict]`. Sends: `tuple[int, int]`.
- L197 `def merge_repeat_steps(steps: list[dict]) -> list[dict]` — Drop a step whose technique set repeats the step just before it. Receives: `steps: list[dict]`. Sends: `list[dict]`.
- L219 `def chunk_narrative(steps: list[dict]) -> list[list[dict]]` — Cut an advisory's ordered steps into MIN..MAX-technique chains. Receives: `steps: list[dict]`. Sends: `list[list[dict]]`.
- L227 `def uniq(ss: list[dict]) -> set[str]` — Implements uniq. Receives: `ss: list[dict]`. Sends: `set[str]`.
- L247 `def _tokens(text: str) -> set[str]` — Implements tokens. Receives: `text: str`. Sends: `set[str]`.
- L251 `def classify_cue_type(step: dict, names: dict[str, list[str]]) -> str` — named when the cue spells the technique out, described otherwise. Receives: `step: dict, names: dict[str, list[str]]`. Sends: `str`.
- L286 `def dedupe_revisions(records: list[dict]) -> tuple[list[dict], list[str]]` — Keep one record per advisory, dropping CISA's revision duplicates. Receives: `records: list[dict]`. Sends: `tuple[list[dict], list[str]]`.
- L312 `def build_chains(use_neo4j: bool=True) -> tuple[list[dict], dict]` — Builds chains. Receives: `use_neo4j: bool=True`. Sends: `tuple[list[dict], dict]`.
- L380 `def print_stats(chains: list[dict], report: dict) -> None` — Implements print stats. Receives: `chains: list[dict], report: dict`. Sends: `None`.
- L401 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/ctid_loader.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/ctid_loader.py)

Purpose: CTID Adversary Emulation Library -> attack chains ================================================== Reads the vendored emulation-plan YAMLs (see NOTICE.md) and cuts each plan into chains of consecutive steps suitable for one case-file sample.

- L87 `def _as_list(value) -> list[str]` — Implements as list. Receives: `value`. Sends: `list[str]`.
- L95 `def parse_plan(path: Path) -> tuple[dict, list[dict], list[str], list[str]]` — Return (details, ordered steps, dropped raw ids, applied corrections). Receives: `path: Path`. Sends: `tuple[dict, list[dict], list[str], list[str]]`.
- L145 `def _uniq_ids(steps: list[dict]) -> list[str]` — Implements uniq ids. Receives: `steps: list[dict]`. Sends: `list[str]`.
- L149 `def _split_oversized(group: list[dict]) -> list[list[dict]]` — Cut a single procedure_group that alone exceeds MAX_TECHNIQUES. Receives: `group: list[dict]`. Sends: `list[list[dict]]`.
- L166 `def chunk_steps(steps: list[dict]) -> list[list[dict]]` — Group consecutive steps into chains of MIN..MAX distinct techniques. Receives: `steps: list[dict]`. Sends: `list[list[dict]]`.
- L200 `def collapse_repeats(steps: list[dict]) -> list[dict]` — Merge consecutive steps sharing one technique into a single step. Receives: `steps: list[dict]`. Sends: `list[dict]`.
- L244 `def resolve_stix_ids(attack_ids: set[str]) -> dict[str, str]` — attack_id -> stix_id from Neo4j. Receives: `attack_ids: set[str]`. Sends: `dict[str, str]`.
- L269 `def build_chains(use_neo4j: bool=True) -> tuple[list[dict], dict]` — Builds chains. Receives: `use_neo4j: bool=True`. Sends: `tuple[list[dict], dict]`.
- L316 `def print_stats(chains: list[dict], report: dict) -> None` — Implements print stats. Receives: `chains: list[dict], report: dict`. Sends: `None`.
- L347 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/fetch_cisa.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/fetch_cisa.py)

Purpose: Fetch the CISA TTP Articles Data Set (Zenodo, DOI 10.5281/zenodo.14659512) ========================================================================== 77 CISA cybersecurity advisories (Jul 2020 - Feb 2024) crawled from cisa.gov, kept because they carry an explicit MITRE ATT&CK section.

- L36 `def fetch(force: bool=False) -> Path` — Retrieves fetch. Receives: `force: bool=False`. Sends: `Path`.

### [`rag_service/app/RAG/GraphRAG/evaluation/real_cti/thai_dataset.py`](../../rag_service/app/RAG/GraphRAG/evaluation/real_cti/thai_dataset.py)

Purpose: Thai case-file dataset builder for the real-CTI tier ===================================================== The narratives in CTI_dataset.json are written by hand, chain by chain, not generated by an API call — that is the whole point of this tier.

- L70 `def load_selection() -> dict[str, dict]` — Retrieves selection. Receives: `not applicable`. Sends: `dict[str, dict]`.
- L75 `def step_gold(step: dict) -> list[str]` — Gold ATT&CK IDs of a step, whichever loader produced it. Receives: `step: dict`. Sends: `list[str]`.
- L80 `def step_stix(step: dict) -> list[str]` — Implements step stix. Receives: `step: dict`. Sends: `list[str]`.
- L87 `def step_source_text(step: dict) -> str` — The English text the Thai narrative is rewritten from. Receives: `step: dict`. Sends: `str`.
- L92 `def chain_gold(chain: dict) -> list[str]` — Implements chain gold. Receives: `chain: dict`. Sends: `list[str]`.
- L99 `def chain_stix(chain: dict) -> list[str]` — Implements chain stix. Receives: `chain: dict`. Sends: `list[str]`.
- L111 `def load_dataset() -> dict` — Retrieves dataset. Receives: `not applicable`. Sends: `dict`.
- L127 `def save_dataset(data: dict) -> None` — Persists dataset. Receives: `data: dict`. Sends: `None`.
- L133 `def done_chain_ids(data: dict) -> set[str]` — Implements done chain ids. Receives: `data: dict`. Sends: `set[str]`.
- L142 `def validate(sample: dict, chain: dict, names: dict[str, list[str]]) -> list[str]` — Validates validate. Receives: `sample: dict, chain: dict, names: dict[str, list[str]]`. Sends: `list[str]`.
- L199 `def cmd_status(_args) -> None` — Implements cmd status. Receives: `_args`. Sends: `None`.
- L230 `def cmd_brief(args) -> None` — Implements cmd brief. Receives: `args`. Sends: `None`.
- L246 `def _technique_names(attack_ids: set[str], use_neo4j: bool) -> dict[str, str]` — attack_id -> official name, for the reviewer to check cues against. Receives: `attack_ids: set[str], use_neo4j: bool`. Sends: `dict[str, str]`.
- L273 `def cmd_review(args) -> None` — Implements cmd review. Receives: `args`. Sends: `None`.
- L345 `def cmd_add(args) -> None` — Implements cmd add. Receives: `args`. Sends: `None`.
- L407 `def main() -> None` — Implements main. Receives: `not applicable`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/retriever_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/retriever_metrics.py)

Purpose: Retriever Evaluation Metrics ============================== Pure functions for evaluating retrieval quality.

- L45 `def hit_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — 1.0 if any relevant doc appears in top-K, else 0.0. Receives: `retrieved_ids: list[str], relevant_ids: set[str], k: int`. Sends: `float`.
- L51 `def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Capped recall: hits / min(|relevant|, K). Receives: `retrieved_ids: list[str], relevant_ids: set[str], k: int`. Sends: `float`.
- L67 `def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Fraction of top-K results that are relevant. Receives: `retrieved_ids: list[str], relevant_ids: set[str], k: int`. Sends: `float`.
- L75 `def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float` — Reciprocal rank of the first relevant result (1/rank). Receives: `retrieved_ids: list[str], relevant_ids: set[str]`. Sends: `float`.
- L83 `def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float` — Normalized Discounted Cumulative Gain at K (binary relevance). Receives: `retrieved_ids: list[str], relevant_ids: set[str], k: int`. Sends: `float`.
- L102 `def average_precision(retrieved_ids: list[str], relevant_ids: set[str]) -> float` — Average Precision — average of Precision@k at each relevant position. Receives: `retrieved_ids: list[str], relevant_ids: set[str]`. Sends: `float`.
- L131 `def _step_gold_ids(step: dict) -> set[str]` — Implements step gold ids. Receives: `step: dict`. Sends: `set[str]`.
- L138 `def scoreable_steps(steps: list[dict]) -> list[dict]` — Steps whose gold has at least one STIX ID the retriever could return. Receives: `steps: list[dict]`. Sends: `list[dict]`.
- L149 `def step_coverage_at_k(retrieved_ids: list[str], steps: list[dict], k: int) -> float` — Fraction of steps with at least one gold ID in top-K (S-recall@K). Receives: `retrieved_ids: list[str], steps: list[dict], k: int`. Sends: `float`.
- L158 `def strict_step_coverage_at_k(retrieved_ids: list[str], steps: list[dict], k: int) -> float` — Fraction of steps whose gold IDs ALL appear in top-K. Receives: `retrieved_ids: list[str], steps: list[dict], k: int`. Sends: `float`.
- L170 `def step_best_rank(retrieved_ids: list[str], step: dict) -> Optional[int]` — 1-based rank of the first retrieved ID evidencing the step, else None. Receives: `retrieved_ids: list[str], step: dict`. Sends: `Optional[int]`.
- L183 `def step_coverage_by_cue_type(retrieved_ids: list[str], steps: list[dict], k: int) -> dict[str, float]` — StepCoverage@K broken down by cue_type ("named" vs "described"). Receives: `retrieved_ids: list[str], steps: list[dict], k: int`. Sends: `dict[str, float]`.
- L208 `class RetrieverEvalResult` — Aggregated retriever evaluation results. Receives: `constructor arguments and class fields`. Sends: `RetrieverEvalResult`.
- L237 `def to_table(self) -> str` — Format results as a printable table. Receives: `self`. Sends: `str`.
- L302 `def evaluate_retriever(retriever_fn, samples: list[EvalSample], k_values: list[int] | None=None, retriever_name: str='Retriever') -> RetrieverEvalResult` — Run retriever evaluation across all samples. Receives: `retriever_fn, samples: list[EvalSample], k_values: list[int] | None=None, retriever_name: str='Retriever'`. Sends: `RetrieverEvalResult`.
- L389 `def mean(lst)` — Implements mean. Receives: `lst`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/evaluation/test_metrics.py`](../../rag_service/app/RAG/GraphRAG/evaluation/test_metrics.py)

Purpose: Unit Tests for Evaluation Metrics ==================================== Tests metric functions with known inputs/outputs.

- L49 `def test_hit_at_k()` — Implements test hit at k. Receives: `not applicable`. Sends: `inferred or None`.
- L61 `def test_recall_at_k()` — Implements test recall at k. Receives: `not applicable`. Sends: `inferred or None`.
- L80 `def test_step_coverage_at_k()` — Implements test step coverage at k. Receives: `not applicable`. Sends: `inferred or None`.
- L111 `def test_precision_at_k()` — Implements test precision at k. Receives: `not applicable`. Sends: `inferred or None`.
- L121 `def test_reciprocal_rank()` — Implements test reciprocal rank. Receives: `not applicable`. Sends: `inferred or None`.
- L131 `def test_ndcg_at_k()` — Implements test ndcg at k. Receives: `not applicable`. Sends: `inferred or None`.
- L144 `def test_average_precision()` — Implements test average precision. Receives: `not applicable`. Sends: `inferred or None`.
- L159 `def test_token_f1()` — Implements test token f1. Receives: `not applicable`. Sends: `inferred or None`.
- L167 `def test_rouge_l()` — Implements test rouge l. Receives: `not applicable`. Sends: `inferred or None`.
- L175 `def test_extract_attack_ids()` — Implements test extract attack ids. Receives: `not applicable`. Sends: `inferred or None`.
- L187 `def test_extract_technique_names()` — Implements test extract technique names. Receives: `not applicable`. Sends: `inferred or None`.
- L201 `def test_technique_set_score()` — Implements test technique set score. Receives: `not applicable`. Sends: `inferred or None`.
- L226 `def test_tactic_level_score()` — Implements test tactic level score. Receives: `not applicable`. Sends: `inferred or None`.
- L239 `def test_guard_metrics()` — Implements test guard metrics. Receives: `not applicable`. Sends: `inferred or None`.
- L268 `def test_ground_truth_io()` — Implements test ground truth io. Receives: `not applicable`. Sends: `inferred or None`.
- L302 `def run_all_tests()` — Executes all tests. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/ingestion/__init__.py`](../../rag_service/app/RAG/GraphRAG/ingestion/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/ingestion/graph_loader.py`](../../rag_service/app/RAG/GraphRAG/ingestion/graph_loader.py)

Purpose: Neo4j Graph Database Loader ============================ Loads parsed ATT&CK entities and relationships into Neo4j.

- L18 `class GraphLoader` — Loads ATT&CK data into Neo4j. Receives: `constructor arguments and class fields`. Sends: `GraphLoader`.
- L21 `def __init__(self)` — Implements init. Receives: `self`. Sends: `inferred or None`.
- L25 `def close(self)` — Implements close. Receives: `self`. Sends: `inferred or None`.
- L28 `def clear_database(self)` — Remove all existing nodes and relationships. Receives: `self`. Sends: `inferred or None`.
- L34 `def create_constraints(self)` — Create uniqueness constraints for fast lookups. Receives: `self`. Sends: `inferred or None`.
- L53 `def create_indexes(self)` — Create indexes for common query patterns. Receives: `self`. Sends: `inferred or None`.
- L70 `def load_entities(self, entities: list[AttackEntity]) -> int` — Load all entities as nodes into Neo4j in bulk batches. Receives: `self, entities: list[AttackEntity]`. Sends: `int`.
- L104 `def _entity_to_props(self, entity: AttackEntity) -> dict` — Convert entity to Neo4j property dict. Receives: `self, entity: AttackEntity`. Sends: `dict`.
- L137 `def load_relationships(self, relationships)` — Retrieves relationships. Receives: `self, relationships`. Sends: `inferred or None`.
- L194 `def load_all(self, parser: StixParser) -> None` — Full ingestion: clear → constraints → nodes → edges. Receives: `self, parser: StixParser`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/ingestion/stix_parser.py`](../../rag_service/app/RAG/GraphRAG/ingestion/stix_parser.py)

Purpose: STIX 2.1 Parser for MITRE ATT&CK Data ====================================== Parses enterprise-attack.json and mobile-attack.json into typed entities and relationships matching the schema_design.md specification.

- L32 `def _get_attack_id(obj: dict) -> str` — Extract ATT&CK ID (e.g., T1566) from external_references. Receives: `obj: dict`. Sends: `str`.
- L40 `def _get_url(obj: dict) -> str` — Extract ATT&CK URL from external_references. Receives: `obj: dict`. Sends: `str`.
- L48 `def _is_revoked_or_deprecated(obj: dict) -> bool` — Check if object is revoked or deprecated. Receives: `obj: dict`. Sends: `bool`.
- L53 `def _get_tactics_from_kill_chain(obj: dict) -> list[str]` — Extract tactic shortnames from kill_chain_phases. Receives: `obj: dict`. Sends: `list[str]`.
- L89 `class StixParser` — Parses MITRE ATT&CK STIX 2.1 JSON bundles into entities and relationships. Receives: `constructor arguments and class fields`. Sends: `StixParser`.
- L92 `def __init__(self)` — Implements init. Receives: `self`. Sends: `inferred or None`.
- L103 `def parse_folder(self, folder: Path, domain: str='enterprise') -> None` — Parse STIX bundle JSON files in a folder. Receives: `self, folder: Path, domain: str='enterprise'`. Sends: `None`.
- L124 `def parse_file(self, filepath: Path, domain: str='enterprise', finalize: bool=True) -> None` — Parse a single STIX bundle JSON file. Receives: `self, filepath: Path, domain: str='enterprise', finalize: bool=True`. Sends: `None`.
- L239 `def _parse_technique(self, obj: dict, domain: str) -> Technique` — Parses technique. Receives: `self, obj: dict, domain: str`. Sends: `Technique`.
- L254 `def _parse_group(self, obj: dict, domain: str) -> Group` — Parses group. Receives: `self, obj: dict, domain: str`. Sends: `Group`.
- L265 `def _parse_software(self, obj: dict, stix_type: str, domain: str) -> Software` — Parses software. Receives: `self, obj: dict, stix_type: str, domain: str`. Sends: `Software`.
- L277 `def _parse_campaign(self, obj: dict, domain: str) -> Campaign` — Parses campaign. Receives: `self, obj: dict, domain: str`. Sends: `Campaign`.
- L288 `def _parse_mitigation(self, obj: dict, domain: str) -> Mitigation` — Parses mitigation. Receives: `self, obj: dict, domain: str`. Sends: `Mitigation`.
- L298 `def _parse_tactic(self, obj: dict, domain: str) -> Tactic` — Parses tactic. Receives: `self, obj: dict, domain: str`. Sends: `Tactic`.
- L309 `def _parse_data_source(self, obj: dict, domain: str) -> DataSource` — Parses data source. Receives: `self, obj: dict, domain: str`. Sends: `DataSource`.
- L320 `def _parse_data_component(self, obj: dict, domain: str) -> DataComponent` — Parses data component. Receives: `self, obj: dict, domain: str`. Sends: `DataComponent`.
- L331 `def _build_relationships(self, raw_rels: list[dict]) -> None` — Build typed relationships from raw STIX relationship objects. Receives: `self, raw_rels: list[dict]`. Sends: `None`.
- L363 `def _build_tactic_edges(self) -> None` — Derive IN_TACTIC edges from technique kill_chain_phases. Receives: `self`. Sends: `None`.
- L387 `def _build_data_source_edges(self) -> None` — Derive HAS_COMPONENT edges from x_mitre_data_source_ref. Receives: `self`. Sends: `None`.
- L409 `def get_entities_by_label(self, label: str) -> list[AttackEntity]` — Get all entities of a specific node label. Receives: `self, label: str`. Sends: `list[AttackEntity]`.
- L413 `def get_relationships_by_label(self, label: str) -> list[AttackRelationship]` — Get all relationships of a specific edge label. Receives: `self, label: str`. Sends: `list[AttackRelationship]`.
- L417 `def finalize_parsing(self) -> None` — Apply tombstones and deduplicate entities and relationships. Receives: `self`. Sends: `None`.
- L447 `def parse_all_domains() -> StixParser` — Parse all configured ATT&CK domain folders and return a unified parser. Receives: `not applicable`. Sends: `StixParser`.

### [`rag_service/app/RAG/GraphRAG/ingestion/vector_loader.py`](../../rag_service/app/RAG/GraphRAG/ingestion/vector_loader.py)

Purpose: Qdrant Vector Loader ======================= Embeds ATT&CK entity descriptions and relationship descriptions into Qdrant.

- L33 `def uuid_from_stix_id(stix_id: str) -> str` — Generate a valid UUID from a STIX ID. Receives: `stix_id: str`. Sends: `str`.
- L52 `class VectorLoader` — Embeds and stores ATT&CK data in Qdrant (Hybrid). Receives: `constructor arguments and class fields`. Sends: `VectorLoader`.
- L55 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None)` — Implements init. Receives: `self, embed_model: Optional[BGEM3FlagModel]=None`. Sends: `inferred or None`.
- L72 `def _embed_texts(self, texts: list[str]) -> dict` — Embed a batch of texts returning dense and sparse vectors. Receives: `self, texts: list[str]`. Sends: `dict`.
- L82 `def _init_collection(self, collection_name: str)` — Create Qdrant collection with both dense and sparse configurations. Receives: `self, collection_name: str`. Sends: `inferred or None`.
- L100 `def load_entities(self, entities: list[AttackEntity]) -> int` — Embed and store entity descriptions. Receives: `self, entities: list[AttackEntity]`. Sends: `int`.
- L184 `def load_relationships(self, relationships: list[AttackRelationship]) -> int` — Embed and store relationship descriptions. Receives: `self, relationships: list[AttackRelationship]`. Sends: `int`.
- L267 `def load_all(self, parser: StixParser) -> None` — Full vector ingestion: embed entities + relationships. Receives: `self, parser: StixParser`. Sends: `None`.

### [`rag_service/app/RAG/GraphRAG/llm_content.py`](../../rag_service/app/RAG/GraphRAG/llm_content.py)

Purpose: Safe extraction of visible text from LangChain message responses.

- L6 `class LlmContentError(ValueError)` — Raised when an LLM response has no usable visible text. Receives: `constructor arguments and class fields`. Sends: `LlmContentError`.
- L10 `def require_message_text(message: BaseMessage, *, operation: str) -> str` — Return canonical visible message text or fail without exposing content. Receives: `message: BaseMessage, *, operation: str`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/llm_provider.py`](../../rag_service/app/RAG/GraphRAG/llm_provider.py)

Purpose: Production cloud LLM factory for Anthropic-compatible chat clients.

- L16 `class CoreLlmConfigurationError(RuntimeError)` — The selected cloud provider cannot be constructed safely. Receives: `constructor arguments and class fields`. Sends: `CoreLlmConfigurationError`.
- L19 `def __init__(self, provider: CoreLlmProvider, key_env_name: str) -> None` — Implements init. Receives: `self, provider: CoreLlmProvider, key_env_name: str`. Sends: `None`.
- L29 `class CoreLlmTarget` — Encapsulates corellmtarget. Receives: `constructor arguments and class fields`. Sends: `CoreLlmTarget`.
- L38 `def resolve_core_llm_target(anthropic_model: str | None=None, *, require_key: bool=True) -> CoreLlmTarget` — Resolve the selected production provider without consulting eval keys. Receives: `anthropic_model: str | None=None, *, require_key: bool=True`. Sends: `CoreLlmTarget`.
- L86 `def create_core_chat_model(*, anthropic_model: str | None=None, temperature: float | int, max_tokens: int) -> ChatAnthropic` — Create one cloud ChatAnthropic client for the selected provider. Receives: `*, anthropic_model: str | None=None, temperature: float | int, max_tokens: int`. Sends: `ChatAnthropic`.

### [`rag_service/app/RAG/GraphRAG/main.py`](../../rag_service/app/RAG/GraphRAG/main.py)

Purpose: MITRE ATT&CK GraphRAG — CLI Entrypoint ======================================== Run as a module from rag_service/app — the package uses relative imports, so `python main.py` fails with ImportError: python -m RAG.GraphRAG.main --ingest # Parse STIX → Neo4j + Qdrant python -m RAG.GraphRAG.main --test # Run test queries python -m RAG.GraphRAG.main # Interactive mode python -m RAG.GraphRAG.main --retrieve-only # Retrieval without LLM.

- L41 `def run_ingest()` — Parse STIX data and load into Neo4j + Qdrant. Receives: `not applicable`. Sends: `inferred or None`.
- L111 `def run_tests(retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False)` — Run test queries. Receives: `retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False`. Sends: `inferred or None`.
- L153 `def run_interactive(retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False)` — Interactive query mode. Receives: `retrieve_only: bool=False, fast: bool=False, ultrafast: bool=False`. Sends: `inferred or None`.
- L219 `def main()` — Implements main. Receives: `not applicable`. Sends: `inferred or None`.

### [`rag_service/app/RAG/GraphRAG/model_registry.py`](../../rag_service/app/RAG/GraphRAG/model_registry.py)

Purpose: Central OpenRouter model registry, curated presets, and alias resolver for GraphRAG.

- L12 `class ModelPreset` — Encapsulates modelpreset. Receives: `constructor arguments and class fields`. Sends: `ModelPreset`.
- L75 `def resolve_openrouter_model(name_or_alias: str | None) -> str` — Resolve a friendly model nickname, alias, or full ID to the canonical OpenRouter ID. Receives: `name_or_alias: str | None`. Sends: `str`.
- L100 `def list_available_models() -> list[dict[str, object]]` — Return structured catalog of ready-selection models. Receives: `not applicable`. Sends: `list[dict[str, object]]`.
- L115 `def format_model_table() -> str` — Render formatted ASCII comparison table of curated ready-selection models. Receives: `not applicable`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/models.py`](../../rag_service/app/RAG/GraphRAG/models.py)

Purpose: Pydantic Models for MITRE ATT&CK Entities ========================================== Typed representations of STIX 2.1 objects parsed from ATT&CK data.

- L10 `class AttackEntity(BaseModel)` — Base model for all ATT&CK entities (graph nodes). Receives: `constructor arguments and class fields`. Sends: `AttackEntity`.
- L21 `class Technique(AttackEntity)` — Encapsulates technique. Receives: `constructor arguments and class fields`. Sends: `Technique`.
- L28 `class Group(AttackEntity)` — Encapsulates group. Receives: `constructor arguments and class fields`. Sends: `Group`.
- L33 `class Software(AttackEntity)` — Encapsulates software. Receives: `constructor arguments and class fields`. Sends: `Software`.
- L39 `class Campaign(AttackEntity)` — Encapsulates campaign. Receives: `constructor arguments and class fields`. Sends: `Campaign`.
- L44 `class Mitigation(AttackEntity)` — Encapsulates mitigation. Receives: `constructor arguments and class fields`. Sends: `Mitigation`.
- L48 `class Tactic(AttackEntity)` — Encapsulates tactic. Receives: `constructor arguments and class fields`. Sends: `Tactic`.
- L53 `class DataSource(AttackEntity)` — Encapsulates datasource. Receives: `constructor arguments and class fields`. Sends: `DataSource`.
- L58 `class DataComponent(AttackEntity)` — Encapsulates datacomponent. Receives: `constructor arguments and class fields`. Sends: `DataComponent`.
- L62 `class AttackRelationship(BaseModel)` — Represents a STIX relationship between two ATT&CK entities. Receives: `constructor arguments and class fields`. Sends: `AttackRelationship`.

### [`rag_service/app/RAG/GraphRAG/pipeline/__init__.py`](../../rag_service/app/RAG/GraphRAG/pipeline/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py`](../../rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py)

Purpose: LangGraph Agentic RAG Pipeline ================================ The only pipeline serving ``POST /query``.

- L75 `class AgentState(TypedDict)` — Shared state flowing through every node in the graph. Receives: `constructor arguments and class fields`. Sends: `AgentState`.
- L115 `class AgentResponse` — Structured response returned by ``GraphRAGAgent.query()``. Receives: `constructor arguments and class fields`. Sends: `AgentResponse`.
- L127 `def to_dict(self) -> dict` — Serialize for JSON API responses. Receives: `self`. Sends: `dict`.
- L141 `class GraphRAGAgent` — Agentic RAG pipeline built on LangGraph. Receives: `constructor arguments and class fields`. Sends: `GraphRAGAgent`.
- L148 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Any]=None) -> None` — Implements init. Receives: `self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Any]=None`. Sends: `None`.
- L213 `def close(self) -> None` — Clean up resources. Receives: `self`. Sends: `None`.
- L217 `def retrieve_only(self, user_query: str) -> str` — Execute only the retrieval portion of the pipeline. Receives: `self, user_query: str`. Sends: `str`.
- L230 `def query_fast(self, user_query: str, verbose: bool=True) -> AgentResponse` — Minimal-latency path — single retrieve → one combined reason+answer call. Receives: `self, user_query: str, verbose: bool=True`. Sends: `AgentResponse`.
- L293 `def _get_ultrafast_llm(self)` — Lazily build (and cache) a low-output-token LLM for ultrafast mode. Receives: `self`. Sends: `inferred or None`.
- L308 `def query_ultrafast(self, user_query: str, verbose: bool=True) -> AgentResponse` — Absolute-minimum-latency path. Receives: `self, user_query: str, verbose: bool=True`. Sends: `AgentResponse`.
- L360 `def query(self, user_query: str, verbose: bool=True) -> AgentResponse` — Execute the agentic RAG pipeline. Receives: `self, user_query: str, verbose: bool=True`. Sends: `AgentResponse`.
- L398 `def _build_graph(self) -> Any` — Construct and compile the LangGraph state machine. Receives: `self`. Sends: `Any`.
- L461 `def _node_route_query(self, state: AgentState) -> dict` — Classify the query as GENERAL_EXPLANATION or INCIDENT_ANALYSIS. Receives: `self, state: AgentState`. Sends: `dict`.
- L477 `def _node_general_explanation(self, state: AgentState) -> dict` — Handle general knowledge questions without retrieval. Receives: `self, state: AgentState`. Sends: `dict`.
- L511 `def _node_prepare(self, state: AgentState) -> dict` — Detect the response language. Receives: `self, state: AgentState`. Sends: `dict`.
- L536 `def _node_retrieve(self, state: AgentState) -> dict` — Execute decomposed multi-query hybrid retrieval (Vector + Graph). Receives: `self, state: AgentState`. Sends: `dict`.
- L579 `def _node_evaluate_context(self, state: AgentState) -> dict` — Evaluate whether the retrieved context is sufficient. Receives: `self, state: AgentState`. Sends: `dict`.
- L600 `def _node_broaden_search(self, state: AgentState) -> dict` — Execute the BROADEN_SEARCH strategy by rewriting the query and looping. Receives: `self, state: AgentState`. Sends: `dict`.
- L623 `def _node_reasoning(self, state: AgentState) -> dict` — Reasoning LLM — synthesize the retrieved context into the answer. Receives: `self, state: AgentState`. Sends: `dict`.
- L694 `def _node_translate_output(self, state: AgentState) -> dict` — Stage 3: Translation LLM — render English answer into Thai. Receives: `self, state: AgentState`. Sends: `dict`.
- L726 `def _edge_after_route(state: AgentState) -> str` — Route based on query classification. Receives: `state: AgentState`. Sends: `str`.
- L734 `def _edge_after_evaluation(state: AgentState) -> str` — Decide next step based on context evaluation. Receives: `state: AgentState`. Sends: `str`.
- L771 `def _edge_after_reasoning(state: AgentState) -> str` — Decide whether to translate the answer to Thai. Receives: `state: AgentState`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/pipeline/chain.py`](../../rag_service/app/RAG/GraphRAG/pipeline/chain.py)

Purpose: LangChain LCEL Chain for MITRE ATT&CK GraphRAG — EVALUATION ONLY ================================================================== NOT a production path.

- L62 `def _print_sources(graphrag_result: GraphRAGResult, top_n: int=5) -> None` — Print the top retrieval sources for verbose/debug output. Receives: `graphrag_result: GraphRAGResult, top_n: int=5`. Sends: `None`.
- L75 `class ChainResponse` — Answer plus the retrieval artifacts behind it (for the MITRE table). Receives: `constructor arguments and class fields`. Sends: `ChainResponse`.
- L83 `class GraphRAGChain` — Full GraphRAG pipeline with cross-lingual support. Receives: `constructor arguments and class fields`. Sends: `GraphRAGChain`.
- L86 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, use_local: bool=False)` — Implements init. Receives: `self, embed_model: Optional[BGEM3FlagModel]=None, use_local: bool=False`. Sends: `inferred or None`.
- L153 `def close(self)` — Clean up resources. Receives: `self`. Sends: `inferred or None`.
- L157 `def query(self, user_query: str, verbose: bool=True) -> str` — Execute the full GraphRAG pipeline and return the answer text. Receives: `self, user_query: str, verbose: bool=True`. Sends: `str`.
- L165 `def query_with_details(self, user_query: str, verbose: bool=True) -> ChainResponse` — Execute the full GraphRAG pipeline. Receives: `self, user_query: str, verbose: bool=True`. Sends: `ChainResponse`.
- L324 `def retrieve_only(self, user_query: str) -> str` — Run retrieval without LLM generation (for testing/debugging). Receives: `self, user_query: str`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/pipeline/context_builder.py`](../../rag_service/app/RAG/GraphRAG/pipeline/context_builder.py)

Purpose: Context Builder ================ Assembles the final context from Vector + Graph retrieval results into a structured prompt for the LLM.

- L12 `def build_context(result: GraphRAGResult, max_context_length: int=10000, max_vector: int | None=None, max_graph: int=3) -> str` — Build a structured context string from GraphRAG results. Receives: `result: GraphRAGResult, max_context_length: int=10000, max_vector: int | None=None, max_graph: int=3`. Sends: `str`.
- L84 `def build_generation_prompt(context: str, original_query: str, english_query: str, respond_in_thai: bool=True) -> str` — Build the final prompt for LLM generation. Receives: `context: str, original_query: str, english_query: str, respond_in_thai: bool=True`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py`](../../rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py)

Purpose: Cross-Lingual Translation Layer ================================= Language routing for the RAG pipeline.

- L138 `def _is_thai(text: str) -> bool` — Check if text contains Thai characters. Receives: `text: str`. Sends: `bool`.
- L144 `def build_retrieval_queries(original_query: str, english_query: str, extra_queries: list[str] | None=None) -> list[str]` — Build the query list for cross-lingual retrieval. Receives: `original_query: str, english_query: str, extra_queries: list[str] | None=None`. Sends: `list[str]`.
- L175 `def _is_mostly_english(text: str) -> bool` — Check if text is predominantly English. Receives: `text: str`. Sends: `bool`.
- L184 `class CrossLingualLayer` — Manages Thai ↔ English translation for cross-lingual RAG. Receives: `constructor arguments and class fields`. Sends: `CrossLingualLayer`.
- L187 `def __init__(self, use_local: bool=False)` — Implements init. Receives: `self, use_local: bool=False`. Sends: `inferred or None`.
- L208 `def translate_query(self, query: str) -> str` — Translate a Thai query to English for retrieval. Receives: `self, query: str`. Sends: `str`.
- L242 `def get_reasoning_system_prompt() -> str` — Return the system prompt for the Reasoning LLM (Stage 2). Receives: `not applicable`. Sends: `str`.
- L251 `def get_translation_system_prompt() -> str` — Return the system prompt for the Translation LLM (Stage 3). Receives: `not applicable`. Sends: `str`.
- L260 `def get_fast_system_prompt(respond_in_thai: bool) -> str` — The DEFAULT production prompt for Thai answers, despite the name. Receives: `respond_in_thai: bool`. Sends: `str`.
- L283 `def get_ultrafast_system_prompt(respond_in_thai: bool) -> str` — Terse single-pass prompt for --ultrafast mode. Receives: `respond_in_thai: bool`. Sends: `str`.
- L306 `def should_respond_in_thai(query: str) -> bool` — Determine if the final output should be in Thai based on the query language. Receives: `query: str`. Sends: `bool`.

### [`rag_service/app/RAG/GraphRAG/pipeline/evaluator.py`](../../rag_service/app/RAG/GraphRAG/pipeline/evaluator.py)

Purpose: Context Sufficiency Evaluator ============================== Uses the LLM to judge whether retrieved context can adequately answer the user's query.

- L47 `class EvaluationResult` — Structured result from the context evaluator. Receives: `constructor arguments and class fields`. Sends: `EvaluationResult`.
- L59 `def __post_init__(self)` — Implements post init. Receives: `self`. Sends: `inferred or None`.
- L162 `class ContextEvaluator` — Evaluates whether retrieved context is sufficient to answer a query. Receives: `constructor arguments and class fields`. Sends: `ContextEvaluator`.
- L165 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L177 `def evaluate(self, original_query: str, english_query: str, context: str, retry_count: int=0, verbose: bool=True) -> EvaluationResult` — Judge context sufficiency. Receives: `self, original_query: str, english_query: str, context: str, retry_count: int=0, verbose: bool=True`. Sends: `EvaluationResult`.
- L267 `def _build_prompt(original_query: str, english_query: str, context: str, retry_count: int=0) -> str` — Build the evaluation prompt. Receives: `original_query: str, english_query: str, context: str, retry_count: int=0`. Sends: `str`.
- L304 `def _parse_response(raw: str) -> EvaluationResult` — Parse the LLM's JSON response into an EvaluationResult. Receives: `raw: str`. Sends: `EvaluationResult`.

### [`rag_service/app/RAG/GraphRAG/pipeline/mitre_table.py`](../../rag_service/app/RAG/GraphRAG/pipeline/mitre_table.py)

Purpose: MITRE Mapping Table Builder ============================ Converts a raw ``GraphRAGResult`` into a structured MITRE ATT&CK mapping table for the backend/frontend, filtering out retrieval noise.

- L52 `class MitreTableRow(BaseModel)` — One entry of the MITRE mapping table exposed to the backend. Receives: `constructor arguments and class fields`. Sends: `MitreTableRow`.
- L66 `def build_mitre_table(rag_result, answer: str, score_threshold: Optional[float]=None) -> list[MitreTableRow]` — Build the filtered MITRE mapping table from raw retrieval results. Receives: `rag_result, answer: str, score_threshold: Optional[float]=None`. Sends: `list[MitreTableRow]`.
- L125 `def _collect_candidates(rag_result) -> dict[str, dict]` — Gather unique entities from vector hits, graph seeds, and neighbors. Receives: `rag_result`. Sends: `dict[str, dict]`.
- L166 `def _tactic_map(rag_result) -> dict[str, str]` — Map technique name → tactic name from IN_TACTIC graph edges. Receives: `rag_result`. Sends: `dict[str, str]`.
- L176 `def _is_cited(attack_id: str, name: str, cited_ids: set[str], answer_lower: str) -> bool` — Determines cited. Receives: `attack_id: str, name: str, cited_ids: set[str], answer_lower: str`. Sends: `bool`.
- L197 `def _mitre_url(attack_id: str) -> Optional[str]` — Implements mitre url. Receives: `attack_id: str`. Sends: `Optional[str]`.

### [`rag_service/app/RAG/GraphRAG/pipeline/query_decomposer.py`](../../rag_service/app/RAG/GraphRAG/pipeline/query_decomposer.py)

Purpose: Query Decomposer ================ Breaks a compound security-incident query into multiple ATOMIC MITRE search queries — one per distinct attacker action — so each technique is retrieved on its own channel (parallel multi-query retrieval, fed into ``retrieve_multi_quota``).

- L105 `def _is_conversational(line: str) -> bool` — True when a line addresses the user rather than the retrieval engine. Receives: `line: str`. Sends: `bool`.
- L114 `def _parse(text: str, cap: int) -> list[str]` — Turn the LLM's line-per-query output into a clean, deduped query list. Receives: `text: str, cap: int`. Sends: `list[str]`.
- L148 `class QueryDecomposer` — LLM step: incident → list of atomic, native-language sub-queries. Receives: `constructor arguments and class fields`. Sends: `QueryDecomposer`.
- L151 `def __init__(self, use_local: bool=False)` — Implements init. Receives: `self, use_local: bool=False`. Sends: `inferred or None`.
- L175 `def decompose(self, incident: str, max_subqueries: int=_MAX_SUBQUERIES, verbose: bool=True) -> list[str]` — Return atomic native-language sub-queries, or a single-element fallback. Receives: `self, incident: str, max_subqueries: int=_MAX_SUBQUERIES, verbose: bool=True`. Sends: `list[str]`.

### [`rag_service/app/RAG/GraphRAG/pipeline/query_sanitizer.py`](../../rag_service/app/RAG/GraphRAG/pipeline/query_sanitizer.py)

Purpose: Retrieval Query Sanitizer ========================= Cleans LLM-written retrieval queries before they are embedded.

- L20 `def sanitize_retrieval_query(text: str) -> str` — Strip markdown and bare ATT&CK ID tokens from a rewritten query. Receives: `text: str`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/pipeline/router.py`](../../rag_service/app/RAG/GraphRAG/pipeline/router.py)

Purpose: Query Router ================================= Classifies user queries to determine the appropriate processing pipeline.

- L71 `class QueryRouter` — Encapsulates queryrouter. Receives: `constructor arguments and class fields`. Sends: `QueryRouter`.
- L72 `def __init__(self, use_local: bool=False)` — Implements init. Receives: `self, use_local: bool=False`. Sends: `inferred or None`.
- L93 `def route_query(self, query: str) -> str` — Classify the user query as GENERAL_EXPLANATION or INCIDENT_ANALYSIS. Receives: `self, query: str`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/retrieval/__init__.py`](../../rag_service/app/RAG/GraphRAG/retrieval/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/GraphRAG/retrieval/graph_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/graph_retriever.py)

Purpose: Neo4j Graph Retriever ====================== Expands subgraphs from Neo4j given STIX IDs retrieved from vector search.

- L26 `class GraphNode` — A node from the graph expansion. Receives: `constructor arguments and class fields`. Sends: `GraphNode`.
- L37 `class GraphEdge` — An edge from the graph expansion. Receives: `constructor arguments and class fields`. Sends: `GraphEdge`.
- L47 `class SubgraphResult` — Result of a graph expansion query. Receives: `constructor arguments and class fields`. Sends: `SubgraphResult`.
- L54 `def to_text(self) -> str` — Format the subgraph as readable text for LLM context. Receives: `self`. Sends: `str`.
- L100 `class GraphRetriever` — Expands subgraphs from Neo4j for GraphRAG context enrichment. Receives: `constructor arguments and class fields`. Sends: `GraphRetriever`.
- L103 `def __init__(self)` — Implements init. Receives: `self`. Sends: `inferred or None`.
- L107 `def close(self)` — Implements close. Receives: `self`. Sends: `inferred or None`.
- L110 `def expand(self, stix_ids: list[str]) -> list[SubgraphResult]` — Expand subgraphs for a list of STIX IDs. Receives: `self, stix_ids: list[str]`. Sends: `list[SubgraphResult]`.
- L120 `def expand_batch(self, stix_ids: list[str]) -> list[SubgraphResult]` — Batched graph expansion — 3 Cypher queries for the whole seed list. Receives: `self, stix_ids: list[str]`. Sends: `list[SubgraphResult]`.
- L225 `def _expand_single(self, stix_id: str) -> SubgraphResult` — Expand a single node's subgraph. Receives: `self, stix_id: str`. Sends: `SubgraphResult`.
- L323 `def query_cypher(self, cypher: str, params: Optional[dict]=None) -> list[dict]` — Execute an arbitrary Cypher query and return results as dicts. Receives: `self, cypher: str, params: Optional[dict]=None`. Sends: `list[dict]`.
- L329 `def get_multi_hop_path(self, start_name: str, end_name: str, max_hops: int=4) -> str` — Find paths between two named entities. Receives: `self, start_name: str, end_name: str, max_hops: int=4`. Sends: `str`.

### [`rag_service/app/RAG/GraphRAG/retrieval/hybrid_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/hybrid_retriever.py)

Purpose: Hybrid GraphRAG Retriever ========================== Combines Vector Search + Graph Expansion into a single retrieval step.

- L24 `class GraphRAGResult` — Combined result from vector search + graph expansion. Receives: `constructor arguments and class fields`. Sends: `GraphRAGResult`.
- L32 `def get_context_text(self, max_length: int=8000) -> str` — Format combined results as text for LLM context. Receives: `self, max_length: int=8000`. Sends: `str`.
- L77 `class HybridRetriever` — Orchestrates Vector + Graph retrieval for GraphRAG. Receives: `constructor arguments and class fields`. Sends: `HybridRetriever`.
- L80 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Reranker]=None)` — Implements init. Receives: `self, embed_model: Optional[BGEM3FlagModel]=None, reranker: Optional[Reranker]=None`. Sends: `inferred or None`.
- L90 `def close(self)` — Implements close. Receives: `self`. Sends: `inferred or None`.
- L100 `def _reweight_by_type(vector_results: list) -> list` — Down/up-weight reranked vector hits by node type, then re-sort so the graph-seed order (taken from this list) is technique-first. Receives: `vector_results: list`. Sends: `list`.
- L111 `def retrieve(self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None, expand_graph: bool=True) -> GraphRAGResult` — Execute the full GraphRAG retrieval pipeline. Receives: `self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None, expand_graph: bool=True`. Sends: `GraphRAGResult`.
- L189 `def retrieve_multi(self, queries: list[str], top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None) -> GraphRAGResult` — Execute hybrid retrieval for multiple queries and merge results. Receives: `self, queries: list[str], top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None`. Sends: `GraphRAGResult`.
- L260 `def retrieve_multi_quota(self, queries: list[str], per_query_k: int=3, top_k: int=VECTOR_TOP_K, max_vector: int=15, max_graph: int=8, node_label_filter: Optional[str]=None) -> 'GraphRAGResult'` — Multi-query retrieval with a PER-QUERY QUOTA. Receives: `self, queries: list[str], per_query_k: int=3, top_k: int=VECTOR_TOP_K, max_vector: int=15, max_graph: int=8, node_label_filter: Optional[str]=None`. Sends: `'GraphRAGResult'`.

### [`rag_service/app/RAG/GraphRAG/retrieval/reranker.py`](../../rag_service/app/RAG/GraphRAG/retrieval/reranker.py)

Purpose: Cross-Encoder Reranker ======================= Post-retrieval reranker that rescores vector search results using a cross-encoder model for joint query-document relevance.

- L15 `class Reranker` — Reranks a list of VectorResults using a cross-encoder model. Receives: `constructor arguments and class fields`. Sends: `Reranker`.
- L18 `def __init__(self, model_name: str=RERANKER_MODEL) -> None` — Implements init. Receives: `self, model_name: str=RERANKER_MODEL`. Sends: `None`.
- L24 `def rerank(self, query: str, results: list[VectorResult], top_k: int=FINAL_TOP_K) -> list[VectorResult]` — Score each (query, document) pair and return top_k results sorted by cross-encoder score, in [0, 1]. Receives: `self, query: str, results: list[VectorResult], top_k: int=FINAL_TOP_K`. Sends: `list[VectorResult]`.

### [`rag_service/app/RAG/GraphRAG/retrieval/vector_retriever.py`](../../rag_service/app/RAG/GraphRAG/retrieval/vector_retriever.py)

Purpose: Qdrant Vector Retriever ========================== Performs hybrid search (Dense + Sparse) over entity and relationship embeddings using BGE-M3 and Qdrant's native RRF fusion.

- L38 `class VectorResult` — A single result from vector search. Receives: `constructor arguments and class fields`. Sends: `VectorResult`.
- L47 `class VectorRetriever` — Retrieves semantically similar ATT&CK documents from Qdrant using Hybrid Search. Receives: `constructor arguments and class fields`. Sends: `VectorRetriever`.
- L50 `def __init__(self, embed_model: Optional[BGEM3FlagModel]=None)` — Implements init. Receives: `self, embed_model: Optional[BGEM3FlagModel]=None`. Sends: `inferred or None`.
- L75 `def _search_hybrid(self, collection_name: str, query: str, top_k: int, qdrant_filter: Optional[Filter]=None) -> list[VectorResult]` — Hybrid search: dense + sparse with RRF fusion natively in Qdrant. Receives: `self, collection_name: str, query: str, top_k: int, qdrant_filter: Optional[Filter]=None`. Sends: `list[VectorResult]`.
- L140 `def search_entities(self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None) -> list[VectorResult]` — Search entity descriptions semantically. Receives: `self, query: str, top_k: int=VECTOR_TOP_K, node_label_filter: Optional[str]=None`. Sends: `list[VectorResult]`.
- L181 `def search_relationships(self, query: str, top_k: int=VECTOR_TOP_K, edge_label_filter: Optional[str]=None) -> list[VectorResult]` — Search relationship descriptions semantically. Receives: `self, query: str, top_k: int=VECTOR_TOP_K, edge_label_filter: Optional[str]=None`. Sends: `list[VectorResult]`.
- L208 `def _normalize_scores(results: list['VectorResult']) -> None` — Min-max normalize scores in-place so results from different collections are comparable on the same [0, 1] scale. Receives: `results: list['VectorResult']`. Sends: `None`.
- L221 `def search_all(self, query: str, top_k: int=VECTOR_TOP_K) -> list[VectorResult]` — Search both entity and relationship collections. Receives: `self, query: str, top_k: int=VECTOR_TOP_K`. Sends: `list[VectorResult]`.

### [`rag_service/app/RAG/legal_reference/__init__.py`](../../rag_service/app/RAG/legal_reference/__init__.py)

Purpose: External legal reference lookup for the RAG service.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/legal_reference/client.py`](../../rag_service/app/RAG/legal_reference/client.py)

Purpose: Thanoy legal reference client ============================= Sends the incident text to an external Thai legal service and returns the provisions it names.

- L60 `def _first(row: dict, names: tuple[str, ...]) -> str` — Implements first. Receives: `row: dict, names: tuple[str, ...]`. Sends: `str`.
- L68 `def _score(row: dict) -> float | None` — Implements score. Receives: `row: dict`. Sends: `float | None`.
- L76 `def _iapp_row(row: dict) -> LegalProvision | None` — Read one documented row: {"law", "section", "snippet"}. Receives: `row: dict`. Sends: `LegalProvision | None`.
- L96 `def extract_provisions(payload, limit: int) -> list[LegalProvision]` — Provisions from a response, documented shape first. Receives: `payload, limit: int`. Sends: `list[LegalProvision]`.
- L130 `class ThanoyClient` — Thin HTTP client. Receives: `constructor arguments and class fields`. Sends: `ThanoyClient`.
- L133 `def __init__(self, url: str | None=None, api_key: str | None=None, timeout: float | None=None)` — Implements init. Receives: `self, url: str | None=None, api_key: str | None=None, timeout: float | None=None`. Sends: `inferred or None`.
- L146 `def configured(self) -> bool` — Implements configured. Receives: `self`. Sends: `bool`.
- L149 `def search(self, query: str, limit: int | None=None) -> LegalReferenceResult` — Implements search. Receives: `self, query: str, limit: int | None=None`. Sends: `LegalReferenceResult`.
- L179 `def _post(self, query: str, limit: int)` — Implements post. Receives: `self, query: str, limit: int`. Sends: `inferred or None`.

### [`rag_service/app/RAG/legal_reference/config.py`](../../rag_service/app/RAG/legal_reference/config.py)

Purpose: Legal reference configuration ============================= Everything the Thanoy integration needs from the environment, in one place.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/RAG/legal_reference/schema.py`](../../rag_service/app/RAG/legal_reference/schema.py)

Purpose: Legal reference API types ========================= The third output of /query, beside the retrieval context and the MITRE mapping.

- L21 `class LegalProvision(BaseModel)` — One statutory provision the external service returned. Receives: `constructor arguments and class fields`. Sends: `LegalProvision`.
- L38 `class LegalReferenceResult(BaseModel)` — Provisions that may be relevant — an aid to looking things up. Receives: `constructor arguments and class fields`. Sends: `LegalReferenceResult`.

### [`rag_service/app/routers/__init__.py`](../../rag_service/app/routers/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/routers/context_store.py`](../../rag_service/app/routers/context_store.py)

Purpose: Owns context store behavior for the GraphRAG runtime and evaluation package.

- L13 `def get_retrieval_contexts(req: Request) -> dict[str, dict[str, Any]]` — Retrieves retrieval contexts. Receives: `req: Request`. Sends: `dict[str, dict[str, Any]]`.
- L21 `def prune_retrieval_contexts(req: Request) -> None` — Removes retrieval contexts. Receives: `req: Request`. Sends: `None`.
- L33 `def store_retrieval_context(req: Request, *, query: str, context: str, rag_result: Any, mitre_table: list[Any] | None=None) -> str` — Persists retrieval context. Receives: `req: Request, *, query: str, context: str, rag_result: Any, mitre_table: list[Any] | None=None`. Sends: `str`.
- L58 `def load_retrieval_context(req: Request, context_id: str) -> dict[str, Any] | None` — Retrieves retrieval context. Receives: `req: Request, context_id: str`. Sends: `dict[str, Any] | None`.
- L69 `def export_retrieval_context(req: Request, context_id: str) -> dict[str, Any] | None` — Serializes retrieval context. Receives: `req: Request, context_id: str`. Sends: `dict[str, Any] | None`.

### [`rag_service/app/routers/rag.py`](../../rag_service/app/routers/rag.py)

Purpose: Owns rag behavior for the GraphRAG runtime and evaluation package.

- L25 `def _get_query_limiter(req: Request) -> CapacityLimiter` — Process-wide cap on concurrent pipeline runs. Receives: `req: Request`. Sends: `CapacityLimiter`.
- L39 `def _run_pipeline(rag_agent: Any, query: str) -> tuple[Any, list[Any]]` — The whole blocking section, so one worker thread does all of it. Receives: `rag_agent: Any, query: str`. Sends: `tuple[Any, list[Any]]`.
- L57 `async def health(request: Request)` — Implements health. Receives: `request: Request`. Sends: `inferred or None`.
- L65 `async def query_rag(request: QueryRequest, req: Request)` — Implements query rag. Receives: `request: QueryRequest, req: Request`. Sends: `inferred or None`.
- L107 `async def _legal_reference(req: Request, query: str) -> LegalReferenceResult` — Never raises. Receives: `req: Request, query: str`. Sends: `LegalReferenceResult`.
- L129 `async def get_retrieval_context(context_id: str, req: Request)` — Retrieves retrieval context. Receives: `context_id: str, req: Request`. Sends: `inferred or None`.

### [`rag_service/app/schemas/__init__.py`](../../rag_service/app/schemas/__init__.py)

Purpose: Defines the public package surface for the GraphRAG runtime and evaluation package.

No named functions, classes, interfaces, types, or enums are declared in this file.

### [`rag_service/app/schemas/rag.py`](../../rag_service/app/schemas/rag.py)

Purpose: Owns rag behavior for the GraphRAG runtime and evaluation package.

- L11 `class QueryRequest(BaseModel)` — Encapsulates queryrequest. Receives: `constructor arguments and class fields`. Sends: `QueryRequest`.
- L24 `class QueryResponse(BaseModel)` — Encapsulates queryresponse. Receives: `constructor arguments and class fields`. Sends: `QueryResponse`.
- L45 `def normalize_empty_retrieval_context_id(cls, value: Any) -> Any` — Normalizes empty retrieval context id. Receives: `cls, value: Any`. Sends: `Any`.
- L49 `class RetrievalContextSnapshot(BaseModel)` — Encapsulates retrievalcontextsnapshot. Receives: `constructor arguments and class fields`. Sends: `RetrievalContextSnapshot`.

## Graphrag Regression Suite

### [`rag_service/tests/test_core_llm_provider.py`](../../rag_service/tests/test_core_llm_provider.py)

Purpose: Verifies core llm provider behavior in the GraphRAG regression suite.

- L23 `def test_default_provider_and_openrouter_target(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test default provider and openrouter target. Receives: `monkeypatch: pytest.MonkeyPatch`. Sends: `None`.
- L38 `def test_explicit_anthropic_target(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test explicit anthropic target. Receives: `monkeypatch: pytest.MonkeyPatch`. Sends: `None`.
- L51 `def test_invalid_selector_is_rejected() -> None` — Implements test invalid selector is rejected. Receives: `not applicable`. Sends: `None`.
- L56 `def test_missing_selected_key_does_not_fallback_to_other_or_evaluation_key(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test missing selected key does not fallback to other or evaluation key. Receives: `monkeypatch: pytest.MonkeyPatch`. Sends: `None`.
- L75 `def test_factory_constructs_selected_client(monkeypatch: pytest.MonkeyPatch, provider: str, expected_model: str, has_openrouter_headers: bool) -> None` — Implements test factory constructs selected client. Receives: `monkeypatch: pytest.MonkeyPatch, provider: str, expected_model: str, has_openrouter_headers: bool`. Sends: `None`.
- L83 `class FakeChatAnthropic` — Encapsulates fakechatanthropic. Receives: `constructor arguments and class fields`. Sends: `FakeChatAnthropic`.
- L84 `def __init__(self, **kwargs: object) -> None` — Implements init. Receives: `self, **kwargs: object`. Sends: `None`.
- L109 `def test_local_mode_takes_precedence_over_cloud_factory(monkeypatch: pytest.MonkeyPatch) -> None` — Implements test local mode takes precedence over cloud factory. Receives: `monkeypatch: pytest.MonkeyPatch`. Sends: `None`.
- L116 `class FakeChatOllama` — Encapsulates fakechatollama. Receives: `constructor arguments and class fields`. Sends: `FakeChatOllama`.
- L117 `def __init__(self, **kwargs: object) -> None` — Implements init. Receives: `self, **kwargs: object`. Sends: `None`.
- L123 `def fail_cloud_factory(**kwargs: object) -> None` — Implements fail cloud factory. Receives: `**kwargs: object`. Sends: `None`.
- L133 `def test_all_production_pipeline_modules_use_central_factory() -> None` — Implements test all production pipeline modules use central factory. Receives: `not applicable`. Sends: `None`.

### [`rag_service/tests/test_llm_content.py`](../../rag_service/tests/test_llm_content.py)

Purpose: Verifies llm content behavior in the GraphRAG regression suite.

- L27 `class StubLlm` — Encapsulates stubllm. Receives: `constructor arguments and class fields`. Sends: `StubLlm`.
- L28 `def __init__(self, response: AIMessage) -> None` — Implements init. Receives: `self, response: AIMessage`. Sends: `None`.
- L31 `def invoke(self, messages: object) -> AIMessage` — Implements invoke. Receives: `self, messages: object`. Sends: `AIMessage`.
- L35 `class RaisingLlm` — Encapsulates raisingllm. Receives: `constructor arguments and class fields`. Sends: `RaisingLlm`.
- L36 `def invoke(self, messages: object) -> AIMessage` — Implements invoke. Receives: `self, messages: object`. Sends: `AIMessage`.
- L40 `class StubRouter` — Encapsulates stubrouter. Receives: `constructor arguments and class fields`. Sends: `StubRouter`.
- L41 `def route_query(self, query: str) -> str` — Implements route query. Receives: `self, query: str`. Sends: `str`.
- L45 `class BrokenTextMessage(AIMessage)` — Encapsulates brokentextmessage. Receives: `constructor arguments and class fields`. Sends: `BrokenTextMessage`.
- L47 `def text(self) -> str` — Implements text. Receives: `self`. Sends: `str`.
- L51 `def message(content: Any) -> AIMessage` — Implements message. Receives: `content: Any`. Sends: `AIMessage`.
- L55 `def test_string_content_is_returned_without_trimming() -> None` — Implements test string content is returned without trimming. Receives: `not applicable`. Sends: `None`.
- L62 `def test_mixed_reasoning_and_text_returns_only_visible_text() -> None` — Implements test mixed reasoning and text returns only visible text. Receives: `not applicable`. Sends: `None`.
- L78 `def test_text_blocks_are_concatenated_in_order() -> None` — Implements test text blocks are concatenated in order. Receives: `not applicable`. Sends: `None`.
- L92 `def test_unknown_blocks_are_ignored_when_visible_text_exists() -> None` — Implements test unknown blocks are ignored when visible text exists. Receives: `not applicable`. Sends: `None`.
- L118 `def test_empty_unknown_and_malformed_content_raises(content: Any) -> None` — Implements test empty unknown and malformed content raises. Receives: `content: Any`. Sends: `None`.
- L123 `def test_error_does_not_expose_block_or_property_secrets() -> None` — Implements test error does not expose block or property secrets. Receives: `not applicable`. Sends: `None`.
- L143 `def test_evaluator_reads_visible_json_and_propagates_empty_content() -> None` — Implements test evaluator reads visible json and propagates empty content. Receives: `not applicable`. Sends: `None`.
- L169 `def test_router_falls_back_only_for_content_error() -> None` — Implements test router falls back only for content error. Receives: `not applicable`. Sends: `None`.
- L182 `def test_decomposer_keeps_existing_whole_query_fallback() -> None` — Implements test decomposer keeps existing whole query fallback. Receives: `not applicable`. Sends: `None`.
- L193 `def test_cross_lingual_translation_returns_original_on_content_error() -> None` — Implements test cross lingual translation returns original on content error. Receives: `not applicable`. Sends: `None`.
- L207 `def test_chain_final_answer_excludes_non_text_blocks() -> None` — Implements test chain final answer excludes non text blocks. Receives: `not applicable`. Sends: `None`.
- L231 `def test_pipeline_files_do_not_directly_consume_response_content() -> None` — Implements test pipeline files do not directly consume response content. Receives: `not applicable`. Sends: `None`.

### [`rag_service/tests/test_rag_query_concurrency.py`](../../rag_service/tests/test_rag_query_concurrency.py)

Purpose: POST /query must not block the event loop, so sessions run concurrently.

- L19 `def anyio_backend() -> str` — Implements anyio backend. Receives: `not applicable`. Sends: `str`.
- L23 `class BlockingRagAgent` — Stands in for GraphRAGAgent: query() blocks the calling thread. Receives: `constructor arguments and class fields`. Sends: `BlockingRagAgent`.
- L26 `def __init__(self, duration: float=QUERY_DURATION) -> None` — Implements init. Receives: `self, duration: float=QUERY_DURATION`. Sends: `None`.
- L33 `def query(self, query: str, *, verbose: bool) -> SimpleNamespace` — Implements query. Receives: `self, query: str, *, verbose: bool`. Sends: `SimpleNamespace`.
- L50 `def _make_app(agent: BlockingRagAgent) -> FastAPI` — Implements make app. Receives: `agent: BlockingRagAgent`. Sends: `FastAPI`.
- L58 `def _client(app: FastAPI) -> httpx.AsyncClient` — Implements client. Receives: `app: FastAPI`. Sends: `httpx.AsyncClient`.
- L65 `def stub_mitre_table(monkeypatch) -> None` — Implements stub mitre table. Receives: `monkeypatch`. Sends: `None`.
- L70 `async def test_sessions_query_concurrently_and_keep_their_own_context() -> None` — Implements test sessions query concurrently and keep their own context. Receives: `not applicable`. Sends: `None`.
- L78 `async def run(query: str) -> None` — Executes run. Receives: `query: str`. Sends: `None`.
- L108 `async def test_event_loop_stays_responsive_while_a_query_runs() -> None` — Implements test event loop stays responsive while a query runs. Receives: `not applicable`. Sends: `None`.
- L130 `async def test_capacity_limiter_caps_parallel_pipelines() -> None` — Implements test capacity limiter caps parallel pipelines. Receives: `not applicable`. Sends: `None`.

### [`rag_service/tests/test_rag_query_route.py`](../../rag_service/tests/test_rag_query_route.py)

Purpose: Verifies rag query route behavior in the GraphRAG regression suite.

- L12 `class FakeRagAgent` — Encapsulates fakeragagent. Receives: `constructor arguments and class fields`. Sends: `FakeRagAgent`.
- L13 `def __init__(self) -> None` — Implements init. Receives: `self`. Sends: `None`.
- L17 `def query(self, query: str, *, verbose: bool) -> SimpleNamespace` — Implements query. Receives: `self, query: str, *, verbose: bool`. Sends: `SimpleNamespace`.
- L25 `def retrieve_with_details(self, query: str) -> None` — Implements retrieve with details. Receives: `self, query: str`. Sends: `None`.
- L30 `def test_query_runs_full_agent_pipeline_without_exposing_generated_answer(monkeypatch) -> None` — Implements test query runs full agent pipeline without exposing generated answer. Receives: `monkeypatch`. Sends: `None`.
- L40 `def build_table(result: object, answer: str) -> list[object]` — Builds table. Receives: `result: object, answer: str`. Sends: `list[object]`.

### [`rag_service/tests/test_stix_parser.py`](../../rag_service/tests/test_stix_parser.py)

Purpose: Unit Tests for STIX 2.1 Parser =============================== Validates tombstoning, version overrides, relationship filtering, latest-file folder parsing defaults, and T1527 regression logic.

- L22 `def make_mock_bundle(objects)` — Implements make mock bundle. Receives: `objects`. Sends: `inferred or None`.
- L31 `def test_revoked_tombstone_exclusions()` — Parser test: older file has active object, newer file marks it revoked -> final entities exclude it. Receives: `not applicable`. Sends: `inferred or None`.
- L72 `def test_newer_version_overrides()` — Parser test: older active object, newer active object with same STIX ID -> newer active wins. Receives: `not applicable`. Sends: `inferred or None`.
- L115 `def test_relationships_referencing_tombstones_removed()` — Parser test: relationships referencing tombstoned objects are removed. Receives: `not applicable`. Sends: `inferred or None`.
- L176 `def test_default_folder_parsing_prefers_main_file(monkeypatch)` — Parser test: default folder parsing prefers enterprise-attack.json when present. Receives: `monkeypatch`. Sends: `inferred or None`.
- L228 `def test_regression_t1527()` — Regression test: T1527 is not present in parsed entities. Receives: `not applicable`. Sends: `inferred or None`.
