"""
Grasschalant Backend — MongoDB Atlas Vector Search Service
Queries the meme_vault collection using $vectorSearch to find matching meme archetypes.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from typing import Optional, List, Dict, Any
from functools import lru_cache


_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the MongoDB async client singleton."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _client


def get_db():
    """Get the grasschalant database handle."""
    settings = get_settings()
    return get_mongo_client()[settings.MONGODB_DB_NAME]


def get_meme_collection():
    """Get the meme_vault collection handle."""
    settings = get_settings()
    return get_db()[settings.MONGODB_COLLECTION_MEMES]


def get_outings_collection():
    """Get the outings collection handle."""
    settings = get_settings()
    return get_db()[settings.MONGODB_COLLECTION_OUTINGS]


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute dot product of two normalized vectors."""
    return sum(a * b for a, b in zip(vec1, vec2))


async def _exact_vector_search_fallback(
    query_embedding: List[float],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Fallback cosine similarity search directly against stored vectors in MongoDB.
    Guarantees search functionality even if Atlas Vector Search index is pending.
    """
    collection = get_meme_collection()
    candidates = []
    async for doc in collection.find({}, {
        "name": 1,
        "description": 1,
        "visual_tags": 1,
        "image_url": 1,
        "category": 1,
        "embedding": 1,
    }):
        emb = doc.get("embedding")
        if emb and len(emb) == len(query_embedding):
            score = _cosine_similarity(query_embedding, emb)
            candidates.append({
                "name": doc.get("name"),
                "description": doc.get("description"),
                "visual_tags": doc.get("visual_tags", []),
                "image_url": doc.get("image_url"),
                "category": doc.get("category"),
                "score": round(float(score), 4),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


async def vector_search_memes(
    query_embedding: List[float],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Execute a MongoDB Atlas $vectorSearch against the meme_vault collection.
    Gracefully falls back to exact vector cosine search if Atlas index is pending.

    Args:
        query_embedding: 512-dim CLIP vector from the PaliGemma analogy concept.
        top_k: Number of nearest neighbors to return.

    Returns:
        List of matched meme documents with similarity scores.
    """
    settings = get_settings()
    collection = get_meme_collection()

    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.MONGODB_VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "description": 1,
                "visual_tags": 1,
                "image_url": 1,
                "category": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    results = []
    try:
        async for doc in collection.aggregate(pipeline):
            results.append(doc)
    except Exception as e:
        print(f"[MemeSearch] Atlas $vectorSearch notice ({e}), using exact vector fallback...")

    # If Atlas index is still building or returned 0 results, use fallback
    if not results:
        results = await _exact_vector_search_fallback(query_embedding, top_k=top_k)

    return results
