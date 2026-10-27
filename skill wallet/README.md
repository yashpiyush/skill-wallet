# Multimodal Construction Intelligence Platform

**Skill Wallet Capstone Project 1**  
*An AI-assisted civil engineering and site management platform combining multimodal computer vision, deterministic planning calculators, and weather-aware safety advisories.*

---

## 🏗️ 1. Project Overview

The **Multimodal Construction Intelligence Platform** bridges modern multimodal artificial intelligence with civil engineering workflows. Built with **Streamlit**, **Google Gemini Multimodal AI**, and **Pillow**, the platform assists safety officers, project engineers, quantity surveyors, and contractors in auditing site hazards, screening structural defects, estimating financial requirements, and adhering to environmental weather regulations.

### Core Value Pillars
- **Multimodal Site Safety:** Clinical visual analysis of Personal Protective Equipment (PPE) compliance and environmental site hazards.
- **Structural Integrity Screening:** Preliminary visual defect classification for concrete and masonry cracks with mandatory engineering review safeguards.
- **Deterministic Estimation:** Rigorous mathematical budgeting, material consumption heuristics (steel & cement), and illustrative market valuation without AI hallucinations.
- **Weather-Aware Safety:** Proactive operational checklists aligned with OSHA and Indian Standards (IS) for extreme weather (high winds, monsoons, heat stress, freezing).
- **Audit Trails & Export:** Session-level history and instant downloadable JSON audit reports.

---

## 🚀 2. System Architecture & Modules

```
construction-intelligence-platform/
├── .streamlit/
│   └── config.toml             # Theme (slate/amber) and server configuration
├── src/
│   ├── __init__.py             # Package declaration
│   ├── ai_service.py           # Google Gen AI SDK wrapper, error handling & JSON parser
│   ├── safety_analysis.py      # Module 1: PPE inspection & hazard taxonomy
│   ├── crack_analysis.py       # Module 2: Visual crack diagnostics & defect screening
│   ├── planning.py             # Module 3: Deterministic budget & valuation engine
│   ├── weather_advisory.py     # Module 4: Weather checklists & standards alignment
│   ├── report_utils.py         # Standardized JSON envelopes & INR formatting
│   └── validation.py           # Image integrity checks & numerical input guards
├── tests/
│   ├── __init__.py             # Test package
│   ├── test_ai_service.py      # AI mocks, JSON extractors & fallback tests
│   ├── test_crack_analysis.py  # Crack classification & engineer review guards
│   ├── test_planning.py        # Budget, expenditure, steel, cement & INR format tests
│   ├── test_reports.py         # JSON contract serialization tests
│   ├── test_safety_analysis.py # PPE status normalization & hazard severity tests
│   ├── test_validation.py      # Image format, size, and numerical boundary tests
│   └── test_weather_advisory.py# Weather condition checklists & precautions tests
├── app.py                      # Streamlit dashboard & multi-module UI
├── requirements.txt            # Python dependencies
├── .gitignore                  # Production Git ignore rules
└── README.md                   # Comprehensive technical documentation
```

### Module Breakdown

| Module | Engine | Primary Function | Minimum Output Contract |
|---|---|---|---|
| **1. Site Safety & PPE Audit** | Multimodal Gemini Vision | Evaluates helmets, vests, footwear, harnesses, eye protection, and physical hazards. | `site_safety_ppe_audit` JSON |
| **2. Crack Diagnostics & Structural** | Multimodal Gemini Vision | Screens surface defects (shear, settlement, hairline, spalling) and flags urgency. | `crack_diagnostics` JSON |
| **3. Planning & Real Estate Valuation** | Deterministic Python Engine | Computes budgets, expenditures, remaining balances, steel/cement quantities, and valuation. | `planning_and_real_estate_valuation` JSON |
| **4. Daily Site Assistant & Weather** | Rule Engine + Gemini Text | Condition-specific weather checklists (wind, rain, heat, cold) & engineering Q&A. | Interactive Checklists & Technical Guidance |
| **5. Session Reports & System Info** | In-Memory Registry | Central repository of all generated reports with one-click JSON export. | Consolidated Session Bundle JSON |

---

## 🧮 3. Deterministic Planning Formulas

All calculations in **Module Three (Planning & Real Estate Valuation)** are strictly deterministic and mathematically reproducible:

$$
\text{Total Budget} = \text{Built-up Area} \times \text{Assumed Cost per sq ft}
$$

$$
\text{Estimated Expenditure} = \text{Total Budget} \times \left(\frac{\text{Completion Percentage}}{100}\right)
$$

$$
\text{Remaining Budget} = \text{Total Budget} - \text{Estimated Expenditure}
$$

$$
\text{Illustrative Valuation} = \text{Built-up Area} \times \text{Assumed Market Value per sq ft}
$$

$$
\text{Indicative Steel Quantity (kg)} = \text{Built-up Area} \times \text{Steel Requirement per sq ft (kg)}
$$

