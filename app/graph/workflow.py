"""
LangGraph workflow for orchestrating all agents.
Multi-agent LLM-powered financial AI pipeline.
"""

import logging
from typing import Dict, List, Any
from pydantic import BaseModel
from app.agents.planner_agent import PlannerAgent
from app.agents.fraud_agent import FraudAgent
from app.agents.risk_agent import RiskAgent
from app.agents.research_agent import ResearchAgent
from app.agents.advisory_agent import AdvisoryAgent
from app.agents.explainability_agent import ExplainabilityAgent
from app.memory.memory_store import MemoryStore

logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """State passed through the workflow."""
    query: str = ""
    transaction: Dict = {}
    plan: Dict = {}
    fraud_analysis: Dict = {}
    risk_analysis: Dict = {}
    research_findings: Dict = {}
    recommendation: Dict = {}
    final_synthesis: Dict = {}
    explanation: Dict = {}
    errors: List[str] = []
    flow_metadata: Dict = {}


class FinancialAIWorkflow:
    """
    Main workflow orchestrator using LLM-based agents.
    Implements complete financial AI pipeline with synthesis and explainability.
    """
    
    def __init__(self, use_rag: bool = True, enable_memory: bool = True):
        """
        Initialize workflow with all agents.
        
        Args:
            use_rag: Enable RAG for research
            enable_memory: Store decisions in memory
        """
        self.planner_agent = PlannerAgent()
        self.fraud_agent = FraudAgent()
        self.risk_agent = RiskAgent()
        self.research_agent = ResearchAgent(use_rag=use_rag)
        self.advisory_agent = AdvisoryAgent()
        self.explainability_agent = ExplainabilityAgent()
        
        self.memory = MemoryStore() if enable_memory else None
        self.enable_memory = enable_memory
        
        logger.info("FinancialAIWorkflow initialized with all agents")
    
    def execute(self, query: str, transaction: Dict = None, **kwargs) -> Dict:
        """
        Execute full workflow pipeline.
        
        Args:
            query: User query or analysis request
            transaction: Optional transaction to analyze
            
        Returns:
            Final synthesis and recommendations
        """
        state = WorkflowState(query=query, transaction=transaction or {})
        
        try:
            # Step 1: Plan the analysis
            state = self._plan_step(state)
            logger.info(f"Planning complete: {state.plan}")
            
            # Step 2: Fraud Analysis
            if 'fraud_agent' in state.plan.get('required_agents', []):
                state = self._fraud_step(state)
                logger.info("Fraud analysis complete")
            
            # Step 3: Risk Analysis
            if 'risk_agent' in state.plan.get('required_agents', []):
                state = self._risk_step(state)
                logger.info("Risk analysis complete")
            
            # Step 4: Research & Knowledge
            if 'research_agent' in state.plan.get('required_agents', []):
                state = self._research_step(state)
                logger.info("Research complete")
            
            # Step 5: Advisory Recommendation
            if 'advisory_agent' in state.plan.get('required_agents', []):
                state = self._advisory_step(state)
                logger.info("Advisory complete")
            
            # Step 6: LLM-based Synthesis & Final Decision (NEW)
            if 'planner_agent' in state.plan.get('required_agents', []):
                state = self._synthesis_step(state)
                logger.info("Synthesis complete")
            
            # Step 7: Explainability
            if 'explainability_agent' in state.plan.get('required_agents', []):
                state = self._explainability_step(state)
                logger.info("Explainability complete")
            
            # Save to memory
            if self.enable_memory:
                self._save_to_memory(state)
            
            return self._format_output(state)
        
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            state.errors.append(str(e))
            return {
                'success': False,
                'error': str(e),
                'state': state.dict() if state else {}
            }
    
    # ==================== WORKFLOW STEPS ====================
    
    def _plan_step(self, state: WorkflowState) -> WorkflowState:
        """Plan which agents to run based on query."""
        try:
            state.plan = {
                "query": state.query,
                "required_agents": [
                    "fraud_agent",
                    "risk_agent",
                    "research_agent",
                    "advisory_agent",
                    "planner_agent",
                    "explainability_agent"
                ],
                "steps": [
                    {"step": 1, "agent": "fraud_agent", "description": "Analyze transaction fraud risk"},
                    {"step": 2, "agent": "risk_agent", "description": "Assess financial risk"},
                    {"step": 3, "agent": "research_agent", "description": "Research market context"},
                    {"step": 4, "agent": "advisory_agent", "description": "Generate advisory"},
                    {"step": 5, "agent": "planner_agent", "description": "LLM synthesis & final decision"},
                    {"step": 6, "agent": "explainability_agent", "description": "Explain reasoning"}
                ]
            }
            state.flow_metadata['planning_complete'] = True
        except Exception as e:
            state.errors.append(f"Planning error: {e}")
            logger.error(f"Planning error: {e}")
        
        return state
    
    def _fraud_step(self, state: WorkflowState) -> WorkflowState:
        """Perform fraud analysis."""
        try:
            if state.transaction:
                state.fraud_analysis = self.fraud_agent.analyze_transaction(state.transaction)
            else:
                state.fraud_analysis = {'info': 'No transaction to analyze for fraud'}
            
            state.flow_metadata['fraud_analysis_complete'] = True
        except Exception as e:
            state.errors.append(f"Fraud analysis error: {e}")
            state.fraud_analysis = {'error': str(e)}
            logger.error(f"Fraud analysis error: {e}")
        
        return state
    
    def _risk_step(self, state: WorkflowState) -> WorkflowState:
        """Perform risk analysis."""
        try:
            if state.transaction:
                state.risk_analysis = self.risk_agent.assess_transaction_risk(state.transaction)
            else:
                state.risk_analysis = {'info': 'Risk assessment available for transactions'}
            
            state.flow_metadata['risk_analysis_complete'] = True
        except Exception as e:
            state.errors.append(f"Risk analysis error: {e}")
            state.risk_analysis = {'error': str(e)}
            logger.error(f"Risk analysis error: {e}")
        
        return state
    
    def _research_step(self, state: WorkflowState) -> WorkflowState:
        """Perform research and knowledge retrieval."""
        try:
            if state.query:
                findings = self.research_agent.research_topic(state.query)
                state.research_findings = findings
            
            state.flow_metadata['research_complete'] = True
        except Exception as e:
            state.errors.append(f"Research error: {e}")
            state.research_findings = {'error': str(e)}
            logger.error(f"Research error: {e}")
        
        return state
    
    def _advisory_step(self, state: WorkflowState) -> WorkflowState:
        """Generate advisory recommendation."""
        try:
            analysis_results = {
                'fraud_analysis': state.fraud_analysis,
                'risk_analysis': state.risk_analysis,
                'research_findings': state.research_findings,
                'transaction': state.transaction
            }
            
            state.recommendation = self.advisory_agent.generate_recommendation(analysis_results)
            state.flow_metadata['advisory_complete'] = True
        except Exception as e:
            state.errors.append(f"Advisory error: {e}")
            state.recommendation = {'error': str(e)}
            logger.error(f"Advisory error: {e}")
        
        return state
    
    def _synthesis_step(self, state: WorkflowState) -> WorkflowState:
        """LLM-based synthesis and final decision (NEW)."""
        try:
            # Prepare state dict for planner
            synthesis_input = {
                'query': state.query,
                'fraud_analysis': state.fraud_analysis,
                'risk_analysis': state.risk_analysis,
                'research_findings': state.research_findings,
                'recommendation': state.recommendation
            }
            
            # Get final synthesis from planner agent
            state.final_synthesis = self.planner_agent.synthesize(synthesis_input)
            state.flow_metadata['synthesis_complete'] = True
        except Exception as e:
            state.errors.append(f"Synthesis error: {e}")
            state.final_synthesis = {'error': str(e)}
            logger.error(f"Synthesis error: {e}")
        
        return state
    
    def _explainability_step(self, state: WorkflowState) -> WorkflowState:
        """Generate explanation of the decision."""
        try:
            all_results = {
                'fraud_analysis': state.fraud_analysis,
                'risk_analysis': state.risk_analysis,
                'research_findings': state.research_findings,
                'advisory_recommendation': state.recommendation,
                'final_synthesis': state.final_synthesis
            }
            
            state.explanation = self.explainability_agent.explain_decision(all_results)
            state.flow_metadata['explainability_complete'] = True
        except Exception as e:
            state.errors.append(f"Explainability error: {e}")
            state.explanation = {'error': str(e)}
            logger.error(f"Explainability error: {e}")
        
        return state
    
    def _save_to_memory(self, state: WorkflowState):
        """Save workflow results to memory."""
        try:
            decision = {
                'query': state.query,
                'recommendation': state.recommendation,
                'final_synthesis': state.final_synthesis,
                'fraud_analysis': state.fraud_analysis,
                'risk_analysis': state.risk_analysis,
                'transaction': state.transaction
            }
            
            if self.memory:
                self.memory.add_decision(decision)
                
                if state.fraud_analysis:
                    self.memory.add_fraud_alert(state.transaction, state.fraud_analysis)
                
                if state.risk_analysis:
                    asset = state.transaction.get('transaction_id', 'unknown')
                    self.memory.add_risk_assessment(asset, state.risk_analysis)
                
                self.memory.add_query(state.query, {
                    'recommendation': state.recommendation,
                    'synthesis': state.final_synthesis,
                    'errors': state.errors
                })
        except Exception as e:
            logger.warning(f"Memory save failed: {e}")
    
    def _format_output(self, state: WorkflowState) -> Dict:
        """Format workflow output."""
        return {
            'success': len(state.errors) == 0,
            'query': state.query,
            'fraud_assessment': state.fraud_analysis,
            'risk_assessment': state.risk_analysis,
            'research_findings': state.research_findings,
            'advisory_recommendation': state.recommendation,
            'final_decision': state.final_synthesis,  # NEW: Final LLM synthesis
            'explanation': state.explanation,
            'metadata': state.flow_metadata,
            'errors': state.errors,
            'audit_trail': {
                'plan': state.plan,
                'steps_executed': list(state.flow_metadata.keys())
            }
        }
    def get_memory_summary(self):
        """Return summary of stored memory."""
        if not self.memory:
            return {"message": "Memory is disabled"}

        mem = self.memory.memory  # 🔥 IMPORTANT LINE

        return {
            "total_queries": len(mem.get("queries", [])),
            "total_decisions": len(mem.get("decisions", [])),
            "fraud_alerts": len(mem.get("fraud_alerts", [])),
            "risk_assessments": len(mem.get("risk_assessments", []))
        }

    def clear_memory(self):
        """Clear memory store."""
        if self.memory:
            self.memory.memory = {
                'decisions': [],
                'queries': [],
                'fraud_alerts': [],
                'risk_assessments': []
            }