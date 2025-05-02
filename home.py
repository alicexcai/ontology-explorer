import streamlit as st
from utils import load_data   # loads & caches data once for all pages

st.set_page_config(page_title="ONTOLOGY", layout="wide")
st.title("👋 Welcome to the Ontology Demo Branch")

st.info("This is a demo branch of the Ontology of Collective Intelligence. This branch demonstrates multi-dimensional specialization hierarchies based on the semantic roles of the verb, direct object, purpose, and method involved in work activities. Specifically, we analyze the tasks of 'select' from the O*Net database.")
st.markdown(
    """### Website Structure
The 🛠**Task Browser** page allows you to find O*Net tasks by multi-dimensional and hierarchical filtering based on semantic roles. 

The 🌐**Ontology Explorer** page allows you to examine the generalization-specialization hierarchies for each semantic role (verb, object, purpose, method)."""
)

# Trigger data caching so every page gets instant access
load_data()
