"""
Comprehensive test script to verify the Financial AI System installation and functionality.
Run this to ensure everything is working correctly before production deployment.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test critical imports"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ scikit-learn import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✓ Sentence-Transformers imported successfully")
    except ImportError as e:
        print(f"✗ Sentence-Transformers import failed: {e}")
        return False
    
    try:
        import faiss
        print("✓ FAISS imported successfully")
    except ImportError as e:
        print(f"✗ FAISS import failed: {e}")
        return False
    
    return True


def test_project_modules():
    """Test project module imports"""
    print("\n" + "="*60)
    print("TESTING PROJECT MODULES")
    print("="*60)
    
    try:
        from app.agents.planner import PlannerAgent
        print("✓ PlannerAgent imported successfully")
    except Exception as e:
        print(f"✗ PlannerAgent import failed: {e}")
        return False
    
    try:
        from app.agents.fraud_agent import FraudAgent
        print("✓ FraudAgent imported successfully")
    except Exception as e:
        print(f"✗ FraudAgent import failed: {e}")
        return False
    
    try:
        from app.agents.risk_agent import RiskAgent
        print("✓ RiskAgent imported successfully")
    except Exception as e:
        print(f"✗ RiskAgent import failed: {e}")
        return False
    
    try:
        from app.agents.research_agent import ResearchAgent
        print("✓ ResearchAgent imported successfully")
    except Exception as e:
        print(f"✗ ResearchAgent import failed: {e}")
        return False
    
    try:
        from app.agents.advisory_agent import AdvisoryAgent
        print("✓ AdvisoryAgent imported successfully")
    except Exception as e:
        print(f"✗ AdvisoryAgent import failed: {e}")
        return False
    
    try:
        from app.agents.explainability_agent import ExplainabilityAgent
        print("✓ ExplainabilityAgent imported successfully")
    except Exception as e:
        print(f"✗ ExplainabilityAgent import failed: {e}")
        return False
    
    try:
        from app.rag.embedder import Embedder
        from app.rag.vector_store import VectorStore
        from app.rag.retriever import RAGRetriever
        print("✓ RAG modules imported successfully")
    except Exception as e:
        print(f"✗ RAG modules import failed: {e}")
        return False
    
    try:
        from app.models.fraud_model import FraudDetectionModel
        print("✓ FraudDetectionModel imported successfully")
    except Exception as e:
        print(f"✗ FraudDetectionModel import failed: {e}")
        return False
    
    try:
        from app.graph.workflow import FinancialAIWorkflow
        print("✓ FinancialAIWorkflow imported successfully")
    except Exception as e:
        print(f"✗ FinancialAIWorkflow import failed: {e}")
        return False
    
    return True


def test_fraud_detection():
    """Test fraud detection functionality"""
    print("\n" + "="*60)
    print("TESTING FRAUD DETECTION")
    print("="*60)
    
    try:
        from app.agents.fraud_agent import FraudAgent
        
        agent = FraudAgent()
        
        # Test normal transaction
        normal_txn = {
            'amount': 100,
            'time_of_day': 14,
            'location': 'US',
            'merchant_category': 'grocery',
            'frequency_30d': 5,
            'account_age_days': 365
        }
        
        result = agent.analyze_transaction(normal_txn)
        assert result['fraud_risk'] in ['LOW', 'MEDIUM', 'HIGH']
        print(f"✓ Normal transaction test passed: {result['fraud_risk']}")
        
        # Test fraudulent transaction
        fraud_txn = {
            'amount': 5000,
            'time_of_day': 2,
            'location': 'UK',
            'merchant_category': 'jewelry',
            'frequency_30d': 1,
            'account_age_days': 30
        }
        
        result = agent.analyze_transaction(fraud_txn)
        assert result['fraud_risk'] == 'HIGH'
        print(f"✓ Fraudulent transaction test passed: {result['fraud_risk']}")
        
        return True
    except Exception as e:
        print(f"✗ Fraud detection test failed: {e}")
        return False


def test_risk_assessment():
    """Test risk assessment functionality"""
    print("\n" + "="*60)
    print("TESTING RISK ASSESSMENT")
    print("="*60)
    
    try:
        from app.agents.risk_agent import RiskAgent
        
        agent = RiskAgent()
        
        # Test low-risk asset
        low_risk_asset = {
            'symbol': 'SPY',
            'volatility': 0.15,
            'trend': 'up',
            'exposure': 0.3
        }
        
        result = agent.assess_asset_risk(low_risk_asset)
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
        print(f"✓ Low-risk asset test passed: {result['risk_level']}")
        
        # Test high-risk asset
        high_risk_asset = {
            'symbol': 'PENNY',
            'volatility': 0.8,
            'trend': 'down',
            'exposure': 1.0
        }
        
        result = agent.assess_asset_risk(high_risk_asset)
        assert result['risk_level'] == 'HIGH'
        print(f"✓ High-risk asset test passed: {result['risk_level']}")
        
        return True
    except Exception as e:
        print(f"✗ Risk assessment test failed: {e}")
        return False


def test_workflow():
    """Test complete workflow"""
    print("\n" + "="*60)
    print("TESTING WORKFLOW")
    print("="*60)
    
    try:
        from app.graph.workflow import FinancialAIWorkflow
        
        workflow = FinancialAIWorkflow(use_rag=False, enable_memory=False)
        
        # Test simple query
        result = workflow.execute(
            query="Is this transaction fraudulent?",
            transaction={
                'amount': 5000,
                'time_of_day': 2,
                'location': 'UK',
                'merchant_category': 'jewelry',
                'frequency_30d': 1,
                'account_age_days': 30
            }
        )
        
        assert result['success']
        assert 'fraud_assessment' in result
        assert 'recommendation' in result
        print("✓ Workflow execution test passed")
        print(f"  - Fraud Risk: {result['fraud_assessment'].get('fraud_risk')}")
        print(f"  - Recommendation: {result['recommendation'].get('decision')}")
        
        return True
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        return False


def test_data_files():
    """Test data files exist"""
    print("\n" + "="*60)
    print("TESTING DATA FILES")
    print("="*60)
    
    import os
    
    # Check transactions data
    if os.path.exists('data/transactions.csv'):
        with open('data/transactions.csv', 'r') as f:
            lines = f.readlines()
            print(f"✓ Transactions data found ({len(lines)} rows)")
    else:
        print("✗ Transactions data not found")
        return False
    
    # Check financial documents
    if os.path.exists('data/financial_docs.txt'):
        with open('data/financial_docs.txt', 'r') as f:
            content = f.read()
            print(f"✓ Financial documents found ({len(content)} chars)")
    else:
        print("✗ Financial documents not found")
        return False
    
    return True


def test_tools():
    """Test external tools"""
    print("\n" + "="*60)
    print("TESTING EXTERNAL TOOLS")
    print("="*60)
    
    try:
        from app.tools.stock_api import StockAPI
        
        result = StockAPI.get_stock_price('AAPL')
        assert 'current_price' in result
        print(f"✓ Stock API test passed: {result['current_price']}")
        
        from app.tools.news_api import NewsAPI
        
        result = NewsAPI.get_news('AAPL')
        assert 'articles' in result
        print(f"✓ News API test passed: {len(result['articles'])} articles")
        
        return True
    except Exception as e:
        print(f"✗ Tools test failed: {e}")
        return False


def test_memory():
    """Test memory system"""
    print("\n" + "="*60)
    print("TESTING MEMORY SYSTEM")
    print("="*60)
    
    try:
        from app.memory.memory_store import MemoryStore
        
        # Use temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_path = f.name
        
        memory = MemoryStore(storage_path=temp_path)
        
        # Add a decision
        memory.add_decision({'decision': 'TEST', 'value': 100})
        
        # Retrieve decisions
        decisions = memory.get_recent_decisions(limit=1)
        assert len(decisions) > 0
        
        print("✓ Memory system test passed")
        
        # Cleanup
        os.unlink(temp_path)
        
        return True
    except Exception as e:
        print(f"✗ Memory system test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FINANCIAL AI SYSTEM - VERIFICATION TESTS")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Project Modules", test_project_modules),
        ("Fraud Detection", test_fraud_detection),
        ("Risk Assessment", test_risk_assessment),
        ("Data Files", test_data_files),
        ("External Tools", test_tools),
        ("Memory System", test_memory),
        ("Workflow", test_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS READY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Please fix before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
