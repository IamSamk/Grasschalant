"""
Grasschalant Backend Tests
Tests configuration, VLM parser, embedder, and API endpoints.
"""

import unittest
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import get_settings
from app.services.vlm import _parse_vlm_response, _generate_fallback_analysis
from app.services.embedder import embed_text
from fastapi.testclient import TestClient
from app.main import app


class TestConfig(unittest.TestCase):
    def test_settings_loaded(self):
        settings = get_settings()
        self.assertEqual(settings.MONGODB_DB_NAME, "grasschalant")
        self.assertEqual(settings.MONGODB_COLLECTION_MEMES, "meme_vault")
        self.assertEqual(settings.MONGODB_COLLECTION_OUTINGS, "outings")
        self.assertEqual(settings.MONGODB_VECTOR_INDEX_NAME, "meme_vector_index")
        self.assertTrue(len(settings.MONGODB_URI) > 0)


class TestVLM(unittest.TestCase):
    def test_clean_json_parsing(self):
        raw = '{"literal_description": "bark on tree", "meme_analogy_concept": "sad face", "explanation": "looks sad", "match_confidence": 0.85, "tags": ["tree", "face"]}'
        parsed = _parse_vlm_response(raw)
        self.assertEqual(parsed["literal_description"], "bark on tree")
        self.assertEqual(parsed["meme_analogy_concept"], "sad face")
        self.assertEqual(parsed["match_confidence"], 0.85)

    def test_markdown_code_block_parsing(self):
        raw = 'Here is the analysis:\n```json\n{"literal_description": "cracked wall", "meme_analogy_concept": "doge", "explanation": "much crack", "match_confidence": 0.9, "tags": ["wall"]}\n```'
        parsed = _parse_vlm_response(raw)
        self.assertEqual(parsed["literal_description"], "cracked wall")
        self.assertEqual(parsed["meme_analogy_concept"], "doge")

    def test_fallback_analysis(self):
        fallback = _generate_fallback_analysis()
        self.assertIn("literal_description", fallback)
        self.assertIn("meme_analogy_concept", fallback)
        self.assertIn("explanation", fallback)
        self.assertIn("match_confidence", fallback)
        self.assertIn("tags", fallback)


class TestEmbedder(unittest.TestCase):
    def test_embed_text_dimensions(self):
        vector = embed_text("surprised yellow mouse face")
        self.assertEqual(len(vector), 512)
        # Vector should be normalized (L2 norm ~ 1.0)
        norm = sum(x**2 for x in vector) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=2)


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["app"], "Grasschalant")
        self.assertIn("Touch Grass", data["tagline"])
        self.assertIn("start_outing", data["endpoints"])

    def test_start_outing_validation(self):
        # Invalid goal steps (< 100)
        res = self.client.post("/api/outings/start", json={"goal_steps": 50, "total_photos_target": 10})
        self.assertEqual(res.status_code, 422)

        # Invalid photo target (> 50)
        res = self.client.post("/api/outings/start", json={"goal_steps": 6000, "total_photos_target": 100})
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()
