"""
Advisory Agent - LLM-powered financial recommendations.
Generates actionable recommendations based on all analyses.
"""

import json
import logging
from typing import Dict, List, Optional
from app.llm.llm_client import LLMClient
from config import GROQ_API_KEY, USE_LLM_FOR_ADVISORY

logger = logging.getLogger(__name__)


class AdvisoryAgent:
    """
    LLM-powered advisory agent using analysis from other agents.
    Generates actionable,well-reasoned recommendations.
    """
    
    SYSTEM_PROMPT = """You are a senior financial advisor with expertise in:
- Investment recommendations
- Risk-adjusted decision making
- Credit analysis and lending decisions
- Transaction verification
- Portfolio optimization

Generate clear, actionable recommendations based on:
1. Fraud risk signals
2. Financial risk metrics  
3. Market research and sentiment
4. Business context

Always include disclaimers and confidence levels.
Be conservative: flag for manual review when uncertain."""
    
    def __init__(self):
        """Initialize advisory agent with LLM."""
        self.llm = LLMClient(api_key=GROQ_API_KEY)
        self.use_llm = USE_LLM_FOR_ADVISORY
        logger.info(f"AdvisoryAgent initialized (LLM enabled: {self.use_llm})")
    
    def generate_recommendation(self, analysis_results: Dict) -> Dict:
        """
        Generate a recommendation based on all analyses using LLM.
        
        Args:
            analysis_results: Dict with fraud, risk, research analyses
            
        Returns:
            Recommendation in standardized format
        """
        try:
            if self.use_llm:
                return self._llm_recommendation(analysis_results)
            else:
                return self._rule_based_recommendation(analysis_results)
        
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return {
                'decision': 'MANUAL_REVIEW_REQUIRED',
                'confidence_score': 0.0,
                'error': str(e),
                'reasoning': ['Error in LLM recommendation generation'],
                'disclaimer': 'This is not investment advice. Consult a financial advisor.'
            }
    
    def _llm_recommendation(self, analysis_results: Dict) -> Dict:
        """Generate recommendation using LLM."""
        try:
            prompt = f"""
Based on comprehensive financial analysis, generate a specific recommendation.

Analysis Results:
{json.dumps(analysis_results, indent=2)}

Provide a professional financial recommendation with:
- Clear decision (APPROVE/REJECT/VERIFY/HOLD/BUY/SELL)
- Confidence level (0.0-1.0)
- Key factors driving the decision
- Risk assessment
- Conditions or requirements
- Next steps

Return JSON with:
{{
    "decision": "APPROVE/REJECT/VERIFY/HOLD/BUY/SELL",
    "confidence_score": 0.0-1.0,
    "reasoning": ["reason1", "reason2", ...],
    "risk_level": "LOW/MEDIUM/HIGH",
    "key_factors": ["factor1", "factor2", ...],
    "conditions": ["condition1", "condition2", ...] or [],
    "next_steps": ["step1", "step2", ...],
    "disclaimer": "Professional disclaimer"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Ensure required fields
            result['sources'] = self._identify_sources(analysis_results)
            
            return result
        
        except Exception as e:
            logger.error(f"LLM recommendation error: {e}")
            return self._rule_based_recommendation(analysis_results)
    
    def _rule_based_recommendation(self, analysis_results: Dict) -> Dict:
        """Fallback rule-based recommendation."""
        recommendation = {
            'decision': 'HOLD',
            'reasoning': [],
            'risk_level': 'MEDIUM',
            'confidence_score': 0.5,
            'sources': [],
            'conditions': [],
            'disclaimer': 'This is not investment advice. Consult a financial advisor.'
        }
        
        fraud_result = analysis_results.get('fraud_analysis', {})
        risk_result = analysis_results.get('risk_analysis', {})
        research_result = analysis_results.get('research_findings', {})
        
        # Fraud analysis
        fraud_risk = fraud_result.get('fraud_risk', 'LOW')
        
        if fraud_risk == 'HIGH':
            recommendation['decision'] = 'REJECT'
            recommendation['reasoning'].append('High fraud risk detected')
            recommendation['risk_level'] = 'HIGH'
        elif fraud_risk == 'MEDIUM':
            recommendation['decision'] = 'VERIFY'
            recommendation['reasoning'].append('Transaction requires verification')
        else:
            recommendation['decision'] = 'APPROVE'
        
        # Risk analysis
        if risk_result:
            risk_level = risk_result.get('transaction_risk_level', 'MEDIUM')
            risk_score = float(risk_result.get('transaction_risk_score', 0.5))
            
            recommendation['risk_level'] = risk_level
            
            if risk_level == 'HIGH' and recommendation['decision'] == 'APPROVE':
                recommendation['decision'] = 'VERIFY'
                recommendation['reasoning'].append(f'High transaction risk: {risk_score:.2f}')
            elif risk_level == 'LOW':
                recommendation['confidence_score'] += 0.15
                recommendation['reasoning'].append(f'Low transaction risk: {risk_score:.2f}')
        
        # Research findings
        if research_result:
            recommendation['reasoning'].append('Market research considered')
        
        # Calculate confidence
        fraud_conf = float(fraud_result.get('confidence', 0.5))
        risk_conf = float(risk_result.get('transaction_risk_score', 0.5)) if risk_result else 0.5
        recommendation['confidence_score'] = round((fraud_conf + risk_conf) / 2, 2)
        recommendation['confidence_score'] = max(0.0, min(1.0, recommendation['confidence_score']))
        
        # Add sources
        recommendation['sources'] = self._identify_sources(analysis_results)
        
        return recommendation
    
    def _identify_sources(self, analysis_results: Dict) -> List[str]:
        """Identify which analyses contributed to recommendation."""
        sources = []
        if analysis_results.get('fraud_analysis'):
            sources.append('Fraud Detection')
        if analysis_results.get('risk_analysis'):
            sources.append('Risk Assessment')
        if analysis_results.get('research_findings'):
            sources.append('Market Research')
        return sources
    
    def generate_approval_decision(self, credit_analysis: Dict) -> Dict:
        """
        Generate loan/credit approval decision using LLM.
        
        Args:
            credit_analysis: Credit analysis results
            
        Returns:
            Approval decision
        """
        try:
            if self.use_llm:
                return self._llm_approval(credit_analysis)
            else:
                return self._rule_based_approval(credit_analysis)
        
        except Exception as e:
            logger.error(f"Error generating approval: {e}")
            return {
                'decision': 'MANUAL_REVIEW_REQUIRED',
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def _llm_approval(self, credit_analysis: Dict) -> Dict:
        """Generate approval decision using LLM."""
        try:
            prompt = f"""
