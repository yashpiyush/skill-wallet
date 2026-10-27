"""Unit tests for Module Two: Crack Diagnostics & Structural Integrity Screening."""

import unittest
from src.crack_analysis import (
    VALID_CRACK_CLASSIFICATIONS,
    VALID_URGENCIES,
    validate_crack_diagnostics_payload,
)


class TestCrackAnalysis(unittest.TestCase):
    """Test crack diagnostic normalization, defect classification, and mandatory engineer review."""

    def test_valid_crack_payload(self):
        raw_ai_output = {
            "module": "crack_diagnostics",
            "visual_classification": "Settlement-related patterns",
            "visible_observations": [
                "Stepped diagonal crack extending through mortar joints near exterior corner"
            ],
            "estimated_width_mm": None,
            "possible_causes": [
                "Differential foundation settlement or footing subsidence"
            ],
            "urgency": "High",
            "recommended_next_steps": [
                "Install calibrated tell-tale crack monitoring gauges to record movement"
            ],
            "limitations": [
                "Depth of crack and footing conditions cannot be visually verified"
            ],
            "human_engineer_review_required": True,
        }

        result = validate_crack_diagnostics_payload(
            raw_ai_output,
            user_inputs={"structure_type": "Brick Masonry Wall"},
        )

        self.assertEqual(result["module"], "crack_diagnostics")
        self.assertEqual(result["visual_classification"], "Settlement-related patterns")
        self.assertIsNone(result["estimated_width_mm"])
        self.assertEqual(result["urgency"], "High")
        self.assertTrue(result["human_engineer_review_required"])
        # Should have engineer step
        self.assertTrue(any("structural engineer" in s.lower() for s in result["recommended_next_steps"]))

    def test_crack_width_numeric_conversion(self):
        # Valid float string
        raw = {"visual_classification": "Hairline cracks", "estimated_width_mm": "0.45"}
        res = validate_crack_diagnostics_payload(raw)
        self.assertEqual(res["estimated_width_mm"], 0.45)

        # Non-numeric string should become None
        raw_invalid = {"visual_classification": "Hairline cracks", "estimated_width_mm": "approx 2mm"}
        res_invalid = validate_crack_diagnostics_payload(raw_invalid)
        self.assertIsNone(res_invalid["estimated_width_mm"])

    def test_urgency_normalization(self):
        raw = {"urgency": "very urgent!"}
        res = validate_crack_diagnostics_payload(raw)
        self.assertEqual(res["urgency"], "Uncertain")

        raw_valid = {"urgency": "urgent"}
        res_valid = validate_crack_diagnostics_payload(raw_valid)
        self.assertEqual(res_valid["urgency"], "Urgent")

    def test_mandatory_structural_caveats_always_injected(self):
        raw = {"visual_classification": "Other or uncertain defects"}
        res = validate_crack_diagnostics_payload(raw)
        self.assertTrue(any("does not constitute a structural safety certificate" in l.lower() for l in res["limitations"]))
        self.assertTrue(any("qualified, registered structural engineer" in l.lower() for l in res["limitations"]))

    def test_invalid_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_crack_diagnostics_payload(["list instead of dict"])


if __name__ == "__main__":
    unittest.main()
