from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

SUPPORTED_MODEL = "all-MiniLM-L6-v2"


class EmbeddingError(Exception):
    """Raised when embeddings cannot be generated."""


class Embedder:
    """Embeds text with chromadb's ONNX backend (all-MiniLM-L6-v2).

    sentence-transformers is not usable on machines where an Application
    Control policy blocks scikit-learn DLLs; the ONNX backend avoids it.
    """

    def __init__(self, model_name: str = SUPPORTED_MODEL) -> None:
        self._model_name = model_name
        self._function = None

    def _load(self):
        if self._function is None:
            if self._model_name != SUPPORTED_MODEL:
                raise EmbeddingError(
                    f"The chromadb ONNX backend embeds '{SUPPORTED_MODEL}' only, "
                    f"got: {self._model_name!r}"
                )
            try:
                from chromadb.utils.embedding_functions import (
                    DefaultEmbeddingFunction,
                )
            except ImportError as exc:
                raise EmbeddingError(
                    "chromadb is not installed. Run: pip install chromadb"
                ) from exc
            try:
                self._function = DefaultEmbeddingFunction()
            except Exception as exc:
                raise EmbeddingError(
                    "Could not load the ONNX embedding model "
                    f"'{SUPPORTED_MODEL}'."
                ) from exc
        return self._function

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._load()(texts)
        logger.debug("embedded texts=%d", len(texts))
        return [[float(value) for value in vector] for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]
