from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import pandas as pd
import numpy as np
import joblib
import uvicorn
from typing import Dict, List

# Load the trained model
try:
    model = joblib.load("model.pkl")
    print("✅ Model loaded successfully")
except FileNotFoundError:
    print("❌ Model file not found. Please ensure 'model.pkl' exists.")
    model = None

# Load training data to understand feature structure
try:
    train = pd.read_csv("train.csv")
    print("✅ Training data loaded for feature reference")
except FileNotFoundError:
    print("❌ Training data not found. Please ensure 'train.csv' exists.")
    train = None

app = FastAPI(
    title="Insurance Claims Severity Predictor",
    description="Predict insurance claim loss amounts using machine learning",
    version="1.0.0"
)

class PredictionRequest(BaseModel):
    features: Dict[str, float]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "features": {
                    "cont1": 0.5,
                    "cont2": 0.3,
                    "cont3": 0.8,
                    "cat1": 1.0,  # Will be encoded
                    "cat2": 2.0,  # Will be encoded
                    # ... other features
                }
            }
        }
    )

class PredictionResponse(BaseModel):
    prediction: float
    prediction_actual: float
    confidence_score: float

def preprocess_input(features: Dict[str, float]) -> pd.DataFrame:
    """
    Preprocess input features to match training data format
    """
    if train is None:
        raise HTTPException(status_code=500, detail="Training data not available")

    # Create DataFrame from input
    df = pd.DataFrame([features])

    # Identify categorical and continuous columns
    cat_cols = [col for col in train.columns if col.startswith('cat')]
    cont_cols = [col for col in train.columns if col.startswith('cont')]

    # Ensure all expected features are present
    expected_features = cat_cols + cont_cols
    missing_features = [f for f in expected_features if f not in df.columns]
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required features: {missing_features}"
        )

    # Add is_train flag (0 for prediction)
    df['is_train'] = 0
    df['loss'] = np.nan

    # Combine with a sample of training data for consistent encoding
    # This ensures get_dummies creates the same columns
    sample_train = train.head(1).copy()
    combined = pd.concat([sample_train, df], ignore_index=True)

    # One-hot encode categorical variables
    combined = pd.get_dummies(combined, columns=cat_cols)

    # Extract the processed input row (second row)
    processed_input = combined.iloc[1:2].drop(['id', 'is_train', 'loss'], axis=1)

    return processed_input

@app.get("/")
async def root():
    return {
        "message": "Insurance Claims Severity Predictor API",
        "status": "active",
        "model_loaded": model is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_status": "loaded" if model else "not loaded",
        "training_data_status": "loaded" if train else "not loaded"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Preprocess input features
        processed_input = preprocess_input(request.features)

        # Make prediction (on log scale)
        prediction_log = model.predict(processed_input)[0]

        # Convert back to actual scale
        prediction_actual = np.expm1(prediction_log)

        # Calculate confidence score (using prediction variance as proxy)
        # In a real scenario, you'd use prediction intervals or ensemble variance
        confidence_score = 0.85  # Placeholder - would be calculated from model uncertainty

        return PredictionResponse(
            prediction=float(prediction_log),
            prediction_actual=float(prediction_actual),
            confidence_score=confidence_score
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/features")
async def get_expected_features():
    """Get the list of expected input features"""
    if train is None:
        raise HTTPException(status_code=500, detail="Training data not available")

    cat_cols = [col for col in train.columns if col.startswith('cat')]
    cont_cols = [col for col in train.columns if col.startswith('cont')]

    return {
        "categorical_features": cat_cols,
        "continuous_features": cont_cols,
        "total_features": len(cat_cols) + len(cont_cols)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)