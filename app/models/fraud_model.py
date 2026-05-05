"""
Fraud detection model using IsolationForest and ML techniques.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, Tuple, Optional
import pickle
import os


class FraudDetectionModel:
    """ML-based fraud detection using IsolationForest."""
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize fraud detection model.
        
        Args:
            contamination: Expected proportion of fraud in data
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.is_trained = False
        self.feature_names = []
        self.categorical_features = {}
    
    def preprocess_transaction(self, transaction: Dict) -> np.ndarray:
        """
        Preprocess a single transaction for prediction.
        
        Args:
            transaction: Dict with transaction features
            
        Returns:
            numpy array of features
        """
        features = []
        
        # Numerical features
        features.append(float(transaction.get('amount', 0)))
        features.append(float(transaction.get('time_of_day', 0)))
        features.append(float(transaction.get('frequency_30d', 0)))
        features.append(float(transaction.get('account_age_days', 0)))
        
        # Categorical features (encoded as location and merchant category)
        location = transaction.get('location', 'US')
        merchant = transaction.get('merchant_category', 'grocery')
        
        # Simple encoding: high risk locations and merchants
        high_risk_locations = ['UK', 'CN', 'JP', 'BR', 'RU', 'DZ', 'NG', 'KE', 'VN', 'GH', 'PK']
        location_risk = 1.0 if location in high_risk_locations else 0.0
        features.append(location_risk)
        
        high_risk_merchants = ['jewelry', 'luxury_goods']
        merchant_risk = 1.0 if merchant in high_risk_merchants else 0.0
        features.append(merchant_risk)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X: np.ndarray):
        """
        Train the isolation forest model.
        
        Args:
            X: Training features of shape (n_samples, n_features)
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
    
    def train_from_dataframe(self, df: pd.DataFrame):
        """
        Train from a pandas DataFrame.
        
        Args:
            df: DataFrame with transaction data
        """
        # Extract features
        features = []
        for _, row in df.iterrows():
            transaction = row.to_dict()
            X = self.preprocess_transaction(transaction)
            features.append(X[0])
        
        X = np.array(features)
        self.train(X)
    
    def predict(self, transaction: Dict) -> Dict:
        """
        Predict fraud for a single transaction.
        
        Args:
            transaction: Dict with transaction features
            
        Returns:
            Dict with fraud_risk, score, reason, confidence
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        # Preprocess
        X = self.preprocess_transaction(transaction)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        score = self.model.score_samples(X_scaled)[0]
        
        # Normalize score to 0-1 range (lower score = more anomalous)
        # score_samples returns negative values for anomalies
        anomaly_score = max(0, min(1, (-score + 5) / 10))
        
        # Determine fraud risk
        reasons = []
        fraud_indicators = 0
        
        # Check various fraud indicators
        amount = float(transaction.get('amount', 0))
        if amount > 5000:
            reasons.append("Unusually high transaction amount")
            fraud_indicators += 1
        
        time_of_day = float(transaction.get('time_of_day', 0))
        if time_of_day < 4 or time_of_day > 22:
            reasons.append("Transaction at unusual hour")
            fraud_indicators += 1
        
        account_age = float(transaction.get('account_age_days', 0))
        if account_age < 30:
            reasons.append("New account with transaction")
            fraud_indicators += 1
        
        location = transaction.get('location', 'US')
        high_risk_locations = ['UK', 'CN', 'JP', 'BR', 'RU', 'DZ', 'NG', 'KE', 'VN', 'GH', 'PK']
        if location in high_risk_locations:
            reasons.append(f"High-risk location: {location}")
            fraud_indicators += 1
        
        merchant = transaction.get('merchant_category', 'grocery')
        high_risk_merchants = ['jewelry', 'luxury_goods']
        if merchant in high_risk_merchants:
            reasons.append(f"High-risk merchant category: {merchant}")
            fraud_indicators += 1
        
        frequency = float(transaction.get('frequency_30d', 0))
        if frequency == 0 and merchant in high_risk_merchants:
            reasons.append("No history of luxury purchases")
            fraud_indicators += 1
        
        # Calculate fraud risk
        if prediction == -1:  # Anomaly detected
            if fraud_indicators >= 3:
                fraud_risk = "HIGH"
                confidence = min(0.99, 0.5 + (fraud_indicators * 0.15))
            else:
                fraud_risk = "MEDIUM"
                confidence = min(0.95, 0.3 + (fraud_indicators * 0.15))
        else:
            if fraud_indicators >= 2:
                fraud_risk = "MEDIUM"
                confidence = 0.6
            else:
                fraud_risk = "LOW"
                confidence = max(0.95, 1.0 - anomaly_score)
        
        return {
            'fraud_risk': fraud_risk,
            'anomaly_score': float(anomaly_score),
            'fraud_indicators': fraud_indicators,
            'reasons': reasons if reasons else ["No obvious fraud indicators"],
            'confidence': float(confidence),
            'ml_prediction': 'FRAUD' if prediction == -1 else 'NORMAL'
        }
    
    def save(self, filepath: str):
        """Save trained model."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
    
    def load(self, filepath: str):
        """Load trained model."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
