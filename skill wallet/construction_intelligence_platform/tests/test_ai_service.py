"""Unit tests for AI service utilities, mock calls, and JSON extraction."""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.ai_service import (
    APIKeyMissingError,
    AIResponseFormatError,
    extract_json_from_text,
    resolve_api_key,
    resolve_model_name,
)


class TestAIService(unittest.TestCase):
    """Test AI service helper functions, extraction, and error handling with mocks."""

    def test_extract_json_from_clean_text(self):
        raw = '{"status": "ok", "count": 42}'
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["count"], 42)

    def test_extract_json_from_markdown_code_block(self):
        raw = """Here is the audit result:
```json
{
  "module": "site_safety_ppe_audit",
  "overall_status": "REQUIRES_HUMAN_REVIEW"
}
```
Please let me know if you need more details."""
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["module"], "site_safety_ppe_audit")
        self.assertEqual(parsed["overall_status"], "REQUIRES_HUMAN_REVIEW")

    def test_extract_json_from_embedded_braces(self):
        raw = "Prefix explanation: {\"urgency\": \"Urgent\", \"causes\": [\"settlement\"]} suffix text."
        parsed = extract_json_from_text(raw)
        self.assertEqual(parsed["urgency"], "Urgent")
        self.assertEqual(parsed["causes"], ["settlement"])

    def test_extract_json_empty_or_malformed(self):
        with self.assertRaises(AIResponseFormatError):
            extract_json_from_text("")

        with self.assertRaises(AIResponseFormatError):
            extract_json_from_text("This contains no JSON whatsoever.")

    def test_resolve_api_key_priority(self):
        # 1. Session key takes top precedence
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env_key_12345"}):
            resolved = resolve_api_key(session_api_key="session_key_99999")
            self.assertEqual(resolved, "session_key_99999")

        # 2. Env key used when session key is absent
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env_key_12345"}):
            resolved = resolve_api_key(session_api_key=None)
            self.assertEqual(resolved, "env_key_12345")

        # 3. None returned when nothing is configured
        with patch.dict(os.environ, {}, clear=True):
            resolved = resolve_api_key(session_api_key="")
            self.assertIsNone(resolved)

    def test_resolve_model_name_default(self):
        with patch.dict(os.environ, {}, clear=True):
            model = resolve_model_name(None)
            self.assertEqual(model, "gemini-2.5-flash")


if __name__ == "__main__":
    unittest.main()
