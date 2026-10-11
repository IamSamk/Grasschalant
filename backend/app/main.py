"""
Grasschalant Backend — FastAPI Application Entry Point
An outdoor exploration companion and digital memory book generator.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api.endpoints import router as api_router
from app.services.meme_search import get_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: verify MongoDB connection on startup."""
    settings = get_settings()
    client = get_mongo_client()
    try:
        await client.admin.command("ping")
        print(f"[Grasschalant] ✅ Connected to MongoDB Atlas — db: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"[Grasschalant] ⚠️  MongoDB connection warning: {e}")
    yield
    client.close()
    print("[Grasschalant] 🔌 MongoDB connection closed.")


app = FastAPI(
    title="Grasschalant API",
    description="Touch Grass Edition — Outdoor exploration companion & digital memory book generator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
settings = get_settings()
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "app": "Grasschalant",
        "tagline": "Touch Grass Edition 🌿",
        "version": "1.0.0",
        "endpoints": {
            "start_outing": "POST /api/outings/start",
            "snap_photo": "POST /api/outings/{id}/snap",
            "get_outing": "GET /api/outings/{id}",
            "list_outings": "GET /api/outings",
        },
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
