"""
app/core/config.py
──────────────────
Pydantic-settings based configuration.
Reads from environment variables and .env file.
All settings are validated and type-checked at startup.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment variables.
    Uses @lru_cache so the .env file is parsed only once.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = Field(default="Rugpull Detection API")
    app_version: str = Field(default="0.1.0")
    app_env: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION")
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Database ─────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://rugpull:rugpull_secret@localhost:5432/rugpull_db"
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg2://rugpull:rugpull_secret@localhost:5432/rugpull_db"
    )
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    db_pool_timeout: int = Field(default=30)

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = Field(default="redis://:redis_secret@localhost:6379/0")
    cache_ttl_seconds: int = Field(default=300)

    # ── Celery ───────────────────────────────────────────────
    celery_broker_url: str = Field(default="redis://:redis_secret@localhost:6379/1")
    celery_result_backend: str = Field(default="redis://:redis_secret@localhost:6379/2")

    # ── Blockchain APIs ───────────────────────────────────────
    etherscan_api_key: str = Field(default="")
    bscscan_api_key: str = Field(default="")
    alchemy_eth_url: str = Field(default="")
    alchemy_bsc_url: str = Field(default="")
    infura_project_id: str = Field(default="")
    defi_llama_base_url: AnyHttpUrl = Field(default="https://api.llama.fi")  # type: ignore[assignment]

    # Rate limits (requests per second)
    etherscan_rate_limit: float = Field(default=5.0)
    bscscan_rate_limit: float = Field(default=5.0)
    alchemy_rate_limit: float = Field(default=10.0)

    # ── Machine Learning ──────────────────────────────────────
    model_dir: Path = Field(default=Path("/app/trained_models"))
    device: Literal["cpu", "cuda", "mps"] = Field(default="cpu")

    # GATv2 hyperparameters
    gatv2_hidden_dim: int = Field(default=64)
    gatv2_num_heads: int = Field(default=4)
    gatv2_num_layers: int = Field(default=2)
    gatv2_dropout: float = Field(default=0.1)

    # TGN hyperparameters (from Rossi et al., 2020)
    tgn_memory_dim: int = Field(default=172)
    tgn_node_embedding_dim: int = Field(default=100)
    tgn_time_embedding_dim: int = Field(default=100)
    tgn_num_heads: int = Field(default=2)
    tgn_dropout: float = Field(default=0.1)

    # Training
    learning_rate: float = Field(default=0.0001)
    batch_size: int = Field(default=200)
    max_epochs: int = Field(default=100)
    early_stopping_patience: int = Field(default=10)

    # ── Security ─────────────────────────────────────────────
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 24)  # 24 hours

    # ── Logging ──────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "text"] = Field(default="json")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def etherscan_api_url(self) -> str:
        return "https://api.etherscan.io/api"

    @property
    def bscscan_api_url(self) -> str:
        return "https://api.bscscan.com/api"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns the cached Settings singleton.
    Use this function everywhere instead of constructing Settings() directly.
    """
    return Settings()


# Module-level settings instance for convenience imports
settings = get_settings()
