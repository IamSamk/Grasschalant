"""
Grasschalant Backend — CLIP Text/Image Embedder Service
Generates 512-dim normalized vectors for meme concept text using sentence-transformers CLIP.
"""

from sentence_transformers import SentenceTransformer
from functools import lru_cache
from typing import List
import numpy as np


@lru_cache(maxsize=1)
def _get_clip_model() -> SentenceTransformer:
    """Lazy-load the CLIP text encoder (downloads ~350MB on first run)."""
    return SentenceTransformer("clip-ViT-B-32")


def embed_text(text: str) -> List[float]:
    """
    Generate a 512-dimensional normalized CLIP embedding for a text string.

    Args:
        text: Descriptive text (e.g., meme concept or visual analogy description).

    Returns:
        A list of 512 floats representing the normalized embedding vector.
    """
    model = _get_clip_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_texts_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate CLIP embeddings for a batch of texts efficiently.

    Args:
        texts: List of descriptive text strings.

    Returns:
        List of 512-dim normalized embedding vectors.
    """
    model = _get_clip_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    return embeddings.tolist()
