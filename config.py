"""
Configuration file for the Financial AI System
"""

import os
from pathlib import Path

# ==================== Project Paths ====================
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ==================== Application Settings ====================

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Database / Storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
MEMORY_STORE_PATH = os.getenv("MEMORY_STORE_PATH", str(DATA_DIR / "memory.json"))

# ==================== RAG Settings ====================

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2

# Vector Store
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", str(DATA_DIR / "vector_store"))
VECTOR_STORE_FAISS_INDEX = VECTOR_STORE_PATH + ".faiss"

# Documents
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", str(DATA_DIR / "financial_docs.txt"))
TRANSACTIONS_DATA_PATH = os.getenv("TRANSACTIONS_DATA_PATH", str(DATA_DIR / "transactions.csv"))

# RAG Retrieval
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# ==================== ML Model Settings ====================

# Fraud Detection
FRAUD_MODEL_PATH = os.getenv("FRAUD_MODEL_PATH", str(DATA_DIR / "fraud_model.pkl"))
FRAUD_CONTAMINATION = float(os.getenv("FRAUD_CONTAMINATION", "0.1"))
FRAUD_RANDOM_STATE = int(os.getenv("FRAUD_RANDOM_STATE", "42"))

# ==================== Agent Settings ====================

# Enable/Disable specific agents
ENABLE_FRAUD_DETECTION = os.getenv("ENABLE_FRAUD_DETECTION", "true").lower() == "true"
ENABLE_RISK_ASSESSMENT = os.getenv("ENABLE_RISK_ASSESSMENT", "true").lower() == "true"
ENABLE_RESEARCH = os.getenv("ENABLE_RESEARCH", "true").lower() == "true"
ENABLE_ADVISORY = os.getenv("ENABLE_ADVISORY", "true").lower() == "true"
ENABLE_EXPLAINABILITY = os.getenv("ENABLE_EXPLAINABILITY", "true").lower() == "true"

# RAG Integration
USE_RAG = os.getenv("USE_RAG", "true").lower() == "true"

# ==================== Memory Settings ====================

ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
MEMORY_RETENTION_DAYS = int(os.getenv("MEMORY_RETENTION_DAYS", "30"))

# ==================== Logging ====================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOG_DIR / "app.log"))
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== Security ====================

# CORS Settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Rate limiting (requests per minute)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))

# ==================== Feature Flags ====================

# Experimental features
ENABLE_BATCH_PROCESSING = True
ENABLE_REAL_TIME_MONITORING = False
ENABLE_ADVANCED_NLP = False

# ==================== API Keys (if using real APIs) ====================

# Stock API
STOCK_API_KEY = os.getenv("STOCK_API_KEY", "")
STOCK_API_BASE_URL = os.getenv("STOCK_API_BASE_URL", "https://api.example.com/stock")

# News API
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_BASE_URL = os.getenv("NEWS_API_BASE_URL", "https://api.example.com/news")

# ==================== LLM (Groq) Settings ====================

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_JSON_TEMPERATURE = float(os.getenv("LLM_JSON_TEMPERATURE", "0.3"))

# Enable/Disable LLM for specific agents
USE_LLM_FOR_FRAUD = os.getenv("USE_LLM_FOR_FRAUD", "true").lower() == "true"
USE_LLM_FOR_RISK = os.getenv("USE_LLM_FOR_RISK", "true").lower() == "true"
USE_LLM_FOR_ADVISORY = os.getenv("USE_LLM_FOR_ADVISORY", "true").lower() == "true"
USE_LLM_FOR_PLANNER = os.getenv("USE_LLM_FOR_PLANNER", "true").lower() == "true"

# ==================== Default Thresholds ====================

# Fraud Detection
FRAUD_THRESHOLD_HIGH = float(os.getenv("FRAUD_THRESHOLD_HIGH", "0.7"))
FRAUD_THRESHOLD_MEDIUM = float(os.getenv("FRAUD_THRESHOLD_MEDIUM", "0.4"))

# Risk Assessment
RISK_THRESHOLD_HIGH = float(os.getenv("RISK_THRESHOLD_HIGH", "0.7"))
RISK_THRESHOLD_MEDIUM = float(os.getenv("RISK_THRESHOLD_MEDIUM", "0.3"))

# Confidence Score
MIN_CONFIDENCE_FOR_APPROVAL = float(os.getenv("MIN_CONFIDENCE_FOR_APPROVAL", "0.75"))

# ==================== Sample Data Settings ====================

# For generating sample transactions
NUM_SAMPLE_TRANSACTIONS = int(os.getenv("NUM_SAMPLE_TRANSACTIONS", "1000"))
FRAUD_PERCENTAGE = float(os.getenv("FRAUD_PERCENTAGE", "0.1"))

# ==================== Streamlit Settings ====================

STREAMLIT_THEME = os.getenv("STREAMLIT_THEME", "light")
STREAMLIT_PAGE_LAYOUT = os.getenv("STREAMLIT_PAGE_LAYOUT", "wide")

# ==================== Development Settings ====================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TESTING = os.getenv("TESTING", "false").lower() == "true"

# ==================== Export Configuration ====================

CONFIG = {
    "api": {
        "host": API_HOST,
        "port": API_PORT,
        "workers": API_WORKERS,
        "reload": API_RELOAD
    },
    "rag": {
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "top_k": RAG_TOP_K,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "enabled": USE_RAG
    },
    "models": {
        "fraud_contamination": FRAUD_CONTAMINATION,
        "random_state": FRAUD_RANDOM_STATE
    },
    "memory": {
        "enabled": ENABLE_MEMORY,
        "retention_days": MEMORY_RETENTION_DAYS,
        "store_path": MEMORY_STORE_PATH
    },
    "thresholds": {
        "fraud_high": FRAUD_THRESHOLD_HIGH,
        "fraud_medium": FRAUD_THRESHOLD_MEDIUM,
        "risk_high": RISK_THRESHOLD_HIGH,
        "risk_medium": RISK_THRESHOLD_MEDIUM
    }
}

if __name__ == "__main__":
    # Print configuration on import for debugging
    import json
    print("Current Configuration:")
    print(json.dumps(CONFIG, indent=2, default=str))
