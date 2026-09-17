# tests/test_llm_client.py
from pydantic import SecretStr

from simpatia.config import LLMConfig
from simpatia.llm.client import AnthropicClient, OpenAICompatClient, build_client


def test_build_client_dispatches_openai_compat():
    config = LLMConfig(backend="openai_compat", api_key=SecretStr("test-key"))
    assert isinstance(build_client(config), OpenAICompatClient)


def test_build_client_dispatches_anthropic():
    config = LLMConfig(backend="anthropic", api_key=SecretStr("test-key"))
    assert isinstance(build_client(config), AnthropicClient)


def test_anthropic_client_omits_seed_from_request():
    """Anthropic's Messages API has no `seed` parameter — sending one is a 400."""
    config = LLMConfig(backend="anthropic", api_key=SecretStr("test-key"), seed=42)
    client = AnthropicClient(config)
    kwargs = client._kwargs("system prompt", [{"role": "user", "content": "hi"}])
    assert "seed" not in kwargs
