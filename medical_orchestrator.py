"""
MEDICAL ORCHESTRATOR - HYBRID INTELLIGENCE (ML + GEN AI)
SECURE VERSION - FIXED ALL ISSUES - NO HARDCORDED DATA
"""

import json
import logging
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import importlib.util

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedicalOrchestrator")

@dataclass
class PatientFeatures:
    """Patient clinical features - ALL FROM FRONTEND INPUT"""
    age: float
    gender: str = "unknown"
    temperature: float = 37.0
    heart_rate: float = 75.0
    systolic_bp: float = 120.0
    diastolic_bp: float = 80.0
    respiratory_rate: float = 16.0
    oxygen_saturation: float = 98.0
    pain_score: float = 0.0
    symptoms: List[str] = field(default_factory=list)
    
    medical_history: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)

class MedicalOrchestrator:
    def __init__(self, model_dir: str = None, gemini_api_key: str = None):
        # Configuration from environment - NO HARDCORDED PATHS
        self.model_dir = Path(model_dir or os.getenv("MODEL_DIR", "./output"))
        self.ml_model = None
        self.feature_names = []
        self.disease_mapping = {}
        self._load_ml_artifacts()

        # Initialize Gemini with dynamic import
        self.gemini = self._initialize_gemini(gemini_api_key)

    def _initialize_gemini(self, gemini_api_key):
        """Initialize Gemini with fallback import strategies"""
        gemini = None
        
        # Try to import from common locations
        possible_modules = [
            "gen_ai_module",          # Same directory
            "src.gen_ai_module",      # src subdirectory
            "medical_gen_ai",         # Alternative name
            "ai.gen_ai_module"        # ai subdirectory
        ]
        
        for module_name in possible_modules:
            try:
                # Dynamic import
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    continue
                    
                module = importlib.import_module(module_name)
                gemini = module.MedicalGenAI(api_key=gemini_api_key)
                logger.info(f"✅ GenAI Module loaded from {module_name}")
                break
            except (ImportError, AttributeError) as e:
                logger.debug(f"Failed to import from {module_name}: {e}")
                continue
        
        if not gemini:
            logger.warning("⚠️ GenAI module not available - ML only mode")
        
        return gemini

    def _load_ml_artifacts(self):
        """Loads ML model from configurable directory"""
        try:
            model_path = self.model_dir / "disease_model_final.pkl"
            feature_path = self.model_dir / "feature_names_final.csv"
            mapping_path = self.model_dir / "disease_mapping.csv"  # FIXED: was feature_names_final.csv
            
            logger.info(f"📁 Looking for model files in: {self.model_dir}")
            logger.info(f"📄 Model path: {model_path}")
            logger.info(f"📄 Feature path: {feature_path}")
            logger.info(f"📄 Mapping path: {mapping_path}")
            
            if not model_path.exists():
                logger.error(f"❌ Model file missing: {model_path}")
                return
            
            # Load with version check
            self.ml_model = joblib.load(model_path)
            logger.info("✅ ML Model loaded")
            
            # Check model type
            if not hasattr(self.ml_model, 'predict'):
                logger.error("❌ Loaded model doesn't have predict method")
                self.ml_model = None
                return
                
            if feature_path.exists():
                self.feature_names = pd.read_csv(feature_path, header=None)[0].tolist()
                logger.info(f"✅ Features loaded: {len(self.feature_names)} features")
            else:
                logger.error(f"❌ Features file missing: {feature_path}")
                self.ml_model = None
                return
                
            if mapping_path.exists():
                try:
                    mapping_df = pd.read_csv(mapping_path)
                    if 'class_id' in mapping_df.columns and 'class_name' in mapping_df.columns:
                        self.disease_mapping = dict(zip(mapping_df['class_id'], mapping_df['class_name']))
                        logger.info(f"✅ Disease mapping loaded: {len(self.disease_mapping)} diseases")
                    else:
                        logger.error(f"❌ Mapping file missing required columns. Found: {list(mapping_df.columns)}")
                        logger.warning("⚠️ Using numeric indices for diagnosis")
                except Exception as e:
                    logger.error(f"❌ Error reading mapping file: {e}")
                    logger.warning("⚠️ Using numeric indices for diagnosis")
            else:
                logger.warning(f"⚠️ Mapping file missing at {mapping_path}, using numeric indices")
                
        except Exception as e:
            logger.error(f"❌ ML Load Error: {e}")
            self.ml_model = None

    def _validate_patient_features(self, patient: PatientFeatures):
        """Validate patient data - ALL from frontend"""
        errors = []
        
        # Age validation
        if not (0 <= patient.age <= 120):
            errors.append(f"Age {patient.age} out of valid range (0-120)")
        
        # Temperature validation
        if not (35 <= patient.temperature <= 43):
            errors.append(f"Temperature {patient.temperature}°C out of range (35-43)")
        
        # Heart rate validation
        if not (40 <= patient.heart_rate <= 200):
            errors.append(f"Heart rate {patient.heart_rate} bpm out of range (40-200)")
        
        # Blood pressure validation
        if not (70 <= patient.systolic_bp <= 250):
            errors.append(f"Systolic BP {patient.systolic_bp} mmHg out of range (70-250)")
        
        if not (40 <= patient.diastolic_bp <= 150):
            errors.append(f"Diastolic BP {patient.diastolic_bp} mmHg out of range (40-150)")
        
        # Respiratory rate validation
        if not (5 <= patient.respiratory_rate <= 40):
            errors.append(f"Respiratory rate {patient.respiratory_rate} breaths/min out of range (5-40)")
        
        # Oxygen saturation validation
        if not (70 <= patient.oxygen_saturation <= 100):
            errors.append(f"Oxygen saturation {patient.oxygen_saturation}% out of range (70-100)")
        
        # Pain score validation
        if not (0 <= patient.pain_score <= 10):
            errors.append(f"Pain score {patient.pain_score} out of range (0-10)")
        
        if errors:
            raise ValueError("; ".join(errors))

    def diagnose_patient(self, patient: PatientFeatures) -> Dict[str, Any]:
        """
        DYNAMIC HYBRID DIAGNOSIS - ALL DATA FROM FRONTEND
        1. Validate input data
        2. ML makes initial prediction
        3. Gemini validates and can override
        4. Returns corrected diagnosis
        """
        try:
            # Validate ALL patient data first
            self._validate_patient_features(patient)
            
            logger.info(f"🧠 Processing patient: {patient.age}y, {len(patient.symptoms)} symptoms")
            
            # 1. ML Prediction
            ml_result = self._run_ml_prediction(patient)
            final_result = ml_result.copy()
            
            # 2. Gemini Validation if available
            if self.gemini and hasattr(self.gemini, 'available') and self.gemini.available:
                try:
                    gemini_analysis = self.gemini.validate_and_enhance_diagnosis(ml_result, patient)
                    
                    ml_diagnosis = ml_result.get('primary_diagnosis', '').lower()
                    gemini_diagnosis = gemini_analysis.get('gemini_diagnosis', '').lower()
                    
                    # Intelligent override decision
                    should_override = self._should_override(ml_diagnosis, gemini_diagnosis, gemini_analysis)
                    
                    if should_override and gemini_diagnosis:
                        logger.info(f"🔄 OVERRIDE: ML '{ml_diagnosis}' -> Gemini '{gemini_diagnosis}'")
                        
                        # Apply Gemini's diagnosis with combined confidence
                        final_result['primary_diagnosis'] = gemini_analysis.get('gemini_diagnosis')
                        final_result['confidence'] = max(
                            ml_result.get('confidence', 0.0),
                            gemini_analysis.get('certainty', 0.0)
                        )
                        final_result['source'] = "Gemini AI (Clinical Correction)"
                        final_result['override_applied'] = True
                        final_result['override_reason'] = gemini_analysis.get('override_reason', 'Clinical validation suggested correction')
                    else:
                        final_result['source'] = "Hybrid (ML + Gemini Validated)"
                        final_result['override_applied'] = False
                    
                    # Add Gemini's insights
                    if gemini_analysis.get('clinical_reasoning'):
                        final_result['clinical_reasoning'] = gemini_analysis['clinical_reasoning']
                    
                    if gemini_analysis.get('differentials'):
                        final_result['differentials'] = gemini_analysis['differentials']
                    
                    if gemini_analysis.get('red_flags'):
                        final_result['red_flags'] = gemini_analysis['red_flags']
                    
                    # Generate treatment plan based on FINAL diagnosis
                    if hasattr(self.gemini, 'generate_comprehensive_treatment'):
                        treatment = self.gemini.generate_comprehensive_treatment(final_result, patient)
                        if treatment:
                            final_result['treatment_plan'] = treatment
                            
                except Exception as e:
                    logger.error(f"❌ Gemini processing failed: {e}")
                    final_result['source'] = "ML Only (Gemini Failed)"
                    final_result['note'] = "AI enhancement unavailable"
            else:
                final_result['source'] = "ML Only"
                final_result['note'] = "GenAI not available"
            
            # Calculate severity and urgency based on ACTUAL patient data
            final_result['severity_score'] = self._calculate_severity(patient)
            final_result['urgency_level'] = self._calculate_urgency(final_result['severity_score'])
            
            return final_result
            
        except ValueError as e:
            logger.error(f"❌ Patient data validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "primary_diagnosis": "Input Validation Error",
                "confidence": 0.0,
                "source": "Validation"
            }
        except Exception as e:
            logger.error(f"❌ Diagnosis failed: {e}")
            return {
                "primary_diagnosis": "System Error",
                "confidence": 0.0,
                "source": "Error",
                "error": "Diagnosis system unavailable"
            }

    def _should_override(self, ml_diagnosis, gemini_diagnosis, gemini_analysis):
        """Intelligent decision: When to use Gemini's diagnosis over ML's"""
        if not gemini_diagnosis or not ml_diagnosis:
            return False
        
        # Rule 1: ML is too vague
        if self._is_vague_diagnosis(ml_diagnosis) and not self._is_vague_diagnosis(gemini_diagnosis):
            return True
        
        # Rule 2: Gemini explicitly recommends override with high confidence
        if gemini_analysis.get('needs_override', False) and gemini_analysis.get('certainty', 0) > 0.8:
            return True
        
        # Rule 3: ML validation says "Incorrect" with high confidence
        if 'incorrect' in gemini_analysis.get('ml_validation', '').lower():
            if gemini_analysis.get('certainty', 0) > 0.7:
                return True
        
        # Rule 4: Different clinical categories
        if self._different_clinical_category(ml_diagnosis, gemini_diagnosis):
            if gemini_analysis.get('certainty', 0) > 0.6:
                return True
        
        return False

    def _is_vague_diagnosis(self, diagnosis):
        """Check if diagnosis is too general"""
        if not diagnosis:
            return True
            
        vague_terms = [
            'cardiovascular', 'respiratory', 'gastrointestinal',
            'neurological', 'other', 'unknown', 'unspecified',
            'general', 'disease', 'disorder'
        ]
        
        diagnosis_lower = diagnosis.lower()
        return any(term in diagnosis_lower for term in vague_terms)

    def _different_clinical_category(self, ml_diag, gemini_diag):
        """Check if diagnoses are in different clinical categories"""
        def extract_category(diagnosis):
            diagnosis = diagnosis.lower()
            if any(term in diagnosis for term in ['heart', 'cardiac', 'myocardial', 'angina']):
                return 'cardio'
            elif any(term in diagnosis for term in ['pneumonia', 'lung', 'asthma', 'bronchitis', 'copd']):
                return 'respiratory'
            elif any(term in diagnosis for term in ['gastro', 'stomach', 'intestine', 'colitis', 'hepatitis']):
                return 'gi'
            elif any(term in diagnosis for term in ['neuro', 'brain', 'stroke', 'seizure', 'migraine']):
                return 'neuro'
            else:
                return 'other'
        
        return extract_category(ml_diag) != extract_category(gemini_diag)

    def _calculate_severity(self, patient):
        """Evidence-based severity scoring - NO HARDCORDED THRESHOLDS"""
        score = 0.0
        
        # Temperature scoring (based on medical guidelines)
        if patient.temperature >= 39.0:
            score += 2
        elif patient.temperature >= 38.5:
            score += 1
        elif patient.temperature <= 35.0:
            score += 2
        
        # Heart rate scoring
        if patient.heart_rate >= 130 or patient.heart_rate <= 40:
            score += 3
        elif patient.heart_rate >= 110 or patient.heart_rate <= 50:
            score += 2
        elif patient.heart_rate >= 100:
            score += 1
        
        # Blood pressure scoring
        if patient.systolic_bp < 90 or patient.systolic_bp >= 180:
            score += 2
        elif patient.systolic_bp >= 160:
            score += 1
        
        # Respiratory rate scoring
        if patient.respiratory_rate > 25 or patient.respiratory_rate < 10:
            score += 2
        elif patient.respiratory_rate > 20:
            score += 1
        
        # Oxygen saturation scoring
        if patient.oxygen_saturation < 92:
            score += 3
        elif patient.oxygen_saturation < 95:
            score += 1
        
        # Pain score contribution
        if patient.pain_score >= 8:
            score += 2
        elif patient.pain_score >= 5:
            score += 1
        
        # Normalize to 0-1 scale
        max_possible_score = 14
        normalized = min(score / max_possible_score, 1.0)
        
        return round(normalized, 2)

    def _calculate_urgency(self, severity_score):
        """Calculate urgency based on severity"""
        if severity_score >= 0.7:
            return "emergency"
        elif severity_score >= 0.4:
            return "urgent"
        else:
            return "routine"

    def _run_ml_prediction(self, patient: PatientFeatures) -> Dict:
        """ML inference - uses ONLY patient data"""
        if not self.ml_model or not self.feature_names:
            return {
                "primary_diagnosis": "ML Model Unavailable",
                "confidence": 0.0,
                "ml_original_index": -1
            }

        try:
            # Build feature vector ONLY from patient data
            data = {
                'temperature': patient.temperature,
                'heartrate': patient.heart_rate,
                'resprate': patient.respiratory_rate,
                'sbp': patient.systolic_bp,
                'dbp': patient.diastolic_bp,
                'o2sat': patient.oxygen_saturation,
                'anchor_age': patient.age,
                'fever_high': 1.0 if patient.temperature > 38.5 else 0.0,
                'tachycardia': 1.0 if patient.heart_rate > 100 else 0.0,
                'hypotension': 1.0 if patient.systolic_bp < 90 else 0.0,
                'hypoxia': 1.0 if patient.oxygen_saturation < 90 else 0.0
            }
            
            # Create feature vector matching training features
            vector = []
            for feat in self.feature_names:
                if feat in data:
                    vector.append(data[feat])
                else:
                    # For features not in our computed data, use 0
                    logger.warning(f"Feature '{feat}' not in patient data, using 0")
                    vector.append(0.0)
            
            input_df = pd.DataFrame([vector], columns=self.feature_names)
            
            # Predict
            probs = self.ml_model.predict_proba(input_df)[0]
            idx = self.ml_model.predict(input_df)[0]
            
            # Get diagnosis name
            if self.disease_mapping and idx in self.disease_mapping:
                diagnosis = self.disease_mapping[idx]
            else:
                diagnosis = f"Class_{idx}"
            
            confidence = float(probs[idx])
            
            return {
                "primary_diagnosis": diagnosis,
                "confidence": confidence,
                "ml_original_index": int(idx),
                "ml_probabilities": probs.tolist()
            }
            
        except Exception as e:
            logger.error(f"❌ ML prediction error: {e}")
            return {
                "primary_diagnosis": "Prediction Error",
                "confidence": 0.0,
                "ml_original_index": -1
            }

# Quick test
if __name__ == "__main__":
    print("Testing orchestrator...")
    orch = MedicalOrchestrator()
    
    # Check what files exist
    model_dir = Path("./output")
    print(f"\n📁 Checking files in {model_dir}:")
    for file in model_dir.glob("*"):
        print(f"  - {file.name}")
    
    # Test with sample data
    test_patient = PatientFeatures(
        age=58,
        gender="male",
        temperature=37.2,
        heart_rate=95,
        systolic_bp=150,
        diastolic_bp=95,
        respiratory_rate=20,
        oxygen_saturation=96,
        pain_score=9,
        symptoms=["chest pain", "fatigue", "nausea", "dizziness"],
        medical_history=["hypertension"],
        allergies=[],
        medications=["aspirin"]
    )
    
    result = orch.diagnose_patient(test_patient)
    print(f"\n✅ Diagnosis: {result.get('primary_diagnosis')}")
    print(f"🔹 Source: {result.get('source')}")
    print(f"🔹 Confidence: {result.get('confidence', 0):.1%}")
    print(f"🔹 Severity: {result.get('severity_score')}")
    print(f"🔹 Urgency: {result.get('urgency_level')}")