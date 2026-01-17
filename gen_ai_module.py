"""
GEN AI MODULE - MODERN VERSION (2026)
SECURE VERSION - FIXED ALL ISSUES
"""

import os
import json
import logging
import re
import time
from typing import Dict, Any, Optional
from functools import wraps

from dotenv import load_dotenv
load_dotenv()  


from google import genai
from google.genai import types

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedicalGenAI")

def retry_with_backoff(max_retries=3, initial_delay=1):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s")
                    time.sleep(delay)
                    delay *= 2
            return None
        return wrapper
    return decorator

class MedicalGenAI:
    def __init__(self, api_key=None, config=None):
        # ALL configuration from environment or parameters
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.config = config or {
            "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "2000")),
            "timeout": int(os.getenv("GEMINI_TIMEOUT", "30")),
            "model_preference": os.getenv("GEMINI_MODEL", "gemini-1.5-flash").split(",")
        }
        
        self.client = None
        self.model_id = None
        self.available = False

        if not self.api_key:
            logger.warning("⚠️ No Gemini API Key provided")
            return

        try:
            self.client = genai.Client(
                api_key=self.api_key,
                http_options={"timeout": self.config["timeout"]}
            )
            self.model_id = self._find_best_model()
            
            if self.model_id:
                self.available = True
                logger.info(f"✅ Gemini AI connected: {self.model_id}")
            else:
                logger.error("❌ No suitable model found")
                
        except Exception as e:
            logger.error(f"❌ Gemini init error: {e}")

    def _find_best_model(self):
        """Find available model - NO HARCODED FALLBACKS"""
        try:
            models = list(self.client.models.list())
            
            # Build mapping of available models
            available_models = {}
            for model in models:
                available_models[model.name] = model
            
            # Check preferences from config
            for pref in self.config["model_preference"]:
                # Look for exact or partial matches
                for model_name in available_models:
                    if pref in model_name:
                        logger.info(f"Selected model: {model_name}")
                        return model_name
            
            # If no preference matches, use first available
            if available_models:
                first_model = list(available_models.keys())[0]
                logger.info(f"Using available model: {first_model}")
                return first_model
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return None

    def _safe_json_parse(self, text):
        """Safely extract and parse JSON from response"""
        try:
            # Try direct parse first
            return json.loads(text)
        except json.JSONDecodeError:
            # Extract JSON from text if wrapped
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    logger.error(f"JSON extraction failed: {e}")
            
            logger.error(f"No valid JSON found in response: {text[:200]}...")
            raise ValueError("Invalid JSON response from AI")

    @retry_with_backoff(max_retries=3)
    def validate_and_enhance_diagnosis(self, ml_result, patient):
        """
        Ask Gemini to validate ML diagnosis
        Uses ONLY data from patient and ml_result - NO HARDCORDED DATA
        """
        if not self.available:
            return self._fallback_response(ml_result, patient)

        try:
            # Build patient context ONLY from patient data
            patient_context = self._build_patient_context(patient)
            
            ml_diagnosis = ml_result.get('primary_diagnosis', 'Unknown')
            ml_confidence = ml_result.get('confidence', 0.0)
            
            prompt = f"""
            You are a senior medical consultant. Review this case:

            PATIENT DATA:
            {patient_context}

            ML MODEL FINDINGS:
            - Diagnosis: {ml_diagnosis}
            - Confidence: {ml_confidence:.1%}

            YOUR TASK:
            1. Provide YOUR diagnosis based SOLELY on clinical presentation above
            2. Validate if ML diagnosis is correct
            3. If ML is wrong or vague, provide specific correction
            4. Explain your clinical reasoning
            5. List differential diagnoses
            6. Identify red flags

            IMPORTANT: 
            - Base diagnosis ONLY on provided patient data
            - Be SPECIFIC (e.g., "Acute Myocardial Infarction" not "Cardiovascular")
            - Rate your confidence (0-1)

            Return ONLY JSON with this structure:
            {{
                "gemini_diagnosis": "Your specific diagnosis",
                "ml_validation": "Correct/Partially Correct/Incorrect/Unsure",
                "clinical_reasoning": "Your explanation",
                "differentials": ["dx1", "dx2", "dx3"],
                "red_flags": ["flag1", "flag2"],
                "certainty": 0.95,
                "needs_override": true/false,
                "override_reason": "Why override is needed"
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction="You are a board-certified physician. Return ONLY valid JSON.",
                    temperature=self.config["temperature"],
                    max_output_tokens=self.config["max_tokens"]
                )
            )
            
            # SAFE JSON PARSING
            result = self._safe_json_parse(response.text)
            
            # Validate required fields
            required_fields = ["gemini_diagnosis", "ml_validation", "clinical_reasoning"]
            if not all(field in result for field in required_fields):
                logger.error(f"Missing required fields: {result.keys()}")
                return self._fallback_response(ml_result, patient)
            
            # Apply override logic based on data
            ml_diag_lower = ml_diagnosis.lower()
            gemini_diag = result.get('gemini_diagnosis', '').lower()
            
            if not result.get('needs_override'):
                # If ML is vague and Gemini is specific
                if self._is_vague(ml_diag_lower) and not self._is_vague(gemini_diag):
                    result['needs_override'] = True
                    result['override_reason'] = "ML diagnosis too vague"
                
                # If categories mismatch
                elif self._different_category(ml_diag_lower, gemini_diag):
                    result['needs_override'] = True
                    result['override_reason'] = "Different disease category suggested"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Gemini validation error: {e}")
            return self._fallback_response(ml_result, patient)

    def _is_vague(self, diagnosis):
        """Check if diagnosis is vague - based on actual diagnosis content"""
        if not diagnosis:
            return True
            
        vague_terms = ['cardiovascular', 'respiratory', 'gastrointestinal', 
                      'neurological', 'other', 'unknown', 'unspecified', 'general']
        
        diagnosis_words = set(diagnosis.lower().split())
        for term in vague_terms:
            if term in diagnosis or term in diagnosis_words:
                return True
        return False

    def _different_category(self, ml_diag, gemini_diag):
        """Check if diagnoses are in different categories"""
        if not ml_diag or not gemini_diag:
            return False
            
        # Define categories with weighted terms
        categories = {
            'cardio': {'heart', 'cardiac', 'mi', 'infarction', 'angina', 'myocardial'},
            'resp': {'pneumonia', 'copd', 'asthma', 'bronchitis', 'lung', 'respiratory'},
            'gi': {'gastritis', 'colitis', 'hepatitis', 'gi', 'abdominal', 'stomach'},
            'neuro': {'stroke', 'seizure', 'migraine', 'encephalopathy', 'neuro', 'brain'}
        }
        
        def get_category(diagnosis):
            diagnosis_words = set(diagnosis.lower().split())
            scores = {}
            for cat, terms in categories.items():
                score = len(diagnosis_words.intersection(terms))
                if score > 0:
                    scores[cat] = score
            return max(scores, key=scores.get) if scores else None
        
        ml_cat = get_category(ml_diag)
        gemini_cat = get_category(gemini_diag)
        
        return ml_cat and gemini_cat and ml_cat != gemini_cat

    def _build_patient_context(self, patient):
        """Build context string ONLY from patient data"""
        context_lines = [
            f"Age: {patient.age} years",
            f"Gender: {patient.gender}",
            f"Temperature: {patient.temperature}°C",
            f"Heart Rate: {patient.heart_rate} bpm",
            f"Blood Pressure: {patient.systolic_bp}/{patient.diastolic_bp} mmHg",
            f"Respiratory Rate: {patient.respiratory_rate} /min",
            f"Oxygen Saturation: {patient.oxygen_saturation}%",
            f"Pain Score: {patient.pain_score}/10"
        ]
        
        if patient.symptoms:
            context_lines.append(f"Symptoms: {', '.join(patient.symptoms)}")
        
        if patient.medical_history:
            context_lines.append(f"Medical History: {', '.join(patient.medical_history)}")
        
        if patient.medications:
            context_lines.append(f"Medications: {', '.join(patient.medications)}")
        
        if patient.allergies:
            context_lines.append(f"Allergies: {', '.join(patient.allergies)}")
        
        return "\n".join(context_lines)

    def _fallback_response(self, ml_result, patient):
        """Fallback when Gemini fails"""
        return {
            "gemini_diagnosis": ml_result.get('primary_diagnosis', 'Unknown'),
            "ml_validation": "Unable to validate",
            "clinical_reasoning": "AI clinical review unavailable",
            "differentials": [],
            "red_flags": [],
            "certainty": 0.5,
            "needs_override": False,
            "override_reason": "Fallback mode"
        }

    @retry_with_backoff(max_retries=2)
    def generate_comprehensive_treatment(self, diagnosis_result, patient):
        """Generate treatment plan based on final diagnosis - NO HARDCORDED DATA"""
        if not self.available:
            return {}

        try:
            final_diagnosis = diagnosis_result.get('primary_diagnosis', 'Unknown')
            severity = diagnosis_result.get('severity_score', 0.0)
            
            patient_context = self._build_patient_context(patient)
            
            prompt = f"""
            Generate treatment plan for:

            DIAGNOSIS: {final_diagnosis}
            SEVERITY: {severity}/1.0
            PATIENT CONTEXT:
            {patient_context}

            Provide structured plan with:
            1. Immediate interventions (first 24h)
            2. Medications
            3. Monitoring
            4. Follow-up
            5. Patient education

            Base recommendations ONLY on provided diagnosis and patient data.

            Return ONLY JSON:
            {{
                "immediate_interventions": ["item1", "item2"],
                "medications": ["med1 - dose", "med2 - dose"],
                "monitoring": ["monitor1", "monitor2"],
                "follow_up": ["followup1", "followup2"],
                "patient_education": ["edu1", "edu2"]
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction="You are a clinical treatment planner. Return ONLY valid JSON.",
                    temperature=self.config["temperature"],
                    max_output_tokens=self.config["max_tokens"]
                )
            )
            
            return self._safe_json_parse(response.text)
            
        except Exception as e:
            logger.error(f"❌ Treatment generation error: {e}")
            return {}

if __name__ == "__main__":
    print("Testing Gemini module...")
    ai = MedicalGenAI()
    print(f"Available: {ai.available}")
    print(f"Model: {ai.model_id}")