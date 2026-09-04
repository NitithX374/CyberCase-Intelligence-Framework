"""Application configuration — modular component mixins loaded from environment / .env."""

from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, Field
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
        """Ensures the URL uses postgresql+asyncpg:// for SQLAlchemy async engine."""
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif "asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

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
    core_llm_provider: Literal["anthropic", "openrouter"] = "openrouter"
    anthropic_api_key: str = ""
    anthropic_messages_url: str = "https://api.anthropic.com/v1/messages"
    openrouter_cybercase: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_messages_url: str = "https://openrouter.ai/api/v1/messages"
    core_llm_openrouter_model: str = "openai/gpt-5.6-luna"
    rag_service_url: str = "http://rag-service:8001"


# ── 4. LLM Token Budgeting & Context Windows ─────────────────────────────────
class LLMTokenBudgetConfig(BaseModel):
    chat_model_context_tokens: int = 128_000
    chat_max_input_tokens: int = 100_000
    chat_reserved_output_tokens: int = 4_000
    chat_safety_margin_tokens: int = 12_000


# ── 5. Follow-up Policy & Gap Analysis ───────────────────────────────────────
class FollowupPolicyConfig(BaseModel):
    chat_followup_policy_enabled: bool = True
    chat_followup_policy_model: str = "openai/gpt-5.6-luna"
    chat_followup_policy_timeout_seconds: float = 45.0
    chat_gap_analysis_max_output_tokens: int = 4_096
    chat_followup_policy_max_output_tokens: int = 2_048
    chat_followup_policy_max_user_chars: int = 400_000
    chat_followup_question_max_chars: int = 4_000
    chat_followup_combined_query_max_chars: int = 400_000
    chat_followup_max_rounds: int = Field(default=2, ge=1, le=16)


# ── 6. Case Analysis & Post-Answer Q&A ────────────────────────────────────────
class CaseAnalysisConfig(BaseModel):
    # Post-answer ASK reasons over the persisted case and latest analysis. It
    # deliberately does not call the retrieval service again.
    chat_ask_model: str = "openai/gpt-5.6-luna"
    chat_ask_timeout_seconds: float = 120.0
    chat_ask_max_output_tokens: int = 16_384
    chat_ask_max_input_chars: int = 400_000
    analysis_input_mode: Literal["raw_direct"] = "raw_direct"


# ── 7. Persisted Report Generation ───────────────────────────────────────────
class ReportConfig(BaseModel):
    chat_report_enabled: bool = True
    chat_report_max_input_chars: int = 100_000
    chat_report_max_text_chars: int = 8_000
    chat_report_max_claims: int = 128
    chat_report_max_limitations: int = 48


# ── 8. Document Ingestion & OCR Recognition ──────────────────────────────────
class DocumentIngestionConfig(BaseModel):
    document_ingestion_max_bytes: int = Field(
        default=20 * 1024 * 1024,
        ge=1,
    )
    document_ingestion_max_pages: int = Field(default=50, ge=1, le=500)
    document_ingestion_max_image_pixels: int = Field(default=40_000_000, ge=1)
    document_ingestion_render_longest_edge: int = Field(default=1_800, ge=512, le=4096)
    document_recognizer: Literal["typhoon", "google_vision"] = "typhoon"
    document_mixed_region_policy: Literal["unified", "review"] = "unified"
    document_unknown_region_policy: Literal["unified", "review"] = "unified"
    document_recognition_timeout_seconds: float = Field(default=60.0, gt=0)
    typhoon_ocr_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("typhoon_ocr_api_key", "typhoon_api_key"),
    )
    typhoon_ocr_base_url: str = "https://api.opentyphoon.ai/v1"
    typhoon_ocr_model: str = "typhoon-ocr"


# ── Root Settings Composition ─────────────────────────────────────────────────
class Settings(
    DatabaseConfig,
    CORSConfig,
    LLMProviderConfig,
    LLMTokenBudgetConfig,
    FollowupPolicyConfig,
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
    "CORSConfig",
    "CaseAnalysisConfig",
    "DatabaseConfig",
    "DocumentIngestionConfig",
    "FollowupPolicyConfig",
    "LLMProviderConfig",
    "LLMTokenBudgetConfig",
    "ReportConfig",
    "Settings",
    "settings",
]
