"""Application configuration — modular component mixins loaded from environment / .env."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── 1. Database Configuration ────────────────────────────────────────────────
class DatabaseConfig(BaseModel):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "cybercase_framework"
    postgres_host: str = "db"
    postgres_port: str = "5432"
    database_url: str = ""

    @property
    def async_database_url(self) -> str:
        """The URL with the driver SQLAlchemy's async engine needs.

        A URL that already names one, such as postgresql+asyncpg://, starts
        with neither spelling below and comes back untouched. The branch this
        replaced ran only when the URL held neither prefix, and then replaced
        a prefix that by definition was not there.
        """

        if self.database_url:
            for spelling in ("postgres://", "postgresql://"):
                if self.database_url.startswith(spelling):
                    return self.database_url.replace(spelling, "postgresql+asyncpg://", 1)
            return self.database_url

        # Construct from components if DATABASE_URL is not provided
        from sqlalchemy.engine.url import URL

        return str(
            URL.create(
                drivername="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=int(self.postgres_port),
                database=self.postgres_db,
            )
        )


# ── 2. CORS Configuration ────────────────────────────────────────────────────
class CORSConfig(BaseModel):
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        # Always allow localhost for development
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

        # Add origins from environment variable if they exist
        if self.cors_origins:
            env_origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
            for o in env_origins:
                # Ensure protocol is present
                if not o.startswith("http"):
                    origins.append(f"https://{o}")
                    origins.append(f"http://{o}")
                else:
                    origins.append(o)

        return list(set(origins))  # Deduplicate


# ── 3. LLM Providers & Core Routing ──────────────────────────────────────────
class LLMProviderConfig(BaseModel):
    openrouter_cybercase: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_messages_url: str = "https://openrouter.ai/api/v1/messages"
    # The model the case analysis runs on. An alias from the registry or a
    # full OpenRouter id.
    case_analysis_model: str = "openai/gpt-5.6-luna"
    rag_service_url: str = "http://rag-service:8001"


# ── 6. Case Analysis & Post-Answer Q&A ────────────────────────────────────────
class CaseAnalysisConfig(BaseModel):
    # Which applicability gate decides whether a case needs ATT&CK:
    # "llm" prompts a model with the whole case, "encoder" runs XLM-R over
    # one sentence at a time, "never" skips retrieval so an ablation can
    # measure what the technical context was worth.
    mitre_gate_mode: Literal["llm", "encoder", "never"] = "llm"
    # Which arm of the analysis the pipeline runs.
    #   direct  Case -> Analysis                    the baseline: nothing is checked
    #   verify  Case -> Analysis -> Verify          what the product ships
    #   revise  Case -> Analysis -> Verify -> Revise  one more model call
    case_analysis_arm: Literal["direct", "verify", "revise"] = "verify"
    case_analysis_max_revisions: int = Field(default=1, ge=1, le=3)
    mitre_gate_model_path: str = "research/mitre_gate/model"
    chat_followup_max_rounds: int = Field(default=2, ge=0)
    chat_followup_gaps_per_round: int = Field(default=3, ge=1)
    chat_ask_model: str = "openai/gpt-5.6-luna"
    chat_ask_timeout_seconds: float = 120.0


# ── 7. Persisted Report Generation ───────────────────────────────────────────
class ReportConfig(BaseModel):
    chat_report_enabled: bool = True


# ── 8. Document Ingestion & OCR Recognition ──────────────────────────────────
class DocumentIngestionConfig(BaseModel):
    document_ingestion_max_bytes: int = Field(
        default=20 * 1024 * 1024,
        ge=1,
    )
    document_ingestion_max_pages: int = Field(default=50, ge=1, le=500)
    document_ingestion_max_image_pixels: int = Field(default=40_000_000, ge=1)
    document_ingestion_render_longest_edge: int = Field(default=1_800, ge=512, le=4096)
    document_recognition_timeout_seconds: float = Field(default=60.0, gt=0)
    typhoon_api_key: str = ""
    typhoon_ocr_base_url: str = "https://api.opentyphoon.ai/v1"
    typhoon_ocr_model: str = "typhoon-ocr"
    document_ingestion_max_concurrent_ocr: int = Field(default=4, ge=1, le=16)


# ── 9. Authentication Configuration ─────────────────────────────────────────────
class AuthConfig(BaseModel):
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    jwt_cookie_name: str = "cybercase_auth_token"
    jwt_cookie_secure: bool = False
    frontend_base_url: str = "http://localhost:3000"
    auth_dev_login_enabled: bool = False


# ── Root Settings Composition ─────────────────────────────────────────────────
class Settings(
    DatabaseConfig,
    CORSConfig,
    AuthConfig,
    LLMProviderConfig,
    CaseAnalysisConfig,
    ReportConfig,
    DocumentIngestionConfig,
    BaseSettings,
):
    """
    All configuration values are read from environment variables.
    A `.env` file in the backend/ directory is also supported.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = False


settings = Settings()

__all__ = [
    "AuthConfig",
    "CORSConfig",
    "CaseAnalysisConfig",
    "DatabaseConfig",
    "DocumentIngestionConfig",
    "LLMProviderConfig",
    "ReportConfig",
    "Settings",
    "settings",
]
