# 💊 Medication Interaction Checker

An intelligent web app that checks for dangerous drug interactions based on patient medication lists and conditions.

## 🚀 Features
- Enter multiple medications
- Patient age and chronic condition support
- AI-based severity classification (mild, moderate, severe)
- Styled and interactive Streamlit UI
- Downloadable report (.txt)

## 🧠 AI Logic
- Rule-based interaction detection using a real dataset
- Severity is adapted based on patient risk factors

## 📦 Installation

```bash
git clone https://github.com/your-username/MedicationChecker.git
cd MedicationChecker/app
pip install -r ../requirements.txt
py -m streamlit run medication_app.py
