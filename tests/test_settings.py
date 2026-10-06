import pytest

from customer_support_agent.config.settings import ConfigError, load_settings


def test_settings_load_with_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_API_KEY", "gsk_test_123")
    monkeypatch.setenv("LLM_MODEL", "llama-3.3-70b-versatile")
    monkeypatch.setenv("MAX_TOOL_ITERATIONS", "7")
    settings = load_settings()
    assert settings.llm_api_key == "gsk_test_123"
    assert settings.llm_provider == "groq"
    assert settings.base_url == "https://api.groq.com/openai/v1"
    assert settings.max_tool_iterations == 7


def test_missing_key_raises_for_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_API_KEY", "")
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        load_settings()


def test_missing_key_raises_for_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "your_api_key_here")
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        load_settings()


def test_openai_provider_has_default_base_url(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    settings = load_settings()
    assert settings.base_url is None


def test_ollama_provider_needs_no_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_MODEL", "llama3.1:8b")
    settings = load_settings()
    assert settings.llm_provider == "ollama"
    assert settings.base_url == "http://127.0.0.1:11434/v1"


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "chatgpt")
    with pytest.raises(ConfigError, match="LLM_PROVIDER"):
        load_settings()


def test_invalid_integer_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("PORT", "not-a-number")
    with pytest.raises(ConfigError):
        load_settings()


def test_key_never_in_repr(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_API_KEY", "gsk-secret-value")
    settings = load_settings()
    assert "gsk-secret-value" not in repr(settings)
    assert "gsk-secret-value" not in str(settings)
