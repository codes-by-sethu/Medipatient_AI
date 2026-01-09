#!/usr/bin/env python3
"""
FIXED AI Diagnosis System - Balanced Training
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(r"C:\Users\SETHULAKSHMI K B\PI2")
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

print("=" * 70)
print("FIXED AI DIAGNOSIS SYSTEM - BALANCED TRAINING")
print("=" * 70)

def create_smart_disease_categories(df):
    """Create better disease categories based on symptoms"""
    print("Creating smart disease categories based on clinical patterns...")
    
    # Start with 'other' as default
    df['disease_category'] = 'other'
    
    # Check vital signs and symptoms to assign better categories
    for idx, row in df.iterrows():
        temp = float(row.get('temperature', 37))
        hr = float(row.get('heartrate', 75))
        o2 = float(row.get('o2sat', 98))
        rr = float(row.get('resprate', 16))
        
        # Rule 1: High fever + low oxygen → Respiratory Infection
        if temp >= 38.5 and o2 < 94:
            df.at[idx, 'disease_category'] = 'respiratory'
            df.at[idx, 'infectious_flag'] = 1
            
        # Rule 2: Very high fever + high heart rate → Infectious Disease
        elif temp >= 39.0 and hr > 100:
            df.at[idx, 'disease_category'] = 'infectious'
            df.at[idx, 'infectious_flag'] = 1
            
        # Rule 3: Normal temp + high heart rate + age > 60 → Cardiovascular
        elif temp < 38.0 and hr > 90 and row.get('anchor_age', 45) > 60:
            df.at[idx, 'disease_category'] = 'cardiovascular'
            
        # Rule 4: High respiratory rate + low oxygen → Respiratory
        elif rr > 22 and o2 < 94:
            df.at[idx, 'disease_category'] = 'respiratory'
            
        # Rule 5: Moderate fever + normal vitals → Other (but not default)
        elif temp >= 37.8 and temp < 38.5:
            df.at[idx, 'disease_category'] = 'mild_infection'
            df.at[idx, 'infectious_flag'] = 1
    
    return df

def main():
    # Load data
    data_path = DATA_DIR / "merged_dataset.csv"
    print(f"Loading data from: {data_path}")
    
    df = pd.read_csv(data_path, low_memory=False)
    print(f"Original shape: {df.shape}")
    
    # Clean data
    print("\nCleaning data...")
    df = df.dropna(axis=1, thresh=len(df)*0.5)
    
    # Fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    # Select clinical features
    clinical_features = [
        'temperature', 'heartrate', 'resprate', 'sbp', 'dbp', 
        'o2sat', 'acuity', 'anchor_age'
    ]
    
    # Keep only columns that exist
    available_features = [f for f in clinical_features if f in df.columns]
    print(f"Using {len(available_features)} clinical features")
    
    # Create feature matrix
    X = df[available_features].copy()
    
    # Fix unrealistic values
    X['temperature'] = X['temperature'].clip(35, 42)
    X['heartrate'] = X['heartrate'].clip(40, 200)
    X['o2sat'] = X['o2sat'].clip(70, 100)
    X['sbp'] = X['sbp'].clip(70, 250)
    X['dbp'] = X['dbp'].clip(40, 150)
    
    # Create disease categories
    print("\nCreating disease categories...")
    
    # Initialize with synthetic data if needed
    if 'disease_category' not in df.columns:
        df['disease_category'] = 'other'
    
    # Create infectious flag based on temperature
    df['infectious_flag'] = (df['temperature'] >= 38.0).astype(int)
    
    # Apply smart categorization
    df = create_smart_disease_categories(df)
    
    # Encode disease categories
    le = LabelEncoder()
    y_disease = le.fit_transform(df['disease_category'])
    
    print(f"\nDisease category distribution:")
    for class_name, count in zip(le.classes_, np.bincount(y_disease)):
        print(f"  {class_name:20}: {count:6} ({count/len(y_disease)*100:.1f}%)")
    
    # Handle class imbalance with SMOTE
    print("\nBalancing classes with SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=2)
    X_balanced, y_balanced = smote.fit_resample(X, y_disease)
    
    print(f"After balancing: {X_balanced.shape}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
    )
    
    # Train model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nFeature Importance:")
    for idx, row in importance.iterrows():
        print(f"  {row['feature']:15}: {row['importance']:.3f}")
    
    # Train infectious model
    print("\nTraining infectious disease detector...")
    y_infectious = df['infectious_flag']
    
    X_train_inf, X_test_inf, y_train_inf, y_test_inf = train_test_split(
        X, y_infectious, test_size=0.2, random_state=42, stratify=y_infectious
    )
    
    infectious_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    infectious_model.fit(X_train_inf, y_train_inf)
    y_pred_inf = infectious_model.predict(X_test_inf)
    inf_accuracy = accuracy_score(y_test_inf, y_pred_inf)
    
    print(f"Infectious model accuracy: {inf_accuracy:.3f}")
    
    # Save models
    print("\nSaving models...")
    
    # Save disease model
    disease_path = OUTPUT_DIR / "disease_model_fixed.pkl"
    joblib.dump(model, disease_path)
    print(f"✅ Saved disease model to {disease_path}")
    
    # Save infectious model
    infectious_path = OUTPUT_DIR / "infectious_model_fixed.pkl"
    joblib.dump(infectious_model, infectious_path)
    print(f"✅ Saved infectious model to {infectious_path}")
    
    # Save feature names
    feature_path = OUTPUT_DIR / "feature_names_fixed.csv"
    pd.Series(available_features).to_csv(feature_path, index=False, header=False)
    print(f"✅ Saved feature names to {feature_path}")
    
    # Save disease mapping
    disease_mapping = pd.DataFrame({
        'class_id': range(len(le.classes_)),
        'class_name': le.classes_
    })
    mapping_path = OUTPUT_DIR / "disease_mapping_fixed.csv"
    disease_mapping.to_csv(mapping_path, index=False)
    print(f"✅ Saved disease mapping to {mapping_path}")
    
    # Save complete package
    package = {
        'disease_model': model,
        'infectious_model': infectious_model,
        'feature_names': available_features,
        'disease_encoder': le,
        'disease_mapping': {i: cls for i, cls in enumerate(le.classes_)}
    }
    
    package_path = OUTPUT_DIR / "diagnosis_models_fixed.pkl"
    joblib.dump(package, package_path)
    print(f"✅ Saved complete package to {package_path}")
    
    
if __name__ == "__main__":
    main()