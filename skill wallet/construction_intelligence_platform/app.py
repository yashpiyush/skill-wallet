"""Multimodal Construction Intelligence Platform.

Skill Wallet Capstone Project 1.
An AI-assisted civil engineering platform combining multimodal visual inspection,
deterministic planning calculators, and weather-aware safety advisories.
"""

from __future__ import annotations

import io
import json
import os
import sys
from typing import Any, Dict, List, Optional
from PIL import Image

import streamlit as st

# Import core domain modules
from src.ai_service import (
    AIServiceError,
    APIAuthError,
    APIKeyMissingError,
    AIProviderUnavailableError,
    APIRateLimitError,
    AIResponseFormatError,
    DEFAULT_GEMINI_MODEL,
    analyze_image_with_gemini,
    ask_site_assistant_gemini,
    is_genai_installed,
    resolve_api_key,
    resolve_model_name,
)
from src.crack_analysis import (
    CRACK_SYSTEM_INSTRUCTION,
    VALID_CRACK_CLASSIFICATIONS,
    validate_crack_diagnostics_payload,
)
from src.planning import (
    LOCATION_TIERS,
    STRUCTURE_TYPES,
    PlanningInputs,
    PlanningOutputs,
    calculate_planning_metrics,
    generate_planning_report,
    get_default_benchmarks,
)
from src.report_utils import (
    format_inr,
    format_inr_compact,
    get_current_timestamp,
    serialize_report,
)
from src.safety_analysis import (
    SAFETY_SYSTEM_INSTRUCTION,
    validate_safety_audit_payload,
)
from src.validation import (
    sanitize_text_input,
    validate_api_key,
    validate_crack_inputs,
    validate_image_file,
    validate_planning_inputs,
)

