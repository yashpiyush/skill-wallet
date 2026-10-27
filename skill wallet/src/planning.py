"""Module Three: Deterministic Planning, Budgeting, and Real Estate Valuation Calculator."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Tuple

from src.report_utils import create_base_report, format_inr, format_inr_compact
from src.validation import validate_planning_inputs


STRUCTURE_TYPES = ["Residential", "Commercial", "Industrial", "Institutional"]
LOCATION_TIERS = ["Tier 1", "Tier 2", "Tier 3"]

# Typical default benchmark estimates (per sq ft) for Indian construction context
# These serve as starting defaults; user can adjust any parameter.
BENCHMARK_DEFAULTS = {
    ("Residential", "Tier 1"): {
        "cost_per_sqft": 2400.0,
        "market_val_per_sqft": 8500.0,
        "steel_kg_per_sqft": 3.75,
        "cement_bags_per_sqft": 0.42,
    },
    ("Residential", "Tier 2"): {
        "cost_per_sqft": 1900.0,
        "market_val_per_sqft": 5200.0,
        "steel_kg_per_sqft": 3.50,
        "cement_bags_per_sqft": 0.40,
    },
    ("Residential", "Tier 3"): {
        "cost_per_sqft": 1600.0,
        "market_val_per_sqft": 3400.0,
        "steel_kg_per_sqft": 3.25,
        "cement_bags_per_sqft": 0.38,
    },
    ("Commercial", "Tier 1"): {
        "cost_per_sqft": 3200.0,
        "market_val_per_sqft": 14000.0,
        "steel_kg_per_sqft": 4.50,
        "cement_bags_per_sqft": 0.48,
    },
    ("Commercial", "Tier 2"): {
        "cost_per_sqft": 2500.0,
        "market_val_per_sqft": 8000.0,
        "steel_kg_per_sqft": 4.20,
        "cement_bags_per_sqft": 0.45,
    },
    ("Commercial", "Tier 3"): {
        "cost_per_sqft": 2100.0,
        "market_val_per_sqft": 5000.0,
        "steel_kg_per_sqft": 3.80,
        "cement_bags_per_sqft": 0.42,
    },
    ("Industrial", "Tier 1"): {
        "cost_per_sqft": 2800.0,
        "market_val_per_sqft": 6500.0,
        "steel_kg_per_sqft": 5.20,
        "cement_bags_per_sqft": 0.45,
    },
    ("Industrial", "Tier 2"): {
        "cost_per_sqft": 2300.0,
        "market_val_per_sqft": 4500.0,
        "steel_kg_per_sqft": 4.80,
        "cement_bags_per_sqft": 0.42,
    },
    ("Industrial", "Tier 3"): {
        "cost_per_sqft": 1900.0,
        "market_val_per_sqft": 3200.0,
        "steel_kg_per_sqft": 4.50,
        "cement_bags_per_sqft": 0.39,
    },
    ("Institutional", "Tier 1"): {
        "cost_per_sqft": 2900.0,
        "market_val_per_sqft": 9000.0,
        "steel_kg_per_sqft": 4.20,
        "cement_bags_per_sqft": 0.44,
    },
    ("Institutional", "Tier 2"): {
        "cost_per_sqft": 2300.0,
        "market_val_per_sqft": 6000.0,
        "steel_kg_per_sqft": 3.90,
        "cement_bags_per_sqft": 0.41,
    },
    ("Institutional", "Tier 3"): {
        "cost_per_sqft": 1850.0,
        "market_val_per_sqft": 4000.0,
        "steel_kg_per_sqft": 3.60,
        "cement_bags_per_sqft": 0.38,
    },
}


@dataclass
class PlanningInputs:
    """User input assumptions for planning calculations."""
    structure_type: str
    built_up_area_sqft: float
    location_tier: str
    cost_per_sqft_inr: float
    completion_pct: float
    market_val_per_sqft_inr: float
    steel_req_kg_per_sqft: float
    cement_req_bags_per_sqft: float


@dataclass
class PlanningOutputs:
    """Calculated planning, material, and valuation metrics."""
    total_budget_inr: float
    estimated_expenditure_inr: float
    remaining_budget_inr: float
    illustrative_market_valuation_inr: float
    indicative_steel_quantity_kg: float
    indicative_steel_quantity_metric_tons: float
    indicative_cement_quantity_bags: float
    completion_percentage: float
    unrealized_equity_or_margin_inr: float


def get_default_benchmarks(structure_type: str, location_tier: str) -> Dict[str, float]:
    """Retrieve sensible default assumptions for a structure type and location tier."""
    key = (structure_type, location_tier)
    if key in BENCHMARK_DEFAULTS:
        return BENCHMARK_DEFAULTS[key].copy()
    # Fallback default
    return {
        "cost_per_sqft": 2200.0,
        "market_val_per_sqft": 6500.0,
        "steel_kg_per_sqft": 3.5,
        "cement_bags_per_sqft": 0.4,
    }


def calculate_planning_metrics(inputs: PlanningInputs) -> PlanningOutputs:
    """Calculate deterministic construction budget, material requirements, and market valuation.

    Formulas:
    1. Total budget = Built-up area × Assumed construction cost per sq ft
    2. Estimated expenditure = Total budget × Completion percentage / 100
    3. Remaining budget = Total budget - Estimated expenditure
    4. Illustrative market valuation = Built-up area × Assumed market value per sq ft
    5. Indicative steel quantity = Built-up area × Assumed steel requirement per sq ft
    6. Indicative cement quantity = Built-up area × Assumed cement requirement per sq ft
    """
    total_budget = inputs.built_up_area_sqft * inputs.cost_per_sqft_inr
    expenditure = total_budget * (inputs.completion_pct / 100.0)
    remaining_budget = total_budget - expenditure
    valuation = inputs.built_up_area_sqft * inputs.market_val_per_sqft_inr

    steel_kg = inputs.built_up_area_sqft * inputs.steel_req_kg_per_sqft
    steel_tons = steel_kg / 1000.0

    cement_bags = inputs.built_up_area_sqft * inputs.cement_req_bags_per_sqft
    margin_equity = valuation - total_budget

    return PlanningOutputs(
        total_budget_inr=round(total_budget, 2),
        estimated_expenditure_inr=round(expenditure, 2),
        remaining_budget_inr=round(remaining_budget, 2),
        illustrative_market_valuation_inr=round(valuation, 2),
        indicative_steel_quantity_kg=round(steel_kg, 2),
        indicative_steel_quantity_metric_tons=round(steel_tons, 3),
        indicative_cement_quantity_bags=round(cement_bags, 2),
        completion_percentage=round(inputs.completion_pct, 2),
        unrealized_equity_or_margin_inr=round(margin_equity, 2),
    )


def generate_planning_report(inputs: PlanningInputs, outputs: PlanningOutputs) -> Dict[str, Any]:
    """Generate structured JSON report for Planning & Real Estate Valuation."""
    report = create_base_report(
        module="planning_and_real_estate_valuation",
        human_review_required=True,
        limitations=[
            "Estimates are purely illustrative and based on user-supplied parameter assumptions.",
            "This report does not constitute an official RICS/CPWD valuation, contractor bill of quantities (BOQ), or certified market appraisal.",
            "Material requirements (steel & cement) are preliminary rule-of-thumb heuristics and require verified structural engineering drawings.",
            "Market valuations are subject to micro-market volatility, location advantages, regulatory approvals, and macroeconomic conditions.",
        ],
        assumptions=[
            f"Structure Type: {inputs.structure_type}",
            f"Location Category: {inputs.location_tier}",
            f"Cost per sq ft: ₹{inputs.cost_per_sqft_inr:,.2f}",
            f"Market Value per sq ft: ₹{inputs.market_val_per_sqft_inr:,.2f}",
            f"Steel consumption assumption: {inputs.steel_req_kg_per_sqft:.2f} kg/sq ft",
            f"Cement consumption assumption: {inputs.cement_req_bags_per_sqft:.2f} bags/sq ft",
        ],
        input_metadata=asdict(inputs),
    )

    report["calculations"] = asdict(outputs)
    report["formatted_summary"] = {
        "total_budget": format_inr(outputs.total_budget_inr),
        "total_budget_compact": format_inr_compact(outputs.total_budget_inr),
        "expenditure_to_date": format_inr(outputs.estimated_expenditure_inr),
        "expenditure_compact": format_inr_compact(outputs.estimated_expenditure_inr),
        "remaining_budget": format_inr(outputs.remaining_budget_inr),
        "remaining_budget_compact": format_inr_compact(outputs.remaining_budget_inr),
        "market_valuation": format_inr(outputs.illustrative_market_valuation_inr),
        "market_valuation_compact": format_inr_compact(outputs.illustrative_market_valuation_inr),
        "steel_quantity_metric_tons": f"{outputs.indicative_steel_quantity_metric_tons:,.2f} MT",
        "cement_quantity_bags": f"{outputs.indicative_cement_quantity_bags:,.0f} bags",
    }
    return report
