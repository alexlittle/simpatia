# src/simpatia/models/locale.py
from pydantic import BaseModel, ConfigDict


class LocaleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language_name: str
    max_sentences: int = 2
    max_sentences_open: int = 4
    max_words: int
    lid_threshold: float = 0.9
    address_default: str = ""
    banned_jargon: list[str] = []
