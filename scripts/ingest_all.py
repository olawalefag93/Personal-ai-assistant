#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from app.rag.vector_store import add_documents

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", "./knowledge_base/notes")).expanduser()
if not KB_DIR.is_absolute():
    KB_DIR = BASE_DIR / KB_DIR

COLLECTION_NAME = "knowledge"


def read_text_files(root: Path) -> List[Path]:
    """
    Return a list of all .md and .txt files under the given root.
    """
    files = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            files.append(path)
    return files


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """
    Very simple chunker: split text into ~max_chars pieces.

    This isn't token-aware, but it's good enough to start.
    Later we can swap in a token-based chunker.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks


def ingest_notes():
    files = read_text_files(KB_DIR)
    print(f"Found {len(files)} note files in {KB_DIR}")

    all_texts = []
    all_ids = []
    all_metadatas = []

    for file_path in files:
        rel_path = file_path.relative_to(BASE_DIR) if file_path.is_relative_to(BASE_DIR) else file_path
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(content, max_chars=1000)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{rel_path.as_posix()}::chunk-{idx}"
            metadata = {
                "source": str(rel_path),
                "chunk_index": idx,
            }
            all_texts.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append(metadata)

    if not all_texts:
        print("No text to ingest.")
        return

    print(f"Ingesting {len(all_texts)} chunks into collection '{COLLECTION_NAME}'...")
    add_documents(
        collection_name=COLLECTION_NAME,
        texts=all_texts,
        ids=all_ids,
        metadatas=all_metadatas,
    )
    print("Ingestion complete.")


def main():
    if not KB_DIR.exists():
        raise RuntimeError(f"Knowledge base dir does not exist: {KB_DIR}")
    ingest_notes()


if __name__ == "__main__":
    main()
