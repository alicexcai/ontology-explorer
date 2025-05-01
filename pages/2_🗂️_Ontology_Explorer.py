import json
from pathlib import Path
import streamlit as st
import ast

DATA_DIR = Path(__file__).parent.parent / "data"

def squash(node):
    if not isinstance(node, dict):          # ignore non-dicts (sets, lists …)
        return node
    if all(isinstance(v, dict) and not v for v in node.values()):
        return list(node)                   # leaf → list of keys
    return {k: squash(v) for k, v in node.items()}

# ---------------------------------------------------------------------
def load_raw(role: str) -> dict:
    with open(DATA_DIR / f"{role}_taxonomy.txt", "r", encoding="utf-8") as fp:   # your file name
        text   = fp.read()
        data   = ast.literal_eval(text)
        squashed = squash(data)
    return squashed

# ---------------------------------------------------------------------
st.header("🗂️ Ontology Explorer")

tabs = st.tabs(["Verb", "Object", "Purpose", "Method"])
for role, tab in zip(["verb", "object", "purpose", "method"], tabs):
    with tab:
        st.subheader(f"{role.capitalize()} taxonomy")
        st.json(load_raw(role), expanded=False)     # toggleable viewer
