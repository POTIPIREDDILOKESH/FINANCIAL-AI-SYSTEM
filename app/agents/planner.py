"""
Planner Agent - breaks down user queries into actionable steps.
"""

from typing import Dict, List


class PlannerAgent:
    """
    Planner agent that breaks down complex queries into a step-by-step plan.
    Uses rule-based logic to determine required analysis steps.
    """
    
    SYSTEM_PROMPT = """You are a financial planning agent. Your role is to break down user queries 
    into a clear sequence of steps that other specialized agents will then execute. 
    Be systematic and thorough. Never hallucinate - base plans on the actual query provided."""
    
    def __init__(self):
        """Initialize planner agent."""
        pass
    
    def plan(self, user_query: str) -> Dict:
        """
        Create a plan for processing the user query.
        
        Args:
            user_query: User's question or request
            
        Returns:
            Dict with plan steps and required agents
        """
        plan = {
            'query': user_query,
            'steps': [],
            'required_agents': [],
            'context': {}
        }
        
        # Detect query type and build plan
        query_lower = user_query.lower()
        
        # Check for fraud detection
        if any(word in query_lower for word in ['fraud', 'suspicious', 'check transaction', 'is this transaction']):
            plan['steps'].append({
                'step_number': 1,
                'agent': 'fraud_agent',
                'task': 'Analyze transaction for fraud risk',
                'input': ['transaction_data']
            })
            plan['required_agents'].append('fraud_agent')
        
        # Check for risk assessment
        if any(word in query_lower for word in ['risk', 'risky', 'portfolio', 'safe']):
            plan['steps'].append({
                'step_number': len(plan['steps']) + 1,
                'agent': 'risk_agent',
                'task': 'Perform risk assessment',
                'input': ['asset_data', 'market_data']
            })
            plan['required_agents'].append('risk_agent')
        
        # Check for research/RAG needs
        if any(word in query_lower for word in ['what', 'how', 'why', 'explain', 'tell me', 'strategy', 'best practice']):
            plan['steps'].append({
                'step_number': len(plan['steps']) + 1,
                'agent': 'research_agent',
                'task': 'Research topic using RAG and retrieve relevant documents',
                'input': ['query_text']
            })
            plan['required_agents'].append('research_agent')
        
        # Check for advisory
        if any(word in query_lower for word in ['recommend', 'should i', 'advise', 'decision', 'approve', 'reject']):
            plan['steps'].append({
                'step_number': len(plan['steps']) + 1,
                'agent': 'advisory_agent',
                'task': 'Generate recommendation',
                'input': ['analysis_results']
            })
            plan['required_agents'].append('advisory_agent')
        
        # Always add explainability
        if plan['steps']:
            plan['steps'].append({
                'step_number': len(plan['steps']) + 1,
                'agent': 'explainability_agent',
                'task': 'Explain decisions and reasoning',
                'input': ['all_previous_results']
            })
            plan['required_agents'].append('explainability_agent')
        
        # If no steps were identified, provide general research
        if not plan['steps']:
            plan['steps'].append({
                'step_number': 1,
                'agent': 'research_agent',
                'task': 'Research and provide information',
                'input': ['query_text']
            })
            plan['required_agents'].append('research_agent')
        
        return plan
    
    def refine_plan(self, plan: Dict, feedback: Dict) -> Dict:
        """
        Refine the plan based on feedback.
        
        Args:
            plan: Original plan
            feedback: Feedback dict with issues
            
        Returns:
            Refined plan
        """
        # Simple refinement logic
        if feedback.get('missing_fraud_check') and 'fraud_agent' not in plan['required_agents']:
            plan['steps'].insert(0, {
                'step_number': 1,
                'agent': 'fraud_agent',
                'task': 'Check for fraud',
                'input': ['transaction_data']
            })
            plan['required_agents'].append('fraud_agent')
        
        return plan
    
    def estimate_execution_time(self, plan: Dict) -> Dict:
        """
        Estimate execution time for the plan.
        
        Args:
            plan: Plan dict
            
        Returns:
            Dict with time estimates
        """
        agent_times = {
            'fraud_agent': 2,
            'risk_agent': 3,
            'research_agent': 5,
            'advisory_agent': 4,
            'explainability_agent': 2
        }
        
        total_time = sum(
            agent_times.get(step['agent'], 2) 
            for step in plan['steps']
        )
        
        return {
            'estimated_seconds': total_time,
            'step_breakdown': [
                {
                    'step': step['step_number'],
                    'agent': step['agent'],
                    'estimated_seconds': agent_times.get(step['agent'], 2)
                }
                for step in plan['steps']
            ]
        }
