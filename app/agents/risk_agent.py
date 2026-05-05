"""
Risk Assessment Agent - LLM-powered risk analysis.
Combines quantitative metrics with LLM reasoning for comprehensive risk evaluation.
"""

import json
import logging
from typing import Dict, List, Optional
from app.llm.llm_client import LLMClient
from app.utils.helpers import calculate_risk_score
from config import GROQ_API_KEY, USE_LLM_FOR_RISK

logger = logging.getLogger(__name__)


class RiskAgent:
    """
    LLM-powered risk assessment agent.
    Combines quantitative analysis with LLM reasoning for business context.
    """
    
    SYSTEM_PROMPT = """You are a senior financial risk analyst with expertise in:
- Market risk and volatility analysis
- Portfolio construction and optimization
- Concentration and diversification risks
- Systemic and macro risks
- Risk mitigation strategies

Analyze risks using quantitative metrics combined with business context.
Provide clear risk assessments with actionable mitigation strategies.
Be realistic about limitations of data and models."""
    
    def __init__(self):
        """Initialize risk agent with LLM."""
        self.llm = LLMClient(api_key=GROQ_API_KEY)
        self.use_llm = USE_LLM_FOR_RISK
        logger.info(f"RiskAgent initialized (LLM enabled: {self.use_llm})")
    
    def assess_asset_risk(self, asset: Dict) -> Dict:
        """
        Assess risk for a single asset using LLM + quantitative metrics.
        
        Args:
            asset: Asset dict with volatility, trend, exposure, etc.
            
        Returns:
            Risk assessment result
        """
        try:
            # Get quantitative signals
            quantitative_analysis = self._calculate_quantitative_metrics(asset)
            
            if self.use_llm:
                # Use LLM for sophisticated analysis
                return self._llm_assess_asset(asset, quantitative_analysis)
            else:
                # Use quantitative only
                return self._quantitative_assess_asset(asset, quantitative_analysis)
        
        except Exception as e:
            logger.error(f"Error assessing asset {asset.get('symbol', 'UNKNOWN')}: {e}")
            return {
                'asset': asset.get('symbol', 'UNKNOWN'),
                'error': str(e),
                'risk_level': 'UNKNOWN',
                'overall_risk_score': 0.5
            }
    
    def _calculate_quantitative_metrics(self, asset: Dict) -> Dict:
        """Calculate quantitative risk metrics."""
        volatility = float(asset.get('volatility', 0.2))
        trend = asset.get('trend', 'stable').lower()
        exposure = float(asset.get('exposure', 0.5))
        
        volatility_risk = min(1.0, volatility / 0.5)
        trend_risk = {
            'up': 0.1, 'stable': 0.5, 'down': 0.8
        }.get(trend, 0.5)
        exposure_risk = min(1.0, exposure)
        
        risk_factors = {
            'volatility': {'score': volatility_risk, 'weight': 0.3},
            'trend': {'score': trend_risk, 'weight': 0.4},
            'exposure': {'score': exposure_risk, 'weight': 0.3}
        }
        
        overall_score = calculate_risk_score(risk_factors)
        
        return {
            'risk_factors': risk_factors,
            'overall_score': overall_score,
            'volatility_pct': volatility * 100,
            'trend_direction': trend,
            'exposure_pct': exposure * 100,
            'current_price': asset.get('current_price'),
            '52_week_high': asset.get('52_week_high'),
            '52_week_low': asset.get('52_week_low')
        }
    
    def _llm_assess_asset(self, asset: Dict, metrics: Dict) -> Dict:
        """Assess asset risk using LLM."""
        try:
            prompt = f"""
Assess the financial risk of this asset:

Asset Details:
- Symbol: {asset.get('symbol', 'UNKNOWN')}
- Volatility: {metrics['volatility_pct']:.2f}%
- Trend: {metrics['trend_direction']}
- Exposure: {metrics['exposure_pct']:.2f}%
- Current Price: ${metrics['current_price'] or 'N/A'}
- 52-week High: ${metrics['52_week_high'] or 'N/A'}
- 52-week Low: ${metrics['52_week_low'] or 'N/A'}

Quantitative Risk Score: {metrics['overall_score']:.3f}

Provide a comprehensive risk assessment with:
- Context and business implications
- Key risk drivers
- Mitigation strategies
- Investment recommendation

Return JSON with:
{{
    "overall_risk_score": 0.0-1.0,
    "risk_level": "LOW/MEDIUM/HIGH",
    "risk_drivers": ["driver1", "driver2", ...],
    "quantitative_confidence": 0.0-1.0,
    "business_context": "explanation of business factors",
    "mitigation_strategies": ["strategy1", "strategy2", ...],
    "recommendation": "BUY/HOLD/SELL/REDUCE"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Add quantitative breakdown
            result['asset'] = asset.get('symbol', 'UNKNOWN')
            result['quantitative_breakdown'] = {
                'volatility_risk': round(metrics['risk_factors']['volatility']['score'], 3),
                'trend_risk': round(metrics['risk_factors']['trend']['score'], 3),
                'exposure_risk': round(metrics['risk_factors']['exposure']['score'], 3)
            }
            result['current_price'] = metrics['current_price']
            result['price_range'] = {
                '52_week_high': metrics['52_week_high'],
                '52_week_low': metrics['52_week_low']
            }
            
            return result
        
        except Exception as e:
            logger.error(f"LLM assessment error: {e}")
            return self._quantitative_assess_asset(asset, metrics)
    
    def _quantitative_assess_asset(self, asset: Dict, metrics: Dict) -> Dict:
        """Quantitative-only risk assessment."""
        score = metrics['overall_score']
        
        if score < 0.3:
            risk_level = 'LOW'
            recommendation = 'BUY/HOLD'
        elif score < 0.7:
            risk_level = 'MEDIUM'
            recommendation = 'HOLD/CAUTIOUS'
        else:
            risk_level = 'HIGH'
            recommendation = 'SELL/REDUCE'
        
        return {
            'asset': asset.get('symbol', 'UNKNOWN'),
            'overall_risk_score': round(score, 3),
            'risk_level': risk_level,
            'quantitative_breakdown': {
                'volatility_risk': round(metrics['risk_factors']['volatility']['score'], 3),
                'trend_risk': round(metrics['risk_factors']['trend']['score'], 3),
                'exposure_risk': round(metrics['risk_factors']['exposure']['score'], 3)
            },
            'current_price': metrics['current_price'],
            'price_range': {
                '52_week_high': metrics['52_week_high'],
                '52_week_low': metrics['52_week_low']
            },
            'mitigation_strategies': self._generate_strategies(risk_level),
            'recommendation': recommendation
        }
    
    def assess_portfolio_risk(self, portfolio: Dict) -> Dict:
        """
        Assess risk for an entire portfolio.
        
        Args:
            portfolio: Portfolio dict with holdings
            
        Returns:
            Portfolio risk assessment
        """
        holdings = portfolio.get('holdings', [])
        
        if not holdings:
            return {
                'portfolio_risk_score': 0.0,
                'portfolio_risk_level': 'N/A',
                'message': 'No holdings in portfolio'
            }
        
        # Assess individual assets
        asset_risks = []
        total_value = 0
        weighted_risk = 0
        
        for holding in holdings:
            asset_risk = self.assess_asset_risk(holding)
            asset_risks.append(asset_risk)
            
            value = holding.get('value', 0)
            total_value += value
            weighted_risk += asset_risk.get('overall_risk_score', 0.5) * value
        
        portfolio_risk_score = weighted_risk / total_value if total_value > 0 else 0
        
        if portfolio_risk_score < 0.3:
            portfolio_risk_level = 'LOW'
        elif portfolio_risk_score < 0.7:
            portfolio_risk_level = 'MEDIUM'
        else:
            portfolio_risk_level = 'HIGH'
        
        concentration = 1.0 / len(holdings)
        if concentration > 0.5:
            concentration_risk = 'HIGH'
        elif concentration > 0.2:
            concentration_risk = 'MEDIUM'
        else:
            concentration_risk = 'LOW'
        
        return {
            'portfolio_risk_score': round(portfolio_risk_score, 3),
            'portfolio_risk_level': portfolio_risk_level,
            'num_holdings': len(holdings),
            'total_value': total_value,
            'concentration_risk': concentration_risk,
            'asset_risks': asset_risks,
            'rebalancing_recommendation': self._get_rebalancing_recommendation(asset_risks),
            'overall_recommendation': self._get_portfolio_recommendation(portfolio_risk_level)
        }
    
    def assess_transaction_risk(self, transaction: Dict) -> Dict:
        """
        Assess risk of a transaction using LLM + quantitative metrics.
        
        Args:
            transaction: Transaction dict
            
        Returns:
            Transaction risk assessment
        """
        try:
            # Get quantitative assessment
            quant_result = self._quantitative_transaction_risk(transaction)
            
            if self.use_llm:
                # Use LLM for context-aware risk assessment
                return self._llm_transaction_risk(transaction, quant_result)
            else:
                return quant_result
        
        except Exception as e:
            logger.error(f"Error assessing transaction risk: {e}")
            return {
                'transaction_risk_level': 'UNKNOWN',
                'transaction_risk_score': 0.5,
                'error': str(e)
            }
    
    def _quantitative_transaction_risk(self, transaction: Dict) -> Dict:
        """Calculate quantitative transaction risk."""
        amount = float(transaction.get('amount', 0))
        location = transaction.get('location', 'US')
        merchant = transaction.get('merchant_category', 'grocery')
        account_age = float(transaction.get('account_age_days', 0))
        
        risk_factors = {}
        
        if amount > 5000:
            risk_factors['amount'] = 0.8
        elif amount > 1000:
            risk_factors['amount'] = 0.5
        else:
            risk_factors['amount'] = 0.1
        
        high_risk_locations = ['UK', 'CN', 'JP', 'BR', 'RU', 'DZ', 'NG', 'KE', 'VN', 'GH', 'PK']
        risk_factors['location'] = 0.7 if location in high_risk_locations else 0.1
        
        high_risk_merchants = ['jewelry', 'luxury_goods']
        risk_factors['merchant'] = 0.8 if merchant in high_risk_merchants else 0.2
        
        if account_age < 30:
            risk_factors['account_age'] = 0.6
        else:
            risk_factors['account_age'] = 0.1
        
        transaction_risk_score = sum(risk_factors.values()) / len(risk_factors) if risk_factors else 0
        
        if transaction_risk_score < 0.3:
            risk_level = 'LOW'
        elif transaction_risk_score < 0.6:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
        
        return {
            'transaction_risk_score': round(transaction_risk_score, 3),
            'transaction_risk_level': risk_level,
            'risk_level': risk_level,
            'risk_breakdown': {k: round(v, 3) for k, v in risk_factors.items()},
            'quantitative_base': True
        }
    
    def _llm_transaction_risk(self, transaction: Dict, quant_result: Dict) -> Dict:
        """Assess transaction risk using LLM."""
        try:
            prompt = f"""
