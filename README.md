# 🚑 MediPatient AI

**Hybrid Clinical Intelligence: ML + LLM Reasoning (2026 Version)**

A research-grade clinical decision support system combining **Random Forest ML** for statistical detection with **Gemini LLM** for clinical reasoning, explainability, and treatment planning.

---

## 🧠 System Overview

### Double-Check Architecture

**Analytical Engine (ML)**  
- Random Forest trained on real hospital data + synthetic textbook cases.  
- Feature engineering includes vitals + derived flags (`fever_high`, `tachycardia`, `hypotension`, `hypoxia`).  
- Outputs preliminary diagnosis with confidence scores.  

**Reasoning Engine (LLM)**  
- Google Gemini 1.5 Flash validates ML predictions.  
- Provides human-readable clinical reasoning, red flags, and differential diagnosis.  
- Generates structured treatment plans.  

**Hybrid Orchestrator**  
- `MedicalOrchestrator` dynamically combines ML + LLM outputs.  
- Intelligent override ensures Gemini corrects vague or incorrect ML predictions.  
- Severity and urgency scoring based on evidence-based rules.

---

## 🏗️ Architecture Pipeline

1. **Patient Data Intake**  
   - Flask API receives structured patient data from frontend (`PatientFeatures`).  

2. **ML Prediction**  
   - Random Forest outputs disease category and confidence.  

3. **LLM Validation**  
   - Gemini AI reviews ML output and applies overrides if needed.  

4. **Treatment Planning & Reasoning**  
   - Clinical reasoning, differentials, red flags, and treatment plan included.  

5. **Data Storage & Reporting**  
   - JSON patient records saved.  
   - PDF reports generated and downloadable.  

---

## 📂 Project Structure

| File / Folder | Role |
|---------------|------|
| `api.py` | Flask server exposing secure endpoints for patient data, predictions, and report downloads. |
| `AI_diagnosis.py` | Hybrid ML trainer (real + synthetic data). |
| `gen_ai_module.py` | Gemini LLM integration (validation & treatment planning). |
| `medical_orchestrator.py` | Hybrid intelligence orchestrator combining ML + LLM outputs. |
| `report_generator.py` | Generates PDF clinical reports. |
| `test_system.py` | Validation & stress-testing of the pipeline. |
| `models/` | Trained ML model artifacts (.pkl, feature names, disease mapping). |
| `.env` | Gemini API key, model/report directories, optional rate limits. |
| `templates/` | Frontend dashboard (HTML). |
| `static/` | CSS/JS frontend assets. |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
````

### 2. Add `.env` configuration

```dotenv
GEMINI_API_KEY=your_key_here
MODEL_DIR=./output
REPORTS_DIR=./output/reports
PATIENT_DIR=./output/patient_data
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000
FLASK_ENV=development
```

### 3. Train ML model (optional)

```bash
python AI_diagnosis.py
```

### 4. Start API

```bash
python api.py
```

### 5. Example request to `/api/predict`

```http
POST /api/predict
Content-Type: application/json

{
  "age": 58,
  "gender": "male",
  "temperature": 37.2,
  "heartRate": 95,
  "systolicBP": 150,
  "diastolicBP": 95,
  "respiratoryRate": 20,
  "oxygenSaturation": 96,
  "painScore": 9,
  "symptoms": ["chest pain", "fatigue", "nausea", "dizziness"],
  "medical_history": ["hypertension"],
  "allergies": [],
  "medications": ["aspirin"]
}
```

---

## ⚙️ Features

* **Hybrid AI:** ML + LLM reasoning.
* **Augmented Training:** Synthetic cases complement real hospital data.
* **Explainable AI:** Full clinical reasoning, differentials, red flags.
* **Intelligent Overrides:** Gemini corrects vague/incorrect ML predictions.
* **Treatment Planning:** Structured plans generated dynamically.
* **Severity & Urgency:** Evidence-based scoring and triage.
* **Secure API:** Rate-limited, CORS-restricted, and path-traversal safe.
* **PDF Reports:** Downloadable via `/download/`.
* **Patient Data Storage:** JSON records with retrieval and deletion endpoints.

---

## 📡 API Endpoints

| Endpoint                         | Method | Description                                              |
| -------------------------------- | ------ | -------------------------------------------------------- |
| `/api/predict`                   | POST   | Hybrid ML+LLM diagnosis, returns PDF link and reasoning. |
| `/download/<filename>`           | GET    | Download report PDF securely.                            |
| `/api/status`                    | GET    | Server health check & model/LLM availability.            |
| `/api/get-reports`               | GET    | List latest PDF reports.                                 |
| `/api/delete-report/<filename>`  | DELETE | Delete report PDF.                                       |
| `/api/get-patients`              | GET    | List latest patient JSON records.                        |
| `/download-patient/<filename>`   | GET    | Download patient JSON securely.                          |
| `/api/delete-patient/<filename>` | DELETE | Delete patient JSON record.                              |

---

## 🧪 Testing

```bash
python test_system.py
```

---

## ⚖️ Disclaimer

* **Research Prototype:** Not intended for real-world clinical diagnosis.
* **Use only under professional supervision.

```

---
