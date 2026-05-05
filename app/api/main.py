"""
FastAPI backend for the Financial AI System.
Provides REST API endpoints for the AI system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from app.graph.workflow import FinancialAIWorkflow
from app.utils.helpers import create_json_response, validate_transaction
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize workflow
workflow = FinancialAIWorkflow(use_rag=True, enable_memory=True)

# Initialize FastAPI app
app = FastAPI(
    title="Financial AI System",
    description="AI-powered financial intelligence system for fraud detection, risk assessment, and advisory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request Models ====================

class Transaction(BaseModel):
    """Transaction data model."""
    transaction_id: str = Field(..., description="Unique transaction ID")
    amount: float = Field(..., description="Transaction amount")
    time_of_day: int = Field(..., description="Hour of transaction (0-23)")
    location: str = Field(..., description="Transaction location/country")
    merchant_category: str = Field(..., description="Merchant category")
    frequency_30d: int = Field(..., description="Transaction frequency in last 30 days")
    account_age_days: int = Field(..., description="Account age in days")


class AnalysisRequest(BaseModel):
    """Request for financial analysis."""
    query: str = Field(..., description="User query/question")
    transaction: Optional[Transaction] = Field(None, description="Optional transaction to analyze")


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis."""
    queries: List[str] = Field(..., description="List of queries to analyze")


# ==================== Health & Info Endpoints ====================

@app.get("/health", tags=["System"])
def health_check() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Financial AI System"
    }


@app.get("/info", tags=["System"])
def system_info() -> Dict:
    """Get system information."""
    return workflow.get_workflow_info()

def make_json_safe(data):
    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, type({}.keys())):   # 🔥 fixes dict_keys
        return list(data)
    else:
        return data

@app.get("/memory", tags=["System"])
def memory_info() -> Dict:
    """Get memory information."""
    return workflow.get_memory_summary()


# ==================== Analysis Endpoints ====================

@app.post("/analyze", tags=["Analysis"])
def analyze(request: AnalysisRequest) -> Dict:
    """
    Main analysis endpoint - runs complete workflow.
    
    POST /analyze
    {
        "query": "Is this transaction fraudulent?",
        "transaction": {
            "transaction_id": "TXN001",
            "amount": 5000,
            "time_of_day": 3,
            ...
        }
    }
    """
    try:
        logger.info(f"Analysis request: {request.query[:100]}...")
        
        # Validate transaction if provided
        if request.transaction:
            is_valid, error_msg = validate_transaction(request.transaction.dict())
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Execute workflow
        result = workflow.execute(
            query=request.query,
            transaction=request.transaction.dict() if request.transaction else None
        )
        
        logger.info(f"Analysis completed with success={result['success']}")
        
        safe_result = make_json_safe(result)

        return create_json_response(
            success=safe_result['success'],
            data=safe_result,
            message="Analysis completed successfully" if safe_result['success'] else "Analysis completed with errors"
        )
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/fraud", tags=["Analysis"])
def analyze_fraud(request: AnalysisRequest) -> Dict:
    """
    Fraud detection specific endpoint.
    
    POST /analyze/fraud
    {
        "transaction": {...}
    }
    """
    try:
        if not request.transaction:
            raise HTTPException(status_code=400, detail="Transaction data required")
        
        fraud_result = workflow.fraud_agent.analyze_transaction(request.transaction.dict())
        
        return create_json_response(
            success=True,
            data={
                'transaction_id': request.transaction.transaction_id,
                'fraud_assessment': fraud_result
            }
        )
    
    except Exception as e:
        logger.error(f"Fraud analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/risk", tags=["Analysis"])
