"""
Research Agent - LLM-powered research using RAG and APIs.
Combines document retrieval with LLM reasoning for financial insights.
"""

import json
import logging
from typing import Dict, List, Optional
from app.rag.retriever import RAGRetriever
from app.llm.llm_client import LLMClient
from app.tools.stock_api import StockAPI
from app.tools.news_api import NewsAPI
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    LLM-powered research agent with RAG and external APIs.
    Synthesizes document knowledge with market data and LLM reasoning.
    """
    
    SYSTEM_PROMPT = """You are a senior financial research analyst with expertise in:
- Financial analysis and equity research
- Market trends and economic indicators
- Risk assessment and portfolio analysis
- Investment thesis development

Conduct thorough research using:
1. Retrieved financial documents
2. Market data and price trends
3. News and sentiment analysis
4. Economic indicators

Provide evidence-based insights and analysis.
Always cite sources and data. Maintain objectivity."""
    
    def __init__(self, use_rag: bool = True):
        """
        Initialize research agent with LLM and RAG.
        
        Args:
            use_rag: Whether to initialize RAG system
        """
        self.retriever = None
        self.llm = LLMClient(api_key=GROQ_API_KEY)
        
        if use_rag:
            self._initialize_rag()
        
        logger.info(f"ResearchAgent initialized (RAG enabled: {use_rag})")
    
    def _initialize_rag(self):
        """Initialize RAG system."""
        try:
            self.retriever = RAGRetriever()
            try:
                self.retriever.initialize_from_docs_file('data/financial_docs.txt')
                logger.info("RAG system initialized successfully")
            except Exception as e:
                logger.warning(f"Could not load financial documents: {e}")
        except Exception as e:
            logger.warning(f"RAG initialization failed: {e}")
            self.retriever = None
    
    def research_topic(self, topic: str, depth: str = 'medium') -> Dict:
        """
        Research a financial topic using RAG + LLM.
        
        Args:
            topic: Topic to research
            depth: Research depth - 'shallow', 'medium', 'deep'
            
        Returns:
            Research findings with LLM analysis
        """
        try:
            findings = {
                'topic': topic,
                'depth': depth,
                'retrieved_documents': [],
                'api_data': {},
                'llm_analysis': {}
            }
            
            # Retrieve relevant documents using RAG
            retrieved_docs = []
            if self.retriever:
                try:
                    retrieved_docs = self.retriever.retrieve(topic, k=5)
                    findings['retrieved_documents'] = retrieved_docs
                except Exception as e:
                    logger.warning(f"RAG retrieval error: {e}")
            
            # Add API data
            findings['api_data'] = self._get_api_data(topic)
            
            # Use LLM to synthesize research
            findings['llm_analysis'] = self._llm_synthesize_research(
                topic, retrieved_docs, findings['api_data'], depth
            )
            
            return findings
        
        except Exception as e:
            logger.error(f"Error researching topic: {e}")
            return {
                'topic': topic,
                'error': str(e),
                'depth': depth
            }
    
    def _llm_synthesize_research(self, topic: str, documents: List, api_data: Dict, 
                                  depth: str) -> Dict:
        """Synthesize research using LLM."""
        try:
            prompt = f"""
Conduct {depth}-level research on: {topic}

Retrieved Knowledge:
{json.dumps(documents[:2], indent=2) if documents else "No documents retrieved"}

Market Data:
{json.dumps(api_data, indent=2) if api_data else "No market data available"}

Provide comprehensive research with:
- Executive summary
- Key findings
- Market context
- Risk factors
- Recommendations

