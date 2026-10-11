"""
Grasschalant Backend — Cloudinary Upload Service
Handles uploading outdoor photos to Cloudinary CDN.
"""

import cloudinary
import cloudinary.uploader
from app.core.config import get_settings
import base64
import io


def configure_cloudinary():
    """Initialize Cloudinary SDK with credentials from settings."""
    settings = get_settings()
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_photo(image_bytes: bytes, outing_id: str, snap_index: int) -> str:
    """
    Upload a photo to Cloudinary and return the secure URL.

    Args:
        image_bytes: Raw image bytes from the camera capture.
        outing_id: The outing session ID for folder organization.
        snap_index: The sequential snap number within the outing.

    Returns:
        The secure URL of the uploaded image.
    """
    settings = get_settings()
    configure_cloudinary()

    public_id = f"{settings.CLOUDINARY_FOLDER}/{outing_id}/snap_{snap_index}"

    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=public_id,
        folder=None,  # public_id already includes the folder path
        resource_type="image",
        overwrite=True,
        transformation=[
            {"quality": "auto:good", "fetch_format": "auto"},
        ],
    )

    return result["secure_url"]
