
from typing import Literal
from pydantic import SecretStr


llm_backend: Literal["openai_compat", "anthropic"] = "openai_compat"
llm_base_url: str = "http://localhost:11434/v1"
llm_model: str = "qwen3:14b"
llm_api_key: SecretStr = SecretStr("ollama")