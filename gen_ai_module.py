"""
GEN AI MODULE - STRICT SEPARATION (UNIQUE KEYS)
"""
import os
import json
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedicalGenAI")

class MedicalGenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.available = False
        self.model_id = "gemini-2.5-flash-lite" 

        if self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={'api_version': 'v1beta'}
                )
                self.available = True
                logger.info(f"✅ MedicalGenAI: Online (Target: {self.model_id})")
            except Exception as e:
                logger.warning(f"⚠️ Connection Error: {e}")
                self.available = False

    def validate_and_enhance_diagnosis(self, ml_result, patient):
        """
        SECTION 1: DIAGNOSIS
        Returns key: 'clinical_note'
        """
        data = None
        if self.available:
            try:
                # PROMPT: STRICTLY DIAGNOSTIC
                prompt = f"""
                Act as a Senior Consultant. 
                Patient: {patient.age}y {patient.gender}. 
                Vitals: T{patient.temperature}C, HR{patient.heart_rate}, BP{patient.systolic_bp}/{patient.diastolic_bp}.
                Diagnosis: {ml_result.get('primary_diagnosis')}.
                
                Task: Write a concise clinical note (Max 3 sentences).
                - Use **Bold** for critical findings (e.g. **Hypotension**).
                - Focus ONLY on the 'Why' (Pathophysiology).
                - DO NOT include treatment plans.
                
                Return JSON only:
                {{
                    "clinical_note": "The patient exhibits **Septic Shock** physiology. Notable **hypotension (85/50)** and **tachycardia** indicate compensatory failure.",
                    "gemini_diagnosis": "{ml_result.get('primary_diagnosis')}",
                    "risk_score": "High"
                }}
                """
                response = self.client.models.generate_content(
                    model=self.model_id, contents=prompt
                )
                text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
            except Exception:
                pass

        # Fallback
        if not data:
            data = {
                "clinical_note": f"Assessment indicates **{ml_result.get('primary_diagnosis')}** based on vitals (BP {patient.systolic_bp}/{patient.diastolic_bp}). Clinical review required.",
                "gemini_diagnosis": ml_result.get('primary_diagnosis'),
                "risk_score": "Medium"
            }
        
        return data

    def generate_comprehensive_treatment(self, diagnosis_result, patient):
        """
        SECTION 2: TREATMENT
        Returns key: 'treatment_steps'
        """
        data = None
        if self.available:
            try:
                # PROMPT: STRICTLY ACTIONABLE STEPS
                prompt = f"""
                Create a treatment protocol for {diagnosis_result.get('primary_diagnosis')}.
                Patient: {patient.age}y {patient.gender}.
                
                Return JSON with a 'treatment_steps' list.
                Each step MUST be: ["Category", "Action"].
                
                Example:
                {{
                    "protocol_title": "SEPSIS BUNDLE",
                    "treatment_steps": [
                        ["Resuscitation", "IV Fluids 30ml/kg"],
                        ["Medication", "Broad-spectrum Antibiotics"],
                        ["Labs", "Lactate, Blood Cultures"]
                    ]
                }}
                """
                response = self.client.models.generate_content(
                    model=self.model_id, contents=prompt
                )
                text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
            except Exception as e:
                logger.warning(f"⚠️ AI Table Gen Failed: {e}")

        # Fallback
        if not data:
            data = {
                "protocol_title": "STANDARD PROTOCOL",
                "treatment_steps": [
                    ["Monitoring", "Continuous Vitals"],
                    ["Treatment", "Symptomatic Care"],
                    ["Labs", "Standard Panel"]
                ]
            }

        # SANITIZER: Ensure clean list structure
        # We look specifically for 'treatment_steps' now
        if "treatment_steps" in data:
            cleaned_steps = []
            for item in data["treatment_steps"]:
                if isinstance(item, dict):
                    cleaned_steps.append(list(item.values()))
                elif isinstance(item, list):
                    cleaned_steps.append(item[:2]) 
            data["treatment_steps"] = cleaned_steps

        # Compatibility map (In case UI looks for 'steps')
        data["steps"] = data.get("treatment_steps", [])
        
        return data