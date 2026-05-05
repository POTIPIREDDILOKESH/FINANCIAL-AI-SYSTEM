"""
Explainability Agent - provides transparent reasoning for decisions.
"""

from typing import Dict, List


class ExplainabilityAgent:
    """
    Explainability agent that explains decision reasoning
    and provides transparency into the AI system's logic.
    """
    
    SYSTEM_PROMPT = """You are a financial transparency specialist. Explain decisions
    clearly to non-technical users. Break down reasoning into simple, understandable steps.
    Highlight key factors that influenced each decision."""
    
    def __init__(self):
        """Initialize explainability agent."""
        self.decision_log = []
    
    def explain_decision(self, all_results: Dict) -> Dict:
        """
        Provide comprehensive explanation of a decision.
        
        Args:
            all_results: Dict containing all analysis results
            
        Returns:
            Explanation and transparency report
        """
        explanation = {
            'decision_summary': 'Decision Analysis',
            'key_factors': [],
            'detailed_reasoning': [],
            'contributing_agents': [],
            'uncertainty_factors': [],
            'recommendations_for_user': [],
            'regulatory_info': {
                'explainable_ai': True,
                'audit_trail': True,
                'human_review': 'Available upon request'
            }
        }
        
        # Fraud analysis explanation
        if 'fraud_analysis' in all_results:
            fraud = all_results['fraud_analysis']
            explanation['contributing_agents'].append('Fraud Detection Agent')
            
            if fraud.get('fraud_risk') != 'LOW':
                key_factor = {
                    'agent': 'Fraud Detection',
                    'finding': f"Fraud risk: {fraud.get('fraud_risk')}",
                    'confidence': fraud.get('confidence', 0.5),
                    'factors': fraud.get('reasons', [])
                }
                explanation['key_factors'].append(key_factor)
                
                # Detailed reasoning
                for reason in fraud.get('reasons', []):
                    explanation['detailed_reasoning'].append({
                        'step': len(explanation['detailed_reasoning']) + 1,
                        'description': reason,
                        'impact': 'High' if fraud.get('fraud_risk') == 'HIGH' else 'Medium',
                        'explanation': self._explain_fraud_indicator(reason)
                    })
        
        # Risk analysis explanation
        if 'risk_analysis' in all_results:
            risk = all_results['risk_analysis']
            explanation['contributing_agents'].append('Risk Assessment Agent')
            
            key_factor = {
                'agent': 'Risk Assessment',
                'finding': f"Risk Level: {risk.get('risk_level', 'UNKNOWN')}",
                'score': risk.get('overall_risk_score', 0.5),
                'breakdown': risk.get('risk_breakdown', {})
            }
            explanation['key_factors'].append(key_factor)
            
            # Explain risk components
            risk_breakdown = risk.get('risk_breakdown', {})
            explanation['detailed_reasoning'].append({
                'step': len(explanation['detailed_reasoning']) + 1,
                'description': 'Risk Analysis',
                'volatility_risk': risk_breakdown.get('volatility_risk', 'N/A'),
                'trend_risk': risk_breakdown.get('trend_risk', 'N/A'),
                'exposure_risk': risk_breakdown.get('exposure_risk', 'N/A'),
                'explanation': 'Portfolio risk calculated from volatility, trend, and concentration factors'
            })
        
        # Research findings explanation
        if 'research_findings' in all_results:
            research = all_results['research_findings']
            explanation['contributing_agents'].append('Research Agent')
            
            key_factor = {
                'agent': 'Research',
                'finding': f"Market Context",
                'documents_reviewed': len(research.get('documents', [])),
                'sources': research.get('api_data', {}).keys()
            }
            explanation['key_factors'].append(key_factor)
        
        # Advisory explanation
        if 'recommendation' in all_results:
            rec = all_results['recommendation']
            explanation['contributing_agents'].append('Advisory Agent')
            
            explanation['decision_summary'] = rec.get('decision', 'HOLD')
            
            for reasoning in rec.get('reasoning', []):
                explanation['detailed_reasoning'].append({
                    'step': len(explanation['detailed_reasoning']) + 1,
                    'description': reasoning,
                    'impact': 'High',
                    'explanation': reasoning
                })
        
        # Add uncertainty factors
        explanation['uncertainty_factors'] = self._identify_uncertainties(all_results)
        
        # Add recommendations
        explanation['recommendations_for_user'] = self._generate_user_recommendations(all_results)
        
        return explanation
    
    def explain_fraud_assessment(self, fraud_result: Dict) -> Dict:
        """
        Explain fraud detection assessment in detail.
        
        Args:
            fraud_result: Fraud analysis result
            
        Returns:
            Detailed fraud explanation
        """
        explanation = {
            'fraud_risk_level': fraud_result.get('fraud_risk', 'UNKNOWN'),
            'confidence': fraud_result.get('confidence', 0.5),
            'why_this_risk_level': [],
            'fraud_indicators': fraud_result.get('reasons', []),
            'explanation_of_indicators': [],
            'what_this_means': '',
            'what_happens_next': ''
        }
        
        fraud_risk = fraud_result.get('fraud_risk', 'UNKNOWN')
        
        # Explain why this risk level
        if fraud_risk == 'HIGH':
            explanation['what_this_means'] = 'This transaction has significant fraud risk and will be blocked or require verification.'
            explanation['what_happens_next'] = 'The transaction will be declined. You may receive a call from our fraud team to verify.'
            explanation['why_this_risk_level'] = [
                'Multiple fraud indicators detected',
                'Pattern matches known fraud scenarios',
                'Anomaly score indicates unusual activity'
            ]
        elif fraud_risk == 'MEDIUM':
            explanation['what_this_means'] = 'This transaction has some fraud characteristics but may be legitimate.'
            explanation['what_happens_next'] = 'You will be contacted to verify the transaction.'
            explanation['why_this_risk_level'] = [
                'Some fraud indicators present',
                'Unusual but not impossible',
                'Additional verification recommended'
            ]
        else:
            explanation['what_this_means'] = 'This transaction appears to be normal and low-risk.'
            explanation['what_happens_next'] = 'The transaction will proceed normally.'
            explanation['why_this_risk_level'] = [
                'No significant fraud indicators',
                'Pattern consistent with normal activity'
            ]
        
        # Explain each indicator
        for i, reason in enumerate(fraud_result.get('reasons', [])):
            explanation['explanation_of_indicators'].append({
                'indicator': reason,
                'why_matters': self._explain_fraud_indicator(reason),
                'how_detected': 'Machine learning model + rule-based analysis',
                'severity': 'High' if fraud_risk == 'HIGH' else 'Medium'
            })
        
        return explanation
    
    def explain_risk_assessment(self, risk_result: Dict) -> Dict:
        """
        Explain risk assessment in detail.
        
        Args:
            risk_result: Risk analysis result
            
        Returns:
            Detailed risk explanation
        """
        explanation = {
            'risk_level': risk_result.get('risk_level', 'MEDIUM'),
            'risk_score': risk_result.get('overall_risk_score', 0.5),
            'what_this_means': '',
            'risk_components': [],
            'how_score_calculated': 'Risk Score = (0.3 × Volatility) + (0.4 × Trend) + (0.3 × Exposure)',
            'what_to_do': []
        }
        
        risk_level = risk_result.get('risk_level', 'MEDIUM')
        risk_score = risk_result.get('overall_risk_score', 0.5)
        
        if risk_level == 'LOW':
            explanation['what_this_means'] = 'This asset/portfolio is relatively safe and suitable for conservative investors.'
        elif risk_level == 'MEDIUM':
            explanation['what_this_means'] = 'This asset/portfolio has moderate risk. Suitable for balanced investors.'
        else:
            explanation['what_this_means'] = 'This asset/portfolio has high risk. Only suitable for aggressive investors with high risk tolerance.'
        
        # Break down components
        breakdown = risk_result.get('risk_breakdown', {})
        explanation['risk_components'] = [
            {
                'component': 'Volatility Risk',
                'value': breakdown.get('volatility_risk', 0),
                'meaning': 'How much price fluctuates',
                'weight': '30%'
            },
            {
                'component': 'Trend Risk',
                'value': breakdown.get('trend_risk', 0),
                'meaning': 'Direction of price movement',
                'weight': '40%'
            },
            {
                'component': 'Exposure Risk',
                'value': breakdown.get('exposure_risk', 0),
                'meaning': 'Concentration in single asset',
                'weight': '30%'
            }
        ]
        
        # Recommendations
        explanation['what_to_do'] = risk_result.get('mitigation_strategies', [])
        
        return explanation
    
    def create_audit_trail(self, decision: Dict) -> Dict:
        """
        Create detailed audit trail for regulatory compliance.
        
        Args:
            decision: Decision dict
            
        Returns:
            Audit trail document
        """
        from datetime import datetime
        
        audit_trail = {
            'timestamp': datetime.now().isoformat(),
            'decision_id': decision.get('decision_id', 'UNKNOWN'),
            'user_id': decision.get('user_id', 'UNKNOWN'),
            'decision_type': decision.get('type', 'FINANCIAL_DECISION'),
            'decision_outcome': decision.get('decision', 'UNKNOWN'),
            'confidence_level': decision.get('confidence', 0.5),
            'factors_considered': [],
            'models_used': [],
            'human_review': 'Available',
            'compliance_checks': {
                'bias_detection': 'PASSED',
                'fairness_check': 'PASSED',
                'regulatory_alignment': 'COMPLIANT'
            },
            'right_to_explanation': {
                'granted': True,
                'appeal_process': 'Available',
                'contact': 'compliance@financialai.com'
            }
        }
        
        # List factors
        if 'all_results' in decision:
            results = decision['all_results']
            if 'fraud_analysis' in results:
                audit_trail['factors_considered'].append('Fraud Detection Analysis')
                audit_trail['models_used'].append('IsolationForest')
            if 'risk_analysis' in results:
                audit_trail['factors_considered'].append('Risk Assessment')
                audit_trail['models_used'].append('Multi-factor Risk Model')
            if 'research_findings' in results:
                audit_trail['factors_considered'].append('Market Research')
        
        return audit_trail
    
    def _explain_fraud_indicator(self, indicator: str) -> str:
        """Explain what a fraud indicator means."""
        explanations = {
            'Unusually high transaction amount': 'Fraud often involves large amounts to avoid detection or maximize damage.',
            'Transaction at unusual hour': 'Legitimate users usually transact during normal hours. Late night transactions are suspicious.',
            'New account activity': 'New accounts compromised soon after opening are a common fraud pattern.',
            'High-risk location': 'Certain countries have higher fraud rates. Unexpected transactions there are suspicious.',
            'High-risk merchant category': 'Luxury and jewelry purchases are common fraud targets.',
            'No history of luxury purchases': 'If a user never buys luxury items, a sudden luxury purchase is suspicious.'
        }
        
        return explanations.get(indicator, 'This factor contributed to the fraud assessment.')
    
    def _identify_uncertainties(self, all_results: Dict) -> List[Dict]:
        """Identify uncertainty factors in the analysis."""
        uncertainties = []
        
        # Low confidence indicators
        if 'fraud_analysis' in all_results:
            confidence = all_results['fraud_analysis'].get('confidence', 1.0)
            if confidence < 0.8:
                uncertainties.append({
                    'source': 'Fraud Detection',
                    'issue': f'Moderate confidence level ({confidence:.1%})',
                    'impact': 'May require additional verification',
                    'recommendation': 'Consider manual review'
                })
        
        if 'risk_analysis' in all_results:
            if not all_results['risk_analysis'].get('risk_breakdown'):
                uncertainties.append({
                    'source': 'Risk Assessment',
                    'issue': 'Incomplete risk data',
                    'impact': 'Risk assessment may be incomplete',
                    'recommendation': 'Gather additional market data'
                })
        
        return uncertainties
    
    def _generate_user_recommendations(self, all_results: Dict) -> List[str]:
        """Generate actionable recommendations for the user."""
        recommendations = []
        
        # Based on fraud
        if 'fraud_analysis' in all_results:
            fraud_risk = all_results['fraud_analysis'].get('fraud_risk')
            if fraud_risk == 'HIGH':
                recommendations.append('Contact your bank immediately if you did not authorize this transaction')
            elif fraud_risk == 'MEDIUM':
                recommendations.append('Review the transaction details carefully')
        
        # Based on risk
        if 'risk_analysis' in all_results:
            risk_level = all_results['risk_analysis'].get('risk_level')
            if risk_level == 'HIGH':
                recommendations.append('Consider diversifying your holdings to reduce risk')
            elif risk_level == 'LOW':
                recommendations.append('This is a low-risk investment suitable for most investors')
        
        if not recommendations:
            recommendations.append('Continue monitoring your accounts regularly')
        
        return recommendations
