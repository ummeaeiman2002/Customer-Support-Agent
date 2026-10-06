from __future__ import annotations

import logging
import sys

from customer_support_agent.config.settings import ConfigError, load_settings
from customer_support_agent.rag.embeddings import Embedder
from customer_support_agent.rag.ingestion import chunk_directory
from customer_support_agent.rag.vector_store import VectorStore
from customer_support_agent.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    setup_logging(settings.log_level)

    try:
        chunks = chunk_directory(settings.knowledge_dir)
        embedder = Embedder(settings.embedding_model)
        store = VectorStore(settings.chroma_path)
        store.reset()
        logger.info("embedding_started chunks=%d", len(chunks))
        embeddings = embedder.embed_texts([c.text for c in chunks])
        store.add(chunks, embeddings)
    except Exception as exc:
        print(f"Ingestion failed: {exc}")
        sys.exit(1)

    sources = sorted({c.source_file for c in chunks})
    print(f"Ingested {len(chunks)} chunks from {len(sources)} files:")
    for source in sources:
        print(f"  - {source}")
    print(f"Vector store: {settings.chroma_path} ({store.count()} vectors)")


if __name__ == "__main__":
    main()
