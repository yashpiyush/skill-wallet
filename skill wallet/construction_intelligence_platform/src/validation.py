"""Validation module for user inputs, uploaded images, and operational constraints."""

from __future__ import annotations

import io
from typing import Optional, Tuple
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_MAX_IMAGE_MB = 10.0


def validate_image_file(
    file_bytes: bytes,
    filename: str,
    max_size_mb: float = DEFAULT_MAX_IMAGE_MB,
) -> Tuple[bool, Optional[str], Optional[Image.Image]]:
    """Validate uploaded image file bytes, extension, and integrity.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original name of the uploaded file.
        max_size_mb: Maximum allowed file size in megabytes.

    Returns:
        A tuple of (is_valid, error_message, pil_image).
    """
    if not file_bytes or len(file_bytes) == 0:
        return False, "No image file was provided or file is empty.", None

    # Check file size
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return (
            False,
            f"File size ({size_mb:.2f} MB) exceeds maximum allowed size of {max_size_mb:.1f} MB.",
            None,
        )

    # Check extension
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        return (
            False,
            f"Unsupported file format '.{extension}'. Allowed formats are: {allowed}.",
            None,
        )

    # Verify image integrity via Pillow
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verifies file header and integrity
        # Re-open for actual return as verify() alters image internal state
        verified_image = Image.open(io.BytesIO(file_bytes))
        
        # Verify non-trivial dimensions
        width, height = verified_image.size
        if width < 10 or height < 10:
            return False, f"Image dimensions ({width}x{height}) are too small for visual inspection.", None

        return True, None, verified_image
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return False, f"Invalid or corrupted image file: {str(exc)}", None


def validate_planning_inputs(
    built_up_area: float,
    cost_per_sqft: float,
    completion_pct: float,
    market_val_per_sqft: float,
    steel_req_per_sqft: float,
    cement_req_per_sqft: float,
) -> Tuple[bool, list[str]]:
    """Validate numeric inputs for deterministic construction planning.

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    errors: list[str] = []

    if built_up_area <= 0:
        errors.append("Built-up area must be strictly greater than 0 sq ft.")
    if built_up_area > 50_000_000:
        errors.append("Built-up area exceeds maximum realistic threshold (50,000,000 sq ft).")

    if cost_per_sqft < 0:
        errors.append("Construction cost per sq ft cannot be negative.")
    if cost_per_sqft > 1_000_000:
        errors.append("Construction cost per sq ft exceeds realistic maximum (₹1,000,000).")

    if completion_pct < 0.0 or completion_pct > 100.0:
        errors.append("Completion percentage must be between 0.0% and 100.0%.")

    if market_val_per_sqft < 0:
        errors.append("Assumed market value per sq ft cannot be negative.")
    if market_val_per_sqft > 5_000_000:
        errors.append("Market value per sq ft exceeds realistic maximum (₹5,000,000).")

    if steel_req_per_sqft < 0:
        errors.append("Steel requirement cannot be negative.")
    if steel_req_per_sqft > 100:
        errors.append("Steel requirement per sq ft is unrealistically high (>100 kg/sq ft).")

    if cement_req_per_sqft < 0:
        errors.append("Cement requirement cannot be negative.")
    if cement_req_per_sqft > 50:
        errors.append("Cement requirement per sq ft is unrealistically high (>50 bags/sq ft).")

    return len(errors) == 0, errors


def validate_api_key(api_key: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Validate format and presence of Gemini API key."""
    if not api_key or not isinstance(api_key, str) or not api_key.strip():
        return False, "Gemini API key is not configured or is empty."

    cleaned = api_key.strip()
    if cleaned in {"YOUR_API_KEY", "your_gemini_api_key", "ENTER_KEY_HERE"}:
        return False, "Placeholder API key detected. Please configure a valid Google Gemini API key."

    if len(cleaned) < 15:
        return False, "Gemini API key appears too short to be valid."

    return True, None


def sanitize_text_input(text: Optional[str], max_length: int = 1500) -> str:
    """Sanitize and limit length of user-entered prompt questions or notes."""
    if not text:
        return ""
    sanitized = text.strip()
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized


def validate_crack_inputs(measured_width_mm: Optional[float]) -> Tuple[bool, Optional[str]]:
    """Validate optional physical crack width measurement in millimetres."""
    if measured_width_mm is not None:
        if measured_width_mm < 0:
            return False, "Crack width measurement cannot be negative."
        if measured_width_mm > 500:
            return False, "Measured crack width exceeds maximum realistic limit (500 mm)."
    return True, None
