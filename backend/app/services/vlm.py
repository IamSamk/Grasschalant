"""
Grasschalant Backend — PaliGemma Vision Language Model Service
Analyzes outdoor photos for pareidolia and meme analogy detection.
Uses HF Serverless Inference API with LM Studio fallback.
"""

import httpx
import base64
import json
import re
from typing import Dict, Any, Optional
from app.core.config import get_settings

# The structured prompt for pareidolia / meme analogy detection
ANALOGY_PROMPT = """You are an expert in pareidolia and internet culture. Analyze this outdoor image:
1. What is the literal physical object/subject? (e.g., cracked bark on an elm tree).
2. What famous meme template, reaction face, or internet character does this contour, shape, or texture resemble?
3. Explain the visual analogy: why can't someone unsee this?
4. Return valid JSON:
{
  "literal_description": "string",
  "meme_analogy_concept": "string",
  "explanation": "string",
  "match_confidence": 0.88,
  "tags": ["tree", "surprised-face", "pikachu"]
}
Only return the JSON object, no other text."""


async def analyze_outdoor_photo(image_bytes: bytes) -> Dict[str, Any]:
    """
    Send an outdoor photo to PaliGemma for pareidolia and meme analogy analysis.

    Tries HF Serverless Inference API first, falls back to LM Studio if configured.

    Args:
        image_bytes: Raw bytes of the captured outdoor photo.

    Returns:
        Dict with literal_description, meme_analogy_concept, explanation,
        match_confidence, and tags.
    """
    settings = get_settings()

    # Try Hugging Face Serverless API first
    if settings.HF_TOKEN:
        try:
            result = await _call_hf_inference(image_bytes, settings)
            if result:
                return result
        except Exception as e:
            print(f"[VLM] HF Inference failed: {e}, trying LM Studio fallback...")

    # Fallback to LM Studio local
    try:
        result = await _call_lmstudio(image_bytes, settings)
        if result:
            return result
    except Exception as e:
        print(f"[VLM] LM Studio fallback also failed: {e}")

    # Ultimate fallback: return a generic analysis
    return _generate_fallback_analysis()


async def _call_hf_inference(image_bytes: bytes, settings) -> Optional[Dict[str, Any]]:
    """Call Hugging Face Serverless Inference API for vision analysis."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Use the text-generation endpoint with vision capability
    api_url = f"https://api-inference.huggingface.co/models/{settings.HF_VISION_MODEL}"

    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {
            "image": b64_image,
            "text": ANALOGY_PROMPT,
        },
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        # Parse the generated text response
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
        elif isinstance(result, dict):
            generated_text = result.get("generated_text", str(result))
        else:
            generated_text = str(result)

        return _parse_vlm_response(generated_text)


async def _call_lmstudio(image_bytes: bytes, settings) -> Optional[Dict[str, Any]]:
    """Call LM Studio local server as fallback."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": settings.LOCAL_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                    {
                        "type": "text",
                        "text": ANALOGY_PROMPT,
                    },
                ],
            }
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.LMSTUDIO_BASE_URL}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {settings.LMSTUDIO_API_KEY}"},
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_vlm_response(content)


def _parse_vlm_response(raw_text: str) -> Dict[str, Any]:
    """
    Extract JSON from the VLM's raw text response.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    json_match = re.search(r"\{[^{}]*\"literal_description\"[^{}]*\}", raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    # If all parsing fails, construct from raw text
    return {
        "literal_description": raw_text[:200].strip(),
        "meme_analogy_concept": "mysterious outdoor object",
        "explanation": "This outdoor scene has an uncanny resemblance to something from the internet.",
        "match_confidence": 0.5,
        "tags": ["outdoor", "nature", "mystery"],
    }


def _generate_fallback_analysis() -> Dict[str, Any]:
    """Generate a fallback analysis when all inference methods fail."""
    return {
        "literal_description": "An intriguing outdoor scene captured during a walk",
        "meme_analogy_concept": "contemplative nature moment",
        "explanation": "Sometimes nature itself is the meme — this scene captures a moment of pure outdoor contemplation that anyone who's touched grass can relate to.",
        "match_confidence": 0.42,
        "tags": ["outdoor", "nature", "contemplation", "touch-grass"],
    }
