"""
Grasschalant Backend — Core Configuration
Loads all environment variables via pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # MongoDB Atlas
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "grasschalant"
    MONGODB_COLLECTION_MEMES: str = "meme_vault"
    MONGODB_COLLECTION_OUTINGS: str = "outings"
    MONGODB_VECTOR_INDEX_NAME: str = "meme_vector_index"

    # Hugging Face
    HF_TOKEN: str = ""
    HF_VISION_MODEL: str = "google/paligemma-3b-pt-224"

    # LM Studio fallback
    LMSTUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LMSTUDIO_API_KEY: str = "lm-studio"
    LOCAL_VISION_MODEL: str = "abetlen/paligemma-3b-mix-224-gguf"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER: str = "grasschalant_walks"

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
