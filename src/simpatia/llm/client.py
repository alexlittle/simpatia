"""Thin adapter over an OpenAI-compatible chat endpoint.

Deliberately provider-agnostic: the same code targets Ollama, vLLM,
LM Studio, OpenRouter and OpenAI by changing the config's base_url.
"""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any, Literal, Protocol

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from simpatia.config import LLMConfig, get_settings

Message = dict[str, str]  # {"role": "user" | "assistant", "content": str}

Role = Literal["patient", "examiner"]


class LLMClient(Protocol):
    async def complete(self, system: str, messages: list[Message]) -> str: ...
    def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]: ...


class OpenAICompatClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key.get_secret_value(),
        )

    def _payload(self, system: str, messages: list[Message]) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "messages": [{"role": "system", "content": system}, *messages],
            "seed": self.config.seed,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

    async def complete(self, system: str, messages: list[Message]) -> str:
        response = await self._client.chat.completions.create(**self._payload(system, messages))
        return response.choices[0].message.content or ""

    async def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            **self._payload(system, messages), stream=True
        )
        async for chunk in stream:
            if delta := chunk.choices[0].delta.content:
                yield delta


class AnthropicClient:
    """Anthropic Messages API.

    No `seed` support — determinism for the examiner relies on temperature=0
    alone (enforced in config.py).
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = AsyncAnthropic(api_key=config.api_key.get_secret_value())

    def _kwargs(self, system: str, messages: list[Message]) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system,
            "messages": messages,
        }

    async def complete(self, system: str, messages: list[Message]) -> str:
        response = await self._client.messages.create(**self._kwargs(system, messages))
        return "".join(block.text for block in response.content if block.type == "text")

    async def stream(self, system: str, messages: list[Message]) -> AsyncIterator[str]:
        async with self._client.messages.stream(**self._kwargs(system, messages)) as stream:
            async for text in stream.text_stream:
                yield text


def build_client(config: LLMConfig) -> LLMClient:
    """Construct a client for an arbitrary config — no global state.

    This is the entry point for eval harnesses sweeping across models.
    """
    if config.backend == "openai_compat":
        return OpenAICompatClient(config)
    if config.backend == "anthropic":
        return AnthropicClient(config)
    raise NotImplementedError(f"backend {config.backend!r} not yet implemented")


@lru_cache
def get_client(role: Role) -> LLMClient:
    """Per-role singleton — avoids opening a new HTTP pool per turn."""
    config: LLMConfig = getattr(get_settings(), role)
    return build_client(config)
