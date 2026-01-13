"""
GEN AI MODULE - STABLE VERSION
Uses the standard 'google-generativeai' library for maximum compatibility.
"""
import os
import json
import logging
import google.generativeai as genai
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedicalGenAI")

class MedicalGenAI:
    def __init__(self, api_key=None):
        # 1. Get API Key
        self.api_key = api_key or Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model = None
        self.available = False

        if not self.api_key:
            print("⚠️ GenAI: No Key Provided")
            return

        try:
            # 2. Configure the Standard Library
            genai.configure(api_key=self.api_key)
            
            # 3. CRITICAL: List available models to find one that works
            print("🔍 Searching for available models...")
            found_model = self._find_best_model()
            
            if found_model:
                self.model = genai.GenerativeModel(found_model)
                self.available = True
                print(f"✅ GenAI Module: Online (Connected to {found_model})")
            else:
                print("❌ GenAI Error: Your API Key cannot see any 'generateContent' models.")
                
        except Exception as e:
            print(f"❌ GenAI Init Error: {e}")

    def _find_best_model(self):
        """
        Asks Google: 'Which models does this key have access to?'
        """
        try:
            # Get all models the key can see
            models = list(genai.list_models())
            
            # Priority list (Fastest -> Strongest)
            preferences = [
                "gemini-1.5-flash",
                "gemini-1.5-flash-001",
                "gemini-1.5-pro", 
                "gemini-1.0-pro",
                "gemini-pro"
            ]
            
            # Check which preferred model exists in the available list
            available_names = [m.name.replace("models/", "") for m in models]
            
            for pref in preferences:
                if pref in available_names:
                    return pref
            
            # Fallback: Just take the first one that supports text generation
            for m in models:
                if "generateContent" in m.supported_generation_methods:
                    name = m.name.replace("models/", "")
                    return name
                    
            return None

        except Exception as e:
            print(f"Error listing models: {e}")
            return "gemini-1.5-flash" # Blind guess if listing fails

    def enhance_diagnosis(self, ml_result, patient):
        """Asks Gemini to review the ML Model's findings."""
        if not self.available: return {}

        try:
            prompt = f"""
            Act as a senior doctor. Review:
            Patient: {patient.age}y, {patient.gender}, Temp {patient.temperature}C, O2 {patient.oxygen_saturation}%
            Symptoms: {', '.join(patient.symptoms)}
            Diagnosis: {ml_result.get('primary_diagnosis')}
            
            Task:
            1. Explain the diagnosis.
            2. List 2 differentials.
            3. Check for red flags.
            
            Return ONLY valid JSON:
            {{
                "gemini_diagnostic_plan": "Reasoning...",
                "gemini_differentials": ["Diff1", "Diff2"],
                "red_flags": ["Flag1"],
                "clinical_findings": "Note..."
            }}
            """
            
            response = self.model.generate_content(prompt)
            # Clean response to ensure it's JSON
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)

        except Exception as e:
            logger.error(f"GenAI Enhancement Failed: {e}")
            return {}

    def generate_comprehensive_treatment(self, diagnosis_result, patient):
        """Generates a treatment plan."""
        if not self.available: return {}

        try:
            prompt = f"""
            Treatment plan for {diagnosis_result.get('primary_diagnosis')} (Severity {diagnosis_result.get('severity_score', 0)}/1).
            Return ONLY valid JSON: {{ "immediate_interventions": ["A", "B"], "definitive_treatment": ["C", "D"] }}
            """
            
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)

        except Exception as e:
            logger.error(f"Treatment Gen Failed: {e}")
            return {}

if __name__ == "__main__":
    ai = MedicalGenAI()