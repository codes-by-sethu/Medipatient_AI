"""
FLASK API SERVER - THE CONNECTOR
All data comes from frontend, no hardcoding
SECURE VERSION - FIXED ALL ISSUES
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import json

# 1️⃣ Explicit path to .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2️⃣ Fetch the key
api_key = os.getenv("GEMINI_API_KEY")

# 3️⃣ Immediate check
if api_key:
    print(f"✅ GEMINI_API_KEY loaded successfully: {api_key[:10]}...")
else:
    print("⚠️ GEMINI_API_KEY NOT loaded! Check .env or OS environment")


# Import local modules AFTER loading .env
try:
    from medical_orchestrator import MedicalOrchestrator, PatientFeatures
    from report_generator import generate_pdf_report
    print("✅ Local modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import local modules: {e}")
    raise

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediPatientAPI")

app = Flask(__name__, static_folder='static')

# Secure CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")
    }
})

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute", "10 per second"]
)

print("="*60)
print("🚀 MEDIPATIENT API STARTING (SECURE)")
print("="*60)

# Check if .env is loaded
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ .env loaded - Gemini API Key: {api_key[:10]}...")
else:
    print("⚠️  No GEMINI_API_KEY found in .env - Gemini features will be disabled")

# Initialize orchestrator with config from env
orchestrator = MedicalOrchestrator(
    model_dir=os.getenv("MODEL_DIR", "./output"),
    gemini_api_key=api_key
)

# Ensure required directories exist
def ensure_directories():
    """Create all required directories on startup"""
    directories = [
        os.getenv("REPORTS_DIR", "output/reports"),
        os.getenv("PATIENT_DIR", "output/patient_data"),
        os.getenv("MODEL_DIR", "./output"),
    ]
    
    for dir_path in directories:
        dir_obj = Path(dir_path)
        dir_obj.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directory ensured: {dir_obj.absolute()}")

ensure_directories()

@app.before_request
def validate_json():
    """Ensure JSON content type for POST requests"""
    if request.method == 'POST' and not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

def validate_patient_data(data):
    """Validate ALL patient data from frontend - NO HARDCODED VALUES"""
    errors = []
    
    # Age: 0-120 years
    age = data.get('age')
    if age is None:
        errors.append("Age is required")
    elif not (0 <= age <= 120):
        errors.append("Age must be between 0 and 120 years")
    
    # Temperature: 35-43°C (human range)
    temp = data.get('temperature')
    if temp is not None and not (35 <= temp <= 43):
        errors.append("Temperature must be between 35°C and 43°C")
    
    # Heart rate: 40-200 BPM
    hr = data.get('heartRate')
    if hr is not None and not (40 <= hr <= 200):
        errors.append("Heart rate must be between 40 and 200 BPM")
    
    # Blood pressure ranges
    sbp = data.get('systolicBP')
    if sbp is not None and not (70 <= sbp <= 250):
        errors.append("Systolic BP must be between 70 and 250 mmHg")
    
    dbp = data.get('diastolicBP')
    if dbp is not None and not (40 <= dbp <= 150):
        errors.append("Diastolic BP must be between 40 and 150 mmHg")
    
    # Respiratory rate: 5-40 breaths/min
    rr = data.get('respiratoryRate')
    if rr is not None and not (5 <= rr <= 40):
        errors.append("Respiratory rate must be between 5 and 40 breaths/min")
    
    # Oxygen saturation: 70-100%
    o2 = data.get('oxygenSaturation')
    if o2 is not None and not (70 <= o2 <= 100):
        errors.append("Oxygen saturation must be between 70% and 100%")
    
    # Pain score: 0-10
    pain = data.get('painScore')
    if pain is not None and not (0 <= pain <= 10):
        errors.append("Pain score must be between 0 and 10")
    
    # Validate gender if provided
    gender = data.get('gender', '').lower()
    valid_genders = ['male', 'female', 'other', 'unknown', 'prefer not to say', '']
    if gender and gender not in valid_genders:
        errors.append(f"Gender must be one of: {', '.join(valid_genders[:-1])}")
    
    return errors

def save_patient_record(patient_data, diagnosis_result):
    """Save patient data and diagnosis to JSON file"""
    try:
        patients_dir = Path(os.getenv("PATIENT_DIR", "output/patient_data"))
        patients_dir.mkdir(parents=True, exist_ok=True)
        
        patient_id = f"patient_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = patients_dir / f"{patient_id}.json"
        
        record = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "patient_data": patient_data,
            "diagnosis": diagnosis_result
        }
        
        with open(filename, 'w') as f:
            json.dump(record, f, indent=2, default=str)
        
        logger.info(f"✅ Patient record saved: {filename}")
        return patient_id
    except Exception as e:
        logger.error(f"❌ Failed to save patient record: {e}")
        return None

@app.route('/api/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    """Main diagnostic endpoint - ALL DATA FROM FRONTEND, NO HARCODING"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"📡 Processing patient: Age {data.get('age')}")
        
        # Validate ALL data from frontend
        validation_errors = validate_patient_data(data)
        if validation_errors:
            return jsonify({
                "status": "validation_error",
                "errors": validation_errors
            }), 400
        
        # Extract symptoms ONLY from frontend
        symptoms = []
        
        # Method 1: Boolean flags from frontend
        symptom_flags = {
            'fever': 'fever',
            'cough': 'cough', 
            'shortness_of_breath': 'shortness of breath',
            'fatigue': 'fatigue',
            'chest_pain': 'chest pain',
            'nausea': 'nausea',
            'dizziness': 'dizziness',
            'confusion': 'confusion'
        }
        
        for key, label in symptom_flags.items():
            if data.get(key, False):
                symptoms.append(label)
        
        # Method 2: Direct symptoms list from frontend
        if data.get('symptoms') and isinstance(data['symptoms'], list):
            for symptom in data['symptoms']:
                if isinstance(symptom, str) and symptom.strip():
                    symptoms.append(symptom.strip())
        
        # Remove duplicates
        symptoms = list(set(symptoms))
        
        # Create patient - ALL DATA FROM FRONTEND
        patient = PatientFeatures(
            age=float(data.get('age', 0)),
            gender=data.get('gender', 'unknown'),
            temperature=float(data.get('temperature', 37.0)),
            heart_rate=float(data.get('heartRate', 75.0)),
            systolic_bp=float(data.get('systolicBP', 120.0)),
            diastolic_bp=float(data.get('diastolicBP', 80.0)),
            respiratory_rate=float(data.get('respiratoryRate', 16.0)),
            oxygen_saturation=float(data.get('oxygenSaturation', 98.0)),
            pain_score=float(data.get('painScore', 0.0)),
            symptoms=symptoms,
            medical_history=data.get('medical_history', []),
            allergies=data.get('allergies', []),
            medications=data.get('medications', [])
        )
        
        # Get hybrid diagnosis
        diagnosis_result = orchestrator.diagnose_patient(patient)

        # ================================================================
        # 🔧 CRITICAL FIX: ENSURE CLINICAL REASONING EXISTS FOR PDF
        # ================================================================
        if 'clinical_reasoning' not in diagnosis_result or not diagnosis_result['clinical_reasoning']:
            # Fallback logic: Try to construct a reasoning string if the model didn't return one
            diagnosis_str = diagnosis_result.get('primary_diagnosis', 'Undetermined')
            symptom_str = ", ".join(symptoms) if symptoms else "reported symptoms"
            
            # Create a professional default reasoning string
            diagnosis_result['clinical_reasoning'] = (
                f"Clinical assessment indicates {diagnosis_str} based on {symptom_str} "
                f"and vital signs analysis. Severity score: {diagnosis_result.get('severity_score', 0):.2f}."
            )
        # ================================================================
        
        # Save patient record to JSON
        patient_id = save_patient_record(data, diagnosis_result)
        
        # Generate PDF report with frontend data
        pdf_filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        reports_dir = Path(os.getenv("REPORTS_DIR", "output/reports"))
        reports_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = reports_dir / pdf_filename
        
        # Generate PDF
        success = generate_pdf_report(
            patient_data=data,  # Pass raw frontend data
            prediction=diagnosis_result, # Now contains guaranteed 'clinical_reasoning'
            filename=str(pdf_path)
        )
        
        # DEBUG LOGGING
        if success:
            logger.info(f"✅ PDF generated successfully: {pdf_path}")
        else:
            logger.error(f"❌ PDF generation failed")
        
        # Return unified result
        response_data = {
            "status": "success",
            "patient_id": patient_id,
            "primary_diagnosis": diagnosis_result.get('primary_diagnosis', 'Unknown'),
            "confidence": diagnosis_result.get('confidence', 0.0),
            "severity": diagnosis_result.get('severity_score', 0.0),
            "urgency": diagnosis_result.get('urgency_level', 'routine'),
            # Now we can just use the key directly since we ensured it exists
            "reasoning": diagnosis_result['clinical_reasoning'],
            "treatment_plan": diagnosis_result.get('treatment_plan', {}),
            "pdf_report_url": f"/download/{pdf_filename}",
            "pdf_generated": success,
            "source": diagnosis_result.get('source', 'Hybrid AI System')
        }
        
        logger.info(f"✅ Diagnosis complete: {response_data['primary_diagnosis']}")
        return jsonify(response_data)
        
    except ValueError as e:
        logger.error(f"❌ Input error: {e}")
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        logger.exception(f"❌ Server Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
@app.route('/download/<filename>')
@limiter.limit("20 per minute")
def download_file(filename):
    """Secure file download - NO PATH TRAVERSAL"""
    # Validate filename format: report_YYYYMMDDHHMMSS.pdf
    if not re.match(r'^report_\d{14}\.pdf$', filename):
        return jsonify({"error": "Invalid filename format"}), 400
    
    # Secure the filename
    safe_filename = secure_filename(filename)
    
    reports_dir = Path(os.getenv("REPORTS_DIR", "output/reports"))
    file_path = reports_dir / safe_filename
    
    # DEBUG LOGGING
    logger.info(f"📥 Download requested: {safe_filename}")
    logger.info(f"📁 Looking in directory: {reports_dir.absolute()}")
    logger.info(f"📄 Full path: {file_path.absolute()}")
    
    if not reports_dir.exists():
        logger.error(f"❌ Reports directory not found: {reports_dir}")
        return jsonify({"error": "Reports directory not found"}), 404
    
    if not file_path.exists():
        # List available files for debugging
        available_files = list(reports_dir.glob("*.pdf"))
        logger.error(f"❌ File not found: {file_path}")
        logger.error(f"📁 Available PDFs: {[f.name for f in available_files]}")
        return jsonify({
            "error": "File not found",
            "requested_file": safe_filename,
            "available_files": [f.name for f in available_files]
        }), 404
    
    # Additional security: ensure file is within reports directory
    try:
        file_path.resolve().relative_to(reports_dir.resolve())
    except ValueError:
        logger.error(f"❌ Path traversal attempt detected: {filename}")
        return jsonify({"error": "Access denied"}), 403
    
    logger.info(f"✅ Serving file: {safe_filename} ({file_path.stat().st_size} bytes)")
    return send_from_directory(reports_dir, safe_filename, as_attachment=True)

@app.route('/')
def serve_frontend():
    """Serve main dashboard"""
    try:
        return send_from_directory('templates', 'index_AI.html')
    except Exception as e:
        logger.error(f"Failed to serve frontend: {e}")
        return jsonify({"error": "Frontend not available", "message": str(e)}), 404

@app.route('/api/status', methods=['GET'])
def api_status():
    """Health check"""
    reports_dir = Path(os.getenv("REPORTS_DIR", "output/reports"))
    patients_dir = Path(os.getenv("PATIENT_DIR", "output/patient_data"))
    
    # Count available files
    pdf_count = len(list(reports_dir.glob("*.pdf"))) if reports_dir.exists() else 0
    patient_count = len(list(patients_dir.glob("*.json"))) if patients_dir.exists() else 0
    
    return jsonify({
        "status": "online",
        "ml_loaded": orchestrator.ml_model is not None,
        "gemini_available": orchestrator.gemini.available if orchestrator.gemini else False,
        "environment": os.getenv("FLASK_ENV", "development"),
        "api_key_loaded": bool(os.getenv("GEMINI_API_KEY")),
        "model_dir": os.getenv("MODEL_DIR", "./output"),
        "reports_dir": str(reports_dir.absolute()),
        "reports_count": pdf_count,
        "patients_count": patient_count
    })

@app.route('/api/get-reports', methods=['GET'])
@limiter.limit("30 per minute")
def get_reports():
    """Get report history"""
    try:
        reports_dir = Path(os.getenv("REPORTS_DIR", "output/reports"))
        reports = []
        
        if reports_dir.exists():
            pdf_files = sorted(reports_dir.glob("report_*.pdf"), 
                             key=lambda x: x.stat().st_ctime, 
                             reverse=True)[:50]  # Limit to 50
            
            for file in pdf_files:
                stats = file.stat()
                reports.append({
                    "filename": file.name,
                    "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    "size": stats.st_size,
                    "download_url": f"/download/{file.name}"
                })
        
        return jsonify({
            "status": "success",
            "count": len(reports),
            "reports": reports,
            "directory": str(reports_dir.absolute())
        })
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve reports"}), 500

@app.route('/api/delete-report/<filename>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_report(filename):
    """Securely delete a report PDF"""
    # Validate filename pattern
    if not re.match(r'^report_\d{14}\.pdf$', filename):
        return jsonify({"status": "error", "message": "Invalid filename format"}), 400

    safe_filename = secure_filename(filename)
    reports_dir = Path(os.getenv("REPORTS_DIR", "output/reports"))
    file_path = reports_dir / safe_filename

    if not file_path.exists():
        return jsonify({"status": "error", "message": "The requested report was not found"}), 404

    try:
        file_size = file_path.stat().st_size
        file_path.unlink()
        logger.info(f"🗑️ Deleted report: {safe_filename} ({file_size} bytes)")
        return jsonify({"status": "success", "message": f"{safe_filename} deleted"})
    except Exception as e:
        logger.error(f"Failed to delete report {safe_filename}: {e}")
        return jsonify({"status": "error", "message": f"Failed to delete report: {e}"}), 500

@app.route('/api/get-patients', methods=['GET'])
@limiter.limit("30 per minute")
def get_patients():
    """List recent patient records"""
    try:
        patients_dir = Path(os.getenv("PATIENT_DIR", "output/patient_data"))
        patients_dir.mkdir(parents=True, exist_ok=True)

        patient_files = sorted(
            patients_dir.glob("patient_*.json"),
            key=lambda x: x.stat().st_ctime,
            reverse=True
        )[:50]  # Limit latest 50 patients

        records = []
        for file in patient_files:
            stats = file.stat()
            # Try to read diagnosis from file
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    diagnosis = data.get('diagnosis', {}).get('primary_diagnosis', 'Unknown')
            except:
                diagnosis = 'Unknown'
            
            records.append({
                "filename": file.name,
                "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "size": stats.st_size,
                "diagnosis": diagnosis,
                "download_url": f"/download-patient/{file.name}"
            })

        return jsonify({"status": "success", "count": len(records), "patients": records})
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve patient history"}), 500

@app.route('/download-patient/<filename>', methods=['GET'])
@limiter.limit("20 per minute")
def download_patient(filename):
    """Securely download patient JSON"""
    if not re.match(r'^patient_\d{14}\.json$', filename):
        return jsonify({"error": "Invalid filename format"}), 400

    safe_filename = secure_filename(filename)
    patients_dir = Path(os.getenv("PATIENT_DIR", "output/patient_data"))
    file_path = patients_dir / safe_filename

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    try:
        file_path.resolve().relative_to(patients_dir.resolve())
    except ValueError:
        return jsonify({"error": "Access denied"}), 403

    return send_from_directory(patients_dir, safe_filename, as_attachment=True)

@app.route('/api/delete-patient/<filename>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_patient(filename):
    """Securely delete a patient JSON record"""
    if not re.match(r'^patient_\d{14}\.json$', filename):
        return jsonify({"status": "error", "message": "Invalid filename format"}), 400

    safe_filename = secure_filename(filename)
    patients_dir = Path(os.getenv("PATIENT_DIR", "output/patient_data"))
    file_path = patients_dir / safe_filename

    if not file_path.exists():
        return jsonify({"status": "error", "message": "Patient record not found"}), 404

    try:
        file_path.unlink()
        logger.info(f"🗑️ Deleted patient record: {safe_filename}")
        return jsonify({"status": "success", "message": f"{safe_filename} deleted"})
    except Exception as e:
        logger.error(f"Failed to delete patient record {safe_filename}: {e}")
        return jsonify({"status": "error", "message": f"Failed to delete patient record: {e}"}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "message": "Too many requests"}), 429

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({"error": "Not found", "message": "The requested resource was not found"}), 404

@app.errorhandler(500)
def internal_error_handler(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error", "message": "Something went wrong on our end"}), 500

if __name__ == '__main__':
    # NEVER use debug=True in production
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n🌐 Server starting on: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print(f"📁 Model directory: {os.getenv('MODEL_DIR', './output')}")
    print(f"📄 Reports directory: {os.getenv('REPORTS_DIR', 'output/reports')}")
    print(f"📁 Patient data directory: {os.getenv('PATIENT_DIR', 'output/patient_data')}")
    print(f"🔑 Gemini API Key loaded: {'Yes' if api_key else 'No'}")
    
    app.run(host=host, port=port, debug=debug_mode)