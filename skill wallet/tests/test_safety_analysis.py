"""Unit tests for Module One: Site Safety & PPE Audit normalization and contract adherence."""

import unittest
from src.safety_analysis import (
    SAFETY_SYSTEM_INSTRUCTION,
    VALID_HAZARD_SEVERITIES,
    VALID_PPE_STATUSES,
    validate_safety_audit_payload,
)


class TestSafetyAnalysis(unittest.TestCase):
    """Test safety audit payload validation, category mapping, and disclaimer enforcement."""

    def test_valid_payload_normalization(self):
        raw_ai_output = {
            "module": "site_safety_ppe_audit",
            "overall_status": "REQUIRES_HUMAN_REVIEW",
            "ppe_detection": [
                {
                    "item": "Safety helmets",
                    "status": "Compliant and visibly present",
                    "visible_evidence": "All 3 workers in foreground wearing yellow hard hats",
                    "notes": "Proper chinstraps not clearly verifiable",
                },
                {
                    "item": "Safety harnesses",
                    "status": "Not visible",
                    "visible_evidence": "Workers are ground-level; no elevated tasks observed",
                    "notes": "Harness not required at ground grade",
                },
            ],
            "hazards": [
                {
                    "hazard_description": "Uncapped starter rebar protruding near walkway",
                    "severity": "High",
                    "evidence": "Vertical rebar without mushroom safety caps",
                    "corrective_action": "Install high-visibility rebar protection caps immediately",
                    "uncertainty_level": "Clearly visible in left foreground",
                }
            ],
            "site_observations": ["Foundation casting stage"],
            "limitations": ["Camera angle restricted to north foundation"],
            "human_review_required": True,
        }

        result = validate_safety_audit_payload(raw_ai_output)
        self.assertEqual(result["module"], "site_safety_ppe_audit")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(len(result["ppe_detection"]), 2)
        self.assertEqual(result["ppe_detection"][0]["status"], "Compliant and visibly present")
        self.assertEqual(result["ppe_detection"][1]["status"], "Not visible")
        self.assertEqual(len(result["hazards"]), 1)
        self.assertEqual(result["hazards"][0]["severity"], "High")

    def test_malformed_ppe_status_normalization(self):
        raw = {
            "ppe_detection": [
                {"item": "Vest", "status": "present on site"},
                {"item": "Boots", "status": "worker feet unseen"},
                {"item": "Glasses", "status": "random text"},
            ]
        }
        result = validate_safety_audit_payload(raw)
        statuses = [item["status"] for item in result["ppe_detection"]]
        self.assertEqual(statuses[0], "Compliant and visibly present")
        self.assertEqual(statuses[1], "Not visible")
        self.assertEqual(statuses[2], "Uncertain")

    def test_malformed_hazard_severity_normalization(self):
        raw = {
            "hazards": [
                {"hazard_description": "Wet floor", "severity": "super dangerous!"},
                {"hazard_description": "Scaffold edge", "severity": "critical"},
            ]
        }
        result = validate_safety_audit_payload(raw)
        self.assertEqual(result["hazards"][0]["severity"], "Uncertain")
        self.assertEqual(result["hazards"][1]["severity"], "Critical")

    def test_mandatory_disclaimers_always_present(self):
        raw = {"ppe_detection": [], "hazards": [], "limitations": []}
        result = validate_safety_audit_payload(raw)
        self.assertTrue(result["human_review_required"])
        # Verify explicit safety limitations are present
        self.assertTrue(any("cannot verify certified material ratings" in l for l in result["limitations"]))
        self.assertTrue(any("blind spots" in l for l in result["limitations"]))

    def test_invalid_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_safety_audit_payload("not a dictionary")


if __name__ == "__main__":
    unittest.main()
