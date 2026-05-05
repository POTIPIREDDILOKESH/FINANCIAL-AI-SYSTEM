"""
Memory store for persisting decisions and past interactions.
"""

from typing import Dict, List, Optional
import json
import os
from datetime import datetime


class MemoryStore:
    """Simple in-memory store with file persistence."""
    
    def __init__(self, storage_path: str = "data/memory.json"):
        """
        Initialize memory store.
        
        Args:
            storage_path: Path to store memory as JSON
        """
        self.storage_path = storage_path
        self.memory: Dict = {
            'decisions': [],
            'queries': [],
            'fraud_alerts': [],
            'risk_assessments': []
        }
        self.load()
    
    def add_decision(self, decision: Dict):
        """
        Add a decision to memory.
        
        Args:
            decision: Dict with decision details
        """
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision
        }
        self.memory['decisions'].append(decision_record)
        self.save()
    
    def add_query(self, query: str, result: Dict):
        """
        Add a query and result to memory.
        
        Args:
            query: Query string
            result: Result dict
        """
        query_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'result': result
        }
        self.memory['queries'].append(query_record)
        self.save()
    
    def add_fraud_alert(self, transaction: Dict, fraud_result: Dict):
        """
        Log a fraud detection result.
        
        Args:
            transaction: Transaction dict
            fraud_result: Fraud detection result
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'transaction': transaction,
            'fraud_assessment': fraud_result
        }
        self.memory['fraud_alerts'].append(alert)
        self.save()
    
    def add_risk_assessment(self, asset: str, risk_result: Dict):
        """
        Log a risk assessment.
        
        Args:
            asset: Asset or symbol
            risk_result: Risk assessment result
        """
        assessment = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'risk_assessment': risk_result
        }
        self.memory['risk_assessments'].append(assessment)
        self.save()
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent decisions."""
        return self.memory['decisions'][-limit:]
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get recent queries."""
        return self.memory['queries'][-limit:]
    
    def get_fraud_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent fraud alerts."""
        return self.memory['fraud_alerts'][-limit:]
    
    def get_risk_assessments(self, limit: int = 10) -> List[Dict]:
        """Get recent risk assessments."""
        return self.memory['risk_assessments'][-limit:]
    
    def search_decisions(self, keyword: str) -> List[Dict]:
        """Search decisions by keyword."""
        results = []
        for decision_record in self.memory['decisions']:
            decision_str = json.dumps(decision_record).lower()
            if keyword.lower() in decision_str:
                results.append(decision_record)
        return results
    
    def clear_old_records(self, days: int = 30):
        """
        Clear records older than specified days.
        
        Args:
            days: Number of days to keep
        """
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for key in self.memory:
            self.memory[key] = [
                record for record in self.memory[key]
                if datetime.fromisoformat(record['timestamp']) > cutoff
            ]
        
        self.save()
    
    def save(self):
        """Save memory to file."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def load(self):
        """Load memory from file."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                try:
                    self.memory = json.load(f)
                except:
                    # File corrupted, use defaults
                    self.memory = {
                        'decisions': [],
                        'queries': [],
                        'fraud_alerts': [],
                        'risk_assessments': []
                    }
    
    def get_summary(self) -> Dict:
        """Get memory summary."""
        return {
            'total_decisions': len(self.memory['decisions']),
            'total_queries': len(self.memory['queries']),
            'total_fraud_alerts': len(self.memory['fraud_alerts']),
            'total_risk_assessments': len(self.memory['risk_assessments']),
            'recent_activity': {
                'latest_decision': self.memory['decisions'][-1] if self.memory['decisions'] else None,
                'latest_query': self.memory['queries'][-1] if self.memory['queries'] else None,
                'latest_fraud_alert': self.memory['fraud_alerts'][-1] if self.memory['fraud_alerts'] else None,
            }
        }
