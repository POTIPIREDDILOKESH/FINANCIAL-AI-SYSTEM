"""
Planner Agent - LLM-based synthesis and decision-making.
Synthesizes all agent results into final decisions.
"""

import json
import logging
from typing import Dict, Optional
from app.llm.llm_client import LLMClient
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    LLM-powered planner agent that synthesizes results from all agents.
    Makes final decisions based on fraud, risk, research, and other analyses.
    """
    
    SYSTEM_PROMPT = """You are a senior financial decision-maker with deep expertise in:
- Fraud detection and prevention
- Financial risk management
- Investment analysis
- Regulatory compliance

Your role is to synthesize analyses from multiple specialists and make clear, 
data-driven financial decisions. Always base your recommendations on evidence.
Be concise and actionable."""
    
    def __init__(self):
        """Initialize planner agent with LLM."""
        self.llm = LLMClient(api_key=GROQ_API_KEY)
        logger.info("PlannerAgent initialized with LLM")
    
    def synthesize(self, state: Dict) -> Dict:
        """
        Synthesize all agent analyses into a final decision.
        
        Args:
            state: WorkflowState dict with all agent results
            
        Returns:
            Final decision dict
        """
        try:
            prompt = self._build_synthesis_prompt(state)
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                'success': True,
                'decision': result.get('decision', 'HOLD'),
                'confidence': result.get('confidence', 0.5),
                'key_factors': result.get('key_factors', []),
                'risks_identified': result.get('risks', []),
                'recommendations': result.get('recommendations', []),
                'reasoning': result.get('reasoning', ''),
                'next_steps': result.get('next_steps', [])
            }
        
        except Exception as e:
            logger.error(f"Error in planner synthesis: {e}")
            return {
                'success': False,
                'error': str(e),
                'decision': 'MANUAL_REVIEW_REQUIRED'
            }
    
    def plan_next_steps(self, query: str, findings: Dict) -> Dict:
        """
        Plan recommended next actions based on findings.
        
        Args:
            query: Original user query
            findings: Analysis findings
            
        Returns:
            Recommended action plan
        """
        try:
            prompt = f"""
Query: {query}

Current Findings:
{json.dumps(findings, indent=2)}

Based on these findings, what should be the next steps?

Respond with JSON:
{{
    "immediate_actions": ["action1", "action2", ...],
    "follow_up_analysis": ["analysis1", "analysis2", ...],
    "escalation_needed": true/false,
    "escalation_reason": "...",
    "timeline": "immediate/24h/week/ongoing",
    "owner": "person/team responsible"
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3
            )
            
            return {
                'success': True,
                'action_plan': result
            }
        
        except Exception as e:
            logger.error(f"Error in planning next steps: {e}")
            return {'success': False, 'error': str(e)}
    
    def assess_decision_quality(self, decision: Dict, context: Dict) -> Dict:
        """
        Assess the quality and confidence of a decision.
        
        Args:
            decision: The decision to assess
            context: Original context/query
            
        Returns:
            Quality assessment
        """
        try:
            prompt = f"""
Original Context:
{json.dumps(context, indent=2)}

Decision:
{json.dumps(decision, indent=2)}

Assess this decision on:
- Data sufficiency (is there enough data?)
- Logic consistency (are conclusions sound?)
- Risk coverage (what risks might be missed?)
- Alternative considerations (what else should be considered?)

Respond with JSON:
{{
    "overall_quality_score": 0.0-1.0,
    "data_sufficiency": "sufficient/marginal/insufficient",
    "logic_consistency": "sound/mostly_sound/questionable",
    "coverage_gaps": ["gap1", "gap2", ...],
    "alternative_views": ["view1", "view2", ...],
    "confidence_justification": "..."
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3
            )
            
            return {'success': True, 'assessment': result}
        
        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            return {'success': False, 'error': str(e)}
    
    def _build_synthesis_prompt(self, state: Dict) -> str:
        """Build comprehensive synthesis prompt from state."""
        prompt = f"""
Query: {state.get('query', 'N/A')}

=== FRAUD ANALYSIS ===
{json.dumps(state.get('fraud_analysis', {}), indent=2)}

=== RISK ANALYSIS ===
{json.dumps(state.get('risk_analysis', {}), indent=2)}

=== RESEARCH FINDINGS ===
{json.dumps(state.get('research_findings', {}), indent=2)}

=== ADVISORY RECOMMENDATION ===
{json.dumps(state.get('recommendation', {}), indent=2)}

Synthesize all analyses above and provide a final decision.

Return JSON with:
{{
    "decision": "APPROVE/REJECT/VERIFY/HOLD/MANUAL_REVIEW",
    "confidence": 0.0-1.0,
    "key_factors": [list of critical factors],
    "risks": [identified risks],
    "recommendations": [actionable recommendations],
    "reasoning": "Clear explanation of decision",
    "next_steps": [recommended next actions]
}}

Base your decision on:
1. Fraud risk level and confidence
2. Portfolio/transaction risk metrics
3. Research findings and market context
4. Existing advisory recommendations
5. Overall confidence thresholds

Be decisive but cautious. Flag for manual review if confidence < 0.6.
"""
        return prompt
