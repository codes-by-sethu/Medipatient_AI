"""
Configuration management for MediPatient AI system.
Centralized settings for all modules.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration constants for the healthcare AI system."""
    
    # Path configurations
    BASE_DIR = Path(__file__).parent
    MODEL_DIR = BASE_DIR / "models"
    DATA_DIR = BASE_DIR / "data"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # Model file paths
    TABULAR_MODEL_PATH = MODEL_DIR / "diagnosis_model.pkl"
    LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///patients.db")
    
    # ML model parameters
    DIAGNOSIS_THRESHOLD = 0.7
    PNEUMONIA_THRESHOLD = 0.5
    MAX_FEATURES = 50
    
    # Clinical thresholds
    CLINICAL_THRESHOLDS = {
        'fever': 38.0,  # °C
        'tachycardia': 100,  # bpm
        'bradycardia': 60,  # bpm
        'tachypnea': 20,  # breaths/min
        'hypotension_systolic': 90,  # mmHg
        'hypotension_diastolic': 60,  # mmHg
        'hypoxia': 94  # SpO2 %
    }
    
    # Gen AI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for cost efficiency
    LLM_TEMPERATURE = 0.3  # Lower for medical accuracy
    
    # Dashboard settings
    DASHBOARD_PORT = 8501
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [cls.MODEL_DIR, cls.DATA_DIR, cls.ASSETS_DIR]
        for directory in directories:
            directory.mkdir(exist_ok=True)

# Initialize directories
Config.ensure_directories()