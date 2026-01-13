"""
MEDICAL ORCHESTRATOR - HYBRID INTELLIGENCE (ML + GEN AI)
Merges Statistical ML Predictions with Generative AI Clinical Reasoning.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Import Configuration
try:
    from config import Config
    # Use Config paths if available
    BASE_DIR = Path(Config.BASE_DIR)
    OUTPUT_DIR = Config.MODEL_DIR 
except ImportError:
    # Fallback paths
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = BASE_DIR / "output"

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PatientFeatures:
    """Patient clinical features normalized for the orchestrator."""
    age: float
    temperature: Optional[float] = 37.0
    heart_rate: Optional[float] = 75.0
    systolic_bp: Optional[float] = 120.0
    diastolic_bp: Optional[float] = 80.0
    respiratory_rate: Optional[float] = 16.0
    oxygen_saturation: Optional[float] = 98.0
    pain_score: Optional[float] = 0.0
    symptoms: List[str] = field(default_factory=list)
    acuity: Optional[float] = 3.0
    gender: Optional[str] = "unknown"
    medical_history: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)

# ============================================================================
# HYBRID ORCHESTRATOR CLASS
# ============================================================================

class MedicalOrchestrator:
    """
    Orchestrates the synthesis of Machine Learning predictions and GenAI reasoning.
    """
    
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize the hybrid system.
        """
        # 1. Load the "Left Brain" (Analytical ML Model)
        self.ml_model = None
        self.feature_names = []
        self.disease_mapping = {}
        self._load_ml_artifacts()

        # 2. Load the "Right Brain" (Reasoning GenAI)
        self.gemini = None
        try:
            from gen_ai_module import MedicalGenAI
            # Priority: Param -> Config -> Env
            if not gemini_api_key and hasattr(Config, 'GEMINI_API_KEY'):
                gemini_api_key = Config.GEMINI_API_KEY
            
            if gemini_api_key:
                self.gemini = MedicalGenAI(api_key=gemini_api_key)
                logger.info(f"✅ GenAI (Right Brain) initialized: {self.gemini.available}")
            else:
                logger.warning("⚠️ GenAI Key missing. Running in ML-only mode.")
        except ImportError:
            logger.warning("❌ gen_ai_module.py not found.")
        
        logger.info("✅ MedicalOrchestrator Ready (Hybrid Mode)")

    def _load_ml_artifacts(self):
        """Load the trained Random Forest model and metadata."""
        try:
            model_path = OUTPUT_DIR / "disease_model_final.pkl"
            feature_path = OUTPUT_DIR / "feature_names_final.csv"
            mapping_path = OUTPUT_DIR / "disease_mapping.csv"

            if model_path.exists():
                self.ml_model = joblib.load(model_path)
                logger.info("✅ ML Model (Left Brain) loaded")
            else:
                logger.error("❌ ML Model missing. Please run ai_diagnosis.py")

            if feature_path.exists():
                self.feature_names = pd.read_csv(feature_path, header=None)[0].tolist()
            else:
                logger.error("❌ Feature names missing. Using defaults.")
                self.feature_names = []

            if mapping_path.exists():
                mapping_df = pd.read_csv(mapping_path)
                self.disease_mapping = dict(zip(mapping_df['class_id'], mapping_df['class_name']))
            
        except Exception as e:
            logger.error(f"❌ ML Artifact Load Error: {e}")

    def diagnose_patient(self, patient: PatientFeatures) -> Dict[str, Any]:
        """
        CORE LOGIC: The Synthesis Loop
        1. Run ML Model -> Get probabilities.
        2. Feed ML results + Patient Data -> GenAI.
        3. Merge into a comprehensive Final Diagnosis.
        """
        logger.info(f"🧠 Synthesizing diagnosis for patient (Age: {patient.age})")
        
        # --- Step 1: Analytical Diagnosis (ML) ---
        ml_result = self._run_ml_prediction(patient)
        
        # --- Step 2: Clinical Reasoning (GenAI) ---
        combined_result = ml_result.copy()
        
        if self.gemini and self.gemini.available:
            try:
                # Ask Gemini to validate the ML finding
                validation = self.gemini.enhance_diagnosis(ml_result, patient)
                
                combined_result['reasoning'] = validation.get('gemini_diagnostic_plan', 'Analysis provided by AI reasoning.')
                combined_result['differentials'] = validation.get('gemini_differentials', [])
                
                # --- INTELLIGENT OVERRIDE ---
                # If ML is unsure (low confidence) but Gemini has a strong opinion,
                # we can trust Gemini's top differential.
                ml_conf = ml_result.get('confidence', 0.0)
                ml_diag = ml_result.get('primary_diagnosis', 'Other')
                
                if (ml_diag == 'Other' or ml_conf < 0.55) and combined_result['differentials']:
                    top_diff = combined_result['differentials'][0]
                    # Only override if it's a specific disease
                    if top_diff not in ['Other', 'Unknown']:
                        logger.info(f"🔄 Hybrid Override: ML said '{ml_diag}' ({ml_conf:.2f}), upgrading to '{top_diff}'")
                        combined_result['primary_diagnosis'] = top_diff
                        combined_result['source'] = 'Gemini AI (Corrected ML)'
                    else:
                        combined_result['source'] = 'Hybrid (ML + Gemini)'
                else:
                    combined_result['source'] = 'Hybrid (ML + Gemini)'

            except Exception as e:
                logger.error(f"GenAI Synthesis failed: {e}")
                combined_result['note'] = "GenAI enhancement unavailable."
        else:
            combined_result['source'] = 'ML Only'

        # --- Step 3: Action Plan ---
        if self.gemini and self.gemini.available:
            treatment = self.gemini.generate_comprehensive_treatment(combined_result, patient)
            if treatment:
                combined_result['treatment_plan'] = treatment

        return combined_result

    def _run_ml_prediction(self, patient: PatientFeatures) -> Dict:
        """
        Execute the Machine Learning prediction logic.
        CRITICAL: Must match Feature Engineering in ai_diagnosis.py EXACTLY.
        """
        if not self.ml_model or not self.feature_names:
            return {"primary_diagnosis": "System Error: Model Missing", "confidence": 0.0}

        # 1. Initialize logic dictionary with raw values
        data = {
            'temperature': patient.temperature,
            'heartrate': patient.heart_rate,
            'resprate': patient.respiratory_rate,
            'sbp': patient.systolic_bp,
            'dbp': patient.diastolic_bp,
            'o2sat': patient.oxygen_saturation,
            'anchor_age': patient.age
        }

        # 2. Compute Flags (MUST Match ai_diagnosis.py logic)
        # ---------------------------------------------------
        # 'fever_high' > 38.5
        data['fever_high'] = 1.0 if patient.temperature > 38.5 else 0.0
        
        # 'tachycardia' > 100
        data['tachycardia'] = 1.0 if patient.heart_rate > 100 else 0.0
        
        # 'hypotension' < 90
        data['hypotension'] = 1.0 if patient.systolic_bp < 90 else 0.0
        
        # 'hypoxia' < 90
        data['hypoxia'] = 1.0 if patient.oxygen_saturation < 90 else 0.0
        # ---------------------------------------------------

        # 3. Build Vector (Strict Order)
        # We look up keys in 'data'. If a feature from training isn't here, use 0.0
        vector = []
        for feat in self.feature_names:
            vector.append(data.get(feat, 0.0))
        
        input_df = pd.DataFrame([vector], columns=self.feature_names)

        # 4. Predict
        try:
            probs = self.ml_model.predict_proba(input_df)[0]
            pred_idx = self.ml_model.predict(input_df)[0]
            
            primary_dx = self.disease_mapping.get(pred_idx, 'Unknown')
            confidence = float(probs[pred_idx])
            
            # Simple severity calculation
            severity_score = 0.2
            if data['hypoxia'] or data['hypotension']: severity_score = 0.9
            elif data['fever_high']: severity_score = 0.6

            return {
                "primary_diagnosis": primary_dx.title(),
                "confidence": confidence,
                "severity_score": severity_score,
                "clinical_findings": f"Automated analysis detected {primary_dx} pattern."
            }

        except Exception as e:
            logger.error(f"Prediction logic error: {e}")
            return {"primary_diagnosis": "Error", "confidence": 0.0}

# ============================================================================
# INTEGRATION TEST
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("HYBRID INTELLIGENCE SYSTEM TEST")
    print("="*60)
    
    orchestrator = MedicalOrchestrator()
    
    # Test Case: Septic Shock Pattern
    patient = PatientFeatures(
        age=65,
        temperature=39.5,   # High Fever
        heart_rate=115,     # Tachycardia
        respiratory_rate=28,
        oxygen_saturation=88, # Hypoxia
        systolic_bp=85,      # Hypotension
        symptoms=["high fever", "confusion"]
    )
    
    print(f"\nPatient: 65y Male, Temp 39.5°C, BP 85/60 (Critical)")
    
    diagnosis = orchestrator.diagnose_patient(patient)
    
    print(f"\n🔹 FINAL DIAGNOSIS: {diagnosis.get('primary_diagnosis')}")
    print(f"🔹 CONFIDENCE: {diagnosis.get('confidence'):.2%}")
    print(f"🔹 SOURCE: {diagnosis.get('source')}")