# pages/1_Model_Analysis.py
import streamlit as st
import pandas as pd
from src.layout import load_sidebar
from src.schema import DOMAIN_CONFIG
from src.ml_logic import FraudModel

st.set_page_config(page_title="Model Analysis", layout="wide")
load_sidebar()

if 'current_df' not in st.session_state:
    st.error("No data loaded.")
    st.stop()

domain = st.session_state['domain']
df = st.session_state['current_df']
config = DOMAIN_CONFIG[domain]

st.title(f"🧠 Model Training: {domain}")

# --- MODEL SELECTION ---
col_sel1, col_sel2 = st.columns([1, 3])
with col_sel1:
    model_choice = st.selectbox(
        "Select Architecture", 
        ["Random Forest", "Gradient Boosting"]
    )

with col_sel2:
    st.info(
        "**Random Forest**: Good for balanced robustness.\n\n"
        "**Gradient Boosting**: Better at finding specific, hard-to-catch fraud patterns."
    )

if st.button(f"Train {model_choice}", type="primary"):
    with st.spinner("Training..."):
        
        # Pass model_choice to the class
        model = FraudModel(df, config, model_type=model_choice)
        metrics = model.train()
        
        if "error" in metrics:
            st.error(metrics['error'])
            st.stop()

        st.session_state['trained_model'] = model
        st.success(f"{model_choice} Training Complete!")
        
        # --- METRICS & DEBUG ---
        with st.expander("Debug Info", expanded=False):
            st.write(metrics['debug'])

        c1, c2, c3 = st.columns(3)
        c1.metric("Precision", f"{metrics['precision']:.2%}")
        c2.metric("Recall", f"{metrics['recall']:.2%}")
        c3.metric("F1 Score", f"{metrics['f1']:.2%}")
        
        # --- FEATURE IMPORTANCE ---
        st.subheader("What did this model learn?")
        importance_df = pd.DataFrame(
            list(metrics['importance'].items()), 
            columns=['Feature', 'Importance']
        ).sort_values(by='Importance', ascending=False).head(10)
        
        st.bar_chart(importance_df.set_index('Feature'))