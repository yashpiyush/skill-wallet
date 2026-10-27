"""Unit tests for input validation, file security, and constraint enforcement."""

import io
import unittest
from PIL import Image

from src.validation import (
    sanitize_text_input,
    validate_api_key,
    validate_crack_inputs,
    validate_image_file,
    validate_planning_inputs,
)


def create_in_memory_image(format: str = "JPEG", size: tuple = (100, 100)) -> bytes:
    """Helper to generate a clean synthetic image buffer in memory."""
    buf = io.BytesIO()
    # JPEG does not support RGBA, use RGB
    mode = "RGB" if format.upper() == "JPEG" else "RGBA"
    img = Image.new(mode, size, color=(255, 140, 0))
    img.save(buf, format=format)
    return buf.getvalue()


class TestValidationModule(unittest.TestCase):
    """Test validation boundaries for files, numbers, and credentials."""

    def test_valid_jpeg_image(self):
        img_bytes = create_in_memory_image("JPEG")
        is_valid, err, pil_img = validate_image_file(img_bytes, "test_site.jpg")
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertIsNotNone(pil_img)
        self.assertEqual(pil_img.size, (100, 100))

    def test_valid_png_image(self):
        img_bytes = create_in_memory_image("PNG")
        is_valid, err, pil_img = validate_image_file(img_bytes, "blueprint.png")
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertIsNotNone(pil_img)

    def test_invalid_image_extension(self):
        img_bytes = create_in_memory_image("JPEG")
        is_valid, err, _ = validate_image_file(img_bytes, "executable.exe")
        self.assertFalse(is_valid)
        self.assertIn("Unsupported file format", err)

    def test_empty_image_bytes(self):
        is_valid, err, _ = validate_image_file(b"", "empty.jpg")
        self.assertFalse(is_valid)
        self.assertIn("empty", err.lower())

    def test_oversized_image_rejection(self):
        # Create a small image but set max_size_mb threshold artificially low (0.0001 MB = 100 bytes)
        img_bytes = create_in_memory_image("JPEG")
        is_valid, err, _ = validate_image_file(img_bytes, "large.jpg", max_size_mb=0.0001)
        self.assertFalse(is_valid)
        self.assertIn("exceeds maximum allowed size", err)

    def test_corrupted_image_bytes(self):
        corrupt_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00fake_corrupt_data"
        is_valid, err, _ = validate_image_file(corrupt_bytes, "corrupt.jpg")
        self.assertFalse(is_valid)
        self.assertIn("corrupted", err.lower())

    def test_planning_inputs_valid(self):
        is_valid, errors = validate_planning_inputs(
            built_up_area=2500.0,
            cost_per_sqft=2000.0,
            completion_pct=50.0,
            market_val_per_sqft=6000.0,
            steel_req_per_sqft=3.5,
            cement_req_per_sqft=0.4,
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_planning_inputs_negative_area(self):
        is_valid, errors = validate_planning_inputs(
            built_up_area=-500.0,
            cost_per_sqft=2000.0,
            completion_pct=50.0,
            market_val_per_sqft=6000.0,
            steel_req_per_sqft=3.5,
            cement_req_per_sqft=0.4,
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("Built-up area" in e for e in errors))

    def test_planning_inputs_completion_percentage_range(self):
        # Above 100%
        is_valid, errors = validate_planning_inputs(
            built_up_area=1000.0,
            cost_per_sqft=2000.0,
            completion_pct=105.0,
            market_val_per_sqft=6000.0,
            steel_req_per_sqft=3.5,
            cement_req_per_sqft=0.4,
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("Completion percentage" in e for e in errors))

        # Below 0%
        is_valid, errors = validate_planning_inputs(
            built_up_area=1000.0,
            cost_per_sqft=2000.0,
            completion_pct=-5.0,
            market_val_per_sqft=6000.0,
            steel_req_per_sqft=3.5,
            cement_req_per_sqft=0.4,
        )
        self.assertFalse(is_valid)

    def test_api_key_validation(self):
        # Empty
        valid, _ = validate_api_key("")
        self.assertFalse(valid)

        # None
        valid, _ = validate_api_key(None)
        self.assertFalse(valid)

        # Placeholder
        valid, msg = validate_api_key("YOUR_API_KEY")
        self.assertFalse(valid)
        self.assertIn("Placeholder", msg)

        # Too short
        valid, msg = validate_api_key("abc12")
        self.assertFalse(valid)

        # Realistic
        valid, msg = validate_api_key("AIzaSyD-sample_test_key_123456789")
        self.assertTrue(valid)
        self.assertIsNone(msg)

    def test_sanitize_text_input(self):
        self.assertEqual(sanitize_text_input("  Hello world  "), "Hello world")
        self.assertEqual(sanitize_text_input(None), "")
        long_text = "A" * 2000
        sanitized = sanitize_text_input(long_text, max_length=100)
        self.assertEqual(len(sanitized), 100)

    def test_crack_input_validation(self):
        # Valid None (optional field)
        valid, _ = validate_crack_inputs(None)
        self.assertTrue(valid)

        # Valid float
        valid, _ = validate_crack_inputs(2.5)
        self.assertTrue(valid)

        # Negative width
        valid, err = validate_crack_inputs(-1.0)
        self.assertFalse(valid)
        self.assertIn("negative", err)

        # Excessively large
        valid, err = validate_crack_inputs(1000.0)
        self.assertFalse(valid)
        self.assertIn("exceeds", err)


if __name__ == "__main__":
    unittest.main()
