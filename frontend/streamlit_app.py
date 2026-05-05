"""
Streamlit frontend for the Financial AI System.
Provides interactive UI for analysis and recommendations.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph.workflow import FinancialAIWorkflow
from app.utils.helpers import format_currency, format_percentage

# Page configuration
st.set_page_config(
    page_title="Financial AI System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'workflow' not in st.session_state:
    st.session_state.workflow = FinancialAIWorkflow(use_rag=True, enable_memory=True)

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# ==================== Helper Functions ====================

def display_fraud_result(fraud_analysis):
    """Display fraud detection results."""
    if not fraud_analysis or 'error' in fraud_analysis:
        st.warning("Fraud analysis unavailable")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fraud_risk = fraud_analysis.get('fraud_risk', 'UNKNOWN')
        if fraud_risk == 'HIGH':
            st.metric("Fraud Risk", fraud_risk, delta=-1, delta_color="inverse")
        elif fraud_risk == 'MEDIUM':
            st.metric("Fraud Risk", fraud_risk, delta=0)
        else:
            st.metric("Fraud Risk", fraud_risk, delta=1)
    
    with col2:
        confidence = fraud_analysis.get('confidence', 0)
        st.metric("Confidence", f"{confidence:.1%}")
    
    with col3:
        action = fraud_analysis.get('recommended_action', 'N/A')
        st.metric("Action", action)
    
    # Fraud reasons
    reasons = fraud_analysis.get('reasons', [])
    if reasons:
        st.subheader("Fraud Indicators")
        for reason in reasons:
            st.write(f"• {reason}")


def display_risk_result(risk_analysis):
    """Display risk assessment results."""
    if not risk_analysis or 'error' in risk_analysis:
        st.warning("Risk analysis unavailable")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_level = risk_analysis.get('risk_level', 'UNKNOWN')
        if risk_level == 'HIGH':
            st.metric("Risk Level", risk_level, delta=-1, delta_color="inverse")
        elif risk_level == 'MEDIUM':
            st.metric("Risk Level", risk_level, delta=0)
        else:
            st.metric("Risk Level", risk_level, delta=1)
    
    with col2:
        risk_score = risk_analysis.get('risk_score', 0) or risk_analysis.get('transaction_risk_score', 0)
        st.metric("Risk Score", f"{risk_score:.2f}")
    
    with col3:
        recommendation = risk_analysis.get('recommendation', 'N/A')
        st.metric("Recommendation", recommendation)
    
    # Risk breakdown
    breakdown = risk_analysis.get('risk_breakdown', {})
    if breakdown:
        st.subheader("Risk Components")
        for component, value in breakdown.items():
            st.write(f"• {component.replace('_', ' ').title()}: {value:.3f}")


def display_recommendation(recommendation):
    """Display advisory recommendation."""
    if not recommendation or 'error' in recommendation:
        st.warning("Recommendation unavailable")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        decision = recommendation.get('decision', 'HOLD')
        if decision in ['BUY', 'APPROVE', 'ACCEPT']:
            st.metric("Decision", decision, delta=1)
        elif decision in ['SELL', 'REJECT', 'DECLINE']:
            st.metric("Decision", decision, delta=-1, delta_color="inverse")
        else:
            st.metric("Decision", decision, delta=0)
    
    with col2:
        risk_level = recommendation.get('risk_level', 'MEDIUM')
        st.metric("Risk Level", risk_level)
    
    with col3:
        confidence = recommendation.get('confidence_score', 0)
        st.metric("Confidence", f"{confidence:.1%}")
    
    # Reasoning
    reasoning = recommendation.get('reasoning', [])
    if reasoning:
        st.subheader("Reasoning")
        for reason in reasoning:
            st.write(f"• {reason}")


def display_explanation(explanation):
    """Display decision explanation."""
    if not explanation or 'error' in explanation:
        st.warning("Explanation unavailable")
        return
    
    st.subheader("Decision Explanation")
    st.write(explanation.get('decision_summary', 'Analysis complete'))
    
    # Key factors
    key_factors = explanation.get('key_factors', [])
    if key_factors:
        st.subheader("Key Factors")
        for factor in key_factors:
            st.write(f"**{factor.get('agent', 'N/A')}**: {factor.get('finding', 'N/A')}")
    
    # Detailed reasoning
    detailed_reasoning = explanation.get('detailed_reasoning', [])
    if detailed_reasoning:
        st.subheader("Detailed Reasoning")
        for step in detailed_reasoning:
            st.write(f"**Step {step.get('step', '')}**: {step.get('description', '')}")
    
    # Recommendations
    recommendations = explanation.get('recommendations_for_user', [])
    if recommendations:
        st.subheader("Recommendations for You")
        for rec in recommendations:
            st.write(f"• {rec}")


# ==================== Main App ====================

def main():
    """Main app function."""
    
    # Header
    st.title("💰 Financial AI System")
    st.markdown("AI-Powered Financial Intelligence for Risk, Fraud Detection & Advisory")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page:",
            ["Analysis", "Transaction Scanner", "Portfolio Risk", "Market Research", "Memory & History"]
        )
    
    # ==================== Analysis Page ====================
    if page == "Analysis":
        st.header("Financial Analysis")
        
        # Input columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Query")
            query = st.text_area(
                "Enter your financial question or concern:",
                placeholder="e.g., Is this transaction fraudulent? What's the risk in this portfolio?"
            )
        
        with col2:
            st.subheader("Transaction Details (Optional)")
            add_transaction = st.checkbox("Analyze a transaction")
            
            transaction = None
            if add_transaction:
                col_t1, col_t2 = st.columns(2)
                
                with col_t1:
                    transaction_id = st.text_input("Transaction ID", value="TXN001")
                    amount = st.number_input("Amount ($)", value=100.0, min_value=0.0)
                    time_of_day = st.slider("Time of Day (Hour)", 0, 23, 12)
                    location = st.selectbox(
                        "Location",
                        ["US", "UK", "CN", "JP", "BR", "RU", "DZ", "NG", "KE", "VN", "GH", "PK"]
                    )
                
                with col_t2:
                    merchant = st.selectbox(
                        "Merchant Category",
                        ["grocery", "gas", "restaurant", "pharmacy", "electronics", "jewelry", "luxury_goods"]
                    )
                    frequency = st.number_input("Frequency (30 days)", value=5, min_value=0)
                    account_age = st.number_input("Account Age (days)", value=365, min_value=0)
                
                transaction = {
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'time_of_day': time_of_day,
                    'location': location,
                    'merchant_category': merchant,
                    'frequency_30d': frequency,
                    'account_age_days': account_age
                }
        
        # Analyze button
        if st.button("🚀 Analyze", key="analyze_btn", use_container_width=True):
            if not query.strip():
                st.error("Please enter a query")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        result = st.session_state.workflow.execute(query, transaction)
                        
                        # Store in history
                        st.session_state.analysis_history.append({
                            'timestamp': datetime.now(),
                            'query': query,
                            'result': result
                        })
                        
                        # Display results
                        if result['success']:
                            st.success("Analysis completed successfully!")
                            
                            # Tabs for different results
                            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                                "Fraud", "Risk", "Research", "Recommendation", "Explanation"
                            ])
                            
                            with tab1:
                                display_fraud_result(result.get('fraud_assessment'))
                            
                            with tab2:
                                display_risk_result(result.get('risk_assessment'))
                            
                            with tab3:
                                research = result.get('research_findings', {})
                                if research and 'documents' in research:
                                    st.subheader("Retrieved Documents")
                                    for doc in research['documents'][:3]:
                                        st.write(f"📄 {doc.get('document', '')[:200]}...")
                            
                            with tab4:
                                display_recommendation(result.get('recommendation'))
                            
                            with tab5:
                                display_explanation(result.get('explanation'))
                        else:
                            st.error(f"Analysis failed: {result.get('errors', [])}")
                    
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
    
    # ==================== Transaction Scanner ====================
    elif page == "Transaction Scanner":
        st.header("🔍 Transaction Fraud Scanner")
        
        # Sample transactions
        st.subheader("Sample Transactions")
        
        sample_txns = [
            {
                'transaction_id': 'TXN006',
                'amount': 5000,
                'time_of_day': 2,
                'location': 'UK',
                'merchant_category': 'jewelry',
                'frequency_30d': 1,
                'account_age_days': 30
            },
            {
                'transaction_id': 'TXN003',
                'amount': 45.75,
                'time_of_day': 16,
                'location': 'US',
                'merchant_category': 'gas',
                'frequency_30d': 8,
                'account_age_days': 365
            }
        ]
        
        for txn in sample_txns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{txn['transaction_id']}** | {format_currency(txn['amount'])} | {txn['location']}")
            
            with col2:
                if st.button("Scan", key=txn['transaction_id']):
                    with st.spinner("Scanning transaction..."):
                        result = st.session_state.workflow.fraud_agent.analyze_transaction(txn)
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Risk Level", result.get('fraud_risk'))
                        with col_b:
                            st.metric("Confidence", f"{result.get('confidence', 0):.1%}")
                        with col_c:
                            st.metric("Action", result.get('recommended_action'))
                        
                        reasons = result.get('reasons', [])
                        if reasons:
                            st.write("**Indicators:**")
                            for r in reasons:
                                st.write(f"• {r}")
    
    # ==================== Portfolio Risk ====================
    elif page == "Portfolio Risk":
        st.header("📊 Portfolio Risk Assessment")
        
        st.subheader("Portfolio Analytics")
        
        # Sample portfolio
        portfolio_data = [
            {'symbol': 'AAPL', 'shares': 100, 'price': 178.50, 'volatility': 0.25},
            {'symbol': 'GOOGL', 'shares': 50, 'price': 130.00, 'volatility': 0.22},
            {'symbol': 'SPY', 'shares': 200, 'price': 450.00, 'volatility': 0.18},
        ]
        
        df = pd.DataFrame(portfolio_data)
        df['value'] = df['shares'] * df['price']
        
        st.dataframe(df, use_container_width=True)
        
        if st.button("Analyze Portfolio Risk"):
            with st.spinner("Analyzing..."):
                portfolio = {'holdings': [
                    {'symbol': r['symbol'], 'volatility': r['volatility'], 'value': r['value']}
                    for _, r in df.iterrows()
                ]}
                
                result = st.session_state.workflow.risk_agent.assess_portfolio_risk(portfolio)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Portfolio Risk", result.get('portfolio_risk_level'))
                with col2:
                    st.metric("Risk Score", f"{result.get('portfolio_risk_score', 0):.3f}")
                with col3:
                    st.metric("Concentration Risk", result.get('concentration_risk'))
    
    # ==================== Market Research ====================
    elif page == "Market Research":
        st.header("📈 Market Research")
        
        research_type = st.radio("Research Type:", ["Stock", "Sector", "Topic"])
        
        if research_type == "Stock":
            symbol = st.selectbox("Select Stock", ["AAPL", "GOOGL", "MSFT", "JPM", "BAC"])
            
            if st.button("Research Stock"):
                with st.spinner("Researching..."):
                    result = st.session_state.workflow.research_agent.research_stock(symbol)
                    
                    # Stock data
                    st.subheader(f"{symbol} Analysis")
                    col1, col2, col3 = st.columns(3)
                    
                    stock_data = result.get('stock_data', {})
                    with col1:
                        st.metric("Price", format_currency(stock_data.get('current_price', 0)))
                    with col2:
                        st.metric("Volatility", f"{stock_data.get('volatility', 0):.1%}")
                    with col3:
                        st.metric("Trend", stock_data.get('trend', 'N/A'))
                    
                    # News
                    st.subheader("Recent News")
                    news = result.get('news', {})
                    for article in news.get('articles', [])[:3]:
                        st.write(f"📰 {article.get('headline')}")
        
        elif research_type == "Topic":
            topic = st.text_input("Enter research topic:", placeholder="e.g., Portfolio diversification")
            
            if st.button("Research Topic"):
                with st.spinner("Researching..."):
                    result = st.session_state.workflow.research_agent.research_topic(topic, depth='deep')
                    
                    st.subheader(f"Research: {topic}")
                    
                    documents = result.get('documents', [])
                    if documents:
                        st.write(f"Found {len(documents)} relevant documents\n")
                        for doc in documents[:3]:
                            st.write(f"📄 {doc.get('document', '')[:300]}...\n")
    
    # ==================== Memory & History ====================
    elif page == "Memory & History":
        st.header("📚 Analysis History & Memory")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Analyses")
            for i, item in enumerate(st.session_state.analysis_history[-5:]):
                st.write(f"{i+1}. {item['query'][:50]}...")
        
        with col2:
            st.subheader("Memory Summary")
            memory_info = st.session_state.workflow.get_memory_summary()
            
            for key, value in memory_info.items():
                if key != 'recent_activity':
                    st.write(f"{key.replace('_', ' ').title()}: {value}")
        
        # Clear memory
        if st.button("Clear Old Memory (>30 days)"):
            st.session_state.workflow.clear_old_memory(30)
            st.success("Memory cleared!")


if __name__ == "__main__":
    main()
