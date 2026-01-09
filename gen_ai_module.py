"""
Gen AI module for medical reasoning, differential diagnosis, and patient communication.
Uses LLMs for advanced clinical decision support.
Compatible with OpenAI 2.x API.
"""

from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from openai import OpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

# Try to import from config and diagnosis_engine, but provide fallbacks
try:
    from config import Config
except ImportError:
    class Config:
        OPENAI_API_KEY = None
        LLM_MODEL = "gpt-3.5-turbo"
        LLM_TEMPERATURE = 0.3

try:
    from diagnosis_engine import PatientFeatures, DiagnosisResult
except ImportError:
    # Define fallback classes if import fails
    class PatientFeatures:
        def __init__(self, age=45, temperature=38.5, heart_rate=95,
                    systolic_bp=130, diastolic_bp=85, respiratory_rate=22,
                    oxygen_saturation=96, pain_score=4, symptoms=None):
            self.age = age
            self.temperature = temperature
            self.heart_rate = heart_rate
            self.systolic_bp = systolic_bp
            self.diastolic_bp = diastolic_bp
            self.respiratory_rate = respiratory_rate
            self.oxygen_saturation = oxygen_saturation
            self.pain_score = pain_score
            self.symptoms = symptoms or ['fever', 'cough', 'fatigue']
    
    class DiagnosisResult:
        def __init__(self, primary_diagnosis="Community-Acquired Pneumonia",
                    confidence=0.85, differential_diagnoses=None,
                    clinical_findings="Consolidation on auscultation",
                    severity_score=0.6, urgency_level="HIGH",
                    recommended_tests=None, treatment_suggestions=None,
                    risk_factors=None):
            self.primary_diagnosis = primary_diagnosis
            self.confidence = confidence
            self.differential_diagnoses = differential_diagnoses or ['Bronchitis', 'Influenza', 'COVID-19']
            self.clinical_findings = clinical_findings
            self.severity_score = severity_score
            self.urgency_level = urgency_level
            self.recommended_tests = recommended_tests or ['Chest X-ray', 'CBC', 'Blood Cultures']
            self.treatment_suggestions = treatment_suggestions or ['Antibiotics', 'Oxygen if needed']
            self.risk_factors = risk_factors or ['Smoking history', 'Age > 65']

@dataclass
class MedicalContext:
    """Container for medical context data."""
    patient_data: PatientFeatures
    diagnosis_result: Optional[DiagnosisResult] = None
    lab_results: Optional[Dict] = None
    medical_history: Optional[Dict] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

