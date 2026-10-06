import math

import pytest

from customer_support_agent.rag.embeddings import Embedder
from customer_support_agent.rag.ingestion import (
    Chunk,
    Document,
    IngestionError,
    chunk,
    chunk_directory,
    clean,
    load_documents,
)
from customer_support_agent.rag.retriever import (
    NO_RESULTS_MESSAGE,
    Retriever,
)
from customer_support_agent.rag.vector_store import VectorStore

KEYWORD_VECTORS = {
    "refund": [1.0, 0.0, 0.0],
    "product": [0.0, 1.0, 0.0],
    "shipping": [0.0, 0.0, 1.0],
}


def fake_embed(text: str) -> list[float]:
    lowered = text.lower()
    for keyword, vector in KEYWORD_VECTORS.items():
        if keyword in lowered:
            return vector
    return [0.5, 0.5, 0.5]


class FakeEmbedder(Embedder):
    def __init__(self) -> None:
        super().__init__("fake-model")

    def _load(self):
        return object()

    def embed_texts(self, texts):
        return [fake_embed(t) for t in texts]


def test_clean_removes_code_blocks_and_links():
    text = "Hello ```secret``` world [link](http://x.com) done"
    result = clean(text)
    assert "secret" not in result
    assert "link" in result
    assert "http://x.com" not in result


def test_chunk_respects_size():
    doc = Document(
        source_file="test.md",
        text="\n\n".join(f"Paragraph number {i} " + "x" * 100 for i in range(20)),
    )
    chunks = chunk(doc, size=300, overlap=50)
    assert chunks
    assert all(len(c.text) <= 300 for c in chunks)
    assert len({c.id for c in chunks}) == len(chunks)


def test_chunk_empty_document_returns_nothing():
    assert chunk(Document(source_file="a.md", text="   ")) == []


def test_load_documents_missing_directory(tmp_path):
    with pytest.raises(IngestionError):
        load_documents(tmp_path / "nope")


def test_load_documents_empty_directory(tmp_path):
    with pytest.raises(IngestionError):
        load_documents(tmp_path)


def test_load_and_chunk_directory(tmp_path):
    (tmp_path / "company.md").write_text("# Company\n\nWe sell gadgets.", encoding="utf-8")
    (tmp_path / "policy.md").write_text("# Policy\n\nRefunds in 30 days.", encoding="utf-8")
    chunks = chunk_directory(tmp_path)
    assert len(chunks) >= 2
    assert {c.source_file for c in chunks} == {"company.md", "policy.md"}


def test_vector_store_add_and_query(tmp_path):
    store = VectorStore(tmp_path / "chroma")
    chunks = [
        Chunk(id="a:0", text="refund policy text", source_file="a.md", index=0),
        Chunk(id="b:0", text="product details", source_file="b.md", index=0),
    ]
    embeddings = [fake_embed(c.text) for c in chunks]
    store.add(chunks, embeddings)

    results = store.query(fake_embed("refund"), k=2)
    assert results
    assert results[0].source_file == "a.md"
    assert results[0].score == pytest.approx(1.0, abs=0.01)


def test_vector_store_reset_is_repeatable(tmp_path):
    store = VectorStore(tmp_path / "chroma")
    chunks = [Chunk(id="a:0", text="refund text", source_file="a.md", index=0)]
    for _ in range(2):
        store.reset()
        store.add(chunks, [fake_embed("refund text")])
        assert store.count() == 1


def test_retriever_filters_low_scores(tmp_path):
    store = VectorStore(tmp_path / "chroma")
    chunks = [
        Chunk(id="a:0", text="refund policy", source_file="a.md", index=0),
        Chunk(id="b:0", text="product details", source_file="b.md", index=0),
    ]
    store.add(chunks, [fake_embed(c.text) for c in chunks])

    retriever = Retriever(
        store=store, embedder=FakeEmbedder(), top_k=2, min_score=0.9
    )
    results = retriever.search("refund window")
    assert len(results) == 1
    assert results[0].source_file == "a.md"


def test_retriever_empty_store_returns_nothing(tmp_path):
    store = VectorStore(tmp_path / "chroma")
    retriever = Retriever(store=store, embedder=FakeEmbedder())
    assert retriever.search("anything") == []


def test_retriever_empty_query_returns_nothing(tmp_path):
    store = VectorStore(tmp_path / "chroma")
    store.add(
        [Chunk(id="a:0", text="refund", source_file="a.md", index=0)],
        [[1.0, 0.0, 0.0]],
    )
    retriever = Retriever(store=store, embedder=FakeEmbedder())
    assert retriever.search("   ") == []


def test_format_context_no_results():
    retriever = Retriever(store=None, embedder=FakeEmbedder())
    assert retriever.format_context([]) == NO_RESULTS_MESSAGE


def test_format_context_includes_source():
    from customer_support_agent.rag.vector_store import ScoredChunk

    retriever = Retriever(store=None, embedder=FakeEmbedder())
    formatted = retriever.format_context(
        [ScoredChunk(text="30 days", source_file="refund-policy.md", score=0.95)]
    )
    assert "30 days" in formatted
    assert "refund-policy.md" in formatted
    assert math.isclose(0.95, 0.95)
