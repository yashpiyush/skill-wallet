"""Module Two: AI-Assisted Visual Crack Diagnostics & Structural Integrity Screening."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.report_utils import create_base_report

VALID_CRACK_CLASSIFICATIONS = [
    "Hairline cracks",
    "Settlement-related patterns",
    "Possible structural shear patterns",
    "Thermal expansion-related patterns",
    "Spalling and rebar exposure",
    "Other or uncertain defects",
    "Uncertain",
]

VALID_URGENCIES = ["Low", "Moderate", "High", "Urgent", "Uncertain"]

CRACK_SYSTEM_INSTRUCTION = """
You are a structural engineering visual inspection specialist.
Perform a preliminary visual screening of the uploaded structural element photograph (wall, column, beam, slab, or foundation).

CRITICAL ENGINEERING PRINCIPLES:
1. Strict Limitations:
   - Visual inspection from a 2D photograph CANNOT verify subsurface stress, core compressive strength, rebar degradation, or active ground movement.
   - You must NEVER provide a structural safety certificate or state that a structure is guaranteed safe.
   - Do NOT invent or guess numerical crack widths unless a calibrated scale or physical measurement ruler is visibly placed adjacent to the defect. Otherwise, return null for estimated_width_mm.

2. Possible Defect Classifications:
   Choose from:
   - "Hairline cracks" (superficial crazing or non-structural shrinkage)
   - "Settlement-related patterns" (e.g. stepped diagonal cracks in masonry or foundation level shifts)
   - "Possible structural shear patterns" (e.g. 45-degree diagonal cracks near beam-column joints or load points)
   - "Thermal expansion-related patterns" (straight longitudinal movement joints or roof slab expansion)
   - "Spalling and rebar exposure" (concrete cover delamination with oxidised reinforcement)
   - "Other or uncertain defects"
   - "Uncertain"

3. Urgency Evaluation:
   - "Urgent": Diagonal cracks on load-bearing columns/beams, severe spalling with buckling rebar, cracks accompanied by noticeable deflection or crushing.
   - "High": Cracks with active water seepage, widespread stepped cracks, expanding shear signs.
   - "Moderate": Noticeable shrinkage or thermal cracks > 1.5mm without obvious shear.
   - "Low": Hairline superficial shrinkage crazing < 0.3mm on non-structural plaster.
   - "Uncertain": Resolution insufficient, heavy surface paint obscuring depth, or ambiguous pattern.

4. Output Format:
   Respond ONLY with a valid JSON object matching this exact contract:
   {
     "module": "crack_diagnostics",
     "visual_classification": "Uncertain",
     "visible_observations": [
       "Description of crack orientation, location on member, and surface texture"
     ],
     "estimated_width_mm": null,
     "possible_causes": [
       "Differential settlement / thermal movement / concrete shrinkage / shear stress"
     ],
     "urgency": "Low | Moderate | High | Urgent | Uncertain",
     "recommended_next_steps": [
       "Immediate or near-term steps including crack gauge monitoring and qualified PE review"
     ],
     "limitations": [
       "Explicit caveats regarding image lighting, scale absence, and subsurface unpredictability"
     ],
     "human_engineer_review_required": true
   }
DO NOT wrap in Markdown code blocks or preface with text. Return pure JSON.
"""


def validate_crack_diagnostics_payload(
    raw_data: Any,
    user_inputs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate and sanitize AI crack screening output against structural safety contract."""
    if not isinstance(raw_data, dict):
        raise ValueError("AI crack diagnostic response is not a valid JSON dictionary.")

    validated: Dict[str, Any] = create_base_report(
        module="crack_diagnostics",
        human_review_required=True,
        input_metadata=user_inputs or {},
    )

    # Classification
    classification = str(raw_data.get("visual_classification", "Uncertain")).strip()
    # Normalize if close
    matched = False
    for valid_cls in VALID_CRACK_CLASSIFICATIONS:
        if valid_cls.lower() in classification.lower():
            classification = valid_cls
            matched = True
            break
    if not matched:
        classification = "Other or uncertain defects"
    validated["visual_classification"] = classification

    # Visible observations
    obs = raw_data.get("visible_observations", [])
    validated["visible_observations"] = [str(o) for o in obs] if isinstance(obs, list) else []

    # Estimated width (float or None)
    raw_width = raw_data.get("estimated_width_mm")
    if raw_width is not None:
        try:
            validated["estimated_width_mm"] = float(raw_width)
        except (ValueError, TypeError):
            validated["estimated_width_mm"] = None
    else:
        validated["estimated_width_mm"] = None

    # Possible causes
    causes = raw_data.get("possible_causes", [])
    validated["possible_causes"] = [str(c) for c in causes] if isinstance(causes, list) else []

    # Urgency
    urg = str(raw_data.get("urgency", "Uncertain")).strip().capitalize()
    if urg not in VALID_URGENCIES:
        urg = "Uncertain"
    validated["urgency"] = urg

    # Recommended next steps
    steps = raw_data.get("recommended_next_steps", [])
    validated["recommended_next_steps"] = [str(s) for s in steps] if isinstance(steps, list) else []
    # Ensure engineer review is emphasized
    engineer_step = "Engage a licensed structural engineer for physical on-site NDT (Non-Destructive Testing) and core inspection."
    if not any("structural engineer" in s.lower() for s in validated["recommended_next_steps"]):
        validated["recommended_next_steps"].insert(0, engineer_step)

    # Limitations
    lims = raw_data.get("limitations", [])
    if isinstance(lims, list):
        for item in lims:
            if str(item) not in validated["limitations"]:
                validated["limitations"].append(str(item))

    # Standard explicit structural engineering disclaimers
    mandatory_caveats = [
        "This analysis is a preliminary computer-vision screening and does NOT constitute a structural safety certificate.",
        "Internal shear stresses, reinforcement degradation, foundation movement, and concrete strength cannot be determined from an image.",
        "Physical inspection by a qualified, registered structural engineer is mandatory before making occupancy or remediation decisions.",
    ]
    for caveat in mandatory_caveats:
        if caveat not in validated["limitations"]:
            validated["limitations"].append(caveat)

    validated["human_engineer_review_required"] = True
    return validated
