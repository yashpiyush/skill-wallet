"""Unit tests for Module Three: Planning, Budgeting, and Real Estate Valuation."""

import unittest
from src.planning import (
    PlanningInputs,
    PlanningOutputs,
    calculate_planning_metrics,
    generate_planning_report,
    get_default_benchmarks,
)
from src.report_utils import format_inr, format_inr_compact


class TestPlanningCalculations(unittest.TestCase):
    """Test deterministic formulas and currency formatting for construction planning."""

    def setUp(self):
        self.sample_inputs = PlanningInputs(
            structure_type="Residential",
            built_up_area_sqft=2000.0,
            location_tier="Tier 1",
            cost_per_sqft_inr=2500.0,
            completion_pct=40.0,
            market_val_per_sqft_inr=8000.0,
            steel_req_kg_per_sqft=3.5,
            cement_req_bags_per_sqft=0.4,
        )

    def test_total_budget_calculation(self):
        """Formula: Total budget = Built-up area × Assumed construction cost per sq ft."""
        outputs = calculate_planning_metrics(self.sample_inputs)
        expected_budget = 2000.0 * 2500.0  # 5,000,000 INR
        self.assertEqual(outputs.total_budget_inr, expected_budget)

    def test_expenditure_and_remaining_budget_calculation(self):
        """Formula:
        Estimated expenditure = Total budget × Completion percentage / 100
        Remaining budget = Total budget - Estimated expenditure
        """
        outputs = calculate_planning_metrics(self.sample_inputs)
        expected_expenditure = 5000000.0 * (40.0 / 100.0)  # 2,000,000 INR
        expected_remaining = 5000000.0 - 2000000.0         # 3,000,000 INR

        self.assertEqual(outputs.estimated_expenditure_inr, expected_expenditure)
        self.assertEqual(outputs.remaining_budget_inr, expected_remaining)
        self.assertEqual(
            outputs.estimated_expenditure_inr + outputs.remaining_budget_inr,
            outputs.total_budget_inr,
        )

    def test_property_valuation_calculation(self):
        """Formula: Illustrative market valuation = Built-up area × Assumed market value per sq ft."""
        outputs = calculate_planning_metrics(self.sample_inputs)
        expected_valuation = 2000.0 * 8000.0  # 16,000,000 INR
        self.assertEqual(outputs.illustrative_market_valuation_inr, expected_valuation)

    def test_steel_and_cement_quantities(self):
        """Formulas:
        Indicative steel quantity = Built-up area × Steel requirement per sq ft
        Indicative cement quantity = Built-up area × Cement requirement per sq ft
        """
        outputs = calculate_planning_metrics(self.sample_inputs)
        expected_steel_kg = 2000.0 * 3.5      # 7,000 kg
        expected_steel_tons = 7000.0 / 1000.0 # 7.0 MT
        expected_cement_bags = 2000.0 * 0.4   # 800 bags

        self.assertEqual(outputs.indicative_steel_quantity_kg, expected_steel_kg)
        self.assertEqual(outputs.indicative_steel_quantity_metric_tons, expected_steel_tons)
        self.assertEqual(outputs.indicative_cement_quantity_bags, expected_cement_bags)

    def test_boundary_zero_and_hundred_percent_completion(self):
        """Test 0% and 100% completion edge cases."""
        # 0% completion
        inputs_0 = PlanningInputs(
            structure_type="Commercial",
            built_up_area_sqft=1000.0,
            location_tier="Tier 2",
            cost_per_sqft_inr=3000.0,
            completion_pct=0.0,
            market_val_per_sqft_inr=7000.0,
            steel_req_kg_per_sqft=4.0,
            cement_req_bags_per_sqft=0.45,
        )
        out_0 = calculate_planning_metrics(inputs_0)
        self.assertEqual(out_0.estimated_expenditure_inr, 0.0)
        self.assertEqual(out_0.remaining_budget_inr, 3000000.0)

        # 100% completion
        inputs_100 = PlanningInputs(
            structure_type="Commercial",
            built_up_area_sqft=1000.0,
            location_tier="Tier 2",
            cost_per_sqft_inr=3000.0,
            completion_pct=100.0,
            market_val_per_sqft_inr=7000.0,
            steel_req_kg_per_sqft=4.0,
            cement_req_bags_per_sqft=0.45,
        )
        out_100 = calculate_planning_metrics(inputs_100)
        self.assertEqual(out_100.estimated_expenditure_inr, 3000000.0)
        self.assertEqual(out_100.remaining_budget_inr, 0.0)

    def test_indian_rupee_formatting(self):
        """Test Indian numbering system comma grouping."""
        self.assertEqual(format_inr(0), "₹ 0")
        self.assertEqual(format_inr(500), "₹ 500")
        self.assertEqual(format_inr(1500), "₹ 1,500")
        self.assertEqual(format_inr(50000), "₹ 50,000")
        self.assertEqual(format_inr(100000), "₹ 1,00,000")
        self.assertEqual(format_inr(12500000), "₹ 1,25,00,000")
        self.assertEqual(format_inr(-50000), "-₹ 50,000")

    def test_compact_currency_formatting(self):
        """Test Lakh and Crore compact formatting."""
        self.assertEqual(format_inr_compact(1500000), "₹ 15.00 Lakh")
        self.assertEqual(format_inr_compact(25000000), "₹ 2.50 Cr")

    def test_planning_report_generation(self):
        """Test structured JSON contract for planning module."""
        outputs = calculate_planning_metrics(self.sample_inputs)
        report = generate_planning_report(self.sample_inputs, outputs)

        self.assertEqual(report["module"], "planning_and_real_estate_valuation")
        self.assertTrue(report["human_review_required"])
        self.assertIn("calculations", report)
        self.assertIn("limitations", report)
        self.assertGreater(len(report["limitations"]), 0)
        self.assertEqual(report["calculations"]["total_budget_inr"], 5000000.0)


if __name__ == "__main__":
    unittest.main()
