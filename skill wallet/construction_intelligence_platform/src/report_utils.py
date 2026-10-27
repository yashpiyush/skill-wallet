"""Utilities for creating, standardizing, and serializing JSON audit and planning reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def get_current_timestamp() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def create_base_report(
    module: str,
    human_review_required: bool = True,
    limitations: Optional[List[str]] = None,
    assumptions: Optional[List[str]] = None,
    input_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a standardized base envelope for all platform reports.

    Guarantees the required metadata fields:
    - module
    - timestamp_utc
    - input_metadata
    - assumptions
    - limitations
    - human_review_required
    """
    default_limitations = [
        "Visual assessments are preliminary screening tools and cannot replace professional on-site audits.",
        "Assessments are limited strictly to features visible within the submitted photograph and lighting conditions.",
    ]

    return {
        "module": module,
        "platform": "Multimodal Construction Intelligence Platform",
        "version": "1.0.0",
        "timestamp_utc": get_current_timestamp(),
        "input_metadata": input_metadata or {},
        "assumptions": assumptions or [],
        "limitations": limitations if limitations is not None else default_limitations,
        "human_review_required": human_review_required,
    }


def serialize_report(report_dict: Dict[str, Any], indent: int = 2) -> str:
    """Serialize report dictionary to formatted JSON string.

    Ensures robust serialization without throwing on non-primitive objects.
    """
    def default_serializer(obj: Any) -> str:
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        return str(obj)

    return json.dumps(report_dict, indent=indent, default=default_serializer)


def format_inr(value: float) -> str:
    """Format numeric value in Indian Rupees (INR) with Indian numbering comma system.

    Examples:
        1000 -> ₹ 1,000
        100000 -> ₹ 1,00,000 (1 Lakh)
        12500000 -> ₹ 1,25,00,000 (1.25 Crore)
    """
    if value is None:
        return "₹ 0"

    is_negative = value < 0
    value = abs(value)

    # Split into integer and decimal parts
    int_part = int(round(value))
    s = str(int_part)

    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        # Group remaining digits in pairs of two from right to left
        pairs = []
        while len(remaining) > 2:
            pairs.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            pairs.append(remaining)
        pairs.reverse()
        formatted = ",".join(pairs) + "," + last_three

    prefix = "-₹ " if is_negative else "₹ "
    return f"{prefix}{formatted}"


def format_inr_compact(value: float) -> str:
    """Format large INR numbers into human-readable Crores or Lakhs.

    Examples:
        1500000 -> ₹ 15.00 Lakh
        25000000 -> ₹ 2.50 Cr
    """
    if value is None:
        return "₹ 0"
    abs_val = abs(value)
    prefix = "-" if value < 0 else ""
    if abs_val >= 10_000_000:  # 1 Crore = 10,000,000
        return f"{prefix}₹ {abs_val / 10_000_000:.2f} Cr"
    if abs_val >= 100_000:     # 1 Lakh = 100,000
        return f"{prefix}₹ {abs_val / 100_000:.2f} Lakh"
    return format_inr(value)
