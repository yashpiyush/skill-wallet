"""Unit tests for Module Four: Weather-Aware Safety Advisory and Checklists."""

import unittest
from src.weather_advisory import (
    WEATHER_ADVISORIES,
    WEATHER_CONDITIONS,
    get_weather_advisory,
)


class TestWeatherAdvisory(unittest.TestCase):
    """Test weather condition guidance, checklist completeness, and fallback behavior."""

    def test_all_defined_weather_conditions_exist(self):
        for condition in WEATHER_CONDITIONS:
            self.assertIn(condition, WEATHER_ADVISORIES)
            advisory = get_weather_advisory(condition)
            self.assertIn("title", advisory)
            self.assertIn("checklist", advisory)
            self.assertIn("precautions", advisory)
            self.assertGreater(len(advisory["checklist"]), 0)

    def test_fallback_for_unknown_weather(self):
        fallback = get_weather_advisory("Severe Hurricane")
        self.assertEqual(fallback["title"], WEATHER_ADVISORIES["Normal"]["title"])

    def test_high_wind_checklist_content(self):
        wind = get_weather_advisory("High Wind")
        checklist_text = " ".join([item["item"] for item in wind["checklist"]]).lower()
        self.assertIn("crane", checklist_text)
        self.assertIn("loose", checklist_text)

    def test_heavy_rain_checklist_content(self):
        rain = get_weather_advisory("Heavy Rain")
        checklist_text = " ".join([item["item"] for item in rain["checklist"]]).lower()
        self.assertIn("trench", checklist_text)
        self.assertIn("electrical", checklist_text)

    def test_extreme_heat_checklist_content(self):
        heat = get_weather_advisory("Extreme Heat")
        checklist_text = " ".join([item["item"] for item in heat["checklist"]]).lower()
        self.assertIn("hydration", checklist_text)
        self.assertIn("rest", checklist_text)

    def test_cold_conditions_checklist_content(self):
        cold = get_weather_advisory("Cold Conditions")
        checklist_text = " ".join([item["item"] for item in cold["checklist"]]).lower()
        self.assertIn("concrete", checklist_text)
        self.assertIn("ice", checklist_text)


if __name__ == "__main__":
    unittest.main()