Return JSON with:
{{
    "executive_summary": "brief overview",
    "key_findings": ["finding1", "finding2", ...],
    "market_context": "industry/economic context",
    "data_sources": ["source1", "source2", ...],
    "risk_factors": ["risk1", "risk2", ...],
    "investment_thesis": "if applicable",
    "recommendations": "actionable insights",
    "confidence": 0.0-1.0
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.5 if depth == 'deep' else 0.3,
                max_tokens=1500
            )
            
            return result
        
        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")
            return {
                'error': str(e),
                'fallback': True
            }
    
    def research_stock(self, symbol: str) -> Dict:
        """
        Research a specific stock using LLM + RAG + APIs.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Stock research report
        """
        try:
            report = {
                'symbol': symbol,
                'stock_data': {},
                'news': {},
                'market_context': {},
                'llm_analysis': {}
            }
            
            # Get stock data
            report['stock_data'] = StockAPI.get_stock_price(symbol)
            
            # Get news
            report['news'] = NewsAPI.get_news(symbol)
            
            # Get market context
            report['market_context'] = StockAPI.get_market_data()
            
            # Retrieve relevant documents about this stock
            documents = []
            if self.retriever:
                try:
                    documents = self.retriever.retrieve(f"equity analysis {symbol}", k=3)
                except:
                    pass
            
            # Use LLM for stock analysis
            report['llm_analysis'] = self._llm_stock_analysis(symbol, report, documents)
            
            return report
        
        except Exception as e:
            logger.error(f"Error researching stock {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    def _llm_stock_analysis(self, symbol: str, report: Dict, documents: List) -> Dict:
        """Generate LLM-based stock analysis."""
        try:
            prompt = f"""
Analyze stock: {symbol}

Market Data:
- Price: ${report['stock_data'].get('current_price', 'N/A')}
- Trend: {report['stock_data'].get('trend', 'N/A')}
- Volume: {report['stock_data'].get('volume', 'N/A')}

News Sentiment: {report['news'].get('market_sentiment', 'N/A')}

Retrieved Knowledge:
{json.dumps(documents[:1], indent=2) if documents else "None"}

Provide:
- Investment thesis
- Key risks
- Price targets
- Buy/Sell/Hold recommendation

Return JSON with:
{{
    "recommendation": "BUY/SELL/HOLD",
    "thesis": "investment thesis",
    "price_target": value or null,
    "risks": ["risk1", "risk2"],
    "catalysts": ["catalyst1", "catalyst2"],
    "confidence": 0.0-1.0
}}
"""
            
            result = self.llm.generate_json(
                prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1000
            )
            
            return result
        
        except Exception as e:
            logger.error(f"LLM stock analysis error: {e}")
            return {'error': str(e)}
        
        if any(word in topic_lower for word in ['apple', 'aapl', 'google', 'googl', 'microsoft', 'msft']):
            symbols = []
            if 'apple' in topic_lower or 'aapl' in topic_lower:
                symbols.append('AAPL')
            if 'google' in topic_lower or 'googl' in topic_lower:
                symbols.append('GOOGL')
            if 'microsoft' in topic_lower or 'msft' in topic_lower:
                symbols.append('MSFT')
            
            data['stocks'] = [StockAPI.get_stock_price(s) for s in symbols]
        
        if any(word in topic_lower for word in ['news', 'market', 'sentiment']):
            data['news'] = NewsAPI.get_news('Market', limit=3)
        
        if any(word in topic_lower for word in ['economic', 'calendar', 'events']):
            data['economic_calendar'] = NewsAPI.get_economic_calendar()
        
        return data
    
    def _generate_summary(self, findings: Dict) -> List[str]:
        """Generate summary from research findings."""
        summary = []
        
        documents = findings.get('documents', [])
        if documents:
            summary.append(f"Found {len(documents)} relevant documents")
        
        api_data = findings.get('api_data', {})
        if api_data:
            summary.append(f"Gathered data from {len(api_data)} sources")
        
        summary.append(f"Topic: {findings.get('topic', '')}")
        
        return summary
    
    def _generate_stock_insights(self, report: Dict) -> List[Dict]:
        """Generate insights about a stock."""
        insights = []
        
        stock_data = report.get('stock_data', {})
        news = report.get('news', {})
        
        if stock_data:
            volatility = stock_data.get('volatility', 0)
            trend = stock_data.get('trend', 'stable')
            
            if volatility > 0.3:
                insights.append({
                    'type': 'volatility',
                    'message': f'High volatility ({volatility:.1%}) - increased risk',
                    'action': 'Consider hedging strategies'
                })
            
            if trend == 'down':
                insights.append({
                    'type': 'trend',
                    'message': 'Downward trend detected',
                    'action': 'Monitor for support levels'
                })
        
        if news:
            sentiment = news.get('market_sentiment', 'NEUTRAL')
            if sentiment == 'POSITIVE':
                insights.append({
                    'type': 'sentiment',
                    'message': 'Market sentiment is positive',
                    'action': 'Consider accumulating on dips'
                })
        
        return insights
    
    def _generate_sector_insights(self, report: Dict) -> List[Dict]:
        """Generate insights about a sector."""
        insights = []
        
        news = report.get('news', {})
        
        if news:
            performance = news.get('sector_performance', 'neutral')
            insights.append({
                'type': 'performance',
                'message': f'Sector is {performance}',
                'implications': 'Monitor sector rotation trends'
            })
        
        return insights
