from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULTS = {
    "LLM_PROVIDER": "groq",
    "LLM_MODEL": "openai/gpt-oss-120b",
    "GROQ_BASE_URL": "https://api.groq.com/openai/v1",
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434/v1",
    "EMBEDDING_PROVIDER": "chromadb",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "RETRIEVAL_MIN_SCORE": "0.3",
    "CHROMA_PATH": "./.chroma",
    "KNOWLEDGE_DIR": "./knowledge",
    "RETRIEVAL_TOP_K": "4",
    "MAX_TOOL_ITERATIONS": "5",
    "HOST": "127.0.0.1",
    "PORT": "8000",
    "LOG_LEVEL": "INFO",
}

VALID_PROVIDERS = ("groq", "openai", "ollama")

PROVIDERS_REQUIRING_KEY = ("groq", "openai")

PLACEHOLDER_KEY = "your_api_key_here"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    llm_api_key: str = field(repr=False)
    llm_provider: str
    llm_model: str
    base_url: str | None
    embedding_provider: str
    embedding_model: str
    chroma_path: Path
    knowledge_dir: Path
    retrieval_top_k: int
    retrieval_min_score: float
    max_tool_iterations: int
    host: str
    port: int
    log_level: str


def load_dotenv(path: Path | None = None) -> None:
    env_file = path or PROJECT_ROOT / ".env"
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _read_int(name: str) -> int:
    raw = os.environ.get(name, DEFAULTS[name])
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got: {raw!r}") from exc


def _base_url_for(provider: str) -> str | None:
    if provider == "openai":
        return None
    env_name = f"{provider.upper()}_BASE_URL"
    return os.environ.get(env_name, DEFAULTS[env_name])


def _read_float(name: str) -> float:
    raw = os.environ.get(name, DEFAULTS[name])
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got: {raw!r}") from exc


def load_settings() -> Settings:
    load_dotenv()

    provider = os.environ.get("LLM_PROVIDER", DEFAULTS["LLM_PROVIDER"]).lower()
    if provider not in VALID_PROVIDERS:
        raise ConfigError(
            f"LLM_PROVIDER must be one of {VALID_PROVIDERS}, got: {provider!r}"
        )

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if provider in PROVIDERS_REQUIRING_KEY and (
        not api_key or api_key == PLACEHOLDER_KEY
    ):
        raise ConfigError(
            f"LLM_PROVIDER is '{provider}' but LLM_API_KEY is missing or still "
            "set to the placeholder. Paste your free key in .env "
            "(console.groq.com for Groq)."
        )

    embedding_provider = os.environ.get(
        "EMBEDDING_PROVIDER", DEFAULTS["EMBEDDING_PROVIDER"]
    ).lower()
    if embedding_provider != "chromadb":
        raise ConfigError(
            "Version 1 supports only EMBEDDING_PROVIDER=chromadb "
            "(ONNX all-MiniLM-L6-v2). sentence-transformers is blocked by "
            f"Application Control policy on this machine. Got: {embedding_provider!r}"
        )

    return Settings(
        llm_api_key=api_key,
        llm_provider=provider,
        llm_model=os.environ.get("LLM_MODEL", DEFAULTS["LLM_MODEL"]),
        base_url=_base_url_for(provider),
        embedding_provider=os.environ.get(
            "EMBEDDING_PROVIDER", DEFAULTS["EMBEDDING_PROVIDER"]
        ),
        embedding_model=os.environ.get(
            "EMBEDDING_MODEL", DEFAULTS["EMBEDDING_MODEL"]
        ),
        chroma_path=PROJECT_ROOT
        / os.environ.get("CHROMA_PATH", DEFAULTS["CHROMA_PATH"]),
        knowledge_dir=PROJECT_ROOT
        / os.environ.get("KNOWLEDGE_DIR", DEFAULTS["KNOWLEDGE_DIR"]),
        retrieval_top_k=_read_int("RETRIEVAL_TOP_K"),
        retrieval_min_score=_read_float("RETRIEVAL_MIN_SCORE"),
        max_tool_iterations=_read_int("MAX_TOOL_ITERATIONS"),
        host=os.environ.get("HOST", DEFAULTS["HOST"]),
        port=_read_int("PORT"),
        log_level=os.environ.get("LOG_LEVEL", DEFAULTS["LOG_LEVEL"]).upper(),
    )
