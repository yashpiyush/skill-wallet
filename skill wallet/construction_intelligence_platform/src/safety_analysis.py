"""Module One: Multimodal Site Safety & PPE Audit Analysis."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.report_utils import create_base_report

VALID_PPE_STATUSES = {
    "Compliant and visibly present",
    "Potentially missing",
    "Not visible",
    "Uncertain",
}

VALID_HAZARD_SEVERITIES = {
    "Low",
    "Medium",
    "High",
    "Critical",
    "Uncertain",
}

SAFETY_SYSTEM_INSTRUCTION = """
You are a senior occupational health and safety (OHS) auditor specialized in civil engineering and construction site safety (OSHA, IS, and international standards).
Analyze the provided construction site photograph with clinical objectivity, high rigor, and strict safety discipline.

CRITICAL RULES:
1. Strict PPE Status Categories:
   For each item evaluated, categorize status strictly as one of:
   - "Compliant and visibly present"
   - "Potentially missing" (e.g. worker head clearly exposed in hazardous work zone without helmet)
   - "Not visible" (e.g. feet are cut off by lower frame or occluded behind rebar/materials)
   - "Uncertain" (e.g. distance, low resolution, or heavy shadows prevent confident identification)
   DO NOT infer that personal protective equipment is absent merely because it cannot be seen or is out of frame.

2. Equipment to evaluate:
   - Safety helmets (Hard hats)
   - High-visibility vests / apparel
   - Protective footwear (only evaluate when feet/ground contact is clearly visible in frame)
   - Safety harnesses (where work at height, scaffolding, or unprotected edges are visible)
   - Eye / face protection (where cutting, welding, grinding, or dust generation is visible)

3. Potential Hazards & Unsafe Conditions:
   Identify visible environmental, structural, housekeeping, or procedural hazards:
   - Unprotected edges / lack of guardrails at height
   - Trip/slip hazards, unmanaged debris, or open floor penetrations
   - Proximity to live electrical lines or improper cable routing
   - Excavation/trenching collapse hazards
   - Improper scaffolding, ladder setup, or unstable stacking
   - Proximity to active heavy plant / machinery swinging radiuses

4. Output Format:
   Respond ONLY with a valid JSON object matching the following exact contract:
   {
     "module": "site_safety_ppe_audit",
     "overall_status": "REQUIRES_HUMAN_REVIEW",
     "ppe_detection": [
       {
         "item": "Safety helmets",
         "status": "Compliant and visibly present | Potentially missing | Not visible | Uncertain",
         "visible_evidence": "Description of what is visible regarding this item",
         "notes": "Actionable commentary or qualification"
       }
     ],
     "hazards": [
       {
         "hazard_description": "Precise hazard description",
         "severity": "Low | Medium | High | Critical | Uncertain",
         "evidence": "Visual indicators observed in the image",
         "corrective_action": "Immediate recommended mitigation action",
         "uncertainty_level": "Documented limitations or confidence caveats"
       }
     ],
     "site_observations": [
       "Key visible context: e.g. excavation stage, concrete casting, facade work"
     ],
     "limitations": [
       "Explicit limitations based on camera angle, distance, lighting, and resolution"
     ],
     "human_review_required": true
   }
DO NOT wrap in Markdown code blocks or preface with text. Return pure JSON.
"""


def validate_safety_audit_payload(raw_data: Any) -> Dict[str, Any]:
    """Validate and sanitize AI response to strictly satisfy the site safety contract."""
    if not isinstance(raw_data, dict):
        raise ValueError("AI safety response is not a valid JSON dictionary.")

    validated: Dict[str, Any] = create_base_report(
        module="site_safety_ppe_audit",
        human_review_required=True,
    )

    validated["overall_status"] = str(raw_data.get("overall_status", "REQUIRES_HUMAN_REVIEW"))

    # Sanitize PPE detection items
    ppe_list: List[Dict[str, str]] = []
    raw_ppe = raw_data.get("ppe_detection", [])
    if isinstance(raw_ppe, list):
        for entry in raw_ppe:
            if isinstance(entry, dict):
                status = str(entry.get("status", "Uncertain")).strip()
                if status not in VALID_PPE_STATUSES:
                    # Normalize if close
                    status_lower = status.lower()
                    if "compliant" in status_lower or "present" in status_lower:
                        status = "Compliant and visibly present"
                    elif "missing" in status_lower:
                        status = "Potentially missing"
                    elif "not visible" in status_lower or "unseen" in status_lower:
                        status = "Not visible"
                    else:
                        status = "Uncertain"

                ppe_list.append({
                    "item": str(entry.get("item", "Unspecified PPE")),
                    "status": status,
                    "visible_evidence": str(entry.get("visible_evidence", "No explicit visible evidence noted.")),
                    "notes": str(entry.get("notes", "")),
                })
    validated["ppe_detection"] = ppe_list

    # Sanitize Hazards
    hazard_list: List[Dict[str, str]] = []
    raw_hazards = raw_data.get("hazards", [])
    if isinstance(raw_hazards, list):
        for entry in raw_hazards:
            if isinstance(entry, dict):
                sev = str(entry.get("severity", "Uncertain")).strip().capitalize()
                if sev not in VALID_HAZARD_SEVERITIES:
                    sev = "Uncertain"

                hazard_list.append({
                    "hazard_description": str(entry.get("hazard_description", "Unspecified hazard")),
                    "severity": sev,
                    "evidence": str(entry.get("evidence", "Visual evidence visible in photograph")),
                    "corrective_action": str(entry.get("corrective_action", "Conduct supervisor inspection before resuming work.")),
                    "uncertainty_level": str(entry.get("uncertainty_level", "Preliminary visual screening")),
                })
    validated["hazards"] = hazard_list

    # Site observations & limitations
    obs = raw_data.get("site_observations", [])
    validated["site_observations"] = [str(o) for o in obs] if isinstance(obs, list) else []

    lims = raw_data.get("limitations", [])
    if isinstance(lims, list) and lims:
        # Append to base limitations without duplicates
        for item in lims:
            if str(item) not in validated["limitations"]:
                validated["limitations"].append(str(item))

    # Standard explicit safety guarantees
    if "AI assessment cannot verify certified material ratings or test dates." not in validated["limitations"]:
        validated["limitations"].append("AI assessment cannot verify certified material ratings or test dates.")
    if "Hidden or out-of-frame blind spots cannot be certified as hazard-free." not in validated["limitations"]:
        validated["limitations"].append("Hidden or out-of-frame blind spots cannot be certified as hazard-free.")

    validated["human_review_required"] = True
    return validated
