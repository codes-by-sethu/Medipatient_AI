"""
FLASK API SERVER - THE CONNECTOR
Connects Frontend -> Medical Orchestrator -> Report Generator
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from pathlib import Path

# 1. IMPORT YOUR WORKING ORCHESTRATOR
from medical_orchestrator import MedicalOrchestrator, PatientFeatures
from config import Config
from report_generator import generate_pdf_report

app = Flask(__name__, static_folder='static')
CORS(app)

print("="*60)
print("🚀 STARTING MEDIPATIENT API (CONNECTED TO ORCHESTRATOR)")
print("="*60)

# 2. INITIALIZE THE COMBINED BRAIN
# This loads the ML Model AND connects to Gemini
orchestrator = MedicalOrchestrator()

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print(f"📡 Processing patient: Age {data.get('age')}, Temp {data.get('temperature')}")
        
        # 3. CONVERT DATA FOR ORCHESTRATOR
        # We convert the raw frontend JSON into the format the Orchestrator expects
        symptoms = []
        if data.get('fever'): symptoms.append('fever')
        if data.get('cough'): symptoms.append('cough')
        if data.get('shortness_of_breath'): symptoms.append('shortness of breath')
        if data.get('fatigue'): symptoms.append('fatigue')
        if data.get('chest_pain'): symptoms.append('chest pain')
        
        patient = PatientFeatures(
            age=float(data.get('age', 0)),
            gender=data.get('gender', 'unknown'),
            temperature=float(data.get('temperature', 37.0)),
            heart_rate=float(data.get('heartRate', 80)),
            systolic_bp=float(data.get('systolicBP', 120)),
            diastolic_bp=float(data.get('diastolicBP', 80)),
            respiratory_rate=float(data.get('respiratoryRate', 16)),
            oxygen_saturation=float(data.get('oxygenSaturation', 98)),
            pain_score=float(data.get('painScore', 0)),
            symptoms=symptoms,
            medical_history=data.get('medical_history', []),
            allergies=data.get('allergies', []),
            medications=data.get('medications', [])
        )

        # 4. GET THE COMBINED DIAGNOSIS
        # This single line runs ML + Gemini and merges them
        diagnosis_result = orchestrator.diagnose_patient(patient)
        
        # 5. GENERATE PDF REPORT
        pdf_filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Create output/reports folder if it doesn't exist
        reports_dir = Path("output") / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = reports_dir / pdf_filename
        
        generate_pdf_report(
            patient_data=data,
            prediction=diagnosis_result,
            filename=str(pdf_path)
        )
        
        print(f"✅ Diagnosis: {diagnosis_result.get('primary_diagnosis')} | Source: {diagnosis_result.get('source')}")

        # 6. RETURN UNIFIED RESULT
        return jsonify({
            "status": "success",
            "primary_diagnosis": diagnosis_result.get('primary_diagnosis'),
            "confidence": diagnosis_result.get('confidence'),
            "severity": diagnosis_result.get('severity_score'),
            "urgency": diagnosis_result.get('urgency_level'),
            # The 'reasoning' field comes from Gemini (via Orchestrator)
            "reasoning": diagnosis_result.get('reasoning', 'Analysis provided by ML Model.'),
            "treatment_plan": diagnosis_result.get('treatment_plan', {}),
            "pdf_report_url": f"/download/{pdf_filename}"
        })

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(Path("output") / "reports", filename)

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)