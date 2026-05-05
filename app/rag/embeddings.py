import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("open_ai_key"))

# Cheap + good general-purpose embedding model
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def embed_text(texts: List[str]) -> List[List[float]]:
    """
    Turn a list of strings into a list of embedding vectors.

    We keep this in a separate module so:
    - we can swap models later,
    - we can add logging / batching easily.
    """
    if not isinstance(texts, list):
        texts = [texts]

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]