Make a credit/loan approval decision based on this analysis:

{json.dumps(credit_analysis, indent=2)}

Return JSON with:
{{
    "decision": "APPROVE/CONDITIONAL/REJECT",
    "confidence_score": 0.0-1.0,
    "reasoning": ["reason1", "reason2", ...],
    "risk_level": "LOW/MEDIUM/HIGH",
    "conditions": ["condition1", "condition2", ...] or [],
    "required_documents": ["doc1", "doc2", ...] or [],
    "recommendation": "lending recommendation"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=800
            )
            
            return result
        
        except Exception as e:
            logger.error(f"LLM approval error: {e}")
            return self._rule_based_approval(credit_analysis)
    
    def _rule_based_approval(self, credit_analysis: Dict) -> Dict:
        """Fallback rule-based approval."""
        decision = {
            'decision': 'MANUAL_REVIEW_REQUIRED',
            'reasoning': [],
            'risk_level': 'MEDIUM',
            'confidence_score': 0.5,
            'conditions': []
        }
        
        credit_score = credit_analysis.get('credit_score', 650)
        debt_to_income = credit_analysis.get('debt_to_income', 0.5)
        
        if credit_score >= 750 and debt_to_income < 0.4:
            decision['decision'] = 'APPROVE'
            decision['confidence_score'] = 0.9
        elif credit_score >= 700 and debt_to_income < 0.5:
            decision['decision'] = 'CONDITIONAL'
            decision['conditions'].append(f'Minimum credit score verification: {credit_score}')
            decision['confidence_score'] = 0.7
        else:
            decision['decision'] = 'REJECT'
            decision['confidence_score'] = 0.6
        
        return decision
        
        # DTI evaluation
        if debt_to_income < 0.36:
            approval_score += 0.3
            decision['reasoning'].append(f'Acceptable debt-to-income ratio: {debt_to_income:.1%}')
        elif debt_to_income < 0.43:
            approval_score += 0.15
            decision['reasoning'].append(f'Borderline debt-to-income ratio: {debt_to_income:.1%}')
        else:
            approval_score -= 0.2
            decision['reasoning'].append(f'High debt-to-income ratio: {debt_to_income:.1%}')
        
        # Payment history
        if payment_history == 'excellent':
            approval_score += 0.2
        elif payment_history == 'good':
            approval_score += 0.1
        elif payment_history == 'fair':
            approval_score += 0.0
        else:
            approval_score -= 0.15
        
        # Income stability
        if income_stability == 'stable':
            approval_score += 0.2
        elif income_stability == 'moderate':
            approval_score += 0.1
        else:
            approval_score -= 0.1
        
        # Convert score to decision
        if approval_score > 0.7:
            decision['decision'] = 'APPROVE'
            decision['confidence_score'] = 0.9
            decision['risk_level'] = 'LOW'
        elif approval_score > 0.3:
            decision['decision'] = 'APPROVE_WITH_CONDITIONS'
            decision['confidence_score'] = 0.7
            decision['risk_level'] = 'MEDIUM'
            decision['conditions'] = [
                'Require proof of income',
                'Require collateral',
                'Higher interest rate'
            ]
        elif approval_score > 0.0:
            decision['decision'] = 'REVIEW'
            decision['confidence_score'] = 0.5
            decision['risk_level'] = 'MEDIUM'
            decision['conditions'] = ['Manual underwriting required']
        else:
            decision['decision'] = 'REJECT'
            decision['confidence_score'] = 0.85
            decision['risk_level'] = 'HIGH'
        
        return decision
    
    def generate_trading_recommendation(self, market_data: Dict) -> Dict:
        """
        Generate trading recommendation.
        
        Args:
            market_data: Market and asset data
            
        Returns:
            Trading recommendation
        """
        recommendation = {
            'action': 'HOLD',
            'entry_point': None,
            'exit_point': None,
            'stop_loss': None,
            'take_profit': None,
            'risk_reward_ratio': 0,
            'timeframe': 'medium_term',
            'confidence': 0.5
        }
        
        current_price = market_data.get('current_price', 100)
        volatility = market_data.get('volatility', 0.2)
        trend = market_data.get('trend', 'stable')
        
        # Calculate levels
        support = current_price * (1 - volatility * 2)
        resistance = current_price * (1 + volatility * 2)
        
        # Generate recommendation
        if trend == 'up':
            recommendation['action'] = 'BUY'
            recommendation['entry_point'] = current_price
            recommendation['stop_loss'] = support
            recommendation['take_profit'] = resistance
        elif trend == 'down':
            recommendation['action'] = 'SELL'
            recommendation['entry_point'] = current_price
            recommendation['stop_loss'] = resistance
            recommendation['take_profit'] = support
        else:
            recommendation['action'] = 'HOLD'
            recommendation['entry_point'] = current_price
        
        # Risk reward
        if recommendation['take_profit'] and recommendation['stop_loss']:
            potential_profit = recommendation['take_profit'] - recommendation['entry_point']
            potential_loss = recommendation['entry_point'] - recommendation['stop_loss']
            if potential_loss > 0:
                recommendation['risk_reward_ratio'] = potential_profit / potential_loss
        
        recommendation['confidence'] = min(1.0, max(0.3, 0.5 + volatility))
        
        return recommendation
    
    def generate_portfolio_advice(self, portfolio_analysis: Dict) -> Dict:
        """
        Generate portfolio management advice.
        
        Args:
            portfolio_analysis: Portfolio risk and holdings analysis
            
        Returns:
            Portfolio advice
        """
        advice = {
            'overall_recommendation': 'HOLD',
            'actions': [],
            'rebalancing': None,
            'diversification_advice': [],
            'risk_tolerance_alignment': 'balanced'
        }
        
        risk_level = portfolio_analysis.get('portfolio_risk_level', 'MEDIUM')
        concentration_risk = portfolio_analysis.get('concentration_risk', 'MEDIUM')
        
        if risk_level == 'HIGH':
            advice['overall_recommendation'] = 'REDUCE_RISK'
            advice['actions'].append('Sell high-risk assets')
            advice['actions'].append('Increase cash allocation')
        elif risk_level == 'LOW':
            advice['overall_recommendation'] = 'MAINTAIN'
        
        if concentration_risk == 'HIGH':
            advice['diversification_advice'].append('Too concentrated - add new asset classes')
            advice['diversification_advice'].append('Consider international exposure')
            advice['diversification_advice'].append('Add defensive sectors')
        
        # Rebalancing recommendation
        rebal = portfolio_analysis.get('rebalancing_recommendation', {})
        if rebal.get('recommended'):
            advice['rebalancing'] = {
                'required': True,
                'reduce': rebal.get('reduce_positions', []),
                'increase': rebal.get('increase_positions', []),
                'reason': rebal.get('reason', '')
            }
        
        return advice
