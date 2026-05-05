"""
Fraud Detection Agent - LLM-powered fraud detection.
Combines ML signals with LLM reasoning for fraud analysis.
"""

import json
import logging
from typing import Dict, Optional
from app.models.fraud_model import FraudDetectionModel
from app.llm.llm_client import LLMClient
from config import GROQ_API_KEY, USE_LLM_FOR_FRAUD
import pandas as pd
import os

logger = logging.getLogger(__name__)


class FraudAgent:
    """
    LLM-powered fraud detection agent.
    Uses ML signals as input to LLM for sophisticated fraud analysis.
    """
    
    SYSTEM_PROMPT = """You are a fraud detection expert with deep knowledge of:
- Payment fraud patterns and schemes
- Money laundering indicators
- Account takeover signs
- Anomaly detection
- Risk assessment

Analyze transactions for fraud signals combining:
1. Quantitative signals (ML scores)
2. Behavioral patterns
3. Contextual information
4. Known fraud indicators

Provide clear, evidence-based reasoning for fraud assessments.
Be conservative - flag anything questionable for manual review."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize fraud agent with LLM and ML model.
        
        Args:
            model_path: Optional path to pre-trained fraud model
        """
        self.model = FraudDetectionModel()
        self.model_trained = False
        
        # Initialize LLM client
        self.llm = LLMClient(api_key=GROQ_API_KEY)
        self.use_llm = USE_LLM_FOR_FRAUD
        logger.info(f"FraudAgent initialized (LLM enabled: {self.use_llm})")
        
        # Try to load pre-trained model or train from data
        if model_path and os.path.exists(model_path):
            self.model.load(model_path)
            self.model_trained = True
        else:
            self._train_model_with_sample_data()
    
    def _train_model_with_sample_data(self):
        """Train model with sample transaction data."""
        try:
            csv_path = 'data/transactions.csv'
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                self.model.train_from_dataframe(df)
                self.model_trained = True
        except Exception as e:
            logger.warning(f"Could not train fraud model: {e}")
    
    def analyze_transaction(self, transaction: Dict) -> Dict:
        """
        Analyze a single transaction for fraud using LLM + ML.
        
        Args:
            transaction: Transaction dict with fields:
                - amount: Transaction amount
                - time_of_day: Hour of transaction (0-23)
                - location: Country/location
                - merchant_category: Type of merchant
                - frequency_30d: Recent transaction frequency
                - account_age_days: Age of account in days
                
        Returns:
            Structured fraud assessment
        """
        try:
            transaction_id = transaction.get('transaction_id', 'UNKNOWN')
            
            # Get ML-based signals
            ml_signals = self._get_ml_signals(transaction)
            
            # Use LLM for sophisticated analysis if enabled
            if self.use_llm:
                llm_analysis = self._llm_analyze(transaction, ml_signals)
                return llm_analysis
            else:
                # Fallback to ML + rule-based
                return self._hybrid_assessment(transaction, ml_signals)
        
        except Exception as e:
            logger.error(f"Error analyzing transaction {transaction_id}: {e}")
            return {
                'transaction_id': transaction.get('transaction_id', 'ERROR'),
                'fraud_risk': 'UNKNOWN',
                'confidence': 0.0,
                'error': str(e),
                'recommended_action': 'MANUAL_REVIEW',
                'alert_level': 'ERROR'
            }
    
    def _get_ml_signals(self, transaction: Dict) -> Dict:
        """Get ML model predictions and signals."""
        signals = {
            'rule_based_score': 0.0,
            'ml_model_available': self.model_trained,
            'ml_score': 0.0,
            'risk_indicators': []
        }
        
        if self.model_trained:
            try:
                ml_result = self.model.predict(transaction)
                signals['ml_score'] = ml_result.get('fraud_score', 0.0)
                signals['ml_risk_level'] = ml_result.get('fraud_risk', 'LOW')
            except Exception as e:
                logger.warning(f"ML model predict error: {e}")
        
        # Add rule-based signals
        rule_result = self._get_rule_signals(transaction)
        signals['rule_based_score'] = rule_result['fraud_score']
        signals['risk_indicators'] = rule_result['reasons']
        
        return signals
    
    def _get_rule_signals(self, transaction: Dict) -> Dict:
        """Get rule-based fraud signals."""
        reasons = []
        fraud_score = 0.0
        
        amount = float(transaction.get('amount', 0))
        if amount > 5000:
            reasons.append("High transaction amount (>$5000)")
            fraud_score += 0.2
        
        time_of_day = float(transaction.get('time_of_day', 0))
        if time_of_day < 4 or time_of_day > 22:
            reasons.append(f"Unusual transaction time ({time_of_day}:00)")
            fraud_score += 0.1
        
        account_age = float(transaction.get('account_age_days', 0))
        if account_age < 30:
            reasons.append(f"New account ({account_age} days old)")
            fraud_score += 0.15
        
        location = transaction.get('location', 'US')
        high_risk_locations = ['UK', 'CN', 'JP', 'BR', 'RU', 'DZ', 'NG', 'KE', 'VN', 'GH', 'PK']
        if location in high_risk_locations:
            reasons.append(f"High-risk location: {location}")
            fraud_score += 0.25
        
        merchant = transaction.get('merchant_category', 'grocery')
        high_risk_merchants = ['jewelry', 'luxury_goods']
        if merchant in high_risk_merchants:
            reasons.append(f"High-risk merchant: {merchant}")
            fraud_score += 0.2
        
        frequency = float(transaction.get('frequency_30d', 0))
        if frequency > 50:
            reasons.append("Unusually high transaction frequency")
            fraud_score += 0.15
        
        return {
            'fraud_score': min(1.0, fraud_score),
            'reasons': reasons if reasons else ["No obvious fraud indicators"]
        }
    
    def _llm_analyze(self, transaction: Dict, ml_signals: Dict) -> Dict:
        """Analyze transaction using LLM."""
        try:
            prompt = f"""
Analyze this financial transaction for fraud risk:

Transaction Details:
{json.dumps(transaction, indent=2)}

Machine Learning Signals:
{json.dumps(ml_signals, indent=2)}

Known Fraud Indicators to Consider:
{json.dumps(self.get_fraud_indicators(), indent=2)}

Provide a comprehensive fraud risk assessment.

Return JSON with:
{{
    "fraud_risk": "LOW/MEDIUM/HIGH",
    "fraud_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasons": ["reason1", "reason2", ...],
    "risk_indicators_triggered": ["indicator1", "indicator2", ...],
    "behavioral_analysis": "analysis of behavioral signals",
    "recommended_action": "APPROVE/VERIFY/BLOCK",
    "reasoning": "detailed explanation"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1024
            )
            
            # Ensure required fields
            result['transaction_id'] = transaction.get('transaction_id', 'UNKNOWN')
            result['status'] = 'ANALYZED'
            result['alert_level'] = 'CRITICAL' if result.get('fraud_risk') == 'HIGH' else \
                                    'WARNING' if result.get('fraud_risk') == 'MEDIUM' else 'NONE'
            
            return result
        
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            # Fallback to hybrid assessment
            return self._hybrid_assessment(transaction, ml_signals)
    
    def _hybrid_assessment(self, transaction: Dict, ml_signals: Dict) -> Dict:
        """Hybrid ML + rule-based assessment."""
        ml_score = ml_signals.get('ml_score', 0.0)
        rule_score = ml_signals.get('rule_based_score', 0.0)
        
        # Weighted combination
        combined_score = 0.6 * ml_score + 0.4 * rule_score
        
        if combined_score > 0.6:
            fraud_risk = 'HIGH'
            action = 'BLOCK'
        elif combined_score > 0.3:
            fraud_risk = 'MEDIUM'
            action = 'VERIFY'
        else:
            fraud_risk = 'LOW'
            action = 'APPROVE'
        
        return {
            'transaction_id': transaction.get('transaction_id', 'UNKNOWN'),
            'fraud_risk': fraud_risk,
            'fraud_score': combined_score,
            'confidence': min(0.95, 0.5 + combined_score),
            'reasons': ml_signals.get('risk_indicators', []),
            'recommended_action': action,
            'alert_level': 'CRITICAL' if fraud_risk == 'HIGH' else \
                          'WARNING' if fraud_risk == 'MEDIUM' else 'NONE',
            'status': 'ANALYZED'
        }
    
    def batch_analyze(self, transactions: list) -> Dict:
        """
        Analyze multiple transactions efficiently.
        
        Args:
            transactions: List of transaction dicts
            
        Returns:
            Dict with analysis summary
        """
        results = []
        fraud_count = 0
        
        for txn in transactions:
            result = self.analyze_transaction(txn)
            results.append(result)
            if result.get('fraud_risk') == 'HIGH':
                fraud_count += 1
        
        return {
            'total_transactions': len(transactions),
            'transactions_analyzed': results,
            'fraud_count': fraud_count,
            'fraud_rate': fraud_count / len(transactions) if transactions else 0,
            'summary': {
                'high_risk': sum(1 for r in results if r.get('fraud_risk') == 'HIGH'),
                'medium_risk': sum(1 for r in results if r.get('fraud_risk') == 'MEDIUM'),
                'low_risk': sum(1 for r in results if r.get('fraud_risk') == 'LOW'),
            }
        }
    
    def get_fraud_indicators(self) -> Dict:
        """Get list of known fraud indicators."""
        return {
            'high_amount': {'threshold': 5000, 'risk_increase': 0.2},
            'unusual_time': {'hours': [0, 1, 2, 3, 4, 23], 'risk_increase': 0.1},
            'new_account': {'days': 30, 'risk_increase': 0.15},
            'high_risk_locations': {
                'countries': ['UK', 'CN', 'JP', 'BR', 'RU', 'DZ', 'NG', 'KE', 'VN', 'GH', 'PK'],
                'risk_increase': 0.25
            },
            'high_risk_merchants': {
                'categories': ['jewelry', 'luxury_goods'],
                'risk_increase': 0.2
            }
        }
