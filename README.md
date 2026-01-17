# 🚑 MediPatient AI
### *Hybrid Clinical Intelligence: Statistical ML + LLM Reasoning*

## 📖 Overview
**MediPatient AI** is a clinical decision support system that combines the speed of Machine Learning with the deep clinical reasoning of Large Language Models (LLMs). 

The system uses a **Double-Check Architecture**:
1. **Analytical Engine:** A Random Forest model trained on hospital datasets to detect statistical patterns.
2. **Reasoning Engine:** Google Gemini 1.5 Flash, which validates predictions and provides human-readable explanations.



---

## 🏗️ System Architecture
The system processes data through a structured clinical pipeline:

1. **Vitals Ingestion:** Receives patient data (BP, Heart Rate, Temp, O2) via FastAPI.
2. **Feature Engineering:** Computes clinical flags like `hypotension` and `tachycardia`.
3. **ML Prediction:** The Random Forest classifies the vitals into a disease category.
4. **AI Validation:** Gemini Pro reviews the case, identifies "Red Flags," and suggests a treatment plan.
5. **PDF Reporting:** An automated, professional clinical report is generated for the physician.

---

## 📂 Project Structure
| File | Role |
| :--- | :--- |
| medical_orchestrator.py | The Master Brain. Links the ML model with Gemini Pro. |
| ai_diagnosis.py | Training script using Augmented Textbook Data. |
| gen_ai_module.py | Integration layer for the Gemini Pro API. |
| api.py | FastAPI server for real-time diagnostic requests. |
| report_generator.py | Generates professional PDF clinical reports. |
| test_system.py | Stress-test suite for clinical accuracy validation. |

---

## 🚀 Installation & Setup

### 1. Install Dependencies
pip install -r requirements.txt

### 2. Configure API Key
Create a .env file in the root directory:
GEMINI_API_KEY=your_key_here

### 3. Run the System
python ai_diagnosis.py
python api.py

---

## ⚖️ Disclaimer
*This project is a research prototype for educational purposes only. It is not intended for real-world clinical use or medical diagnosis without professional supervision.*
