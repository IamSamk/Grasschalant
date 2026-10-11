"""
Grasschalant Backend — API Endpoints
Handles outing sessions, photo snaps, and storybook retrieval.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import json

from app.services.meme_search import get_outings_collection, vector_search_memes
from app.services.cloudinary_upload import upload_photo
from app.services.vlm import analyze_outdoor_photo
from app.services.embedder import embed_text


router = APIRouter(prefix="/api", tags=["outings"])


# ─── Request/Response Models ────────────────────────────────────────────────

class StartOutingRequest(BaseModel):
    goal_steps: int = Field(default=6000, ge=100, le=100000, description="Target step goal")
    total_photos_target: int = Field(default=10, ge=1, le=50, description="Number of photo milestones")


class OutingResponse(BaseModel):
    id: str
    goal_steps: int
    total_photos_target: int
    milestone_interval: int
    current_steps: int
    pages: list
    started_at: str
    status: str


class SnapResponse(BaseModel):
    page_index: int
    real_image_url: str
    meme_image_url: str
    meme_name: str
    literal_description: str
    meme_analogy_concept: str
    explanation: str
    match_confidence: float
    step_count: int
    timestamp: str


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/outings/start", response_model=OutingResponse)
async def start_outing(req: StartOutingRequest):
    """Initialize a new outdoor exploration outing session."""
    collection = get_outings_collection()

    milestone_interval = req.goal_steps // req.total_photos_target

    outing_doc = {
        "goal_steps": req.goal_steps,
        "total_photos_target": req.total_photos_target,
        "milestone_interval": milestone_interval,
        "current_steps": 0,
        "pages": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "status": "active",
    }

    result = await collection.insert_one(outing_doc)
    outing_id = str(result.inserted_id)

    return OutingResponse(
        id=outing_id,
        goal_steps=req.goal_steps,
        total_photos_target=req.total_photos_target,
        milestone_interval=milestone_interval,
        current_steps=0,
        pages=[],
        started_at=outing_doc["started_at"],
        status="active",
    )


@router.post("/outings/{outing_id}/snap", response_model=SnapResponse)
async def snap_photo(
    outing_id: str,
    photo: UploadFile = File(...),
    step_count: int = Form(...),
):
    """
    Capture a photo at a step milestone.

    - Validates step requirement is met
    - Uploads photo to Cloudinary
    - Runs PaliGemma analysis + Atlas vector search for meme match
    - Appends the page to the outing document
    """
    collection = get_outings_collection()

    # Fetch the outing
    try:
        outing = await collection.find_one({"_id": ObjectId(outing_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid outing ID format")

    if not outing:
        raise HTTPException(status_code=404, detail="Outing not found")

    if outing["status"] != "active":
        raise HTTPException(status_code=400, detail="Outing is not active")

    # Validate step milestone
    page_index = len(outing["pages"])
    required_steps = (page_index + 1) * outing["milestone_interval"]

    if step_count < required_steps:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {required_steps} steps for photo #{page_index + 1}. Current: {step_count}",
        )

    if page_index >= outing["total_photos_target"]:
        raise HTTPException(status_code=400, detail="All photo milestones have been captured")

    # Read uploaded image
    image_bytes = await photo.read()

    # 1. Upload to Cloudinary
    real_image_url = await upload_photo(image_bytes, outing_id, page_index)

    # 2. Run PaliGemma analysis
    analysis = await analyze_outdoor_photo(image_bytes)

    # 3. Generate CLIP embedding for the meme analogy concept
    concept_text = f"{analysis.get('meme_analogy_concept', '')} {' '.join(analysis.get('tags', []))}"
    query_embedding = embed_text(concept_text)

    # 4. Vector search for matching meme
    meme_matches = await vector_search_memes(query_embedding, top_k=1)

    meme_match = meme_matches[0] if meme_matches else {
        "name": "Touch Grass Moment",
        "image_url": "https://i.imgflip.com/4t0m5.jpg",
        "description": "Sometimes the best meme is just going outside",
        "score": 0.42,
    }

    # Build the page entry
    timestamp = datetime.now(timezone.utc).isoformat()
    page = {
        "page_index": page_index,
        "real_image_url": real_image_url,
        "meme_image_url": meme_match.get("image_url", ""),
        "meme_name": meme_match.get("name", "Unknown Meme"),
        "literal_description": analysis.get("literal_description", ""),
        "meme_analogy_concept": analysis.get("meme_analogy_concept", ""),
        "explanation": analysis.get("explanation", ""),
        "match_confidence": meme_match.get("score", analysis.get("match_confidence", 0.5)),
        "step_count": step_count,
        "timestamp": timestamp,
    }

    # 5. Update outing document
    update_result = await collection.update_one(
        {"_id": ObjectId(outing_id)},
        {
            "$push": {"pages": page},
            "$set": {"current_steps": step_count},
        },
    )

    # Check if outing is complete
    if page_index + 1 >= outing["total_photos_target"]:
        await collection.update_one(
            {"_id": ObjectId(outing_id)},
            {"$set": {"status": "completed", "ended_at": timestamp}},
        )

    return SnapResponse(**page)


@router.get("/outings/{outing_id}", response_model=OutingResponse)
async def get_outing(outing_id: str):
    """Retrieve a complete outing with all pages for storybook rendering."""
    collection = get_outings_collection()

    try:
        outing = await collection.find_one({"_id": ObjectId(outing_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid outing ID format")

    if not outing:
        raise HTTPException(status_code=404, detail="Outing not found")

    return OutingResponse(
        id=str(outing["_id"]),
        goal_steps=outing["goal_steps"],
        total_photos_target=outing["total_photos_target"],
        milestone_interval=outing["milestone_interval"],
        current_steps=outing["current_steps"],
        pages=outing["pages"],
        started_at=outing["started_at"],
        status=outing["status"],
    )


@router.get("/outings")
async def list_outings():
    """List all outings (most recent first)."""
    collection = get_outings_collection()
    outings = []
    async for doc in collection.find().sort("started_at", -1).limit(20):
        outings.append({
            "id": str(doc["_id"]),
            "goal_steps": doc["goal_steps"],
            "total_photos_target": doc["total_photos_target"],
            "current_steps": doc["current_steps"],
            "pages_count": len(doc.get("pages", [])),
            "started_at": doc["started_at"],
            "status": doc["status"],
        })
    return outings
