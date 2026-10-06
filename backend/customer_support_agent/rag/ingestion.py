from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


@dataclass
class Document:
    source_file: str
    text: str


@dataclass
class Chunk:
    id: str
    text: str
    source_file: str
    index: int


class IngestionError(Exception):
    """Raised when documents cannot be loaded or chunked."""


def load_documents(directory: Path) -> list[Document]:
    if not directory.is_dir():
        raise IngestionError(f"Knowledge directory not found: {directory}")
    files = sorted(directory.glob("*.md"))
    if not files:
        raise IngestionError(f"No .md documents found in {directory}")
    return [
        Document(source_file=path.name, text=path.read_text(encoding="utf-8"))
        for path in files
    ]


def clean(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _paragraphs(text: str) -> list[str]:
    return [block.strip() for block in text.split("\n\n") if block.strip()]


def chunk(
    document: Document,
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    text = clean(document.text)
    if not text:
        return []

    pieces: list[str] = []
    current = ""
    for paragraph in _paragraphs(text):
        if len(paragraph) > size:
            if current:
                pieces.append(current)
                current = ""
            start = 0
            while start < len(paragraph):
                end = min(start + size, len(paragraph))
                pieces.append(paragraph[start:end])
                if end == len(paragraph):
                    break
                start = max(end - overlap, start + 1)
            continue
        if not current:
            current = paragraph
        elif len(current) + 2 + len(paragraph) <= size:
            current = f"{current}\n\n{paragraph}"
        else:
            pieces.append(current)
            current = paragraph
    if current:
        pieces.append(current)

    stem = Path(document.source_file).stem
    return [
        Chunk(
            id=f"{stem}:{index}",
            text=piece,
            source_file=document.source_file,
            index=index,
        )
        for index, piece in enumerate(pieces)
    ]


def chunk_directory(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in load_documents(directory):
        chunks.extend(chunk(document))
    if not chunks:
        raise IngestionError("Documents produced no chunks after cleaning.")
    return chunks
