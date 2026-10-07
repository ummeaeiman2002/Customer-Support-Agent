from __future__ import annotations

import logging
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .agent.agent import create_agent
from .agent.state import ConversationState
from .config.settings import PROJECT_ROOT, ConfigError, Settings, load_settings
from .utils.logging import setup_logging

if os.environ.get("VERCEL") == "1":
    if not str(os.environ.get("CHROMA_PATH", "./.chroma")).startswith("/"):
        os.environ["CHROMA_PATH"] = "/tmp/.chroma"
    os.environ["HOME"] = "/tmp"
    os.environ.setdefault("XDG_CACHE_HOME", "/tmp/.cache")

logger = logging.getLogger(__name__)

MAX_MESSAGE_CHARS = 4000
MAX_SEARCH_QUERY_CHARS = 200

FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"

DOC_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.md$")

_agent: Any = None
_state: ConversationState | None = None
_settings: Settings | None = None
_retriever: Any = None
_config_error: str | None = None


class ChatRequest(BaseModel):
    message: str


def _ensure_knowledge_loaded(settings: Settings) -> None:
    from .rag.embeddings import Embedder
    from .rag.ingestion import chunk_directory
    from .rag.vector_store import VectorStore

    store = VectorStore(settings.chroma_path)
    if store.count() > 0:
        return
    chunks = chunk_directory(settings.knowledge_dir)
    embedder = Embedder(settings.embedding_model)
    store.add(chunks, embedder.embed_texts([c.text for c in chunks]))
    logger.info("knowledge_reingested chunks=%d", len(chunks))


def _init_agent() -> None:
    global _agent, _state, _settings, _retriever, _config_error
    try:
        settings = load_settings()
    except ConfigError as exc:
        _config_error = str(exc)
        _state = ConversationState()
        logger.error("config_error message=%s", exc)
        return
    setup_logging(settings.log_level)
    _settings = settings
    try:
        _ensure_knowledge_loaded(settings)
    except Exception:
        logger.exception("knowledge_reingest_failed")
    try:
        _agent = create_agent(settings)
    except Exception:
        logger.exception("agent_creation_failed")
    _state = ConversationState()
    _retriever = None
    try:
        from .rag.embeddings import Embedder
        from .rag.retriever import Retriever
        from .rag.vector_store import VectorStore

        _retriever = Retriever(
            store=VectorStore(settings.chroma_path),
            embedder=Embedder(settings.embedding_model),
            top_k=settings.retrieval_top_k,
            min_score=settings.retrieval_min_score,
        )
    except Exception:
        logger.exception("kb_search_unavailable")
    logger.info("agent_ready")


@asynccontextmanager
async def lifespan(_: FastAPI):
    _init_agent()
    yield


app = FastAPI(
    title="Customer Support Agent API",
    description="AI customer-support backend API.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_index():
    index = FRONTEND_DIR / "index.html"
    if not index.is_file():
        return JSONResponse(
            status_code=503,
            content={"error": "Frontend files not found.", "path": str(index)},
        )
    return FileResponse(index)


@app.get("/index.html")
def read_index_alias():
    return read_index()


@app.get("/api/health")
def health() -> dict[str, Any]:
    info: dict[str, Any] = {
        "status": "ok",
        "vercel": os.environ.get("VERCEL") == "1",
        "config_error": _config_error,
        "llm_configured": _settings is not None,
        "agent_ready": _agent is not None,
        "retriever_ready": _retriever is not None,
        "static_dir": str(FRONTEND_DIR),
        "static_dir_exists": FRONTEND_DIR.is_dir(),
        "project_root": str(PROJECT_ROOT),
        "cwd": os.getcwd(),
    }
    knowledge_dir = (
        _settings.knowledge_dir if _settings is not None else PROJECT_ROOT / "knowledge"
    )
    info["knowledge_dir"] = str(knowledge_dir)
    info["knowledge_exists"] = knowledge_dir.is_dir()
    if _settings is not None:
        info["chroma_path"] = str(_settings.chroma_path)
        info["llm_provider"] = _settings.llm_provider
        info["llm_model"] = _settings.llm_model
        try:
            from .rag.vector_store import VectorStore

            info["kb_chunks"] = VectorStore(_settings.chroma_path).count()
        except Exception as exc:
            info["kb_chunks_error"] = f"{type(exc).__name__}: {exc}"
    return info


@app.post("/api/reset")
def reset_conversation() -> dict:
    global _state
    _state = ConversationState()
    logger.info("conversation_reset")
    return {"ok": True}


@app.get("/api/knowledge")
def list_documents() -> dict:
    if _settings is None:
        return JSONResponse(
            status_code=503, content={"error": "Service is not ready."}
        )
    documents = []
    for path in sorted(_settings.knowledge_dir.glob("*.md")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            size = path.stat().st_size
        except OSError:
            continue
        title = path.stem
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        documents.append({"name": path.name, "title": title, "bytes": size})
    return {"documents": documents}


@app.get("/api/knowledge/search")
def search_knowledge(q: str) -> JSONResponse:
    query = q.strip()
    if not query:
        return JSONResponse(
            status_code=400, content={"error": "Search query is empty."}
        )
    if _retriever is None:
        return JSONResponse(
            status_code=503, content={"error": "Knowledge search is unavailable."}
        )
    try:
        chunks = _retriever.search(query[:MAX_SEARCH_QUERY_CHARS])
    except Exception:
        logger.exception("kb_search_failed")
        return JSONResponse(
            status_code=500, content={"error": "Search failed. Please retry."}
        )
    results = [
        {
            "source": c.source_file,
            "score": round(c.score, 3),
            "text": c.text,
        }
        for c in chunks
    ]
    return {"query": query, "results": results}


@app.get("/api/knowledge/{name}")
def read_document(name: str) -> JSONResponse:
    if not DOC_NAME_RE.match(name) or _settings is None:
        return JSONResponse(
            status_code=400, content={"error": "Invalid document name."}
        )
    base = _settings.knowledge_dir.resolve()
    path = (base / name).resolve()
    if path.parent != base or not path.is_file():
        return JSONResponse(
            status_code=404, content={"error": "Document not found."}
        )
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return JSONResponse(
            status_code=500, content={"error": "Could not read document."}
        )
    return JSONResponse(content={"name": name, "content": content})


@app.post("/api/chat")
def chat(req: ChatRequest) -> JSONResponse:
    global _state
    message = req.message.strip()
    if not message:
        return JSONResponse(status_code=400, content={"error": "Message is empty."})
    message = message[:MAX_MESSAGE_CHARS]

    if _state is None:
        _state = ConversationState()

    if _agent is None:
        detail = (
            _config_error
            or "Agent is still starting up. Please retry in a moment."
        )
        return JSONResponse(status_code=503, content={"error": detail})

    logger.info("agent_request_received length=%d", len(message))
    try:
        reply = _agent.run(message, _state)
    except Exception:
        logger.exception("handler_error")
        return JSONResponse(
            status_code=500, content={"error": "Something went wrong. Please retry."}
        )
    return JSONResponse(content={"reply": reply})


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
else:
    logger.error("frontend_dir_missing path=%s", FRONTEND_DIR)


def main() -> None:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return

    setup_logging(settings.log_level)

    url = f"http://{settings.host}:{settings.port}"
    print(f"Customer Support Agent running at {url}")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="warning")


if __name__ == "__main__":
    main()
