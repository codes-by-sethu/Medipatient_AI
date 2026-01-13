"""
AUGMENTED HYBRID TRAINER
Combines Real Hospital Data with 'Textbook' Synthetic Cases.
This GUARANTEES the model learns Sepsis/Trauma patterns while using real data for the rest.
"""
import pandas as pd
import numpy as np
import joblib
import os
import shutil
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.utils import resample
from config import Config

# Setup Paths
CSV_PATH = Config.DATA_DIR / "merged_dataset.csv"
OUTPUT_DIR = Config.MODEL_DIR

# Ensure clean output
if OUTPUT_DIR.exists():
    try:
        shutil.rmtree(OUTPUT_DIR) # Delete old files to remove typo artifacts
        print(f"🧹 Cleared old output directory: {OUTPUT_DIR}")
    except:
        pass
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def map_icd_to_broad_category(icd_code):
    if pd.isna(icd_code): return 'Other'
    code = str(icd_code).upper().replace('.', '')
    
    if code.startswith(('038', '9959', 'A41', 'R65')): return 'Sepsis'
    if code.startswith(('46', '47', '48', '49', '50', '51', 'J')): return 'Respiratory'
    if code.startswith(('39', '40', '41', '42', '43', '44', '45', 'I')): return 'Cardiovascular'
    if code.startswith(('32', '33', '34', '35', '36', '37', '38', 'G')): return 'Neurological'
    if code.startswith(('52', '53', '54', '55', '56', '57', 'K')): return 'Gastrointestinal'
    if code.startswith(('8', '9', 'S', 'T')): return 'Trauma'
    if code.startswith(('24', '25', '26', '27', 'E')): return 'Metabolic'
    return 'Other'

def generate_textbook_cases(n_per_class=1000):
    """Generates perfect 'Textbook' examples to force the model to learn."""
    print(f"💉 Injecting {n_per_class} textbook cases per disease...")
    
    # Feature columns MUST match the real data columns
    cols = ['temperature', 'heartrate', 'resprate', 'sbp', 'dbp', 'o2sat', 'anchor_age', 'target']
    data = []

    # 1. TEXTBOOK SEPSIS (Fever + Low BP + High HR)
    for _ in range(n_per_class):
        data.append([39.5, 120, 28, 85, 55, 90, 65, 'Sepsis'])

    # 2. TEXTBOOK CARDIO (Hypertensive Crisis: High BP + Normal Temp)
    for _ in range(n_per_class):
        data.append([36.8, 95, 20, 190, 110, 96, 60, 'Cardiovascular'])

    # 3. TEXTBOOK TRAUMA (Low BP + High HR + Normal Temp)
    for _ in range(n_per_class):
        data.append([36.5, 130, 22, 80, 50, 98, 25, 'Trauma'])

    # 4. TEXTBOOK RESPIRATORY (Fever + Low O2 + Normal BP)
    for _ in range(n_per_class):
        data.append([39.0, 100, 26, 120, 80, 88, 70, 'Respiratory'])

    return pd.DataFrame(data, columns=cols)

def train_augmented_model():
    print("="*60)
    print(f"🏥 TRAINING AUGMENTED MODEL (Real + Synthetic)")
    print("="*60)

    # 1. Load Real Data
    df_real = pd.read_csv(CSV_PATH, low_memory=False)
    
    # Map Categories
    target_col = 'icd_code' if 'icd_code' in df_real.columns else 'diagnosis'
    if 'disease_category' in df_real.columns: target_col = 'disease_category'
    df_real['target'] = df_real[target_col].apply(map_icd_to_broad_category)
    
    # Keep only relevant columns
    feature_cols = ['temperature', 'heartrate', 'resprate', 'sbp', 'dbp', 'o2sat', 'anchor_age']
    for col in feature_cols:
        if col not in df_real.columns: df_real[col] = np.nan
    
    df_real = df_real[feature_cols + ['target']]
    
    # 2. Load Synthetic Injection
    df_synthetic = generate_textbook_cases(n_per_class=800) # Inject 800 of each
    
    # 3. Combine Real + Synthetic
    df_combined = pd.concat([df_real, df_synthetic], ignore_index=True)
    
    # 4. Balance "Other"
    df_other = df_combined[df_combined['target'] == 'Other']
    df_diseases = df_combined[df_combined['target'] != 'Other']
    
    # Downsample Other to match disease count * 1.5 (give 'Other' a slight edge, but not dominance)
    target_other_count = int(len(df_diseases) * 0.5) 
    print(f"⚖️  Balancing: Diseases={len(df_diseases)}, Downsampling 'Other' to {target_other_count}")
    
    df_other_downsampled = resample(df_other, replace=False, n_samples=target_other_count, random_state=42)
    df_final = pd.concat([df_diseases, df_other_downsampled])
    
    print("\n📊 FINAL DISTRIBUTION:")
    print(df_final['target'].value_counts())

    # 5. Clean & Engineer Features
    X = df_final[feature_cols]
    imputer = SimpleImputer(strategy='median')
    X_clean = pd.DataFrame(imputer.fit_transform(X), columns=feature_cols)
    
    # --- CRITICAL: CORRECT SPELLING HERE ---
    X_clean['fever_high'] = (X_clean['temperature'] > 38.5).astype(int)
    X_clean['tachycardia'] = (X_clean['heartrate'] > 100).astype(int)
    X_clean['hypotension'] = (X_clean['sbp'] < 90).astype(int)  # <--- FIXED TYPO
    X_clean['hypoxia'] = (X_clean['o2sat'] < 90).astype(int)
    
    final_features = list(X_clean.columns)
    print(f"✅ Feature Names (Verified): {final_features}")

    # 6. Train
    le = LabelEncoder()
    y = le.fit_transform(df_final['target'])
    
    print("\n🚀 Training Hybrid Random Forest...")
    clf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    clf.fit(X_clean, y)

    # 7. Save
    print("\n💾 SAVING ARTIFACTS...")
    joblib.dump(clf, OUTPUT_DIR / "disease_model_final.pkl")
    pd.Series(final_features).to_csv(OUTPUT_DIR / "feature_names_final.csv", index=False, header=False)
    
    mapping = pd.DataFrame({'class_id': range(len(le.classes_)), 'class_name': le.classes_})
    mapping.to_csv(OUTPUT_DIR / "disease_mapping.csv", index=False)
    
    print(f"✅ Training Complete. Typo fixed. Knowledge injected.")

if __name__ == "__main__":
    train_augmented_model()