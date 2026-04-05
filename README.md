# Insurance Claims Severity Prediction

A complete machine learning project that predicts insurance claim loss amounts using regression techniques. This project demonstrates end-to-end data science workflow from data exploration to model deployment with a full-stack web application.

## 📊 Project Overview

**Dataset**: Allstate Claims Severity (Kaggle Competition)
- **Training samples**: 188,318
- **Test samples**: 125,546
- **Features**: 130 (116 categorical + 14 continuous)
- **Target**: Loss amount (insurance claim severity)

**Problem Type**: Regression
**Evaluation Metric**: Mean Absolute Error (MAE)

## 🏗️ Project Structure

```
insurance-project/
├── main.ipynb              # Main analysis notebook
├── app.py                  # FastAPI backend server
├── streamlit_app.py        # Streamlit web interface
├── run.py                  # Launcher script for easy deployment
├── train.csv              # Training dataset
├── test.csv               # Test dataset
├── requirements.txt       # Python dependencies
├── submission.csv         # Generated predictions
├── model.pkl             # Saved XGBoost model
├── rf_model.pkl          # Saved Random Forest model
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Jupyter Notebook

### Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Quick Launch (Recommended)
```bash
# Install dependencies
python run.py install

# Run both API and web app together
python run.py both
```

#### Manual Launch
```bash
# Start the FastAPI backend
python app.py

# In a new terminal, start the Streamlit frontend
streamlit run streamlit_app.py
```

#### Individual Components
```bash
# Run only the API
python run.py api

# Run only the web interface
python run.py web

# Check if all files are present
python run.py check
```

### API Endpoints

- **GET /**: API information and status
- **GET /health**: Health check
- **GET /features**: List expected input features
- **POST /predict**: Make predictions

Example API usage:
```python
import requests

# Make a prediction
response = requests.post("http://localhost:8000/predict",
    json={
        "features": {
            "cont1": 0.5,
            "cont2": 0.3,
            "cat1": "A",
            # ... other features
        }
    }
)
```

## 📈 Methodology

### 1. Data Exploration
- Analyzed data types and missing values
- Visualized target variable distribution
- Examined feature correlations

### 2. Feature Engineering
- Log-transformed skewed target variable
- One-hot encoded categorical features
- Combined train/test for consistent preprocessing

### 3. Model Development
- **Random Forest**: Baseline ensemble model
- **XGBoost**: Advanced gradient boosting model
- Hyperparameter tuning for optimal performance

### 4. Model Evaluation
- Cross-validation for robust assessment
- MAE calculation on both log and actual scales
- Feature importance analysis

## 📊 Results

| Model | MAE (Log Scale) | MAE (Actual Scale) | Improvement vs Baseline |
|-------|-----------------|-------------------|-------------------------|
| Baseline (Mean) | 0.658 | 1,798 | - |
| Random Forest | 0.458 | 1,248 | 30.5% |
| **XGBoost** | **0.416** | **1,141** | **36.5%** |

**Key Achievement**: XGBoost model achieves competitive performance (top 50% on Kaggle leaderboard)

## 🛠️ Technologies Used

- **Python**: Core programming language
- **pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **scikit-learn**: Machine learning algorithms
- **XGBoost**: Gradient boosting framework
- **matplotlib/seaborn**: Data visualization
- **Jupyter Notebook**: Interactive development environment
- **FastAPI**: REST API framework for model serving
- **Streamlit**: Web application framework for UI
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation for API

## 📝 Skills Demonstrated

- Data preprocessing and feature engineering
- Exploratory data analysis
- Machine learning model development
- Model evaluation and validation
- Python programming best practices
- Technical documentation
- **REST API development with FastAPI**
- **Web application development with Streamlit**
- **Model deployment and serving**
- **Full-stack ML application architecture**

## 🌐 Web Application Features

### Streamlit Interface
- **Interactive Prediction**: Input claim features and get instant predictions
- **Real-time Validation**: Automatic input validation and error handling
- **Visual Analytics**: Model performance metrics and data insights
- **User-friendly Design**: Clean, professional interface with intuitive controls

### FastAPI Backend
- **RESTful API**: Standardized endpoints for model predictions
- **Automatic Documentation**: Interactive API docs at `/docs`
- **Input Validation**: Pydantic models ensure data integrity
- **Error Handling**: Comprehensive error responses and logging
- **Health Monitoring**: API status and model health checks

### Key Features
- 🔮 **Single Claim Prediction**: Predict loss for individual claims
- 📊 **Batch Analysis**: Process multiple claims (planned feature)
- 📈 **Model Insights**: Performance metrics and visualizations
- 🔧 **API Integration**: RESTful endpoints for external integrations

## 🔄 Future Improvements

- Hyperparameter optimization with GridSearchCV
- Feature selection to reduce dimensionality
- Ensemble model stacking
- Cross-validation implementation
- Advanced feature engineering techniques

## 📄 License

This project is for educational purposes. Dataset from Kaggle Allstate Claims Severity competition.

## 👤 Author

Data Science Portfolio Project
- Demonstrates practical ML skills
- End-to-end project workflow
- Production-ready code structure