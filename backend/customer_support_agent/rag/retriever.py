from __future__ import annotations

import logging

from .embeddings import Embedder
from .vector_store import ScoredChunk, VectorStore

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 3000
NO_RESULTS_MESSAGE = "No relevant company information found."


class Retriever:
    def __init__(
        self,
        store: VectorStore,
        embedder: Embedder,
        top_k: int = 4,
        min_score: float = 0.3,
    ) -> None:
        self._store = store
        self._embedder = embedder
        self._top_k = top_k
        self._min_score = min_score

    def search(self, query: str) -> list[ScoredChunk]:
        if not query.strip() or self._store.count() == 0:
            return []
        logger.info("knowledge_search_started query_length=%d", len(query))
        embedding = self._embedder.embed_query(query)
        results = self._store.query(embedding, self._top_k)
        relevant = [r for r in results if r.score >= self._min_score]
        logger.info(
            "knowledge_search_completed hits=%d relevant=%d",
            len(results),
            len(relevant),
        )
        return relevant

    def format_context(self, chunks: list[ScoredChunk]) -> str:
        if not chunks:
            return NO_RESULTS_MESSAGE
        parts = []
        for chunk in chunks:
            parts.append(
                f"[source: {chunk.source_file}, score: {chunk.score:.2f}]\n"
                f"{chunk.text}"
            )
        return "\n\n".join(parts)[:MAX_CONTEXT_CHARS]
