"""
CONFIGURATION FILE
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

class Config:
    # PATHS - Uses your .env BASE_DIR or defaults to current folder
    BASE_DIR = Path(os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__))))
    
    # 1. CRITICAL: Added DATA_DIR (Fixes your error)
    DATA_DIR = BASE_DIR / "data"
    
    OUTPUT_DIR = BASE_DIR / "output"
    MODEL_DIR = BASE_DIR / "output"
    
    # API KEYS
    # Key 1: For Diagnosis (Medical Orchestrator)
    DIAGNOSIS_KEY = os.getenv("GEMINI_API_KEY")
    
    # Key 2: For Reports (Optional backup or specific report tasks)
    REPORT_KEY = os.getenv("AI_REPORT")
    
    # SYSTEM SETTINGS
    # We use the diagnosis key by default for the Orchestrator
    GEMINI_API_KEY = DIAGNOSIS_KEY or REPORT_KEY 
    MODEL_NAME = "gemini-1.5-flash"