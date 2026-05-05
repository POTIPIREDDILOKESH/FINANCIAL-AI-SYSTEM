"""
Mock News API for retrieving financial news and market sentiment.
"""

from typing import Dict, List
import random
from datetime import datetime, timedelta


class NewsAPI:
    """Mock News API for financial data."""
    
    SAMPLE_NEWS = {
        'AAPL': [
            "Apple Q4 earnings beat expectations with strong iPhone sales",
            "Apple announces new AI features for iOS devices",
            "Apple stock rises on strong guidance for Q1"
        ],
        'GOOGL': [
            "Google expands cloud services with new AI tools",
            "Alphabet reports record quarterly revenue",
            "Google faces antitrust scrutiny but remains confident"
        ],
        'MSFT': [
            "Microsoft partners with OpenAI for enterprise solutions",
            "Microsoft achieves record profitability",
            "Azure cloud services see 30% growth"
        ],
        'JPM': [
            "JPMorgan strengthens investment banking business",
            "JPMorgan CEO optimistic about economic outlook",
            "JPMorgan increases dividend to shareholders"
        ],
        'Market': [
            "Fed signals potential rate cuts in coming year",
            "Stock market reaches all-time high amid tech rally",
            "Consumer spending remains robust despite inflation concerns",
            "Unemployment stays near historic lows",
            "Corporate earnings beat expectations across sectors"
        ]
    }
    
    @staticmethod
    def get_news(symbol: str, limit: int = 5) -> Dict:
        """
        Get latest news for a symbol or market.
        
        Args:
            symbol: Stock ticker or 'Market'
            limit: Number of articles to return
            
        Returns:
            Dict with news articles
        """
        if symbol not in NewsAPI.SAMPLE_NEWS:
            symbol = 'Market'
        
        articles = []
        available_news = NewsAPI.SAMPLE_NEWS[symbol]
        
        for i, headline in enumerate(available_news[:limit]):
            days_ago = random.randint(0, 7)
            pub_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            articles.append({
                'headline': headline,
                'summary': f"Detailed analysis: {headline}",
                'source': random.choice(['Reuters', 'Bloomberg', 'CNBC', 'MarketWatch']),
                'published_date': pub_date,
                'sentiment': random.choice(['positive', 'neutral', 'negative']),
                'relevance_score': round(random.uniform(0.7, 1.0), 2)
            })
        
        # Calculate market sentiment
        sentiments = [a['sentiment'] for a in articles]
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        
        sentiment_score = (positive - negative) / len(sentiments) if sentiments else 0
        
        return {
            'symbol': symbol,
            'articles': articles,
            'market_sentiment': NewsAPI._sentiment_to_label(sentiment_score),
            'sentiment_score': round(sentiment_score, 2),
            'positive_articles': positive,
            'negative_articles': negative,
            'neutral_articles': neutral,
        }
    
    @staticmethod
    def get_sector_news(sector: str, limit: int = 5) -> Dict:
        """
        Get news related to a sector.
        
        Args:
            sector: Sector name
            limit: Number of articles
            
        Returns:
            Dict with sector news
        """
        sector_news_map = {
            'Technology': [
                "Tech stocks rally on AI optimism",
                "Semiconductor manufacturers report strong demand",
                "Cloud computing services see accelerating growth",
                "Software companies deliver strong earnings"
            ],
            'Finance': [
                "Banks report record profits from investment banking",
                "Fintech companies disrupt traditional banking",
                "Credit card companies see increased spending",
                "Insurance sector adapts to climate risks"
            ],
            'Commodities': [
                "Oil prices stabilize amid supply concerns",
                "Gold maintains strength as safe-haven asset",
                "Copper prices reflect strong industrial demand",
                "Natural gas prices ease on seasonal decline"
            ]
        }
        
        if sector not in sector_news_map:
            news_items = []
        else:
            news_items = sector_news_map[sector]
        
        articles = []
        for headline in news_items[:limit]:
            days_ago = random.randint(0, 7)
            pub_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            articles.append({
                'headline': headline,
                'sector': sector,
                'source': random.choice(['Financial Times', 'Reuters', 'WSJ']),
                'published_date': pub_date,
                'sentiment': random.choice(['positive', 'neutral', 'negative']),
                'impact_score': round(random.uniform(0.3, 1.0), 2)
            })
        
        return {
            'sector': sector,
            'articles': articles,
            'sector_performance': random.choice(['outperforming', 'neutral', 'underperforming'])
        }
    
    @staticmethod
    def get_market_analysts() -> Dict:
        """
        Get analyst ratings and targets.
        
        Returns:
            Dict with analyst consensus
        """
        return {
            'AAPL': {
                'consensus': 'BUY',
                'target_price': 195.50,
                'current_price': 178.50,
                'upside_potential': 9.5,
                'num_analysts': 45,
                'buy_ratings': 32,
                'hold_ratings': 12,
                'sell_ratings': 1
            },
            'GOOGL': {
                'consensus': 'BUY',
                'target_price': 145.00,
                'current_price': 130.00,
                'upside_potential': 11.5,
                'num_analysts': 42,
                'buy_ratings': 30,
                'hold_ratings': 11,
                'sell_ratings': 1
            },
            'MSFT': {
                'consensus': 'BUY',
                'target_price': 420.00,
                'current_price': 378.50,
                'upside_potential': 11.0,
                'num_analysts': 48,
                'buy_ratings': 38,
                'hold_ratings': 9,
                'sell_ratings': 1
            }
        }
    
    @staticmethod
    def _sentiment_to_label(score: float) -> str:
        """Convert sentiment score to label."""
        if score > 0.3:
            return 'POSITIVE'
        elif score < -0.3:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    @staticmethod
    def get_economic_calendar() -> Dict:
        """
        Get upcoming economic events and calendar.
        
        Returns:
            Dict with economic events
        """
        return {
            'events': [
                {
                    'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'event': 'US Non-Farm Payrolls',
                    'importance': 'HIGH',
                    'forecast': '200K',
                    'previous': '227K'
                },
                {
                    'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'event': 'Federal Reserve Decision',
                    'importance': 'HIGH',
                    'forecast': 'Hold at 5.25-5.50%',
                    'previous': '5.25-5.50%'
                },
                {
                    'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    'event': 'CPI Release',
                    'importance': 'MEDIUM',
                    'forecast': '3.2% YoY',
                    'previous': '3.4% YoY'
                }
            ],
            'market_impact': 'High volatility expected around these events'
        }
