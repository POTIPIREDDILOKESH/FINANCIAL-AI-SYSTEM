"""
Mock Stock API for retrieving stock data and market information.
"""

from typing import Dict, List
import random
from datetime import datetime, timedelta


class StockAPI:
    """Mock Stock API for retrieving financial data."""
    
    SAMPLE_STOCKS = {
        'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'price_range': (150, 200)},
        'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'price_range': (100, 150)},
        'MSFT': {'name': 'Microsoft', 'sector': 'Technology', 'price_range': (300, 400)},
        'JPM': {'name': 'JPMorgan Chase', 'sector': 'Finance', 'price_range': (150, 200)},
        'BAC': {'name': 'Bank of America', 'sector': 'Finance', 'price_range': (30, 50)},
        'GLD': {'name': 'Gold ETF', 'sector': 'Commodities', 'price_range': (180, 220)},
        'SPY': {'name': 'S&P 500 ETF', 'sector': 'Index', 'price_range': (400, 500)},
    }
    
    @staticmethod
    def get_stock_price(symbol: str) -> Dict:
        """
        Get current stock price and info.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with price, volatility, trend
        """
        if symbol not in StockAPI.SAMPLE_STOCKS:
            return {'error': f'Symbol {symbol} not found'}
        
        stock_info = StockAPI.SAMPLE_STOCKS[symbol]
        min_price, max_price = stock_info['price_range']
        
        # Generate mock data
        current_price = random.uniform(min_price, max_price)
        volatility = random.uniform(0.1, 0.5)
        trend = random.choice(['up', 'down', 'stable'])
        
        return {
            'symbol': symbol,
            'name': stock_info['name'],
            'current_price': round(current_price, 2),
            'volatility': round(volatility, 3),
            'trend': trend,
            'sector': stock_info['sector'],
            '52_week_high': round(max_price * 1.2, 2),
            '52_week_low': round(min_price * 0.8, 2),
        }
    
    @staticmethod
    def get_market_data(index: str = 'SPY') -> Dict:
        """
        Get market index data.
        
        Args:
            index: Market index symbol
            
        Returns:
            Dict with market data
        """
        indices = {
            'SPY': {'value': 450, 'name': 'S&P 500'},
            'NASDAQ': {'value': 14000, 'name': 'NASDAQ'},
            'DXY': {'value': 103, 'name': 'US Dollar Index'},
        }
        
        if index not in indices:
            return {'error': f'Index {index} not found'}
        
        info = indices[index]
        value = info['value']
        change = random.uniform(-5, 5)
        
        return {
            'index': index,
            'name': info['name'],
            'value': round(value + change, 2),
            'change_percent': round(change / value * 100, 2),
            'volatility_index': round(random.uniform(10, 40), 2),
        }
    
    @staticmethod
    def get_portfolio_analysis(holdings: List[Dict]) -> Dict:
        """
        Analyze a portfolio of holdings.
        
        Args:
            holdings: List of dicts with 'symbol' and 'quantity'
            
        Returns:
            Dict with portfolio metrics
        """
        total_value = 0
        stocks_data = []
        
        for holding in holdings:
            stock = StockAPI.get_stock_price(holding['symbol'])
            if 'current_price' in stock:
                value = stock['current_price'] * holding['quantity']
                total_value += value
                stocks_data.append({
                    'symbol': stock['symbol'],
                    'price': stock['current_price'],
                    'quantity': holding['quantity'],
                    'value': round(value, 2),
                    'volatility': stock['volatility']
                })
        
        # Calculate portfolio metrics
        avg_volatility = sum(s['volatility'] for s in stocks_data) / len(stocks_data) if stocks_data else 0
        
        return {
            'total_value': round(total_value, 2),
            'num_holdings': len(stocks_data),
            'average_volatility': round(avg_volatility, 3),
            'risk_level': StockAPI._calculate_risk_level(avg_volatility),
            'holdings': stocks_data,
        }
    
    @staticmethod
    def _calculate_risk_level(volatility: float) -> str:
        """Calculate risk level based on volatility."""
        if volatility < 0.15:
            return 'LOW'
        elif volatility < 0.35:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    @staticmethod
    def get_dividend_info(symbol: str) -> Dict:
        """Get dividend information for a stock."""
        if symbol not in StockAPI.SAMPLE_STOCKS:
            return {'error': f'Symbol {symbol} not found'}
        
        return {
            'symbol': symbol,
            'dividend_yield': round(random.uniform(0.5, 4.0), 2),
            'last_dividend_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            'next_dividend_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'annual_dividend': round(random.uniform(0.5, 10.0), 2),
        }
