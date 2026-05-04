# 💰 Financial AI System

**Multi-Agent AI for Fraud Detection, Risk Analysis & Explainable Decision-Making**

---

## 🚀 Overview

The **Financial AI System** is an end-to-end multi-agent AI platform designed to analyze financial transactions and generate **structured, explainable decisions** such as:

* ✅ APPROVE
* ⚠️ VERIFY
* ❌ REJECT

The system combines **fraud detection, risk modeling, and Retrieval-Augmented Generation (RAG)** to ensure decisions are **accurate, explainable, and grounded in data**.

---

## 🎯 Problem Statement

Traditional financial systems suffer from:

* Lack of explainability in ML models
* Isolated fraud/risk analysis without context
* Manual review delays
* Hallucinations in LLM-based systems

This project addresses these challenges by building a **modular, explainable AI system** for real-world financial decision-making.

---

## 🧠 Key Features

* 🔍 **Fraud Detection** – Identifies suspicious transaction patterns
* 📊 **Risk Assessment** – Computes risk scores using behavioral signals
* 📚 **RAG (Retrieval-Augmented Generation)** – Grounds responses using financial knowledge
* 🤖 **Multi-Agent Architecture** – Specialized agents for each task
* 🧾 **Explainability** – Provides reasoning for every decision
* 🧠 **Memory Store** – Tracks past queries, decisions, and alerts
* 🌐 **API + UI** – FastAPI backend with Streamlit frontend

---

## 🏗️ System Architecture

```
User Input
   ↓
Planner Agent
   ↓
Fraud Agent → Risk Agent → Research Agent (RAG)
   ↓
Advisory Agent
   ↓
Explainability Agent
   ↓
Memory Store
   ↓
Final Output (API/UI)
```

---

## ⚙️ Workflow

1. **User Input**

   * Query + transaction details

2. **Planner Agent**

   * Determines execution flow

3. **Fraud Agent**

   * Detects anomalies (amount, time, location)

4. **Risk Agent**

   * Computes transaction risk score

5. **Research Agent (RAG)**

   * Retrieves relevant financial knowledge using embeddings + FAISS

6. **Advisory Agent**

   * Produces final decision: APPROVE / VERIFY / REJECT

7. **Explainability Agent**

   * Generates reasoning for decision

8. **Memory Store**

   * Saves history for auditability

---

## 🛠️ Tech Stack

### 🔹 Core

* Python
* FastAPI
* Streamlit

### 🔹 AI / ML

* Sentence-Transformers
* FAISS (Vector Database)
* NumPy, Pandas, Scikit-learn

### 🔹 Architecture

* Multi-Agent System (custom implementation)
* RAG Pipeline
* JSON-based Memory Store

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/your-username/financial-ai-system.git
cd financial-ai-system

# Create virtual environment (recommended Python 3.10)
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Application

### 🔹 Start Backend (FastAPI)

```bash
uvicorn app.api.main:app --reload
```

### 🔹 Start Frontend (Streamlit)

```bash
streamlit run frontend/streamlit_app.py
```

---

## 🌐 Access

* API Docs: http://127.0.0.1:8000/docs
* UI: http://localhost:8501

---

## 📥 Sample Input

```json
{
  "query": "Should I approve this transaction?",
  "transaction": {
    "transaction_id": "TXN12345",
    "amount": 250000,
    "location": "Mumbai",
    "time_of_day": 3,
    "merchant_category": "electronics",
    "frequency_30d": 2,
    "account_age_days": 120
  }
}
```

---

## 📤 Sample Output

```json
{
  "decision": "VERIFY",
  "fraud_risk": "MEDIUM",
  "risk_level": "MEDIUM",
  "explanation": "High transaction amount at unusual time increases risk"
}
```

---

## 🧠 Decision Logic

* **High Fraud Risk → REJECT**
* **Medium Fraud Risk → VERIFY**
* **Low Fraud + Low Risk → APPROVE**

---

## 📊 Use Cases

* Banking fraud detection systems
* Payment gateways
* Fintech risk analysis
* Credit decision systems

---

## 🚀 Future Improvements

* Real-time streaming pipeline
* Advanced ML-based fraud models
* Cloud deployment (AWS/GCP)
* Scalable vector DB (Pinecone)
* Feedback-based learning

---

## 👨‍💻 Author

**Lokesh P**
Computer Science Engineer | AI/ML Enthusiast

---

## ⭐ Key Highlight

> This project demonstrates the ability to design **end-to-end AI systems**, combining multi-agent orchestration, RAG, and explainable decision-making for real-world applications.

---
