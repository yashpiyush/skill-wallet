"""Module Four: Weather-Aware Safety Advisory and Daily Checklists."""

from __future__ import annotations

from typing import Any, Dict, List

WEATHER_CONDITIONS = [
    "Normal",
    "High Wind",
    "Heavy Rain",
    "Extreme Heat",
    "Cold Conditions",
]

# Detailed, standards-aligned site checklists for each weather category
WEATHER_ADVISORIES: Dict[str, Dict[str, Any]] = {
    "Normal": {
        "title": "Standard Operating Conditions",
        "description": "Routine environmental parameters. Maintain strict standard baseline protocols and safety housekeeping.",
        "alert_level": "LOW",
        "badge_color": "green",
        "checklist": [
            {
                "id": "norm_1",
                "category": "PPE Compliance",
                "item": "Mandatory 100% PPE compliance: Hard hats (IS 2925 / EN 397), high-visibility vests, and steel-toed footwear.",
                "importance": "Mandatory",
            },
            {
                "id": "norm_2",
                "category": "Housekeeping",
                "item": "Perform morning 5S housekeeping; clear walkways, access corridors, and emergency evacuation exits of debris.",
                "importance": "High",
            },
            {
                "id": "norm_3",
                "category": "Plant & Machinery",
                "item": "Execute pre-shift equipment inspection walkaround (fluid levels, brake checks, backup alarms, emergency stops).",
                "importance": "High",
            },
            {
                "id": "norm_4",
                "category": "Briefings",
                "item": "Conduct mandatory morning toolbox talk (TBT) covering daily task-specific hazards and permit-to-work (PTW) checks.",
                "importance": "Mandatory",
            },
            {
                "id": "norm_5",
                "category": "Fall Protection",
                "item": "Inspect guardrails, edge protection boards, and hole covers on all elevated slabs and open shafts.",
                "importance": "Mandatory",
            },
        ],
        "precautions": [
            "Maintain approved standard operating procedures and valid job hazard analyses (JHA).",
            "Ensure first-aid kits are fully stocked and certified first-aiders are on site.",
            "Verify perimeter hoarding and access control gates are secured.",
        ],
    },
    "High Wind": {
        "title": "High Wind Advisory (>35 km/h)",
        "description": "Elevated aerodynamic forces endanger cranes, loose construction materials, perimeter sheeting, and high-altitude workers.",
        "alert_level": "HIGH",
        "badge_color": "red",
        "checklist": [
            {
                "id": "wind_1",
                "category": "Lifting Operations",
                "item": "Monitor anemometer: Suspend all tower crane and mobile crane lifting operations if sustained winds exceed 38 km/h (20 knots) or manufacturer limits.",
                "importance": "Critical",
            },
            {
                "id": "wind_2",
                "category": "Loose Materials",
                "item": "Secure, tie down, or lower all corrugated sheets, plywood boards, insulation panels, insulation rolls, and loose perimeter netting.",
                "importance": "Critical",
            },
            {
                "id": "wind_3",
                "category": "Work at Height",
                "item": "Halt all external suspended cradle (scaffold gondola) work, boom lifts, and unsecured edge operations.",
                "importance": "Critical",
            },
            {
                "id": "wind_4",
                "category": "Scaffolding & Hoarding",
                "item": "Inspect scaffold ties, netting permeability, and temporary site perimeter hoardings for structural stability against wind loads.",
                "importance": "High",
            },
            {
                "id": "wind_5",
                "category": "Crane Jib Free-Slewing",
                "item": "When crane operations are halted, place crane slewing brake in weathervane (free-slewing) mode per manufacturer guidelines.",
                "importance": "Critical",
            },
        ],
        "precautions": [
            "Do not allow workers near high walls or temporary masonry that has not achieved structural curing.",
            "Establish wide exclusion zones beneath scaffolding and exterior facade works.",
            "Maintain continuous wind-speed monitoring via calibrated on-site anemometers.",
        ],
    },
    "Heavy Rain": {
        "title": "Heavy Precipitation & Monsoon Advisory",
        "description": "Excess water saturation compromises slope stability, increases electrocution hazard, and creates severe slip/fall risks.",
        "alert_level": "HIGH",
        "badge_color": "orange",
        "checklist": [
            {
                "id": "rain_1",
                "category": "Excavation & Trenching",
                "item": "Immediately inspect all open trenches, pits, and retaining slopes for signs of slumping, boiling, or soil erosion; evacuate if unstable.",
                "importance": "Critical",
            },
            {
                "id": "rain_2",
                "category": "Electrical Safety",
                "item": "Isolate or elevate all temporary site electrical cables; verify Ground Fault Circuit Interrupters (GFCI/ELCB) and water-resistant junction boxes.",
                "importance": "Critical",
            },
            {
                "id": "rain_3",
                "category": "Dewatering Systems",
                "item": "Deploy and test submersible sump pumps and surface drainage swales to prevent basement and foundation waterlogging.",
                "importance": "High",
            },
            {
                "id": "rain_4",
                "category": "Access Corridors",
                "item": "Apply gravel, anti-slip mats, or wooden boardwalks across waterlogged walkways; enforce slip-resistant safety boots.",
                "importance": "High",
            },
            {
                "id": "rain_5",
                "category": "Concrete Pours",
                "item": "Halt external structural concrete pours unless adequate waterproof tarpaulin shelters are erected and water-cement ratio can be preserved.",
                "importance": "High",
            },
        ],
        "precautions": [
            "Prohibit entry into any excavation deeper than 1.2 m without verified shoring or benching after rainfall.",
            "Never operate ungrounded portable electric power tools in damp or flooded zones.",
            "Inspect tower crane and hoist foundation pads for ground saturation or differential subsidence.",
        ],
    },
    "Extreme Heat": {
        "title": "Extreme Heat Advisory (>38°C / High WBGT)",
        "description": "High ambient temperatures and solar radiation create severe risk of heat stroke, heat exhaustion, and dehydration.",
        "alert_level": "HIGH",
        "badge_color": "orange",
        "checklist": [
            {
                "id": "heat_1",
                "category": "Hydration Stations",
                "item": "Provide shaded, easily accessible hydration points stocked with clean cool water and oral rehydration salts (ORS/electrolytes).",
                "importance": "Critical",
            },
            {
                "id": "heat_2",
                "category": "Work-Rest Cycles",
                "item": "Implement adjusted work schedules: Shift heavy physical tasks to early morning (06:00-11:00) and late afternoon; enforce shaded rest breaks.",
                "importance": "Critical",
            },
            {
                "id": "heat_3",
                "category": "Acclimatisation",
                "item": "Enforce mandatory 7-to-14 day heat acclimatisation protocols for new or returning workers.",
                "importance": "High",
            },
            {
                "id": "heat_4",
                "category": "Medical & First Aid",
                "item": "Train site supervisors and buddies to recognize early symptoms of heat exhaustion (dizziness, nausea, profuse sweating, confusion).",
                "importance": "Critical",
            },
            {
                "id": "heat_5",
                "category": "Curing & Chemical Safety",
                "item": "Keep structural concrete surfaces continuously moist to avoid rapid plastic shrinkage cracking; store chemical adhesives away from direct sun.",
                "importance": "High",
            },
        ],
        "precautions": [
            "Provide breathable neck-flaps attached to safety helmets for workers exposed to open sunlight.",
            "Have an air-conditioned or fan-cooled emergency rest tent ready with ice packs.",
            "Monitor Wet Bulb Globe Temperature (WBGT) index hourly during peak heat windows.",
        ],
    },
    "Cold Conditions": {
        "title": "Cold & Frost Advisory (<10°C / Freezing)",
        "description": "Cold stress diminishes manual dexterity, causes hypothermia/frostbite, and severely retards concrete hydration.",
        "alert_level": "MEDIUM",
        "badge_color": "blue",
        "checklist": [
            {
                "id": "cold_1",
                "category": "Personal Protection",
                "item": "Issue thermal helmet liners, insulated non-slip gloves, and multi-layered cold-weather protective clothing.",
                "importance": "High",
            },
            {
                "id": "cold_2",
                "category": "Slip & Fall Prevention",
                "item": "Inspect ladders, scaffolding planks, ramps, and metal staging for black ice; apply sand or de-icing salt before shift starts.",
                "importance": "Critical",
            },
            {
                "id": "cold_3",
                "category": "Concrete Curing Care",
                "item": "Do not place concrete on frozen ground; maintain placed concrete temperature >= 10°C using insulating thermal blankets or heated enclosures.",
                "importance": "Critical",
            },
            {
                "id": "cold_4",
                "category": "Warm Break Facilities",
                "item": "Provide heated shelter with hot beverages; limit prolonged stationary work in open wind-chill zones.",
                "importance": "High",
            },
            {
                "id": "cold_5",
                "category": "Machinery Pre-heating",
                "item": "Preheat engine blocks and check hydraulic fluid viscosity for cranes, excavators, and generators before loading.",
                "importance": "Medium",
            },
        ],
        "precautions": [
            "Monitor workers for symptoms of hypothermia (uncontrolled shivering, slurred speech, clumsy fingers).",
            "Increase illumination on accessways during low-visibility foggy winter mornings.",
            "Store temperature-sensitive sealants and paints in heated storage spaces.",
        ],
    },
}


def get_weather_advisory(condition: str) -> Dict[str, Any]:
    """Retrieve weather advisory and checklist by condition name."""
    if condition in WEATHER_ADVISORIES:
        return WEATHER_ADVISORIES[condition]
    return WEATHER_ADVISORIES["Normal"]
