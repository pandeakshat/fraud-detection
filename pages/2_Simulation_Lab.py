import streamlit as st
from src.layout import load_sidebar
from src.schema import DOMAIN_CONFIG

st.set_page_config(page_title="Simulation Lab", layout="wide")
load_sidebar()

if 'trained_model' not in st.session_state:
    st.warning("⚠️ Please train the model in 'Model Analysis' first.")
    st.stop()

model = st.session_state['trained_model']
domain = st.session_state['domain']
config = DOMAIN_CONFIG[domain]

st.title("🧪 Fraud Simulation Lab")
st.markdown("Adjust parameters to see how the AI detects fraud risk.")

# --- MODE SELECTION ---
mode = st.radio("Mode", ["Interactive Slider", "Exact Value Input"], horizontal=True)

inputs = {}
col1, col2 = st.columns(2)

# --- DYNAMIC UI ---
with col1:
    st.subheader("Numerical Inputs")
    # Loop through the DICTIONARY of numerical features
    for col, settings in config['features']['numerical'].items():
        if mode == "Interactive Slider":
            # Use specific ranges from schema
            inputs[col] = st.slider(
                f"{col}", 
                min_value=float(settings['min']), 
                max_value=float(settings['max']), 
                step=float(settings.get('step', 10.0))
            )
        else:
            inputs[col] = st.number_input(f"{col}", value=float(settings['min']))

with col2:
    st.subheader("Categorical & Flags")
    for col in config['features']['categorical']:
        # Fetch options from the trained encoder classes if available
        if col in model.encoders:
            options = list(model.encoders[col].classes_)
        else:
            options = ["Unknown"]
        inputs[col] = st.selectbox(f"{col}", options)
        
    for col in config['features']['flags']:
        inputs[col] = st.checkbox(f"{col}", value=False)

st.divider()

if st.button("Analyze Transaction", type="primary"):
    risk_prob = model.predict_single(inputs)
    risk_pct = risk_prob * 100
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Fraud Probability", f"{risk_pct:.1f}%")
        
        # Dynamic Threshold Visual
        if risk_pct > 80:
            st.error("🚨 HIGH RISK: BLOCK")
        elif risk_pct > 50:
            st.warning("⚠️ MEDIUM RISK: REVIEW")
        else:
            st.success("✅ LOW RISK: APPROVE")
            
    with c2:
        st.progress(risk_prob)
        st.caption("Risk Confidence Score")