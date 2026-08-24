from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import traceback

app = FastAPI(title="Razorpay AI Risk Manager API")

model = None
try:
    model = joblib.load("razorpay_risk_model.pkl")
    print("SUCCESS: Model loaded successfully!")
except Exception as e:
    print("ERROR loading model:", e)

class TransactionRequest(BaseModel):
    category: str
    amt: float
    gender: str
    lat: float
    long: float
    city_pop: int
    merch_lat: float
    merch_long: float
    unix_time: int
    trans_date_trans_time: str
    dob: str
    merchant: str = "fraud_unknown"

@app.post("/predict-risk")
def predict_risk(data: TransactionRequest):
    global model
    try:
        try:
            input_dict = data.model_dump()
        except AttributeError:
            input_dict = data.dict()

        raw_data = pd.DataFrame([input_dict])
        
        dt = pd.to_datetime(raw_data['trans_date_trans_time'])
        dob = pd.to_datetime(raw_data['dob'])
        
        raw_data['hour'] = dt.dt.hour
        raw_data['day_of_week'] = dt.dt.dayofweek
        raw_data['distance'] = np.sqrt((raw_data['lat'] - raw_data['merch_lat'])**2 + (raw_data['long'] - raw_data['merch_long'])**2)
        raw_data['age'] = (dt - dob).dt.days // 365
        
        # Risk Score Calculation (Model Prediction + Fallback Safety)
        risk_probability = 0.05  # Default low risk baseline
        
        if model is not None:
            try:
                # Align columns with model
                if hasattr(model, "feature_name_"):
                    expected_features = model.feature_name_
                    for col in expected_features:
                        if col not in raw_data.columns:
                            raw_data[col] = 0
                    model_input = raw_data[expected_features].copy()
                    
                    for col in model_input.columns:
                        if model_input[col].dtype == 'object':
                            model_input[col] = model_input[col].astype('category')
                    
                    risk_probability = float(model.predict_proba(model_input)[0, 1])
            except Exception as inner_e:
                print("LGBM Predict Error, falling back to heuristic engine:", inner_e)
                # Rule-based fallback if categorical features mismatch
                amt = float(raw_data['amt'].values[0])
                dist = float(raw_data['distance'].values[0])
                hour = int(raw_data['hour'].values[0])
                
                # Rule heuristics based on Sparkov dataset features
                score = 0.05
                if amt > 300: score += 0.45
                if dist > 1.5: score += 0.25
                if hour in [22, 23, 0, 1, 2, 3]: score += 0.20
                risk_probability = min(score, 0.98)

        threshold = 0.55
        is_high_risk = risk_probability >= threshold
        
        return {
            "transaction_risk_score": round(risk_probability, 4),
            "decision": "FLAGGED_HIGH_RISK" if is_high_risk else "APPROVED",
            "threshold_applied": threshold,
            "action": "Trigger 2FA / Manual Review" if is_high_risk else "Process Payment"
        }
        
    except Exception as e:
        print("--- SERVER TRACEBACK ERROR ---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "Razorpay AI Risk Manager API is active"}
