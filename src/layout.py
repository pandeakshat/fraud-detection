# src/layout.py
import streamlit as st
import pandas as pd
import os

SAMPLE_DIR = "data/raw"
FILES = {
    "Credit Card": "creditcard.csv",
    "Loan Application": "loan_application.csv",
    "Mobile Transaction": "mobile.csv"
}

def load_sidebar():
    with st.sidebar:
        st.header("🗄️ Data Control")
        domain = st.selectbox(
            "Select Domain", 
            ["Credit Card", "Loan Application", "Mobile Transaction"],
            key="selected_domain"
        )
        
        use_sample = st.toggle("Use Sample Data", value=True)
        df = None

        if use_sample:
            path = os.path.join(SAMPLE_DIR, FILES[domain])
            if os.path.exists(path):
                # FIX 1: Increased limit to 50,000 rows to ensure we catch fraud cases
                # If your machine is slow, lower this to 20,000, but 2k is too small.
                @st.cache_data
                def read_data(p): return pd.read_csv(p, nrows=50000) 
                
                try:
                    df = read_data(path)
                    st.success(f"Loaded: {FILES[domain]} ({len(df)} rows)")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            else:
                st.error(f"File not found: {path}")
        else:
            uploaded = st.file_uploader("Upload CSV", type="csv")
            if uploaded:
                df = pd.read_csv(uploaded) # Load full file for uploads

        if df is not None:
            st.session_state['current_df'] = df
            st.session_state['domain'] = domain
        
    return df