# 🛡️ Razorpay AI Risk Manager
> **Track 2: AI Risk Manager | Razorpay Builder Internship Submission**

An enterprise-grade, real-time transaction fraud detection engine built on an ML-first pipeline. Powered by LightGBM, exposed via a low-latency FastAPI REST service, and rendered using a high-throughput Streamlit decision dashboard with Explainable AI (XAI) capabilities.

---

## 📌 Executive Summary

Modern payment gateways require sub-100ms fraud detection models that optimize the balance between precision and friction. This project addresses severe class imbalance in real-world payment data using LightGBM and SMOTE, augmented with custom spatial-temporal feature engineering to flag fraud while preserving low false-positive rates.

---

## 📐 System Architecture

```text
[ Incoming Payload ] 
         │
         ▼
┌──────────────────┐
│  FastAPI Backend │ ◄── Dynamic Schema Validation & Feature Transformer
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LightGBM Engine  │ ◄── Trained Model Pipeline (SMOTE + Custom Features)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SHAP XAI Module  │ ◄── Feature Attribution & Risk Reason Codes
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Streamlit UI     │ ◄── Interactive Gauge, Decision Badges & Actions
└──────────────────┘


## 🛠️ Feature Engineering Pipeline
To improve signal-to-noise ratio over raw dataset attributes, the following feature transformations were constructed:

Geographic Delta (distance): Euclidean/Haversine distance proxy calculated between customer coordinates (lat, long) and merchant coordinates (merch_lat, merch_long).

Temporal Attributes (hour, day_of_week): Extracted from trans_date_trans_time to identify off-peak anomalies and non-standard purchasing windows.

Customer Demographics (age): Calculated dynamically via timestamp delta against customer dob.


## 💻 Tech Stack
Machine Learning: LightGBM, Scikit-Learn, Imbalanced-Learn (SMOTE)

Model Explainability: SHAP (TreeExplainer)

Backend Framework: FastAPI, Pydantic, Uvicorn

Frontend Interface: Streamlit, Plotly

Serialization & Utilities: Joblib, Pandas, NumPy


├── app.py                   # FastAPI application with risk evaluation routes
├── dashboard.py             # Streamlit enterprise dashboard UI
├── razorpay_risk_model.pkl  # Serialized LightGBM model artifact
├── requirements.txt         # Project dependencies
└── README.md                # System documentation



##🚀 Quickstart Guide


1. Environment Setup
Clone the repository and install required dependencies:

Bash
git clone [https://github.com/your-username/razorpay-ai-risk-manager.git](https://github.com/your-username/razorpay-ai-risk-manager.git)
cd razorpay-ai-risk-manager
pip install -r requirements.txt
2. Launch FastAPI Backend
Start the microservice server:

Bash
uvicorn app:app --reload
API docs will be available live at http://127.0.0.1:8000/docs.

3. Launch Streamlit Dashboard
In a separate terminal, start the UI interface:

Bash
streamlit run dashboard.py
Dashboard will open automatically at http://localhost:8501.