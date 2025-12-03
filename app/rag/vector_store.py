import os
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions

from app.rag.embeddings import embed_text

# Default path lives on your SSD
VECTOR_DB_PATH = os.getenv(
    "VECTOR_DB_PATH",
    "/mnt/external-ssd/olawale_ai/data/vector_store",
)

client = chromadb.PersistentClient(path=VECTOR_DB_PATH)


def get_or_create_collection(name: str = "knowledge"):
    """
    Get or create a Chroma collection.
    """
    return client.get_or_create_collection(name=name)


def add_documents(
    collection_name: str,
    texts: List[str],
    ids: List[str],
    metadatas: List[Dict[str, Any]],
):
    """
    Add document chunks into the vector DB.

    - texts: list of chunk strings
    - ids: unique IDs for each chunk
    - metadatas: per-chunk metadata (source, chunk index, etc.)
    """
    collection = get_or_create_collection(collection_name)
    embeddings = embed_text(texts)
    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )


def query_documents(
    collection_name: str,
    query_text: str,
    n_results: int = 4,
) -> List[Dict[str, Any]]:
    """
    Query the vector DB with a natural language question.

    Returns a list of dicts with:
    - 'text'
    - 'metadata'
    - 'score' (similarity)
    """
    collection = get_or_create_collection(collection_name)
    query_embedding = embed_text([query_text])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    out = []
    for text, meta, dist in zip(docs, metadatas, distances):
        out.append(
            {
                "text": text,
                "metadata": meta,
                "score": dist,
            }
        )
    return out
