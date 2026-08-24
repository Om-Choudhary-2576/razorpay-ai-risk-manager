import streamlit as st
import requests
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="Razorpay AI Risk Manager",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #0284C7; margin-bottom: 0px; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 25px; }
    .card-box {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .status-approved {
        background-color: #065F46; color: #34D399; padding: 12px;
        border-radius: 8px; font-weight: 700; font-size: 20px; text-align: center;
    }
    .status-flagged {
        background-color: #881337; color: #FB7185; padding: 12px;
        border-radius: 8px; font-weight: 700; font-size: 20px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Section
st.markdown('<div class="main-header">💳 Razorpay AI Risk Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-Time Transaction Fraud Detection & Decision Engine</div>', unsafe_allow_html=True)

# 4. Sidebar Controls (Organized Form)
st.sidebar.markdown("### ⚙️ Transaction Details")

with st.sidebar.form("tx_form"):
    category = st.selectbox("Transaction Category", [
        'shopping_net', 'grocery_pos', 'entertainment', 'gas_transport', 
        'misc_net', 'grocery_net', 'shopping_pos', 'online_retail'
    ])
    amt = st.number_input("Amount ($)", value=350.0, step=10.0)
    gender = st.radio("Customer Gender", ['M', 'F'], horizontal=True)
    
    st.markdown("---")
    st.caption("📍 Geographic Parameters")
    col_lat, col_long = st.columns(2)
    with col_lat:
        lat = st.number_input("User Lat", value=33.96, format="%.2f")
        merch_lat = st.number_input("Merch Lat", value=34.50, format="%.2f")
    with col_long:
        long = st.number_input("User Long", value=-80.93, format="%.2f")
        merch_long = st.number_input("Merch Long", value=-82.10, format="%.2f")
        
    city_pop = st.number_input("City Population", value=150000)
    
    st.markdown("---")
    st.caption("🕒 Time & User Metadata")
    trans_date_trans_time = st.text_input("Transaction Time", "2026-08-24 02:14:25")
    dob = st.text_input("Customer DOB", "1992-05-14")
    unix_time = 1371816865

    submit_btn = st.form_submit_button("⚡ Evaluate Risk", use_container_width=True, type="primary")

# 5. Main Dashboard View
if submit_btn:
    payload = {
        "category": category,
        "amt": amt,
        "gender": gender,
        "lat": lat,
        "long": long,
        "city_pop": int(city_pop),
        "merch_lat": merch_lat,
        "merch_long": merch_long,
        "unix_time": int(unix_time),
        "trans_date_trans_time": trans_date_trans_time,
        "dob": dob
    }

    try:
        response = requests.post("http://127.0.0.1:8000/predict-risk", json=payload)
        
        if response.status_code == 200:
            res = response.json()
            score = res["transaction_risk_score"]
            decision = res["decision"]
            action = res["action"]
            threshold = res["threshold_applied"]

            # Columns Layout
            col_gauge, col_details = st.columns([1.2, 1.8])

            with col_gauge:
                # Plotly Risk Gauge Meter
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score * 100,
                    number={'suffix': "%", 'font': {'size': 36}},
                    title={'text': "Risk Probability Score", 'font': {'size': 18}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#EF4444" if score >= threshold else "#10B981"},
                        'steps': [
                            {'range': [0, 35], 'color': "#064E3B"},
                            {'range': [35, 55], 'color': "#78350F"},
                            {'range': [55, 100], 'color': "#7F1D1D"}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': threshold * 100
                        }
                    }
                ))
                fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col_details:
                st.markdown("<br>", unsafe_allow_html=True)
                if decision == "FLAGGED_HIGH_RISK":
                    st.markdown('<div class="status-flagged">🚨 FLAGGED: HIGH RISK TRANSACTION</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-approved">✅ APPROVED: SAFE TRANSACTION</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"**Recommended Action:** `{action}`")
                st.markdown(f"**Applied Risk Threshold:** `{threshold * 100:.0f}%`")

            st.markdown("---")

            # Insights Section
            col_act, col_reason = st.columns(2)

            with col_act:
                st.subheader("📌 System Protocol")
                if decision == "FLAGGED_HIGH_RISK":
                    st.error("• Step-Up 2FA Authentication Triggered.\n\n• Transaction placed in Manual Review Queue.\n\n• Temporary hold applied on merchant payout.")
                else:
                    st.success("• Direct Payment Settlement Approved.\n\n• No additional verification required.\n\n• Normal processing speed.")

            with col_reason:
                st.subheader("💡 AI Explainability (Top Factors)")
                if decision == "FLAGGED_HIGH_RISK":
                    st.warning("• **High Amount:** Spikes risk probability score.\n\n• **Location Mismatch:** Distance between user and merchant is abnormal.\n\n• **Time Factor:** Off-peak hour activity pattern detected.")
                else:
                    st.info("• **Normal Amount:** Within safe threshold limit.\n\n• **Proximity:** Merchant location is close to user coordinates.\n\n• **Verified Pattern:** Standard spending hours.")

        else:
            st.error(f"Backend API Error: {response.text}")

    except Exception as e:
        st.error(f"Could not connect to FastAPI server. Ensure `uvicorn app:app --reload` is running. Error: {e}")
else:
    st.info("👈 Enter transaction payload parameters in the sidebar and click **Evaluate Risk**.")