Assess the financial risk of this transaction:

Transaction Details:
- Amount: ${transaction.get('amount', 0):.2f}
- Location: {transaction.get('location', 'UNKNOWN')}
- Merchant: {transaction.get('merchant_category', 'UNKNOWN')}
- Account Age: {transaction.get('account_age_days', 0)} days
- Time of Day: {transaction.get('time_of_day', 0)}:00

Quantitative Risk Assessment:
{json.dumps(quant_result, indent=2)}

Consider:
- Transaction size and pattern
- Geographic and merchant risks
- Account maturity
- Any unusual characteristics

Return JSON with:
{{
    "transaction_risk_score": 0.0-1.0,
    "transaction_risk_level": "LOW/MEDIUM/HIGH",
    "risk_level": "LOW/MEDIUM/HIGH",
    "risk_drivers": ["driver1", "driver2", ...],
    "context_factors": "business context",
    "recommendation": "APPROVE/VERIFY/BLOCK"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3
            )
            
            result['risk_breakdown'] = quant_result.get('risk_breakdown', {})
            return result
        
        except Exception as e:
            logger.error(f"LLM transaction risk error: {e}")
            return quant_result
    
    def _generate_strategies(self, risk_level: str) -> List[str]:
        """Generate mitigation strategies."""
        strategies = []
        
        if risk_level == 'HIGH':
            strategies.append("Consider reducing exposure to this asset")
            strategies.append("Implement stop-loss orders at 10% below entry")
            strategies.append("Use protective puts or other hedging instruments")
            strategies.append("Increase portfolio diversification")
        elif risk_level == 'MEDIUM':
            strategies.append("Monitor regularly for changes in fundamentals")
            strategies.append("Consider rebalancing if allocation drifts")
            strategies.append("Maintain adequate diversification")
        else:
            strategies.append("Continue regular monitoring")
            strategies.append("Asset suitable for conservative investors")
        
        return strategies
    
    def _get_rebalancing_recommendation(self, asset_risks: List[Dict]) -> Dict:
        """Get rebalancing recommendations."""
        high_risk_assets = [a for a in asset_risks if a.get('risk_level') == 'HIGH']
        low_risk_assets = [a for a in asset_risks if a.get('risk_level') == 'LOW']
        
        return {
            'recommended': len(high_risk_assets) > 0,
            'reduce_positions': [a.get('asset', 'UNKNOWN') for a in high_risk_assets],
            'increase_positions': [a.get('asset', 'UNKNOWN') for a in low_risk_assets],
            'reason': 'Portfolio contains high-risk assets exceeding tolerance' if high_risk_assets else 'Portfolio is well-balanced'
        }
    
    def _get_portfolio_recommendation(self, risk_level: str) -> str:
        """Get overall portfolio recommendation."""
        if risk_level == 'HIGH':
            return 'REDUCE PORTFOLIO RISK'
        elif risk_level == 'MEDIUM':
            return 'MAINTAIN CURRENT ALLOCATION'
        else:
            return 'PORTFOLIO WELL-POSITIONED'
