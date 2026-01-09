"""
Diagnosis Engine for clinical prediction from tabular patient data.
Handles feature engineering, model inference, and result interpretation.
"""
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PatientFeatures:
    """Structured patient feature container."""
    age: float
    temperature: float
    heart_rate: float
    systolic_bp: float
    diastolic_bp: float
    respiratory_rate: float
    oxygen_saturation: float
    pain_score: Optional[float] = None
    acuity_score: Optional[float] = None
    symptoms: Optional[List[str]] = None
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert patient features to DataFrame for model prediction."""
        data = {
            'age': [self.age],
            'temperature': [self.temperature],
            'heart_rate': [self.heart_rate],
            'systolic_bp': [self.systolic_bp],
            'diastolic_bp': [self.diastolic_bp],
            'respiratory_rate': [self.respiratory_rate],
            'oxygen_saturation': [self.oxygen_saturation],
        }
        
        # Add optional features if present
        if self.pain_score is not None:
            data['pain_score'] = [self.pain_score]
        if self.acuity_score is not None:
            data['acuity_score'] = [self.acuity_score]
            
        return pd.DataFrame(data)

@dataclass
class DiagnosisResult:
    """Structured diagnosis result container."""
    primary_diagnosis: str
    confidence: float
    differential_diagnoses: List[Dict[str, float]]
    clinical_findings: Dict[str, str]
    severity_score: float
    urgency_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_tests: List[str]
    treatment_suggestions: List[str]
    risk_factors: List[str]

class DiagnosisEngine:
    """Main engine for clinical diagnosis predictions."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize diagnosis engine with trained model.
        
        Args:
            model_path: Path to saved model. Uses config default if None.
        """
        self.model_path = model_path or Config.TABULAR_MODEL_PATH
        self.label_encoder_path = Config.LABEL_ENCODER_PATH
        
        # Initialize components
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.feature_names = None
        
        self._load_components()
        self._validate_model()
    
    def _load_components(self):
        """Load trained model and associated components."""
        try:
            # Load model
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                logger.info(f"Loaded model with {len(self.feature_names)} features")
            
            # Load label encoder
            with open(self.label_encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
                logger.info(f"Loaded label encoder with {len(self.label_encoder.classes_)} classes")
                
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading model components: {e}")
            raise
    
    def _validate_model(self):
        """Validate loaded model components."""
        if self.model is None:
            raise ValueError("Model not loaded")
        if self.label_encoder is None:
            raise ValueError("Label encoder not loaded")
        if self.scaler is None:
            raise ValueError("Scaler not loaded")
        
        logger.info("Model validation passed")
    
    def preprocess_features(self, patient_features: PatientFeatures) -> np.ndarray:
        """
        Preprocess patient features for model prediction.
        
        Args:
            patient_features: PatientFeatures object containing clinical data
            
        Returns:
            Processed feature array ready for model prediction
        """
        # Convert to DataFrame
        df = patient_features.to_dataframe()
        
        # Ensure all required features are present
        missing_features = set(self.feature_names) - set(df.columns)
        if missing_features:
            # Fill missing features with median values (from training)
            for feature in missing_features:
                df[feature] = np.nan
        
        # Reorder columns to match training
        df = df.reindex(columns=self.feature_names, fill_value=np.nan)
        
        # Fill remaining NaNs with 0 (should be handled during training)
        df = df.fillna(0)
        
        # Scale features
        features_scaled = self.scaler.transform(df)
        
        return features_scaled
    
    def predict(self, patient_features: PatientFeatures) -> DiagnosisResult:
        """
        Generate diagnosis prediction for patient.
        
        Args:
            patient_features: PatientFeatures object
            
        Returns:
            DiagnosisResult with comprehensive clinical assessment
        """
        # Preprocess features
        features_processed = self.preprocess_features(patient_features)
        
        # Get model predictions
        prediction_proba = self.model.predict_proba(features_processed)[0]
        prediction_idx = np.argmax(prediction_proba)
        confidence = prediction_proba[prediction_idx]
        
        # Decode prediction
        diagnosis_label = self.label_encoder.inverse_transform([prediction_idx])[0]
        
        # Generate differential diagnoses
        differentials = self._generate_differentials(prediction_proba)
        
        # Analyze clinical findings
        clinical_findings = self._analyze_clinical_findings(patient_features)
        
        # Calculate severity score
        severity_score = self._calculate_severity(patient_features, diagnosis_label)
        
        # Determine urgency level
        urgency_level = self._determine_urgency(severity_score, clinical_findings)
        
        # Generate recommendations
        recommended_tests = self._recommend_tests(diagnosis_label, clinical_findings)
        treatment_suggestions = self._suggest_treatment(diagnosis_label, severity_score)
        risk_factors = self._identify_risk_factors(patient_features, diagnosis_label)
        
        return DiagnosisResult(
            primary_diagnosis=diagnosis_label,
            confidence=float(confidence),
            differential_diagnoses=differentials,
            clinical_findings=clinical_findings,
            severity_score=float(severity_score),
            urgency_level=urgency_level,
            recommended_tests=recommended_tests,
            treatment_suggestions=treatment_suggestions,
            risk_factors=risk_factors
        )
    
    def _generate_differentials(self, probabilities: np.ndarray) -> List[Dict[str, float]]:
        """Generate differential diagnoses with probabilities."""
        differentials = []
        for idx, prob in enumerate(probabilities):
            if prob > 0.1:  # Include diagnoses with >10% probability
                diagnosis = self.label_encoder.inverse_transform([idx])[0]
                differentials.append({
                    'diagnosis': diagnosis,
                    'probability': float(prob)
                })
        
        # Sort by probability descending
        differentials.sort(key=lambda x: x['probability'], reverse=True)
        return differentials[:5]  # Return top 5
    
    def _analyze_clinical_findings(self, features: PatientFeatures) -> Dict[str, str]:
        """Analyze clinical findings based on vital signs."""
        findings = {}
        
        # Temperature analysis
        if features.temperature >= Config.CLINICAL_THRESHOLDS['fever']:
            findings['temperature'] = 'FEVER_PRESENT'
            if features.temperature >= 39.0:
                findings['fever_severity'] = 'HIGH_GRADE'
            else:
                findings['fever_severity'] = 'LOW_GRADE'
        
        # Heart rate analysis
        if features.heart_rate > Config.CLINICAL_THRESHOLDS['tachycardia']:
            findings['heart_rate'] = 'TACHYCARDIA'
        elif features.heart_rate < Config.CLINICAL_THRESHOLDS['bradycardia']:
            findings['heart_rate'] = 'BRADYCARDIA'
        else:
            findings['heart_rate'] = 'NORMAL'
        
        # Blood pressure analysis
        if features.systolic_bp < Config.CLINICAL_THRESHOLDS['hypotension_systolic']:
            findings['blood_pressure'] = 'HYPOTENSION'
        elif features.systolic_bp > 140 or features.diastolic_bp > 90:
            findings['blood_pressure'] = 'HYPERTENSION'
        else:
            findings['blood_pressure'] = 'NORMAL'
        
        # Respiratory analysis
        if features.respiratory_rate > Config.CLINICAL_THRESHOLDS['tachypnea']:
            findings['respiratory_rate'] = 'TACHYPNEA'
        
        # Oxygen saturation analysis
        if features.oxygen_saturation < Config.CLINICAL_THRESHOLDS['hypoxia']:
            findings['oxygen_saturation'] = 'HYPOXIA'
            if features.oxygen_saturation < 90:
                findings['hypoxia_severity'] = 'SEVERE'
            else:
                findings['hypoxia_severity'] = 'MILD'
        
        return findings
    
    def _calculate_severity(self, features: PatientFeatures, diagnosis: str) -> float:
        """Calculate clinical severity score (0-1 scale)."""
        severity_score = 0.0
        
        # Base severity by diagnosis
        severity_map = {
            'SEPSIS': 0.9,
            'PNEUMONIA': 0.7,
            'MYOCARDIAL_INFARCTION': 0.8,
            'STROKE': 0.85,
            'DIABETIC_KETOACIDOSIS': 0.75
        }
        
        # Add base severity if diagnosis is known
        if diagnosis in severity_map:
            severity_score += severity_map[diagnosis] * 0.4
        
        # Add vital sign abnormalities
        if features.temperature >= 39.0:
            severity_score += 0.2
        elif features.temperature >= 38.0:
            severity_score += 0.1
        
        if features.heart_rate > 120 or features.heart_rate < 50:
            severity_score += 0.15
        
        if features.systolic_bp < 90:
            severity_score += 0.25
        
        if features.oxygen_saturation < 90:
            severity_score += 0.3
        elif features.oxygen_saturation < 94:
            severity_score += 0.1
        
        # Cap at 1.0
        return min(severity_score, 1.0)
    
    def _determine_urgency(self, severity_score: float, findings: Dict) -> str:
        """Determine clinical urgency level."""
        if severity_score >= 0.8:
            return "CRITICAL"
        elif severity_score >= 0.6:
            return "HIGH"
        elif severity_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _recommend_tests(self, diagnosis: str, findings: Dict) -> List[str]:
        """Generate recommended diagnostic tests."""
        test_recommendations = []
        
        # Basic tests for all patients
        test_recommendations.extend(["Complete Blood Count", "Basic Metabolic Panel"])
        
        # Diagnosis-specific tests
        test_mapping = {
            'PNEUMONIA': ["Chest X-Ray", "Sputum Culture", "Blood Culture"],
            'SEPSIS': ["Blood Culture", "Lactate Level", "Coagulation Panel"],
            'MYOCARDIAL_INFARCTION': ["ECG", "Cardiac Enzymes", "Echocardiogram"],
            'STROKE': ["CT Head", "MRI Brain", "Carotid Ultrasound"],
            'DIABETIC_KETOACIDOSIS': ["Blood Glucose", "Ketone Level", "Arterial Blood Gas"]
        }
        
        if diagnosis in test_mapping:
            test_recommendations.extend(test_mapping[diagnosis])
        
        # Finding-specific tests
        if findings.get('hypoxia_severity') == 'SEVERE':
            test_recommendations.append("Arterial Blood Gas")
        
        if findings.get('blood_pressure') == 'HYPOTENSION':
            test_recommendations.append("Central Venous Pressure Monitoring")
        
        return list(set(test_recommendations))  # Remove duplicates
    
    def _suggest_treatment(self, diagnosis: str, severity: float) -> List[str]:
        """Generate initial treatment suggestions."""
        treatments = []
        
        # General supportive care
        treatments.append("Monitor vital signs every 4 hours")
        treatments.append("Maintain adequate hydration")
        
        # Severity-based interventions
        if severity >= 0.7:
            treatments.append("Consider ICU admission")
            treatments.append("Establish IV access")
        
        # Diagnosis-specific treatments
        treatment_mapping = {
            'PNEUMONIA': [
                "Start empirical antibiotics (e.g., ceftriaxone + azithromycin)",
                "Administer oxygen to maintain SpO2 > 92%",
                "Consider chest physiotherapy"
            ],
            'SEPSIS': [
                "Administer broad-spectrum antibiotics within 1 hour",
                "Initiate fluid resuscitation (30ml/kg crystalloid)",
                "Consider vasopressor support if hypotensive"
            ],
            'MYOCARDIAL_INFARCTION': [
                "Administer aspirin 325mg chewed",
                "Start dual antiplatelet therapy",
                "Consider reperfusion therapy (PCI/thrombolytics)"
            ]
        }
        
        if diagnosis in treatment_mapping:
            treatments.extend(treatment_mapping[diagnosis])
        
        return treatments
    
    def _identify_risk_factors(self, features: PatientFeatures, diagnosis: str) -> List[str]:
        """Identify clinical risk factors."""
        risk_factors = []
        
        # Age-based risks
        if features.age > 65:
            risk_factors.append("Advanced age (>65)")
        elif features.age < 5:
            risk_factors.append("Pediatric age group")
        
        # Vital sign risks
        if features.temperature >= 39.0:
            risk_factors.append("High-grade fever")
        
        if features.oxygen_saturation < 92:
            risk_factors.append("Significant hypoxia")
        
        if features.systolic_bp < 100:
            risk_factors.append("Hypotension")
        
        # Diagnosis-specific risks
        risk_mapping = {
            'PNEUMONIA': [
                "Immunocompromised state",
                "Chronic lung disease",
                "Recent hospitalization"
            ],
            'SEPSIS': [
                "Immunosuppression",
                "Chronic illness",
                "Recent invasive procedure"
            ]
        }
        
        if diagnosis in risk_mapping:
            risk_factors.extend(risk_mapping[diagnosis])
        
        return risk_factors
    
    def save_model(self, model: RandomForestClassifier, scaler: StandardScaler, 
                   feature_names: List[str], label_encoder):
        """Save trained model and components."""
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_names': feature_names
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        with open(self.label_encoder_path, 'wb') as f:
            pickle.dump(label_encoder, f)
        
        logger.info(f"Model saved to {self.model_path}")
        logger.info(f"Label encoder saved to {self.label_encoder_path}")