$$
\text{Indicative Cement Quantity (bags)} = \text{Built-up Area} \times \text{Cement Requirement per sq ft (bags)}
$$

*Amounts in Indian Rupees (INR) are rendered using the Indian numbering comma system (e.g., `₹ 1,25,00,000` / `₹ 1.25 Cr`).*

---

## 🛠️ 4. Prerequisites

- **Python:** Version 3.10, 3.11, 3.12, 3.13, or 3.14.
- **Git:** Installed on system.
- **Google Gemini API Key:** (Optional for planning calculator and weather checklists; required for live multimodal vision audits and AI assistant). Get one from [Google AI Studio](https://aistudio.google.com/).

---

## 💻 5. Installation & Local Setup

### Windows PowerShell

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/<your-username>/construction-intelligence-platform.git
   cd construction-intelligence-platform
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set your Gemini API Key (Optional for offline use):**
   ```powershell
   $env:GEMINI_API_KEY="your-gemini-api-key-here"
   ```

5. **Run the application:**
   ```powershell
   $env:PYTHONUTF8=1
   streamlit run app.py
   ```

### macOS / Linux

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/construction-intelligence-platform.git
   cd construction-intelligence-platform
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set your Gemini API Key:**
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key-here"
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The application will open automatically at `http://localhost:8501`.

---

## 🔐 6. API Key & Model Configuration

The application supports three levels of API key configuration with strict precedence:

1. **Session Input (Local Demonstration):** Enter your key directly in the sidebar password box. The key resides only in volatile session memory and is never logged or written to disk.
2. **Streamlit Secrets (`.streamlit/secrets.toml`):**
   Create `.streamlit/secrets.toml` (ignored by git):
   ```toml
   GEMINI_API_KEY = "AIzaSyYourSecretKeyHere"
   GEMINI_MODEL = "gemini-2.5-flash"
   ```
3. **Environment Variables:** Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL`.

*Note: The Planning Calculator and Weather Checklists function 100% offline without any API key.*

---

## 🧪 7. Automated Testing & Verification

The project includes an automated test suite covering all calculation boundaries, image validation rules, and schema contracts.

### Run tests with Python `unittest`:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Run tests with `pytest`:
```bash
pytest -v
```

### Verified Test Matrix:
- ✅ **Planning Metrics:** Total budget, expenditure, remaining budget, equity margin, steel/cement heuristics.
- ✅ **Boundary Conditions:** 0% and 100% completion limits, zero and negative rate bounds.
- ✅ **Currency Formatting:** Indian comma groupings (`₹ 1,00,000`, `₹ 1.25 Cr`).
- ✅ **Image Validation:** JPEG, PNG, WEBP verification, corrupted byte detection, dimension checks, and 10MB limit enforcement.
- ✅ **AI Output Normalization:** Normalization of non-standard PPE status labels into `"Compliant and visibly present"`, `"Potentially missing"`, `"Not visible"`, or `"Uncertain"`.
- ✅ **Safety Disclaimer Invariant:** Verification that human review requirements and engineering disclaimers are present on all generated reports.
- ✅ **Weather Completeness:** Full verification of all 5 weather advisories and safety checklists.

---

## ☁️ 8. Streamlit Community Cloud Deployment

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "feat: complete multimodal construction intelligence platform"
   git branch -M main
   git remote add origin https://github.com/<your-username>/construction-intelligence-platform.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Navigate to [share.streamlit.io](https://share.streamlit.io/).
   - Click **New app** and select your repository, branch (`main`), and entrypoint (`app.py`).
   - Open **Advanced settings** -> **Secrets**.
   - Paste your secret configuration:
     ```toml
     GEMINI_API_KEY = "your-actual-gemini-api-key"
     GEMINI_MODEL = "gemini-2.5-flash"
     ```
   - Click **Deploy!**

---

## ⚠️ 9. Engineering Disclaimers & Responsible AI

> [!WARNING]
> **Mandatory Safety and Regulatory Caveats:**
> 1. **No False Safety Certificates:** Never declare a construction site safe or certify structural integrity solely on the basis of AI visual analysis.
> 2. **2D Image Limitations:** Photographic inspection cannot determine internal reinforcement corrosion, core concrete compressive strength, foundation subsidence, or subsurface shear stress.
> 3. **Non-Inference of Absence:** The platform strictly adheres to the principle that safety equipment is never inferred as absent merely because it is occluded or outside the photograph's field of view.
> 4. **Professional Oversight:** All structural cracks and severe site hazards require immediate on-site physical evaluation by a licensed Professional Engineer (PE) or certified Safety Auditor.
> 5. **Financial Disclaimers:** Planning estimates are purely illustrative rule-of-thumb heuristics and do not constitute certified contractor Bill of Quantities (BOQ) or bank appraisals.

---

## 📄 10. License

Developed for **Skill Wallet Capstone Project 1: Multimodal Construction Intelligence Platform**.
Open-source under the Apache 2.0 / MIT License.
