"""
MEDIPATIENT AI API - Enhanced with Gen AI Report Generation
Production-grade medical diagnosis system with automated clinical documentation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import sys
import os

import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Add current directory to Python path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize variables
GEN_AI_AVAILABLE = False
MedicalGenAI = None
MedicalContext = None

# Try to import Gen AI module - SIMPLIFIED AND FIXED VERSION
try:
    import importlib.util
    
    # Get the path to gen_ai_module.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(current_dir, "gen_ai_module.py")
    
    if os.path.exists(module_path):
        logger.info(f"✅ Found gen_ai_module.py")
        
        # Import the module
        spec = importlib.util.spec_from_file_location("gen_ai_module", module_path)
        if spec and spec.loader:
            gen_ai_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gen_ai_module)
            
            # Get the classes if they exist
            MedicalGenAI = getattr(gen_ai_module, 'MedicalGenAI', None)
            MedicalContext = getattr(gen_ai_module, 'MedicalContext', None)
            
            if MedicalGenAI and MedicalContext:
                GEN_AI_AVAILABLE = True
                logger.info("✅ Gen AI module classes loaded successfully")
            else:
                logger.warning("⚠️ Could not find MedicalGenAI or MedicalContext classes")
                GEN_AI_AVAILABLE = False
        else:
            GEN_AI_AVAILABLE = False
    else:
        logger.warning(f"⚠️ gen_ai_module.py not found at: {module_path}")
        GEN_AI_AVAILABLE = False
        
except ImportError as e:
    logger.warning(f"⚠️ Gen AI module import failed: {e}")
    GEN_AI_AVAILABLE = False
except Exception as e:
    logger.error(f"⚠️ Unexpected error loading gen_ai_module: {e}")
    GEN_AI_AVAILABLE = False


class RealMediPatientAPI:
    """
    Enhanced API class integrating ML diagnosis with Gen AI report generation.
    Maintains all existing functionality while adding automated documentation.
    """
    
    def __init__(self):
        """Initialize the API with ML model and optional Gen AI module."""
        self.base_path = Path(r"C:\Users\SETHULAKSHMI K B\PI2")
        self.output_path = self.base_path / "output"
        
        # Load ML model
        self.disease_model, self.feature_names, self.disease_mapping = self.load_real_model_only()
        
        if self.disease_model is None:
            raise RuntimeError("REAL MODEL REQUIRED: Please run training script first!")
        
        # Initialize Gen AI module
        self.gen_ai = self.initialize_gen_ai_module()
        
        logger.info("=" * 60)
        logger.info("MEDIPATIENT AI - ENHANCED API INITIALIZED")
        logger.info(f"Real Model: {type(self.disease_model).__name__}")
        logger.info(f"Features: {len(self.feature_names)}")
        logger.info(f"Gen AI Available: {'Yes' if self.gen_ai else 'No'}")
        logger.info("=" * 60)
    
    def load_real_model_only(self) -> Tuple[Any, List[str], Dict[int, str]]:
        """
        Load the trained ML model and associated metadata.
        
        Returns:
            Tuple containing (model, feature_names, disease_mapping)
        """
        logger.info("Loading trained ML model...")
        
        # Try to load complete package first
        package_path = self.output_path / "diagnosis_models_complete.pkl"
        if package_path.exists():
            logger.info(f"Loading from package: {package_path.name}")
            package = joblib.load(package_path)
            model = package.get('disease_model')
            feature_names = package.get('feature_names', [])
            disease_mapping = package.get('disease_mapping', {})
        else:
            # Load individual files
            model_path = self.output_path / "disease_model_final.pkl"
            if not model_path.exists():
                logger.error(f"Model file not found: {model_path}")
                logger.error("Please run: python AI_diagnosis.py")
                return None, [], {}
            
            logger.info(f"Loading model: {model_path.name}")
            model = joblib.load(model_path)
            
            # Load feature names
            feature_names = self.load_feature_names(model)
            
            # Load disease mapping
            disease_mapping = self.load_disease_mapping()
        
        logger.info(f"✅ ML model loaded: {type(model).__name__}")
        logger.info(f"✅ Feature count: {len(feature_names)}")
        logger.info(f"✅ Disease categories: {len(disease_mapping)}")
        
        return model, feature_names, disease_mapping
    
    def load_feature_names(self, model: Any) -> List[str]:
        """Load feature names from file or extract from model."""
        feature_path = self.output_path / "feature_names_final.csv"
        
        if feature_path.exists():
            feature_names = pd.read_csv(feature_path, header=None)[0].tolist()
            logger.info(f"Loaded {len(feature_names)} feature names from file")
        elif hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_.tolist()
            logger.info(f"Extracted {len(feature_names)} feature names from model")
        else:
            feature_names = ['temperature', 'heartrate', 'resprate', 'sbp', 'dbp', 
                           'o2sat', 'acuity', 'anchor_age']
            logger.warning("Using default feature names")
        
        return feature_names
    
    def load_disease_mapping(self) -> Dict[int, str]:
        """Load disease category mapping from file or use defaults."""
        mapping_path = self.output_path / "disease_mapping.csv"
        
        if mapping_path.exists():
            mapping_df = pd.read_csv(mapping_path)
            disease_mapping = dict(zip(mapping_df['class_id'], mapping_df['class_name']))
            logger.info(f"Loaded {len(disease_mapping)} disease mappings from file")
        else:
            disease_mapping = {
                0: 'cardiovascular',
                1: 'gastrointestinal', 
                2: 'infectious',
                3: 'injury',
                4: 'other',
                5: 'respiratory'
            }
            logger.warning("Using default disease mapping")
        
        return disease_mapping
    
    def initialize_gen_ai_module(self):
        """
        Initialize the Gen AI module for report generation.
        
        Returns:
            MedicalGenAI instance if available, None otherwise
        """
        if not GEN_AI_AVAILABLE:
            logger.warning("Gen AI module import failed - running in ML-only mode")
            return None
        
        try:
            # IMPORTANT: Make sure your gen_ai_module.py has proper Gemini setup
            api_key = "AIzaSyBdymO3le3SL3SN17IdWk0xqbV9dD3d_9U"  
            gen_ai = MedicalGenAI(api_key=api_key)
            logger.info("✅ Gen AI module initialized successfully")
            return gen_ai
        except Exception as e:
            logger.error(f"Failed to initialize Gen AI: {e}")
            return None
    
    def prepare_features_correctly(self, frontend_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare features for ML model prediction.
        
        Args:
            frontend_data: Raw data from frontend
            
        Returns:
            DataFrame with features in correct order for model
        """
        logger.info(f"Processing {len(frontend_data)} parameters from frontend")
        
        # Default values for clinical parameters
        defaults = {
            'temperature': 37.0,    # Normal body temperature
            'heartrate': 75.0,      # Normal heart rate
            'resprate': 16.0,       # Normal respiratory rate
            'sbp': 120.0,           # Normal systolic blood pressure
            'dbp': 80.0,            # Normal diastolic blood pressure
            'o2sat': 98.0,          # Normal oxygen saturation
            'acuity': 3.0,          # Default pain score
            'anchor_age': 45.0      # Default age
        }
        
        # Mapping between frontend field names and model feature names
        field_mapping = {
            'age': 'anchor_age',
            'temperature': 'temperature',
            'heartRate': 'heartrate',
            'respiratoryRate': 'resprate',
            'oxygenSaturation': 'o2sat',
            'systolicBP': 'sbp',
            'diastolicBP': 'dbp'
        }
        
        # Start with defaults
        features = defaults.copy()
        
        # Apply mapped values from frontend
        for frontend_key, model_key in field_mapping.items():
            if frontend_key in frontend_data:
                try:
                    value = float(frontend_data[frontend_key])
                    features[model_key] = value
                    logger.debug(f"Mapped {frontend_key} -> {model_key}: {value}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid value for {frontend_key}: {frontend_data[frontend_key]}")
        
        # Calculate acuity score from symptoms
        features['acuity'] = self.calculate_acuity_score(frontend_data, features)
        
        # Ensure exact feature order matches training
        ordered_features = []
        for feature in self.feature_names:
            if feature in features:
                ordered_features.append(features[feature])
            else:
                logger.warning(f"Missing feature: {feature}, using default")
                ordered_features.append(0.0)
        
        # Create DataFrame with correct column order
        features_df = pd.DataFrame([ordered_features], columns=self.feature_names)
        
        logger.info("✅ Features prepared for model prediction")
        return features_df
    
    def calculate_acuity_score(self, frontend_data: Dict[str, Any], 
                               features: Dict[str, float]) -> float:
        """
        Calculate pain/acuity score from symptoms and vital signs.
        
        Args:
            frontend_data: Raw frontend data
            features: Current feature values
            
        Returns:
            Acuity score between 1.0 and 10.0
        """
        acuity_score = 3.0  # Start with moderate baseline
        
        # Symptom severity weights
        symptom_weights = {
            'fever': 2.0,
            'chest_pain': 3.0,
            'shortness_of_breath': 2.5,
            'cough': 1.0,
            'headache': 1.5,
            'nausea': 1.0,
            'dizziness': 1.0,
            'fatigue': 0.5
        }
        
        # Add weights for present symptoms
        for symptom, weight in symptom_weights.items():
            if self.is_symptom_present(frontend_data, symptom):
                acuity_score += weight
        
        # Adjust for fever temperature
        if features.get('temperature', 37.0) > 38.5:
            acuity_score += 1.0
        
        # Clamp between 1-10
        return max(1.0, min(acuity_score, 10.0))
    
    def is_symptom_present(self, data: Dict[str, Any], symptom_key: str) -> bool:
        """Check if a symptom is present in the data."""
        if symptom_key not in data:
            return False
        
        value = data[symptom_key]
        return str(value).lower() in ['true', '1', 'yes', 'y']
    
    def make_real_prediction(self, features_df: pd.DataFrame, 
                            frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction using ML model and generate comprehensive results.
        
        Args:
            features_df: Prepared features DataFrame
            frontend_data: Original frontend data
            
        Returns:
            Dictionary containing diagnosis, severity, recommendations, and reports
        """
        logger.info("Making prediction with ML model")
        
        # Get probabilities from model
        probabilities = self.disease_model.predict_proba(features_df)[0]
        prediction_idx = self.disease_model.predict(features_df)[0]
        
        # Get disease information
        disease_key = self.disease_mapping.get(prediction_idx, 'other')
        disease_name = self.get_readable_disease_name(disease_key)
        primary_probability = float(probabilities[prediction_idx])
        
        # Calculate severity
        severity_score, severity_level = self.calculate_severity(features_df.iloc[0])
        
        # Generate clinical recommendations
        recommendations = self.generate_recommendations(disease_key, severity_level)
        
        # Extract symptoms list
        symptoms = self.extract_symptoms_list(frontend_data)
        
        # Generate Gen AI reports if available
        gen_ai_reports = {}
        if self.gen_ai:
            gen_ai_reports = self.generate_gen_ai_reports(
                features_df.iloc[0].to_dict(), 
                disease_name, 
                primary_probability,
                severity_score,
                severity_level,
                symptoms,
                frontend_data
            )
        
        # Compile final result
        result = {
            'success': True,
            'primary_diagnosis': disease_name,
            'disease_category': disease_key,
            'primary_probability': primary_probability,
            'confidence': self.get_confidence_level(primary_probability),
            'all_probabilities': self.format_probabilities(probabilities),
            'is_infectious': disease_key == 'infectious',
            'infectious_probability': float(probabilities[2]) if len(probabilities) > 2 else 0.0,
            'severity': severity_level,
            'severity_score': severity_score,
            'recommendations': recommendations,
            'features_used': self.feature_names,
            'features_with_data': len([f for f in features_df.iloc[0] if f != 0]),
            'model_type': 'REAL_TRAINED_MODEL',
            'symptoms_detected': symptoms,
            'gen_ai_available': self.gen_ai is not None,
            'gen_ai_reports': gen_ai_reports,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Prediction complete: {disease_name} (Confidence: {primary_probability:.1%})")
        logger.info(f"   Severity: {severity_level} | Gen AI Reports: {len(gen_ai_reports)}")
        
        return result
    
    def get_readable_disease_name(self, disease_key: str) -> str:
        """Convert disease key to human-readable name."""
        disease_names = {
            'cardiovascular': 'Cardiovascular Condition',
            'gastrointestinal': 'Gastrointestinal Issue',
            'infectious': 'Infectious Disease',
            'injury': 'Traumatic Injury',
            'other': 'Other Medical Condition',
            'respiratory': 'Respiratory Infection'
        }
        return disease_names.get(disease_key, 'Unknown Condition')
    
    def calculate_severity(self, features: pd.Series) -> Tuple[int, str]:
        """Calculate clinical severity score based on vital signs."""
        score = 0
        
        # Temperature scoring
        temp = features.get('temperature', 37.0)
        if temp >= 40.0:
            score += 4
        elif temp >= 39.0:
            score += 3
        elif temp >= 38.5:
            score += 2
        elif temp >= 38.0:
            score += 1
        
        # Heart rate scoring
        hr = features.get('heartrate', 75.0)
        if hr >= 140:
            score += 4
        elif hr >= 120:
            score += 3
        elif hr >= 100:
            score += 2
        
        # Oxygen saturation scoring
        o2 = features.get('o2sat', 98.0)
        if o2 <= 88:
            score += 4
        elif o2 <= 92:
            score += 3
        elif o2 <= 94:
            score += 2
        elif o2 < 96:
            score += 1
        
        # Blood pressure scoring
        sbp = features.get('sbp', 120.0)
        if sbp >= 180:
            score += 3
        elif sbp >= 160:
            score += 2
        elif sbp >= 140:
            score += 1
        
        # Age factor
        age = features.get('anchor_age', 45.0)
        if age >= 70:
            score += 2
        elif age >= 60:
            score += 1
        
        # Acuity (symptom severity)
        acuity = features.get('acuity', 3.0)
        if acuity >= 9:
            score += 3
        elif acuity >= 7:
            score += 2
        elif acuity >= 5:
            score += 1
        
        # Determine severity level
        if score >= 10:
            level = "critical"
        elif score >= 7:
            level = "severe"
        elif score >= 5:
            level = "moderate"
        elif score >= 3:
            level = "mild"
        else:
            level = "normal"
        
        return min(score, 12), level
    
    def generate_recommendations(self, disease: str, severity: str) -> List[str]:
        """Generate clinical recommendations based on diagnosis and severity."""
        recommendations = []
        
        # Urgency based on severity
        if severity == "critical":
            recommendations.append("IMMEDIATE EMERGENCY RESPONSE REQUIRED")
            recommendations.append("Call emergency services immediately")
            recommendations.append("Prepare for immediate ICU admission")
        elif severity == "severe":
            recommendations.append("URGENT MEDICAL ATTENTION NEEDED")
            recommendations.append("Emergency department evaluation within 30 minutes")
            recommendations.append("Continuous vital sign monitoring")
        elif severity == "moderate":
            recommendations.append("MEDICAL EVALUATION RECOMMENDED")
            recommendations.append("Urgent care or ED visit within 2-4 hours")
            recommendations.append("Monitor symptoms closely")
        else:
            recommendations.append("ROUTINE MEDICAL CARE")
            recommendations.append("Schedule appointment within 24-48 hours")
        
        # Disease-specific recommendations
        if disease == 'infectious':
            recommendations.append("INFECTIOUS DISEASE MANAGEMENT")
            recommendations.append("Consider empirical antibiotics based on guidelines")
            recommendations.append("Infection control precautions")
            recommendations.append("Monitor for sepsis criteria")
        
        elif disease == 'respiratory':
            recommendations.append("RESPIRATORY SUPPORT")
            recommendations.append("Chest X-ray to evaluate for pneumonia")
            recommendations.append("Continuous pulse oximetry monitoring")
            recommendations.append("Consider respiratory therapy consult")
        
        elif disease == 'cardiovascular':
            recommendations.append("CARDIAC WORKUP")
            recommendations.append("12-lead ECG immediately")
            recommendations.append("Cardiac enzymes if indicated")
            recommendations.append("Cardiology consultation")
        
        elif disease == 'injury':
            recommendations.append("TRAUMA ASSESSMENT")
            recommendations.append("Complete trauma survey")
            recommendations.append("Imaging as indicated")
            recommendations.append("Pain management protocol")
        
        # Always include standard assessments
        recommendations.append("STANDARD ASSESSMENT")
        recommendations.append("Complete history and physical examination")
        recommendations.append("Review medications and allergies")
        recommendations.append("Document clinical decision-making")
        
        return recommendations
    
    def extract_symptoms_list(self, frontend_data: Dict[str, Any]) -> List[str]:
        """Extract list of symptoms from frontend data."""
        symptom_fields = ['fever', 'cough', 'chest_pain', 'shortness_of_breath', 
                         'headache', 'nausea', 'dizziness', 'fatigue']
        
        symptoms = []
        for symptom in symptom_fields:
            if self.is_symptom_present(frontend_data, symptom):
                symptoms.append(symptom.replace('_', ' ').title())
        
        return symptoms
    
    def generate_gen_ai_reports(self, features: Dict[str, float], 
                               diagnosis: str, 
                               confidence: float,
                               severity_score: int,
                               severity_level: str,
                               symptoms: List[str],
                               frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive medical reports using Gen AI module.
        
        Args:
            features: Feature values dictionary
            diagnosis: Primary diagnosis
            confidence: Confidence score
            severity_score: Numerical severity score
            severity_level: Text severity level
            symptoms: List of symptoms
            frontend_data: Original frontend data
            
        Returns:
            Dictionary containing generated reports
        """
        if not self.gen_ai:
            return {"available": False, "message": "Gen AI module not available"}
        
        try:
            logger.info("Generating medical reports with Gen AI...")
            
            # Create patient features object for Gen AI
            class PatientFeatures:
                def __init__(self, features_dict, symptoms_list):
                    self.age = features_dict.get('anchor_age', 45.0)
                    self.temperature = features_dict.get('temperature')
                    self.heart_rate = features_dict.get('heartrate')
                    self.systolic_bp = features_dict.get('sbp')
                    self.diastolic_bp = features_dict.get('dbp')
                    self.respiratory_rate = features_dict.get('resprate')
                    self.oxygen_saturation = features_dict.get('o2sat')
                    self.pain_score = features_dict.get('acuity', 3.0)
                    self.symptoms = symptoms_list
            
            # Create diagnosis result object for Gen AI
            class DiagnosisResult:
                def __init__(self, diagnosis, confidence, severity_score, severity_level):
                    self.primary_diagnosis = diagnosis
                    self.confidence = confidence
                    self.differential_diagnoses = []
                    self.clinical_findings = f"Severity: {severity_level}"
                    self.severity_score = severity_score / 12.0
                    self.urgency_level = severity_level.upper()
                    self.recommended_tests = []
                    self.treatment_suggestions = []
                    self.risk_factors = []
            
            # Create objects
            patient_features = PatientFeatures(features, symptoms)
            diagnosis_result = DiagnosisResult(diagnosis, confidence, severity_score, severity_level)
            
            # Create medical context - use the imported MedicalContext class if available
            if MedicalContext:
                medical_context = MedicalContext(
                    patient_data=patient_features,
                    diagnosis_result=diagnosis_result,
                    medical_history=self.extract_medical_history(frontend_data),
                    medications=self.extract_medications(frontend_data),
                    allergies=self.extract_allergies(frontend_data),
                    lab_results=self.extract_lab_results(frontend_data)
                )
            else:
                # Fallback if MedicalContext class is not available
                medical_context = None
            
            # Generate reports
            reports = {}
            if medical_context:
                reports = {
                    "clinical_notes": self.gen_ai.generate_clinical_notes(medical_context, diagnosis_result),
                    "differential_diagnosis": self.gen_ai.generate_differential_diagnosis(medical_context),
                    "treatment_plan": self.gen_ai.generate_treatment_plan(diagnosis, medical_context),
                    "patient_explanation": self.gen_ai.explain_to_patient(diagnosis, medical_context)
                }
            
            logger.info(f"✅ Generated {len(reports)} medical reports")
            return {"available": True, "reports": reports}
            
        except Exception as e:
            logger.error(f"Error generating Gen AI reports: {e}")
            return {"available": False, "error": str(e)}
    
    def extract_medical_history(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract medical history from frontend data."""
        # This can be expanded based on your frontend form
        return {
            'comorbidities': [],
            'surgeries': [],
            'previous_diagnoses': []
        }
    
    def extract_medications(self, frontend_data: Dict[str, Any]) -> List[str]:
        """Extract medications from frontend data."""
        # This can be expanded based on your frontend form
        return []
    
    def extract_allergies(self, frontend_data: Dict[str, Any]) -> List[str]:
        """Extract allergies from frontend data."""
        # This can be expanded based on your frontend form
        return []
    
    def extract_lab_results(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lab results from frontend data."""
        # This can be expanded based on your frontend form
        return {}
    
    def get_confidence_level(self, probability: float) -> str:
        """Determine confidence level based on probability."""
        if probability > 0.7:
            return "high"
        elif probability > 0.4:
            return "medium"
        else:
            return "low"
    
    def format_probabilities(self, probabilities: np.ndarray) -> List[Dict[str, Any]]:
        """Format probabilities for frontend display."""
        formatted = []
        for idx, prob in enumerate(probabilities):
            if idx < len(self.disease_mapping):
                disease_key = self.disease_mapping.get(idx, f'Class {idx}')
                disease_name = self.get_readable_disease_name(disease_key)
                formatted.append({
                    'disease': disease_name,
                    'probability': float(prob)
                })
        
        # Sort by probability descending
        formatted.sort(key=lambda x: x['probability'], reverse=True)
        return formatted


# Initialize API
try:
    api = RealMediPatientAPI()
    logger.info("✅ REAL API WITH GEN AI INITIALIZED SUCCESSFULLY")
except Exception as e:
    logger.error(f"❌ API INITIALIZATION FAILED: {e}")
    logger.error("Please run: python AI_diagnosis.py")
    api = None


# API Routes
@app.route('/')
def index():
    """Serve main frontend interface."""
    return render_template('index_AI.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint with Gen AI report generation.
    
    Returns comprehensive diagnosis including:
    - ML model prediction
    - Clinical recommendations
    - Gen AI generated reports (if available)
    """
    if api is None:
        return jsonify({
            'success': False,
            'error': 'API not initialized. Please run training script first.'
        }), 500
    
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No patient data provided'
            }), 400
        
        logger.info(f"📡 Received prediction request with {len(data)} parameters")
        
        # Prepare features for ML model
        features_df = api.prepare_features_correctly(data)
        
        # Make prediction with Gen AI reports
        result = api.make_real_prediction(features_df, data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500


@app.route('/api/status')
def status():
    """API status endpoint showing model and Gen AI availability."""
    if api is None:
        return jsonify({
            'status': 'error',
            'message': 'API not initialized'
        }), 500
    
    return jsonify({
        'status': 'online',
        'model_loaded': api.disease_model is not None,
        'gen_ai_available': api.gen_ai is not None,
        'feature_count': len(api.feature_names),
        'disease_categories': list(api.disease_mapping.values()),
        'api_version': '5.0-with-gen-ai',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/test/real')
def test_real():
    """Test endpoint with sample patient data."""
    test_cases = [
        {
            'name': 'Respiratory Infection Case',
            'data': {
                'age': 35,
                'temperature': 39.2,
                'heartRate': 110,
                'respiratoryRate': 24,
                'oxygenSaturation': 94,
                'systolicBP': 115,
                'diastolicBP': 78,
                'fever': 1,
                'cough': 1,
                'fatigue': 1
            }
        },
        {
            'name': 'Cardiovascular Case',
            'data': {
                'age': 65,
                'temperature': 37.8,
                'heartRate': 95,
                'respiratoryRate': 18,
                'oxygenSaturation': 97,
                'systolicBP': 155,
                'diastolicBP': 92,
                'chest_pain': 1,
                'dizziness': 1
            }
        }
    ]
    
    results = []
    for case in test_cases:
        features_df = api.prepare_features_correctly(case['data'])
        result = api.make_real_prediction(features_df, case['data'])
        result['test_case'] = case['name']
        results.append(result)
    
    return jsonify({
        'success': True,
        'test_cases': results,
        'note': 'These are REAL predictions with Gen AI report generation'
    })


@app.route('/api/model/info')
def model_info():
    """Detailed model information endpoint."""
    if api is None:
        return jsonify({
            'success': False,
            'error': 'API not initialized'
        }), 500
    
    return jsonify({
        'success': True,
        'model': {
            'type': str(type(api.disease_model).__name__),
            'n_features_in': getattr(api.disease_model, 'n_features_in_', len(api.feature_names)),
            'n_classes': len(api.disease_mapping)
        },
        'features': api.feature_names,
        'disease_categories': [
            {
                'key': key,
                'name': api.get_readable_disease_name(key)
            }
            for key in api.disease_mapping.values()
        ]
    })


if __name__ == '__main__':
    print("=" * 60)
    print("STARTING MEDIPATIENT AI - ENHANCED WITH GEN AI")
    print("=" * 60)
    print("Frontend: http://localhost:5000")
    if api:
        print(f"Features: {api.feature_names}")
        print(f"Categories: {list(api.disease_mapping.values())}")
        print(f"Gen AI: {'Available' if api.gen_ai else 'Not available'}")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)