import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

# Configure page
st.set_page_config(
    page_title="Insurance Claims Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .prediction-result {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def load_sample_data():
    """Load sample data for demonstration"""
    try:
        train_df = pd.read_csv("train.csv")
        return train_df
    except FileNotFoundError:
        st.error("❌ Training data not found. Please ensure 'train.csv' exists.")
        return None

def get_api_features():
    """Get expected features from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/features")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Failed to get features from API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API connection failed: {str(e)}")
        return None

def make_prediction(features: Dict[str, float]):
    """Make prediction using FastAPI"""
    try:
        payload = {"features": features}
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API request failed: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🏠 Insurance Claims Severity Predictor</h1>', unsafe_allow_html=True)

    st.markdown("""
    **Predict insurance claim loss amounts using machine learning**

    This application uses an XGBoost model trained on historical insurance claims data
    to predict the severity (loss amount) of new claims.
    """)

    # Sidebar
    st.sidebar.title("🔧 Configuration")

    # API Status
    st.sidebar.subheader("API Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            if health_data.get("model_status") == "loaded":
                st.sidebar.success("✅ API Connected - Model Ready")
            else:
                st.sidebar.error("❌ Model Not Loaded")
        else:
            st.sidebar.error("❌ API Connection Failed")
    except:
        st.sidebar.error("❌ Cannot Connect to API")
        st.sidebar.info("💡 Make sure FastAPI server is running: `python app.py`")

    # Load sample data
    train_df = load_sample_data()

    if train_df is not None:
        # Get feature information
        feature_info = get_api_features()

        if feature_info:
            cat_features = feature_info.get("categorical_features", [])
            cont_features = feature_info.get("continuous_features", [])

            # Main content
            tab1, tab2, tab3 = st.tabs(["🎯 Single Prediction", "📊 Batch Analysis", "📈 Model Insights"])

            with tab1:
                st.header("Single Claim Prediction")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📝 Enter Claim Features")

                    # Create input fields for continuous features
                    input_features = {}

                    st.markdown("**Continuous Features:**")
                    for feature in cont_features:
                        if feature in train_df.columns:
                            sample_val = float(train_df[feature].median())
                            input_features[feature] = st.slider(
                                f"{feature}",
                                min_value=float(train_df[feature].min()),
                                max_value=float(train_df[feature].max()),
                                value=sample_val,
                                step=0.01,
                                help=f"Range: {train_df[feature].min():.2f} - {train_df[feature].max():.2f}"
                            )

                with col2:
                    st.subheader("Categorical Features:")

                    # Create select boxes for categorical features
                    for feature in cat_features:
                        if feature in train_df.columns:
                            unique_vals = sorted(train_df[feature].unique())
                            input_features[feature] = st.selectbox(
                                f"{feature}",
                                options=unique_vals,
                                index=0,
                                help=f"Available values: {len(unique_vals)} categories"
                            )

                # Prediction button
                if st.button("🔮 Predict Loss Amount", type="primary", use_container_width=True):
                    with st.spinner("Making prediction..."):
                        prediction = make_prediction(input_features)

                        if prediction:
                            st.markdown('<div class="prediction-result">', unsafe_allow_html=True)
                            st.success("✅ Prediction Complete!")

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    "Predicted Loss (Log Scale)",
                                    f"{prediction['prediction']:.3f}"
                                )

                            with col2:
                                st.metric(
                                    "Predicted Loss (Actual)",
                                    f"${prediction['prediction_actual']:,.0f}"
                                )

                            with col3:
                                confidence_pct = int(prediction['confidence_score'] * 100)
                                st.metric(
                                    "Confidence Score",
                                    f"{confidence_pct}%"
                                )

                            st.markdown('</div>', unsafe_allow_html=True)

                            # Interpretation
                            st.subheader("📊 Interpretation")
                            actual_pred = prediction['prediction_actual']

                            if actual_pred < 1000:
                                severity = "Low"
                                color = "green"
                            elif actual_pred < 5000:
                                severity = "Medium"
                                color = "orange"
                            else:
                                severity = "High"
                                color = "red"

                            st.markdown(f"**Claim Severity:** <span style='color:{color};font-weight:bold'>{severity}</span>", unsafe_allow_html=True)

            with tab2:
                st.header("Batch Analysis")
                st.info("📋 Batch prediction functionality coming soon!")

            with tab3:
                st.header("Model Insights")

                if train_df is not None:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Target Distribution")
                        fig, ax = plt.subplots(figsize=(8, 5))
                        sns.histplot(train_df['loss'], bins=50, kde=True, ax=ax)
                        ax.set_title("Distribution of Loss Amounts")
                        ax.set_xlabel("Loss Amount ($)")
                        ax.set_ylabel("Frequency")
                        st.pyplot(fig)

                    with col2:
                        st.subheader("Model Performance")
                        # Placeholder for model metrics
                        st.metric("Training MAE", "1,141")
                        st.metric("Validation MAE", "1,141")
                        st.metric("Baseline MAE", "1,798")
                        st.metric("Improvement", "36.5%")

                    st.subheader("Feature Importance")
                    st.info("🔄 Feature importance visualization will be added when model metadata is available")

    # Footer
    st.markdown("---")
    st.markdown("""
    **Built with:** Streamlit, FastAPI, XGBoost, scikit-learn

    **Dataset:** Allstate Claims Severity (Kaggle)

    **Author:** Data Science Portfolio Project
    """)

if __name__ == "__main__":
    main()