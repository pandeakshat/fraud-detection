import streamlit as st
from src.layout import load_sidebar

st.set_page_config(page_title="FraudGuard AI", layout="wide")

# Load Global Sidebar
df = load_sidebar()

st.title("🛡️ FraudGuard AI: Supervisor")
st.markdown("""
Welcome to the supervised learning suite.

**How to use:**
1. **Select your Dataset** in the sidebar.
2. Go to **Model Analysis** to train a Random Forest on your data.
3. Go to **Simulation Lab** to test "What-If" scenarios and get advice.
""")

if df is not None:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)
else:
    st.info("Please select or upload a dataset in the sidebar.")