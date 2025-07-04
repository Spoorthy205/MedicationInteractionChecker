import streamlit as st
import pandas as pd
from itertools import combinations

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Medication Interaction Checker", layout="wide")

# Load interaction dataset
@st.cache_data
def load_data():
    df = pd.read_csv("app/db_drug_interactions.csv")
    df["Drug 1"] = df["Drug 1"].str.strip().str.lower()
    df["Drug 2"] = df["Drug 2"].str.strip().str.lower()
    interaction_dict = {
        tuple(sorted([row["Drug 1"], row["Drug 2"]])): row["Interaction Description"]
        for _, row in df.iterrows()
    }
    known_drugs = sorted(set(df["Drug 1"]).union(set(df["Drug 2"])))
    return interaction_dict, known_drugs

interaction_dict, known_drugs = load_data()

# Severity classification
SEVERE_KEYWORDS = {"life-threatening", "fatal", "serious", "severe", "toxic", "contraindicated"}
MODERATE_KEYWORDS = {"risk", "increase", "may cause", "enhance", "interfere"}
MILD_KEYWORDS = {"mild", "slight", "temporary", "low"}

def classify_severity(desc):
    desc = desc.lower()
    if any(word in desc for word in SEVERE_KEYWORDS):
        return "Severe"
    elif any(word in desc for word in MODERATE_KEYWORDS):
        return "Moderate"
    elif any(word in desc for word in MILD_KEYWORDS):
        return "Mild"
    else:
        return "Unknown"

def adjust_severity(severity, description, age, conditions):
    desc = description.lower()
    risk_factors = ["kidney", "liver", "blood pressure", "heart", "renal", "diabetes"]
    patient_at_risk = (age > 65 or any(cond in desc for cond in conditions) or any(risk in desc for risk in risk_factors))
    if severity == "Moderate" and patient_at_risk:
        return "Severe"
    elif severity == "Mild" and patient_at_risk:
        return "Moderate"
    else:
        return severity

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #5a6c7d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    .results-header {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .severity-severe {
        background-color: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        min-width: 70px;
    }
    .severity-moderate {
        background-color: #ffc107;
        color: #212529;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        min-width: 70px;
    }
    .severity-mild {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        min-width: 70px;
    }
    .drug-tag {
        background-color: #007bff;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.9rem;
        margin: 0.1rem;
        display: inline-block;
    }
    .interaction-card {
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-header">💊 Medication Interaction Checker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">🧠 AI-Powered Risk Alerts Based on Patient Medications</div>', unsafe_allow_html=True)

# Patient Input
st.markdown('<div class="section-header">🧾 Patient Details</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    drugs = st.multiselect("💊 Select Medications", known_drugs, help="Choose at least two drugs", default=[])
    if drugs:
        tags = ' '.join([f'<span class="drug-tag">{drug.title()}</span>' for drug in drugs])
        st.markdown(tags, unsafe_allow_html=True)

with col2:
    age = st.number_input("🎂 Patient Age", min_value=0, max_value=120, value=45)
    cond_input = st.text_input("💉 Chronic Conditions (comma separated)", value="diabetes")
    conditions = [c.strip().lower() for c in cond_input.split(",") if c.strip()]

# Interaction Check
if len(drugs) >= 2:
    pairs = list(combinations(drugs, 2))
    results = []

    for pair in pairs:
        key = tuple(sorted(pair))
        if key in interaction_dict:
            desc = interaction_dict[key]
            base_sev = classify_severity(desc)
            final_sev = adjust_severity(base_sev, desc, age, conditions)
            results.append({
                "💊 Drug 1": key[0].title(),
                "💊 Drug 2": key[1].title(),
                "Interaction Description": desc,
                "⚠️ Severity": final_sev
            })

    if results:
        st.markdown('<div class="results-header">🧪 Drug Interaction Results</div>', unsafe_allow_html=True)
        for result in results:
            sev_class = f"severity-{result['⚠️ Severity'].lower()}"
            st.markdown(f"""
                <div class="interaction-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div>
                            <strong>💊 Drug 1:</strong> {result['💊 Drug 1']} &nbsp;&nbsp;
                            <strong>💊 Drug 2:</strong> {result['💊 Drug 2']}
                        </div>
                        <div class="{sev_class}">{result['⚠️ Severity']}</div>
                    </div>
                    <div>
                        <strong>Interaction Description:</strong> {result['Interaction Description']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Generate downloadable report
        report_text = "\n\n".join([
            f"Interaction: {r['💊 Drug 1']} + {r['💊 Drug 2']}\n→ {r['Interaction Description']}\n→ Severity: {r['⚠️ Severity']}\n{'-'*40}"
            for r in results
        ])
        st.download_button("⬇️ Download Report (TXT)", report_text, file_name="interaction_report.txt", mime="text/plain")

    else:
        st.success("✅ No known interactions found.")
elif drugs:
    st.warning("⚠️ Please select at least two medications to check for interactions.")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6c757d; margin-top: 2rem;">🚀 Developed by <b>Spoorthy</b> | Techsohy Placement Drive 2025</p>',
    unsafe_allow_html=True
)
