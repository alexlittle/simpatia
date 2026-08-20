# src/simpatia/config.py
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIMPATIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Content
    content_dir: Path = Path(__file__).parents[2] / "content"
    default_locale: str = "en-GB"

    # LLM
    llm_backend: Literal["openai_compat", "anthropic"] = "openai_compat"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen3:14b"
    llm_api_key: SecretStr = SecretStr("ollama")
    llm_seed: int = 42


settings = Settings()