class MedicalGenAI:
    """Generative AI module for medical reasoning and communication."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize medical Gen AI module.
        
        Args:
            api_key: OpenAI API key. Uses config if None.
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key not provided. Some features will be limited.")
            self.client = None
            self.available = False
        else:
            try:
                # Initialize OpenAI client for v2.x
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                logger.info("✅ OpenAI client (v2.x) initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
                self.available = False
        
        # Medical knowledge system prompts
        self.system_prompts = self._load_system_prompts()
        
        # Medical guidelines and protocols
        self.guidelines = self._load_medical_guidelines()
        
        logger.info(f"MedicalGenAI module initialized. Available: {self.available}")
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different medical tasks."""
        return {
            'differential_diagnosis': """You are an expert medical diagnostician with 20+ years of clinical experience.
            Your task is to generate comprehensive differential diagnoses based on patient presentation.
            Always consider:
            1. Most common causes first
            2. Life-threatening conditions that must be ruled out
            3. Patient demographics and risk factors
            4. Local epidemiological patterns
            
            Format your response as structured JSON with:
            - primary_differential: Most likely diagnosis with probability
            - secondary_differentials: List of other possibilities
            - red_flags: Critical signs that require immediate attention
            - diagnostic_approach: Step-by-step workup plan
            - initial_management: First-line interventions""",
            
            'treatment_planning': """You are a consultant physician specializing in treatment planning.
            Generate evidence-based treatment recommendations considering:
            1. Current clinical guidelines
            2. Patient-specific factors (age, comorbidities, allergies)
            3. Available resources and setting
            4. Potential drug interactions
            5. Monitoring requirements
            
            Structure your response with:
            - immediate_interventions: Actions within first hour
            - definitive_treatment: Specific medications/procedures
            - monitoring_plan: Vital sign and lab monitoring schedule
            - patient_education: Key points to communicate
            - followup_plan: When and what to follow up""",
            
            'patient_explanation': """You are a compassionate physician explaining medical information to a patient.
            Your explanations should be:
            1. Clear and jargon-free
            2. Empathetic and reassuring
            3. Accurate but not overwhelming
            4. Action-oriented with clear next steps
            5. Culturally sensitive
            
            Include:
            - What the diagnosis means in simple terms
            - What to expect during recovery
            - When to seek immediate help
            - How to manage symptoms at home
            - Answers to common patient questions""",
            
            'clinical_notes': """You are generating professional clinical documentation.
            Create comprehensive but concise clinical notes including:
            1. Subjective: Patient's story in their words
            2. Objective: Measurable findings
            3. Assessment: Clinical reasoning and diagnosis
            4. Plan: Treatment and follow-up
            5. Medical Decision Making: Complexity justification
            
            Use SOAP format with appropriate medical terminology."""
        }
    
    def _load_medical_guidelines(self) -> Dict[str, Any]:
        """Load evidence-based medical guidelines."""
        # Keep your existing guidelines here
        return {
            'pneumonia': {
                'diagnostic_criteria': ['fever', 'cough', 'abnormal_chest_xray'],
                'severity_assessment': ['CURB-65 score', 'PSI score'],
                'empirical_treatment': {
                    'outpatient': ['amoxicillin', 'doxycycline', 'macrolide'],
                    'inpatient': ['ceftriaxone + azithromycin', 'respiratory_fluoroquinolone']
                },
                'monitoring': ['daily_vital_signs', 'repeat_xray_if_no_improvement']
            }
        }
    
    def generate_differential_diagnosis(self, context: MedicalContext) -> Dict[str, Any]:
        """
        Generate comprehensive differential diagnosis using LLM.
        
        Args:
            context: MedicalContext object with patient data
            
        Returns:
            Structured differential diagnosis with probabilities
        """
        logger.info(f"Generating differential diagnosis for patient age {context.patient_data.age}")
        
        if not self.available or not self.client:
            logger.warning("LLM client not available, using fallback diagnosis")
            return self._generate_fallback_diagnosis(context)
        
        try:
            # Prepare patient context for LLM
            patient_summary = self._create_patient_summary(context)
            
            # Call LLM with structured prompt using OpenAI v2.x API
            response = self.client.chat.completions.create(
                model=getattr(Config, 'LLM_MODEL', 'gpt-3.5-turbo'),
                temperature=getattr(Config, 'LLM_TEMPERATURE', 0.3),
                messages=[
                    {"role": "system", "content": self.system_prompts['differential_diagnosis']},
                    {"role": "user", "content": patient_summary}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse and validate response
            diagnosis_data = json.loads(response.choices[0].message.content)
            validated_data = self._validate_diagnosis_response(diagnosis_data)
            
            # Integrate with ML model results if available
            if context.diagnosis_result:
                validated_data = self._integrate_ml_predictions(
                    validated_data, context.diagnosis_result
                )
            
            logger.info(f"Generated differential diagnosis with {len(validated_data.get('secondary_differentials', []))} possibilities")
            return validated_data
            
        except Exception as e:
            logger.error(f"Error generating differential diagnosis: {e}")
            return self._generate_fallback_diagnosis(context)
    
    def generate_treatment_plan(self, diagnosis: str, context: MedicalContext) -> Dict[str, Any]:
        """
        Generate evidence-based treatment plan.
        
        Args:
            diagnosis: Primary diagnosis
            context: Medical context including patient factors
            
        Returns:
            Comprehensive treatment plan
        """
        logger.info(f"Generating treatment plan for diagnosis: {diagnosis}")
        
        if not self.available or not self.client:
            return self._generate_fallback_treatment(diagnosis, context)
        
        try:
            # Get relevant guidelines
            guidelines = self.guidelines.get(diagnosis.lower(), {})
            
            # Prepare treatment context
            treatment_context = {
                "diagnosis": diagnosis,
                "patient_age": context.patient_data.age,
                "allergies": context.allergies or [],
                "comorbidities": context.medical_history.get('comorbidities', []) if context.medical_history else [],
                "severity": context.diagnosis_result.severity_score if context.diagnosis_result else 0.5,
                "available_guidelines": guidelines
            }
            
            # Call LLM for personalized plan
            response = self.client.chat.completions.create(
                model=getattr(Config, 'LLM_MODEL', 'gpt-3.5-turbo'),
                temperature=0.2,  # Lower temp for treatment recommendations
                messages=[
                    {"role": "system", "content": self.system_prompts['treatment_planning']},
                    {"role": "user", "content": json.dumps(treatment_context)}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse and enhance with clinical guidelines
            treatment_plan = json.loads(response.choices[0].message.content)
            treatment_plan = self._enhance_with_guidelines(treatment_plan, guidelines)
            
            logger.info(f"Generated treatment plan for {diagnosis}")
            return treatment_plan
            
        except Exception as e:
            logger.error(f"Error generating treatment plan: {e}")
            return self._generate_fallback_treatment(diagnosis, context)
    
    def explain_to_patient(self, diagnosis: str, context: MedicalContext) -> Dict[str, Any]:
        """
        Generate patient-friendly explanation of diagnosis and treatment.
        
        Args:
            diagnosis: Medical diagnosis
            context: Patient context
            
        Returns:
            Structured patient education materials
        """
        logger.info(f"Generating patient explanation for: {diagnosis}")
        
        try:
            # Prepare patient-friendly context
            patient_info = {
                "diagnosis": diagnosis,
                "age": context.patient_data.age,
                "key_symptoms": list(context.patient_data.symptoms or []),
                "treatment_plan": self.generate_treatment_plan(diagnosis, context) if self.available else None,
                "reading_level": "8th_grade",  # Default, could be customized
                "primary_language": "English"  # Could be parameterized
            }
            
            # Call LLM for explanation
            if self.available and self.client:
                response = self.client.chat.completions.create(
                    model=getattr(Config, 'LLM_MODEL', 'gpt-3.5-turbo'),
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": self.system_prompts['patient_explanation']},
                        {"role": "user", "content": json.dumps(patient_info)}
                    ],
                    response_format={"type": "json_object"}
                )
                explanation = json.loads(response.choices[0].message.content)
            else:
                explanation = self._generate_basic_explanation(diagnosis, context)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating patient explanation: {e}")
            return {
                "simple_explanation": f"You have been diagnosed with {diagnosis}.",
                "next_steps": "Please discuss treatment options with your doctor.",
                "when_to_seek_help": "If symptoms worsen or you have trouble breathing, seek immediate medical attention.",
                "error": str(e)
            }
    
    def generate_clinical_notes(self, context: MedicalContext, 
                               diagnosis_result: DiagnosisResult) -> Dict[str, Any]:
        """
        Generate professional SOAP notes for medical records.
        
        Args:
            context: Complete medical context
            diagnosis_result: Diagnosis from ML model
            
        Returns:
            Structured clinical documentation
        """
        logger.info(f"Generating clinical notes for {diagnosis_result.primary_diagnosis}")
        
        try:
            # Prepare clinical data for documentation
            clinical_data = {
                "subjective": self._extract_subjective_data(context),
                "objective": self._extract_objective_data(context, diagnosis_result),
                "assessment": {
                    "primary_diagnosis": diagnosis_result.primary_diagnosis,
                    "differentials": diagnosis_result.differential_diagnoses,
                    "severity": diagnosis_result.severity_score,
                    "clinical_reasoning": diagnosis_result.clinical_findings
                },
                "plan": {
                    "diagnostic_tests": diagnosis_result.recommended_tests,
                    "treatments": diagnosis_result.treatment_suggestions,
                    "follow_up": self._generate_followup_plan(diagnosis_result),
                    "patient_instructions": self._generate_instructions(diagnosis_result)
                }
            }
            
            # Generate structured notes
            if self.available and self.client:
                response = self.client.chat.completions.create(
                    model=getattr(Config, 'LLM_MODEL', 'gpt-3.5-turbo'),
                    temperature=0.1,  # Very low temp for consistent documentation
                    messages=[
                        {"role": "system", "content": self.system_prompts['clinical_notes']},
                        {"role": "user", "content": json.dumps(clinical_data)}
                    ],
                    response_format={"type": "json_object"}
                )
                soap_notes = json.loads(response.choices[0].message.content)
            else:
                soap_notes = self._generate_basic_soap_notes(clinical_data)
            
            logger.info(f"Generated clinical notes for {diagnosis_result.primary_diagnosis}")
            return soap_notes
            
        except Exception as e:
            logger.error(f"Error generating clinical notes: {e}")
            return self._generate_minimal_notes(context, diagnosis_result)
    
    def _create_patient_summary(self, context: MedicalContext) -> str:
        """Create comprehensive patient summary for LLM."""
        # Your existing implementation
        summary_parts = []
        
        # Demographic information
        summary_parts.append(f"Patient: {context.patient_data.age}-year-old")
        
        # Vital signs
        vitals = []
        if hasattr(context.patient_data, 'temperature') and context.patient_data.temperature:
            vitals.append(f"Temperature: {context.patient_data.temperature}°C")
        if hasattr(context.patient_data, 'heart_rate') and context.patient_data.heart_rate:
            vitals.append(f"Heart Rate: {context.patient_data.heart_rate} bpm")
        if hasattr(context.patient_data, 'systolic_bp') and context.patient_data.systolic_bp:
            vitals.append(f"Blood Pressure: {context.patient_data.systolic_bp}/{context.patient_data.diastolic_bp} mmHg")
        
        if vitals:
            summary_parts.append("Vital Signs: " + "; ".join(vitals))
        
        # Symptoms
        if hasattr(context.patient_data, 'symptoms') and context.patient_data.symptoms:
            summary_parts.append(f"Symptoms: {', '.join(context.patient_data.symptoms)}")
        
        return "\n".join(summary_parts)
    
    def _validate_diagnosis_response(self, diagnosis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean LLM diagnosis response."""
        # Your existing validation logic
        required_keys = ['primary_differential', 'secondary_differentials', 'red_flags']
        
        for key in required_keys:
            if key not in diagnosis_data:
                if 'differential' in key:
                    diagnosis_data[key] = []
                else:
                    diagnosis_data[key] = {}
        
        return diagnosis_data
    
    def _integrate_ml_predictions(self, llm_data: Dict[str, Any], 
                                 ml_result: DiagnosisResult) -> Dict[str, Any]:
        """Integrate ML model predictions with LLM reasoning."""
        integrated_data = llm_data.copy()
        
        if not ml_result:
            return integrated_data
        
        # Add ML clinical findings
        if hasattr(ml_result, 'clinical_findings'):
            integrated_data['clinical_findings'] = ml_result.clinical_findings
        
        return integrated_data
    
    def _generate_fallback_diagnosis(self, context: MedicalContext) -> Dict[str, Any]:
        """Generate differential diagnosis without LLM."""
        return {
            'primary_differential': {
                'diagnosis': 'Acute Upper Respiratory Infection',
                'probability': 0.6,
                'reasoning': 'Based on common presentation patterns'
            },
            'secondary_differentials': [
                {'diagnosis': 'Bronchitis', 'probability': 0.2},
                {'diagnosis': 'Allergic Rhinitis', 'probability': 0.1}
            ],
            'red_flags': [
                'Shortness of breath',
                'High fever (>39°C)'
            ],
            'metadata': {
                'generated_by': 'fallback_system',
                'note': 'Generated without OpenAI API'
            }
        }
    
    def _generate_fallback_treatment(self, diagnosis: str, 
                                   context: MedicalContext) -> Dict[str, Any]:
        """Generate fallback treatment plan."""
        return {
            'diagnosis': diagnosis,
            'immediate_interventions': [
                'Assess airway, breathing, circulation',
                'Monitor vital signs'
            ],
            'metadata': {
                'generated_by': 'fallback_system'
            }
        }
    
    def _generate_basic_explanation(self, diagnosis: str, 
                                  context: MedicalContext) -> Dict[str, Any]:
        """Generate basic patient explanation without LLM."""
        return {
            'simple_explanation': f'{diagnosis} is a medical condition that requires treatment.',
            'what_it_means': f'You have been diagnosed with {diagnosis}.',
            'when_to_seek_help': [
                'Difficulty breathing',
                'High fever that doesn\'t improve',
                'Severe pain'
            ]
        }
    
    def _generate_basic_soap_notes(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic SOAP notes without LLM."""
        return {
            'subjective': clinical_data.get('subjective', {}),
            'objective': clinical_data.get('objective', {}),
            'assessment': clinical_data.get('assessment', {}),
            'plan': clinical_data.get('plan', {}),
            'note': 'Generated without OpenAI API'
        }
    
    def _extract_subjective_data(self, context: MedicalContext) -> Dict[str, Any]:
        """Extract subjective patient-reported data."""
        return {
            'chief_complaint': 'Patient-reported symptoms',
            'symptoms': list(context.patient_data.symptoms or []),
        }
    
    def _extract_objective_data(self, context: MedicalContext, 
                               diagnosis_result: DiagnosisResult) -> Dict[str, Any]:
        """Extract objective measurable data."""
        objective = {
            'vital_signs': {},
            'diagnostic_findings': {
                'ai_assessment': diagnosis_result.clinical_findings if hasattr(diagnosis_result, 'clinical_findings') else 'No specific findings',
            }
        }
        
        return objective
    
    def _generate_followup_plan(self, diagnosis_result: DiagnosisResult) -> Dict[str, Any]:
        """Generate follow-up plan based on diagnosis."""
        return {
            'timing': '1-2 weeks',
            'triggers': [
                'Worsening symptoms',
                'No improvement after 3 days'
            ]
        }
    
    def _generate_instructions(self, diagnosis_result: DiagnosisResult) -> List[str]:
        """Generate patient instructions."""
        return [
            "Take all medications as prescribed",
            "Return to clinic if symptoms worsen",
            "Follow up as scheduled"
        ]
    
    def _generate_minimal_notes(self, context: MedicalContext, 
                               diagnosis_result: DiagnosisResult) -> Dict[str, Any]:
        """Generate minimal clinical notes when LLM fails."""
        primary_dx = diagnosis_result.primary_diagnosis if hasattr(diagnosis_result, 'primary_diagnosis') else 'Unknown Diagnosis'
        
        return {
            "subjective": f"{context.patient_data.age}-year-old with symptoms",
            "objective": f"AI Diagnosis: {primary_dx}",
            "assessment": primary_dx,
            "plan": "Follow AI-generated recommendations.",
            "note": "Generated without OpenAI API"
        }
    
    def _enhance_with_guidelines(self, treatment_plan: Dict[str, Any], 
                                guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance treatment plan with evidence-based guidelines."""
        enhanced_plan = treatment_plan.copy()
        
        if guidelines:
            enhanced_plan['guideline_references'] = {
                'source': 'Internal Medical Guidelines',
                'applicable_sections': list(guidelines.keys())
            }
        
        return enhanced_plan

def get_medical_gen_ai(api_key: str = None) -> MedicalGenAI:
    """
    Factory function to get MedicalGenAI instance.
    
    Args:
        api_key: Optional OpenAI API key
        
    Returns:
        Configured MedicalGenAI instance
    """
    return MedicalGenAI(api_key=api_key)

if __name__ == "__main__":
    # Simple test to verify the fix
    print("Testing MedicalGenAI module with OpenAI v2.x...")
    
    # Initialize without API key (fallback mode)
    gen_ai = MedicalGenAI()
    
    print(f"Gen AI available: {gen_ai.available}")
    print(f"Client initialized: {gen_ai.client is not None}")
    
    if gen_ai.available:
        print("✅ OpenAI v2.x API is ready to use!")
    else:
        print("⚠️ Running in fallback mode (no API key)")