# src/simpatia/config.py
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["openai_compat", "anthropic"]


class LLMConfig(BaseModel):
    backend: Backend = "openai_compat"
    base_url: str | None = "http://localhost:11434/v1"
    model: str = "gemma3:latest"
    api_key: SecretStr = SecretStr("ollama")
    temperature: float = 0.7
    seed: int | None = 42
    max_tokens: int = 512

    def fingerprint(self) -> dict[str, object]:
        return self.model_dump(exclude={"api_key"}, mode="json")


class PatientLLMConfig(LLMConfig):
    """Warmth and variability wanted — a student shouldn't get identical phrasing twice."""


class ExaminerLLMConfig(LLMConfig):
    """Marking must be reproducible: same transcript, same rubric, same mark."""

    temperature: float = 0.0
    seed: int | None = 7
    max_tokens: int = 1536


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIMPATIA_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    content_dir: Path = Path(__file__).parents[2] / "content"
    default_locale: str = "en-GB"

    patient: PatientLLMConfig = PatientLLMConfig()
    examiner: ExaminerLLMConfig = ExaminerLLMConfig()

    @model_validator(mode="after")
    def _check_examiner_determinism(self) -> "Settings":
        if self.examiner.temperature > 0.0:
            raise ValueError(
                "examiner.temperature must be 0.0 — marking has to be reproducible"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()