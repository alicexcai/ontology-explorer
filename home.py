import streamlit as st
from utils import load_data   # loads & caches data once for all pages

st.set_page_config(page_title="ONTOLOGY", layout="wide")
st.title("👋 Welcome to the Ontology Demo")

st.markdown(
    """
    Use the sidebar to switch between **Task Browser** and  
    **Ontology Explorer** pages.
    """
)

# Trigger data caching so every page gets instant access
load_data()
