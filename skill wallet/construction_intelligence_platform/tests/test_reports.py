"""Unit tests for report generation, metadata contracts, and JSON serialization."""

import json
from datetime import datetime, timezone
import unittest

from src.report_utils import create_base_report, get_current_timestamp, serialize_report


class TestReportUtils(unittest.TestCase):
    """Test report payload envelopes, ISO timestamps, and robust JSON serialization."""

    def test_get_current_timestamp_iso_format(self):
        ts = get_current_timestamp()
        self.assertIsInstance(ts, str)
        # Should be parseable as ISO datetime
        dt = datetime.fromisoformat(ts)
        self.assertIsNotNone(dt.tzinfo)

    def test_create_base_report_contract(self):
        report = create_base_report(
            module="site_safety_ppe_audit",
            human_review_required=True,
            assumptions=["Clear daylight photograph"],
            limitations=["Preliminary visual screening only"],
            input_metadata={"site_id": "SITE-101"},
        )

        self.assertEqual(report["module"], "site_safety_ppe_audit")
        self.assertEqual(report["platform"], "Multimodal Construction Intelligence Platform")
        self.assertEqual(report["version"], "1.0.0")
        self.assertTrue(report["human_review_required"])
        self.assertIn("Preliminary visual screening only", report["limitations"])
        self.assertIn("Clear daylight photograph", report["assumptions"])
        self.assertEqual(report["input_metadata"]["site_id"], "SITE-101")

    def test_serialize_report_json(self):
        sample_report = {
            "module": "crack_diagnostics",
            "timestamp": datetime.now(timezone.utc),
            "findings": ["Diagonal hairline crack"],
            "metrics": {"width_mm": 0.5},
        }

        json_str = serialize_report(sample_report, indent=2)
        self.assertIsInstance(json_str, str)

        # Confirm it re-parses cleanly back to dictionary
        parsed = json.loads(json_str)
        self.assertEqual(parsed["module"], "crack_diagnostics")
        self.assertEqual(parsed["metrics"]["width_mm"], 0.5)


if __name__ == "__main__":
    unittest.main()
