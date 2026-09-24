from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_CASE_ANALYSIS_MODEL = "deepseek/deepseek-v4.1-flash"


class DatabaseConfig(BaseModel):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "cybercase_framework"
    postgres_host: str = "db"
    postgres_port: str = "5432"
    database_url: str = ""

    @property
    def async_database_url(self) -> str:
        if self.database_url:
            for spelling in ("postgres://", "postgresql://"):
                if self.database_url.startswith(spelling):
                    return self.database_url.replace(spelling, "postgresql+asyncpg://", 1)
            return self.database_url

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


class CORSConfig(BaseModel):
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

        if self.cors_origins:
            env_origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
            for o in env_origins:
                if not o.startswith("http"):
                    origins.append(f"https://{o}")
                    origins.append(f"http://{o}")
                else:
                    origins.append(o)

        return list(set(origins))


class LLMProviderConfig(BaseModel):
    openrouter_cybercase: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_messages_url: str = "https://openrouter.ai/api/v1/messages"
    case_analysis_model: str = Field(default=DEFAULT_CASE_ANALYSIS_MODEL, min_length=1)
    rag_service_url: str = "http://rag-service:8001"

    @field_validator("case_analysis_model")
    @classmethod
    def validate_case_analysis_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("CASE_ANALYSIS_MODEL must not be blank")
        return value


class CaseAnalysisConfig(BaseModel):
    mitre_gate_mode: Literal["llm", "encoder", "never"] = "llm"
    mitre_gate_model_path: str = "research/mitre_gate/model"
    chat_followup_max_rounds: int = Field(default=3, ge=0)
    chat_followup_gaps_per_round: int = Field(default=3, ge=1)
    chat_ask_timeout_seconds: float = 120.0


class ReportConfig(BaseModel):
    chat_report_enabled: bool = True


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


class AuthConfig(BaseModel):
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    jwt_cookie_name: str = "cybercase_auth_token"
    jwt_cookie_secure: bool = False
    frontend_base_url: str = "http://localhost:3000"
    auth_dev_login_enabled: bool = False


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
    "DEFAULT_CASE_ANALYSIS_MODEL",
    "DocumentIngestionConfig",
    "LLMProviderConfig",
    "ReportConfig",
    "Settings",
    "settings",
]