# Configure Streamlit page layout and branding
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for construction-themed aesthetic and high-contrast metric presentation
st.markdown(
    """
    <style>
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-green { background-color: #065F46; color: #A7F3D0; }
    .badge-amber { background-color: #92400E; color: #FDE68A; }
    .badge-red { background-color: #991B1B; color: #FECACA; }
    .badge-blue { background-color: #1E40AF; color: #BFDBFE; }
    .badge-gray { background-color: #374151; color: #E5E7EB; }

    .safety-disclaimer-box {
        border-left: 4px solid #F59E0B;
        background-color: rgba(245, 158, 11, 0.08);
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 0.9rem;
    }
    .critical-callout {
        border-left: 4px solid #EF4444;
        background-color: rgba(239, 68, 68, 0.08);
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    """Initialize session state registries for cross-module audit history."""
    if "safety_reports" not in st.session_state:
        st.session_state["safety_reports"] = []
    if "crack_reports" not in st.session_state:
        st.session_state["crack_reports"] = []
    if "planning_reports" not in st.session_state:
        st.session_state["planning_reports"] = []
    if "assistant_history" not in st.session_state:
        st.session_state["assistant_history"] = []
    if "session_api_key" not in st.session_state:
        st.session_state["session_api_key"] = ""
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = DEFAULT_GEMINI_MODEL


initialize_session_state()


# ----------------------------------------------------------------------
# Sidebar Navigation and Global Settings
# ----------------------------------------------------------------------
with st.sidebar:
    st.title("🏗️ Construction Intelligence")
    st.caption("Multimodal AI, Planning & Safety Platform")
    st.markdown("---")

    module_choice = st.radio(
        "Platform Modules",
        [
            "Site Safety & PPE Audit",
            "Crack Diagnostics & Structural",
            "Planning & Real Estate Valuation",
            "Daily Site Assistant & Weather",
            "Session Reports & System Info",
        ],
        index=0,
    )

    st.markdown("---")
    st.subheader("⚙️ AI Configuration")

    # API Key Configuration
    configured_key = resolve_api_key(st.session_state.get("session_api_key"))
    is_key_active = bool(configured_key)

    if is_key_active:
        st.success("🟢 Gemini API Key: Configured")
    else:
        st.warning("🟠 Gemini API Key: Not Configured")

    session_key_input = st.text_input(
        "Session API Key (Optional)",
        value=st.session_state.get("session_api_key", ""),
        type="password",
        help="Enter a key for this active session. It is stored in volatile memory and never persisted.",
    )
    if session_key_input != st.session_state.get("session_api_key"):
        st.session_state["session_api_key"] = session_key_input
        st.rerun()

    # Model selector
    available_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    current_model = resolve_model_name(st.session_state.get("selected_model"))
    if current_model not in available_models:
        available_models.insert(0, current_model)

    selected_model = st.selectbox(
        "Gemini Model",
        available_models,
        index=available_models.index(current_model) if current_model in available_models else 0,
    )
    st.session_state["selected_model"] = selected_model

    # Check SDK installation
    if not is_genai_installed():
        st.error("⚠️ `google-genai` SDK is not installed in current runtime. Multimodal AI requests will be disabled.")
    else:
        st.caption("SDK: `google-genai` installed")

    st.markdown("---")
    st.markdown(
        """
        <div class="safety-disclaimer-box">
        <strong>⚠️ Mandatory Notice:</strong><br>
        AI outputs are preliminary visual screenings only. They do not constitute official engineering certifications, safety approvals, or structural appraisals.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Module 1: Site Safety & PPE Audit
# ----------------------------------------------------------------------
if module_choice == "Site Safety & PPE Audit":
    st.header("🦺 Site Safety & PPE Audit")
    st.markdown(
        "Upload construction site photographs for visual PPE compliance screening "
        "and potential hazard identification adhering to OSHA and IS guidelines."
    )

    st.markdown(
        """
        <div class="safety-disclaimer-box">
        <strong>Audit Rule:</strong> Equipment is never inferred as absent simply because it is occluded or out of frame.
        All findings require human safety officer review.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Photograph Upload")
        uploaded_file = st.file_uploader(
            "Upload Construction Site Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Supported formats: JPG, JPEG, PNG, WEBP (Maximum 10 MB).",
            key="safety_uploader",
        )

        site_notes = st.text_area(
            "Optional Site Context / Specific Area",
            placeholder="e.g., Tower B, 4th floor slab casting, rebar tying crew...",
            max_chars=500,
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            is_valid, err_msg, pil_img = validate_image_file(file_bytes, uploaded_file.name)
            if not is_valid:
                st.error(f"Image validation error: {err_msg}")
            else:
                st.image(pil_img, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
                initiate_btn = st.button("🚀 Initiate Safety & PPE Audit", type="primary", use_container_width=True)
        else:
            st.info("Please upload a construction site photograph to begin.")
            initiate_btn = False

    with col2:
        st.subheader("2. Inspection Findings")

        if uploaded_file and initiate_btn and is_valid:
            api_key = resolve_api_key(st.session_state.get("session_api_key"))
            if not api_key:
                st.error(
                    "❌ No Gemini API key detected. Please configure GEMINI_API_KEY as an environment "
                    "variable, in `.streamlit/secrets.toml`, or enter your key in the sidebar."
                )
            elif not is_genai_installed():
                st.error(
                    "❌ The `google-genai` SDK is not installed in this environment. "
                    "Please run `pip install google-genai` to enable live multimodal analysis."
                )
            else:
                with st.spinner("Analyzing site imagery with multimodal Gemini vision model..."):
                    mime_type = "image/jpeg"
                    if uploaded_file.name.lower().endswith(".png"):
                        mime_type = "image/png"
                    elif uploaded_file.name.lower().endswith(".webp"):
                        mime_type = "image/webp"

                    prompt = "Perform comprehensive site safety and PPE assessment on this construction site image."
                    if site_notes:
                        prompt += f"\nAdditional site context provided by engineer: {site_notes}"

                    try:
                        raw_result = analyze_image_with_gemini(
                            api_key=api_key,
                            model=st.session_state.get("selected_model", DEFAULT_GEMINI_MODEL),
                            prompt=prompt,
                            image_bytes=file_bytes,
                            mime_type=mime_type,
                            system_instruction=SAFETY_SYSTEM_INSTRUCTION,
                        )
                        validated_audit = validate_safety_audit_payload(raw_result)
                        # Save in session state
                        st.session_state["safety_reports"].append(validated_audit)
                        st.session_state["latest_safety_audit"] = validated_audit
                        st.success("✅ Audit analysis completed successfully.")
                    except (APIAuthError, APIRateLimitError, APIKeyMissingError, AIProviderUnavailableError) as a_err:
                        st.error(f"AI Service Notification: {str(a_err)}")
                    except AIResponseFormatError as f_err:
                        st.error(f"Response validation error: {str(f_err)}")
                    except Exception as gen_exc:
                        st.error(f"Unexpected error during safety analysis: {str(gen_exc)}")

        # Display latest audit if available
        latest_audit = st.session_state.get("latest_safety_audit")
        if latest_audit:
            # Overview metric cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Overall Audit Status", latest_audit.get("overall_status", "REQUIRES_HUMAN_REVIEW"))
            with m2:
                ppe_count = len(latest_audit.get("ppe_detection", []))
                st.metric("PPE Elements Checked", ppe_count)
            with m3:
                hazards_count = len(latest_audit.get("hazards", []))
                st.metric("Potential Hazards", hazards_count)

            st.markdown("#### Visible PPE Indicators")
            ppe_entries = latest_audit.get("ppe_detection", [])
            if ppe_entries:
                for ppe in ppe_entries:
                    status = ppe.get("status", "Uncertain")
                    badge_class = "badge-gray"
                    if status == "Compliant and visibly present":
                        badge_class = "badge-green"
                    elif status == "Potentially missing":
                        badge_class = "badge-red"
                    elif status == "Uncertain":
                        badge_class = "badge-amber"

                    st.markdown(
                        f"""
                        <div style="border: 1px solid rgba(255,255,255,0.1); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                            <strong>{ppe.get('item', 'Item')}:</strong> 
                            <span class="status-badge {badge_class}">{status}</span><br>
                            <small style="color: #94A3B8;">Evidence: {ppe.get('visible_evidence', 'N/A')}</small><br>
                            <small style="color: #CBD5E1;">{ppe.get('notes', '')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No distinct PPE indicators could be evaluated.")

            st.markdown("#### Identified Hazards & Unsafe Conditions")
            hazards = latest_audit.get("hazards", [])
            if hazards:
                for h in hazards:
                    sev = h.get("severity", "Uncertain")
                    sev_class = "badge-amber"
                    if sev in ["Critical", "High"]:
                        sev_class = "badge-red"
                    elif sev == "Low":
                        sev_class = "badge-green"

                    with st.expander(f"⚠️ {h.get('hazard_description', 'Hazard')} [{sev}]", expanded=True):
                        st.markdown(f"**Severity Level:** <span class='status-badge {sev_class}'>{sev}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Visible Evidence:** {h.get('evidence', 'N/A')}")
                        st.markdown(f"**Recommended Corrective Action:** {h.get('corrective_action', 'N/A')}")
                        st.markdown(f"**Uncertainty / Limitations:** {h.get('uncertainty_level', 'N/A')}")
            else:
                st.info("No acute visible hazards identified within the evaluated photographic field.")

            # Limitations
            with st.expander("ℹ️ Assessment Limitations & Regulatory Constraints"):
                for lim in latest_audit.get("limitations", []):
                    st.write(f"- {lim}")

            # Download report button
            report_json = serialize_report(latest_audit)
            st.download_button(
                label="📥 Download Safety Audit Report (JSON)",
                data=report_json,
                file_name=f"safety_audit_{get_current_timestamp()[:10]}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            if not (uploaded_file and initiate_btn):
                st.info("Audit findings will appear here once an image is uploaded and analyzed.")


# ----------------------------------------------------------------------
# Module 2: Crack Diagnostics & Structural Integrity
# ----------------------------------------------------------------------
elif module_choice == "Crack Diagnostics & Structural":
    st.header("🔍 Crack Diagnostics & Structural Integrity Screening")
    st.markdown(
        "Upload high-resolution photographs of visible cracks on walls, columns, beams, "
        "slabs, or foundations for preliminary pattern classification and urgency assessment."
    )

    st.markdown(
        """
        <div class="critical-callout">
        <strong>⚠️ Mandatory Structural Engineering Disclaimer:</strong><br>
        2D visual defect screening cannot evaluate internal reinforcement condition, concrete compressive strength, sub-surface shear stresses, or active foundation settlement.
        All structural cracks require in-person physical assessment by a registered structural engineer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Structural Element Photograph")
        crack_file = st.file_uploader(
            "Upload Structural Defect Photograph",
            type=["jpg", "jpeg", "png", "webp"],
            help="Supported formats: JPG, JPEG, PNG, WEBP (Max 10 MB)",
            key="crack_uploader",
        )

        st.subheader("2. Physical Observations & Measurements")
        observed_element = st.selectbox(
            "Observed Structural Element",
            [
                "RCC Column",
                "RCC Beam",
                "Suspended Floor / Roof Slab",
                "Brick / Masonry Wall",
                "Foundation / Retaining Wall",
                "Beam-Column Junction",
                "Plastered Ceiling",
                "Other / Unspecified",
            ],
        )

        defect_location = st.text_input(
            "Defect Location",
            placeholder="e.g., Basement 1 exterior wall, near column C-3",
        )

        has_measurement = st.checkbox("Physical crack width was measured on site with a crack gauge / gauge ruler")
        measured_width: Optional[float] = None
        if has_measurement:
            measured_width = st.number_input(
                "Measured Crack Width (mm)",
                min_value=0.01,
                max_value=300.0,
                value=1.5,
                step=0.1,
                help="Enter physical measurement from a crack comparator or optical gauge.",
            )

        crack_notes = st.text_area(
            "Additional Observations (e.g. water seepage, rust staining, spalling)",
            placeholder="e.g., Moisture staining along crack line; noticed widening over past 2 weeks...",
            max_chars=500,
        )

        if crack_file is not None:
            file_bytes = crack_file.getvalue()
            is_valid, err_msg, pil_img = validate_image_file(file_bytes, crack_file.name)
            if not is_valid:
                st.error(f"Image error: {err_msg}")
            else:
                st.image(pil_img, caption=f"Defect: {crack_file.name}", use_container_width=True)
                run_crack_btn = st.button("🔬 Run Crack Diagnostics", type="primary", use_container_width=True)
        else:
            st.info("Upload an image of the crack or surface defect to proceed.")
            run_crack_btn = False

    with col2:
        st.subheader("3. Diagnostic Screening Report")

        if crack_file and run_crack_btn and is_valid:
            api_key = resolve_api_key(st.session_state.get("session_api_key"))
            if not api_key:
                st.error("❌ Gemini API key not detected. Please configure GEMINI_API_KEY or supply a session key.")
            elif not is_genai_installed():
                st.error("❌ `google-genai` SDK is not installed in current environment.")
            else:
                with st.spinner("Analyzing structural pattern and defect geometry with Gemini..."):
                    mime_type = "image/jpeg"
                    if crack_file.name.lower().endswith(".png"):
                        mime_type = "image/png"
                    elif crack_file.name.lower().endswith(".webp"):
                        mime_type = "image/webp"

                    user_context = {
                        "observed_element": observed_element,
                        "defect_location": defect_location,
                        "measured_width_mm": measured_width,
                        "observations": crack_notes,
                    }

                    prompt = (
                        f"Perform visual crack screening on this structural element.\n"
                        f"Observed element: {observed_element}\n"
                        f"Location: {defect_location or 'Not specified'}\n"
                        f"Measured width by user: {f'{measured_width} mm' if measured_width else 'No scale or gauge provided'}\n"
                        f"User observations: {crack_notes or 'None'}"
                    )

                    try:
                        raw_result = analyze_image_with_gemini(
                            api_key=api_key,
                            model=st.session_state.get("selected_model", DEFAULT_GEMINI_MODEL),
                            prompt=prompt,
                            image_bytes=file_bytes,
                            mime_type=mime_type,
                            system_instruction=CRACK_SYSTEM_INSTRUCTION,
                        )
                        validated_crack = validate_crack_diagnostics_payload(raw_result, user_inputs=user_context)
                        # Save in session
                        st.session_state["crack_reports"].append(validated_crack)
                        st.session_state["latest_crack_report"] = validated_crack
                        st.success("✅ Diagnostic screening completed.")
                    except (APIAuthError, APIRateLimitError, APIKeyMissingError, AIProviderUnavailableError) as a_err:
                        st.error(f"AI Service Notification: {str(a_err)}")
                    except AIResponseFormatError as f_err:
                        st.error(f"Response validation error: {str(f_err)}")
                    except Exception as gen_exc:
                        st.error(f"Unexpected diagnostic error: {str(gen_exc)}")

        latest_crack = st.session_state.get("latest_crack_report")
        if latest_crack:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Pattern Classification", latest_crack.get("visual_classification", "Uncertain"))
            with c2:
                urg = latest_crack.get("urgency", "Uncertain")
                st.metric("Preliminary Urgency", urg)
            with c3:
                width_val = latest_crack.get("estimated_width_mm")
                display_width = f"{width_val:.2f} mm" if width_val is not None else "Scale absent"
                st.metric("Estimated Width", display_width)

            st.markdown("#### Visible Observations")
            for obs in latest_crack.get("visible_observations", []):
                st.write(f"- {obs}")

            st.markdown("#### Possible Underlying Causes")
            for cause in latest_crack.get("possible_causes", []):
                st.write(f"- {cause}")

            st.markdown("#### Recommended Next Steps")
            for step in latest_crack.get("recommended_next_steps", []):
                st.markdown(f"👉 **{step}**")

            with st.expander("ℹ️ Screening Limitations & Engineer Review"):
                for lim in latest_crack.get("limitations", []):
                    st.write(f"- {lim}")

            crack_json = serialize_report(latest_crack)
            st.download_button(
                label="📥 Download Crack Diagnostic Report (JSON)",
                data=crack_json,
                file_name=f"crack_report_{get_current_timestamp()[:10]}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            if not (crack_file and run_crack_btn):
                st.info("Screening report will appear here after image upload and analysis.")


# ----------------------------------------------------------------------
# Module 3: Planning & Real Estate Valuation
# ----------------------------------------------------------------------
elif module_choice == "Planning & Real Estate Valuation":
    st.header("📐 Planning & Real Estate Valuation Calculator")
    st.markdown(
        "Deterministic construction cost estimation, material heuristics, and property valuation. "
        "Calculations run entirely client-side without external dependencies or API keys."
    )

    st.markdown(
        """
        <div class="safety-disclaimer-box">
        <strong>Deterministic Framework:</strong> All outputs are exact mathematical evaluations derived from user-specified rates and dimensions.
        These are illustrative benchmarks and do not constitute an official engineering Bill of Quantities (BOQ) or certified bank appraisal.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Project Specification")
        structure_type = st.selectbox("Structure Type", STRUCTURE_TYPES, index=0)
        location_tier = st.selectbox("Location Tier", LOCATION_TIERS, index=0)

        # Retrieve benchmark defaults
        benchmarks = get_default_benchmarks(structure_type, location_tier)

        built_up_area = st.number_input(
            "Built-up Area (Square Feet)",
            min_value=100.0,
            max_value=10_000_000.0,
            value=2500.0,
            step=100.0,
            help="Total enclosed constructible floor area in sq ft.",
        )

        completion_pct = st.slider(
            "Construction Completion Percentage (%)",
            min_value=0.0,
            max_value=100.0,
            value=45.0,
            step=1.0,
            help="Physical milestone progress achieved to date.",
        )

        st.progress(completion_pct / 100.0)

    with col2:
        st.subheader("2. Rate & Material Assumptions")
        st.caption("Pre-populated with regional benchmarks. You may modify any value.")

        cost_per_sqft = st.number_input(
            "Assumed Construction Cost per sq ft (INR)",
            min_value=100.0,
            max_value=500_000.0,
            value=benchmarks["cost_per_sqft"],
            step=50.0,
            help="Includes structure, civil finishes, and core MEP.",
        )

        market_val_per_sqft = st.number_input(
            "Assumed Market Real Estate Value per sq ft (INR)",
            min_value=100.0,
            max_value=2_000_000.0,
            value=benchmarks["market_val_per_sqft"],
            step=100.0,
            help="Prevailing fair market valuation rate per sq ft.",
        )

        steel_req_sqft = st.number_input(
            "Assumed Steel Requirement (kg per sq ft)",
            min_value=0.5,
            max_value=50.0,
            value=benchmarks["steel_kg_per_sqft"],
            step=0.25,
            help="Reinforcement steel consumption heuristic (typical 3.0 - 5.5 kg/sqft).",
        )

        cement_req_sqft = st.number_input(
            "Assumed Cement Requirement (50kg bags per sq ft)",
            min_value=0.1,
            max_value=10.0,
            value=benchmarks["cement_bags_per_sqft"],
            step=0.02,
            help="Standard 50kg cement bag consumption heuristic (typical 0.35 - 0.50 bags/sqft).",
        )

    # Perform calculations and validation
    is_valid, validation_errors = validate_planning_inputs(
        built_up_area=built_up_area,
        cost_per_sqft=cost_per_sqft,
        completion_pct=completion_pct,
        market_val_per_sqft=market_val_per_sqft,
        steel_req_per_sqft=steel_req_sqft,
        cement_req_per_sqft=cement_req_sqft,
    )

    if not is_valid:
        for err in validation_errors:
            st.error(f"Input Error: {err}")
    else:
        plan_inputs = PlanningInputs(
            structure_type=structure_type,
            built_up_area_sqft=built_up_area,
            location_tier=location_tier,
            cost_per_sqft_inr=cost_per_sqft,
            completion_pct=completion_pct,
            market_val_per_sqft_inr=market_val_per_sqft,
            steel_req_kg_per_sqft=steel_req_sqft,
            cement_req_bags_per_sqft=cement_req_sqft,
        )
        outputs = calculate_planning_metrics(plan_inputs)
        planning_report = generate_planning_report(plan_inputs, outputs)

        st.markdown("---")
        st.subheader("3. Calculated Budget & Valuation Metrics")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(
                label="Estimated Total Budget",
                value=format_inr_compact(outputs.total_budget_inr),
                help=format_inr(outputs.total_budget_inr),
            )
        with m2:
            st.metric(
                label="Expenditure Incurred to Date",
                value=format_inr_compact(outputs.estimated_expenditure_inr),
                delta=f"{outputs.completion_percentage:.0f}% Completed",
                help=format_inr(outputs.estimated_expenditure_inr),
            )
        with m3:
            st.metric(
                label="Remaining Budget Required",
                value=format_inr_compact(outputs.remaining_budget_inr),
                help=format_inr(outputs.remaining_budget_inr),
            )
        with m4:
            st.metric(
                label="Illustrative Property Valuation",
                value=format_inr_compact(outputs.illustrative_market_valuation_inr),
                delta=f"+{format_inr_compact(outputs.unrealized_equity_or_margin_inr)} Margin",
                help=format_inr(outputs.illustrative_market_valuation_inr),
            )

        st.markdown("#### Indicative Material Requirements")
        mat1, mat2 = st.columns(2)
        with mat1:
            st.markdown(
                f"""
                <div style="border: 1px solid rgba(255,255,255,0.1); padding: 14px; border-radius: 8px;">
                    <h4 style="margin:0; color:#38BDF8;">🔩 Reinforcement Steel</h4>
                    <p style="font-size: 1.4rem; font-weight:700; margin: 6px 0;">{outputs.indicative_steel_quantity_metric_tons:,.2f} Metric Tons</p>
                    <small style="color:#94A3B8;">Equivalent to {outputs.indicative_steel_quantity_kg:,.0f} kg ({plan_inputs.steel_req_kg_per_sqft} kg/sq ft)</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with mat2:
            st.markdown(
                f"""
                <div style="border: 1px solid rgba(255,255,255,0.1); padding: 14px; border-radius: 8px;">
                    <h4 style="margin:0; color:#F59E0B;">🧱 Portland Cement</h4>
                    <p style="font-size: 1.4rem; font-weight:700; margin: 6px 0;">{outputs.indicative_cement_quantity_bags:,.0f} Standard Bags</p>
                    <small style="color:#94A3B8;">50kg bags ({plan_inputs.cement_req_bags_per_sqft} bags/sq ft)</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(" ")
        save_col, dl_col = st.columns([1, 1])
        with save_col:
            if st.button("💾 Save Planning Report to Session Registry", use_container_width=True):
                st.session_state["planning_reports"].append(planning_report)
                st.success("Report registered in Session Hub.")

        with dl_col:
            plan_json = serialize_report(planning_report)
            st.download_button(
                label="📥 Download Planning Report (JSON)",
                data=plan_json,
                file_name=f"planning_report_{get_current_timestamp()[:10]}.json",
                mime="application/json",
                use_container_width=True,
            )


# ----------------------------------------------------------------------
# Module 4: Daily Site Assistant & Weather-Aware Advisory
# ----------------------------------------------------------------------
elif module_choice == "Daily Site Assistant & Weather":
    st.header("🌦️ Daily Site Assistant & Weather-Aware Advisory")
    st.markdown(
        "Manage daily on-site environmental safety checklists and consult the AI Construction "
        "Assistant for civil engineering practices, excavation procedures, and safety compliance."
    )

    from src.weather_advisory import WEATHER_CONDITIONS, get_weather_advisory

    tab1, tab2 = st.tabs(["🌦️ Weather-Aware Site Advisory", "💬 Construction AI Assistant"])

    with tab1:
        st.subheader("1. Active Weather Condition")
        st.caption("Select current or forecasted on-site conditions to generate targeted checklists.")

        selected_weather = st.radio(
            "Current On-Site Condition",
            WEATHER_CONDITIONS,
            index=0,
            horizontal=True,
        )

        advisory = get_weather_advisory(selected_weather)

        alert_color = "#10B981"
        if advisory["alert_level"] == "HIGH":
            alert_color = "#EF4444"
        elif advisory["alert_level"] == "MEDIUM":
            alert_color = "#F59E0B"

        st.markdown(
            f"""
            <div style="border-left: 5px solid {alert_color}; background-color: rgba(255,255,255,0.04); padding: 16px; border-radius: 6px; margin: 15px 0;">
                <h3 style="margin: 0; color: {alert_color};">{advisory['title']}</h3>
                <p style="margin: 8px 0 0 0; color: #CBD5E1;">{advisory['description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Mandatory Weather Safety Checklist")
        st.caption("Mark checklist items as verified by the site safety officer during morning walkaround:")

        checklist_items = advisory.get("checklist", [])
        for item in checklist_items:
            importance_badge = "badge-gray"
            if item["importance"] == "Critical":
                importance_badge = "badge-red"
            elif item["importance"] == "Mandatory":
                importance_badge = "badge-amber"

            st.checkbox(
                f"[{item['category']}] {item['item']}",
                key=f"chk_{item['id']}",
                help=f"Importance: {item['importance']}",
            )

        with st.expander("📋 Additional General Precautions"):
            for prec in advisory.get("precautions", []):
                st.write(f"- {prec}")

        st.caption("ℹ️ Note: Weather checklists operate 100% offline and do not consume AI tokens.")

    with tab2:
        st.subheader("2. Civil Engineering & Safety Assistant")
        st.caption("Ask technical questions regarding site operations, concrete pouring, lifting permits, or safety standards.")

        # Quick question pills
        st.markdown("**Quick Inquiries:**")
        quick_questions = [
            "What should be checked before pouring concrete?",
            "What precautions should be taken during heavy rain?",
            "What inspections should precede lifting operations?",
            "What should be checked before excavation work begins?",
        ]

        preset_cols = st.columns(len(quick_questions))
        preset_choice = None
        for idx, q_text in enumerate(quick_questions):
            with preset_cols[idx]:
                if st.button(q_text, key=f"quick_q_{idx}", use_container_width=True):
                    preset_choice = q_text

        query_input = st.text_input(
            "Your Construction Question",
            value=preset_choice if preset_choice else "",
            placeholder="e.g. What is the required curing duration for OPC concrete in hot weather?",
            max_chars=600,
        )

        ask_btn = st.button("🚀 Ask Assistant", type="primary")

        if ask_btn and query_input:
            sanitized_query = sanitize_text_input(query_input)
            if not sanitized_query:
                st.error("Please enter a non-empty question.")
            else:
                api_key = resolve_api_key(st.session_state.get("session_api_key"))
                if not api_key:
                    st.error(
                        "❌ Gemini API key not detected. To use the AI Assistant, please enter a session key "
                        "in the sidebar or configure `GEMINI_API_KEY`."
                    )
                elif not is_genai_installed():
                    st.error("❌ `google-genai` SDK is not installed in the current environment.")
                else:
                    with st.spinner("Consulting construction intelligence assistant..."):
                        try:
                            weather_context = f"Active site condition: {selected_weather} ({advisory['title']})"
                            answer = ask_site_assistant_gemini(
                                api_key=api_key,
                                model=st.session_state.get("selected_model", DEFAULT_GEMINI_MODEL),
                                question=sanitized_query,
                                weather_context=weather_context,
                            )
                            # Record in history
                            record = {
                                "timestamp": get_current_timestamp(),
                                "question": sanitized_query,
                                "weather_condition": selected_weather,
                                "answer": answer,
                            }
                            st.session_state["assistant_history"].append(record)
                        except Exception as a_exc:
                            st.error(f"Assistant request error: {str(a_exc)}")

        # Display history
        if st.session_state["assistant_history"]:
            st.markdown("---")
            st.subheader("Consultation History")
            for entry in reversed(st.session_state["assistant_history"]):
                with st.expander(f"Q: {entry['question']} ({entry['weather_condition']})", expanded=True):
                    st.markdown(entry["answer"])
                    st.caption(f"Generated at: {entry['timestamp']} | Verification with Project EOR required.")


# ----------------------------------------------------------------------
# Module 5: Session Reports & System Information
# ----------------------------------------------------------------------
elif module_choice == "Session Reports & System Info":
    st.header("📊 Session Reports & System Information")
    st.markdown("Inspect all reports generated during this session, export consolidated JSON audits, and verify system status.")

    tab1, tab2 = st.tabs(["📁 Session Audit History", "⚙️ System & Runtime Diagnostics"])

    with tab1:
        st.subheader("Session Reports Registry")

        safety_reports = st.session_state.get("safety_reports", [])
        crack_reports = st.session_state.get("crack_reports", [])
        planning_reports = st.session_state.get("planning_reports", [])
        assistant_records = st.session_state.get("assistant_history", [])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Safety Audits", len(safety_reports))
        c2.metric("Crack Screenings", len(crack_reports))
        c3.metric("Planning Estimates", len(planning_reports))
        c4.metric("Assistant Queries", len(assistant_records))

        total_reports = len(safety_reports) + len(crack_reports) + len(planning_reports)

        if total_reports == 0 and len(assistant_records) == 0:
            st.info("No reports have been generated in this session yet. Navigate to any module to create one.")
        else:
            # Consolidated download
            consolidated_bundle = {
                "bundle_title": "Construction Intelligence Session Export",
                "export_timestamp": get_current_timestamp(),
                "summary_counts": {
                    "safety_audits": len(safety_reports),
                    "crack_screenings": len(crack_reports),
                    "planning_reports": len(planning_reports),
                    "assistant_inquiries": len(assistant_records),
                },
                "safety_audits": safety_reports,
                "crack_screenings": crack_reports,
                "planning_reports": planning_reports,
                "assistant_inquiries": assistant_records,
                "disclaimer": "This session bundle contains preliminary automated screenings and user-specified planning estimates.",
            }

            st.download_button(
                label="📦 Download Complete Session Bundle (JSON)",
                data=serialize_report(consolidated_bundle),
                file_name=f"session_bundle_{get_current_timestamp()[:10]}.json",
                mime="application/json",
                type="primary",
                use_container_width=True,
            )

            st.markdown("---")
            if safety_reports:
                st.markdown("#### Site Safety Audits")
                for idx, rpt in enumerate(safety_reports):
                    with st.expander(f"Safety Audit #{idx + 1} - {rpt.get('timestamp_utc', 'N/A')}"):
                        st.json(rpt)

            if crack_reports:
                st.markdown("#### Crack Screenings")
                for idx, rpt in enumerate(crack_reports):
                    with st.expander(f"Crack Screening #{idx + 1} - {rpt.get('timestamp_utc', 'N/A')}"):
                        st.json(rpt)

            if planning_reports:
                st.markdown("#### Planning Estimates")
                for idx, rpt in enumerate(planning_reports):
                    with st.expander(f"Planning Report #{idx + 1} - {rpt.get('timestamp_utc', 'N/A')}"):
                        st.json(rpt)

    with tab2:
        st.subheader("System Health & Diagnostic Checks")

        current_key = resolve_api_key(st.session_state.get("session_api_key"))
        key_status_label = "Configured" if current_key else "Missing"

        status_items = [
            ("Python Runtime Version", sys.version.split()[0]),
            ("Streamlit Version", st.__version__),
            ("Pillow (PIL) Available", "Yes"),
            ("Google Gen AI SDK Available", "Yes" if is_genai_installed() else "Not Installed"),
            ("Gemini API Key Status", key_status_label),
            ("Active Gemini Model", st.session_state.get("selected_model", DEFAULT_GEMINI_MODEL)),
            ("Operating System", sys.platform),
        ]

        for label, val in status_items:
            c_label, c_val = st.columns([1, 1])
            c_label.write(f"**{label}**")
            c_val.code(val)

        st.markdown("---")
        st.subheader("Engineering & Safety Standards Alignment")
        st.markdown(
            """
            - **Site Safety:** OSHA Standard 1926 (Safety and Health Regulations for Construction) & IS 2925.
            - **Crack Diagnostics:** Preliminary pattern classification (ACI 224R-01 - Control of Cracking in Concrete Structures).
            - **Planning:** Deterministic CPWD-style heuristics with customizable rates and Indian numbering grouping.
            - **Weather Guidance:** National Meteorological & OSHA severe weather guidelines for construction operations.
            """
        )