def analyze_risk(risk_data: Dict) -> Dict:
    """
    Risk assessment specific endpoint.
    
    POST /analyze/risk
    {
        "asset": {...},
        "type": "transaction" or "portfolio"
    }
    """
    try:
        risk_type = risk_data.get('type', 'transaction')
        asset_data = risk_data.get('asset', {})
        
        if risk_type == 'transaction':
            result = workflow.risk_agent.assess_transaction_risk(asset_data)
        else:
            result = workflow.risk_agent.assess_asset_risk(asset_data)
        
        return create_json_response(success=True, data=result)
    
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/research", tags=["Analysis"])
def analyze_research(topic: Dict) -> Dict:
    """
    Research endpoint using RAG and APIs.
    
    POST /analyze/research
    {
        "topic": "Portfolio diversification",
        "depth": "deep"
    }
    """
    try:
        research_topic = topic.get('topic', '')
        depth = topic.get('depth', 'medium')
        
        if not research_topic:
            raise HTTPException(status_code=400, detail="Topic required")
        
        findings = workflow.research_agent.research_topic(research_topic, depth=depth)
        
        return create_json_response(success=True, data=findings)
    
    except Exception as e:
        logger.error(f"Research error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/advisory", tags=["Analysis"])
def get_advisory(analysis: Dict) -> Dict:
    """
    Get advisory/recommendation based on analysis.
    
    POST /analyze/advisory
    {
        "fraud_analysis": {...},
        "risk_analysis": {...},
        ...
    }
    """
    try:
        result = workflow.advisory_agent.generate_recommendation(analysis)
        
        return create_json_response(success=True, data=result)
    
    except Exception as e:
        logger.error(f"Advisory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", tags=["Explainability"])
def explain_decision(decision_data: Dict) -> Dict:
    """
    Get detailed explanation of a decision.
    
    POST /explain
    {
        "all_results": {
            "fraud_analysis": {...},
            "risk_analysis": {...},
            ...
        }
    }
    """
    try:
        result = workflow.explainability_agent.explain_decision(decision_data.get('all_results', {}))
        
        return create_json_response(success=True, data=result)
    
    except Exception as e:
        logger.error(f"Explainability error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Batch Operations ====================

@app.post("/analyze/batch", tags=["Batch"])
def batch_analyze(request: BatchAnalysisRequest) -> Dict:
    """
    Batch analysis of multiple queries.
    
    POST /analyze/batch
    {
        "queries": ["query1", "query2", ...]
    }
    """
    try:
        if not request.queries:
            raise HTTPException(status_code=400, detail="At least one query required")
        
        results = workflow.batch_execute(request.queries)
        
        return create_json_response(
            success=True,
            data={
                'total_queries': len(request.queries),
                'results': results
            }
        )
    
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Stock & Market Data ====================

@app.get("/data/stock/{symbol}", tags=["Market Data"])
def get_stock_data(symbol: str) -> Dict:
    """Get stock price and data."""
    try:
        from app.tools.stock_api import StockAPI
        
        data = StockAPI.get_stock_price(symbol)
        
        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])
        
        return create_json_response(success=True, data=data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/news/{symbol}", tags=["Market Data"])
def get_news_data(symbol: str, limit: int = 5) -> Dict:
    """Get news for a symbol."""
    try:
        from app.tools.news_api import NewsAPI
        
        data = NewsAPI.get_news(symbol, limit=limit)
        
        return create_json_response(success=True, data=data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/market", tags=["Market Data"])
def get_market_data(index: str = "SPY") -> Dict:
    """Get market index data."""
    try:
        from app.tools.stock_api import StockAPI
        
        data = StockAPI.get_market_data(index)
        
        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])
        
        return create_json_response(success=True, data=data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Memory Management ====================

@app.delete("/memory/clear", tags=["Memory"])
def clear_old_memory(days: int = 30) -> Dict:
    """Clear memory records older than specified days."""
    try:
        workflow.clear_old_memory(days)
        
        return create_json_response(
            success=True,
            data={'message': f'Cleared records older than {days} days'}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return create_json_response(
        success=False,
        data={'error': exc.detail},
        message=f"Error: {exc.detail}"
    )


# ==================== Root Endpoint ====================

@app.get("/", tags=["Root"])
def root() -> Dict:
    """Root endpoint with API documentation."""
    return {
        "service": "Financial AI System",
        "version": "1.0.0",
        "description": "AI-powered financial intelligence system",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
