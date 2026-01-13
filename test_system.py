import joblib
import pandas as pd
import numpy as np
from config import Config
import os

def test_model_direct():
    print("="*60)
    print("🧪 ML MODEL STRESS TEST (Direct .pkl Access)")
    print("="*60)

    # 1. Load the Model and Mappings
    try:
        model_path = Config.MODEL_DIR / "disease_model_final.pkl"
        features_path = Config.MODEL_DIR / "feature_names_final.csv"
        mapping_path = Config.MODEL_DIR / "disease_mapping.csv"

        print(f"📂 Loading model from: {model_path}")
        clf = joblib.load(model_path)
        feature_names = pd.read_csv(features_path, header=None)[0].tolist()
        
        mapping_df = pd.read_csv(mapping_path)
        disease_map = dict(zip(mapping_df['class_id'], mapping_df['class_name']))
        
        print("✅ Model & Maps Loaded Successfully")
        print(f"ℹ️  Model expects {len(feature_names)} features: {feature_names}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not load model files. {e}")
        return

    # 2. Define Test Cases (UPDATED FLAGS)
    # We must manually set the flags to match the logic in medical_orchestrator.py
    
    cases = [
        {
            "name": "CASE A: Septic Shock (Critical)",
            "data": {
                # Raw Vitals
                "temperature": 39.5, "heartrate": 115, "resprate": 28, 
                "sbp": 85, "dbp": 50, "o2sat": 88, "anchor_age": 65,
                
                # New Flags (Must match ai_diagnosis.py)
                "fever_high": 1.0,   # Temp > 38.5
                "tachycardia": 1.0,  # HR > 100
                "hypotension": 1.0,  # SBP < 90
                "hypoxia": 1.0       # O2 < 90
            }
        },
        {
            "name": "CASE B: Healthy Adult (Control)",
            "data": {
                "temperature": 37.0, "heartrate": 70, "resprate": 16, 
                "sbp": 120, "dbp": 80, "o2sat": 99, "anchor_age": 30,
                
                # All flags 0
                "fever_high": 0.0, "tachycardia": 0.0, 
                "hypotension": 0.0, "hypoxia": 0.0
            }
        },
        {
            "name": "CASE C: Hypertensive Crisis (Cardio)",
            "data": {
                "temperature": 36.8, "heartrate": 95, "resprate": 20, 
                "sbp": 210, "dbp": 120, "o2sat": 96, "anchor_age": 55,
                
                # Flags
                "fever_high": 0.0, 
                "tachycardia": 0.0, # HR 95 is not > 100
                "hypotension": 0.0, 
                "hypoxia": 0.0
                # Note: There is no 'hypertension' flag in the new model.
                # It relies on the raw 'sbp' value of 210.
            }
        },
        {
            "name": "CASE D: Trauma / Blood Loss",
            "data": {
                "temperature": 36.5, "heartrate": 130, "resprate": 22, 
                "sbp": 80, "dbp": 50, "o2sat": 98, "anchor_age": 25,
                
                # Flags: Tachy + Hypotension + NO Fever
                "fever_high": 0.0, 
                "tachycardia": 1.0, 
                "hypotension": 1.0, 
                "hypoxia": 0.0
            }
        }
    ]

    # 3. Run Predictions
    print("\n--- RUNNING PREDICTIONS ---")
    
    for case in cases:
        # Create a zero-filled row for all features
        row = {feat: 0.0 for feat in feature_names}
        
        # Fill in our test data
        for key, value in case['data'].items():
            if key in row:
                row[key] = value
        
        # Convert to DataFrame (format model expects)
        vector = pd.DataFrame([row.values()], columns=feature_names)
        
        # Predict
        try:
            pred_idx = clf.predict(vector)[0]
            confidence = np.max(clf.predict_proba(vector)[0])
            diagnosis = disease_map.get(pred_idx, f"Unknown ID {pred_idx}")
            
            print(f"\n📋 {case['name']}")
            print(f"   prediction_id: {pred_idx}")
            print(f"   Diagnosis:     {diagnosis}")
            print(f"   Confidence:    {confidence:.4f}")
            
            # Simple result interpretation
            if diagnosis == "Other":
                 print("   ⚠️  Result: OTHER")
            else:
                 print(f"   ✅ Result: {diagnosis}")
                
        except Exception as e:
            print(f"   ❌ Prediction failed: {e}")

if __name__ == "__main__":
    test_model_direct()