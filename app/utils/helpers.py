"""
Utility helper functions.
"""

from typing import Dict, List, Any
import json
from datetime import datetime

def make_json_safe(data):
    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, type({}.keys())):   # 🔥 fixes dict_keys
        return list(data)
    else:
        return data
    
def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def create_json_response(success: bool, data: Any = None, message: str = "") -> Dict:
    """
    Create a standardized JSON response.
    
    Args:
        success: Whether operation was successful
        data: Response data
        message: Optional message
        
    Returns:
        Standardized response dict
    """
    return {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'data': make_json_safe(data),
        'message': message
    }


def validate_transaction(transaction: Dict) -> tuple[bool, str]:
    """
    Validate transaction data.
    
    Args:
        transaction: Transaction dict
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['amount', 'location', 'merchant_category']
    
    for field in required_fields:
        if field not in transaction:
            return False, f"Missing required field: {field}"
    
    try:
        amount = float(transaction['amount'])
        if amount <= 0:
            return False, "Amount must be positive"
    except (ValueError, TypeError):
        return False, "Amount must be a number"
    
    return True, ""


def parse_structured_output(text: str) -> Dict:
    """
    Parse structured output from LLM.
    
    Args:
        text: LLM output text
        
    Returns:
        Parsed dict
    """
    try:
        # Try to extract JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
    except:
        pass
    
    # Fallback: return structured response
    return {
        'raw_output': text,
        'parsed': False
    }


def calculate_risk_score(factors: Dict) -> float:
    """
    Calculate risk score from various factors.
    
    Args:
        factors: Dict with risk factors and weights
        
    Returns:
        Risk score 0.0-1.0
    """
    score = 0.0
    total_weight = 0.0
    
    for factor, value in factors.items():
        # Each factor should be 0.0-1.0
        weight = 1.0
        if isinstance(value, dict) and 'score' in value:
            score += value['score'] * value.get('weight', weight)
            total_weight += value.get('weight', weight)
        elif isinstance(value, (int, float)):
            score += value * weight
            total_weight += weight
    
    if total_weight > 0:
        return min(1.0, max(0.0, score / total_weight))
    return 0.0


def merge_dicts(*dicts) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def pretty_print_dict(d: Dict, indent: int = 2) -> str:
    """Pretty print a dictionary."""
    return json.dumps(d, indent=indent, default=str)
