from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from .ingestion import Chunk

logger = logging.getLogger(__name__)

COLLECTION_NAME = "company_knowledge"


class VectorStoreError(Exception):
    """Raised when the vector store cannot be accessed."""


@dataclass
class ScoredChunk:
    text: str
    source_file: str
    score: float


class VectorStore:
    def __init__(self, path: Path, collection_name: str = COLLECTION_NAME) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise VectorStoreError(
                "chromadb is not installed. Run: pip install chromadb"
            ) from exc
        try:
            self._client = chromadb.PersistentClient(path=str(path))
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError(
                f"Could not open vector store at {path}."
            ) from exc

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunks and embeddings length mismatch.")
        try:
            self._collection.upsert(
                ids=[c.id for c in chunks],
                embeddings=embeddings,
                documents=[c.text for c in chunks],
                metadatas=[
                    {"source_file": c.source_file, "index": c.index}
                    for c in chunks
                ],
            )
        except Exception as exc:
            raise VectorStoreError("Failed to store embeddings.") from exc

    def query(self, embedding: list[float], k: int) -> list[ScoredChunk]:
        try:
            result = self._collection.query(
                query_embeddings=[embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            raise VectorStoreError("Vector search failed.") from exc

        chunks: list[ScoredChunk] = []
        documents = result.get("documents") or [[]]
        metadatas = result.get("metadatas") or [[]]
        distances = result.get("distances") or [[]]
        for document, metadata, distance in zip(
            documents[0], metadatas[0], distances[0]
        ):
            chunks.append(
                ScoredChunk(
                    text=document,
                    source_file=(metadata or {}).get("source_file", "unknown"),
                    score=1.0 - float(distance),
                )
            )
        return chunks

    def reset(self) -> None:
        try:
            self._client.delete_collection(COLLECTION_NAME)
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError("Failed to reset vector store.") from exc

    def count(self) -> int:
        try:
            return self._collection.count()
        except Exception as exc:
            raise VectorStoreError("Failed to read collection size.") from exc
