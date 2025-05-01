from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import pandas as pd
import streamlit as st
import ast

DATA_DIR = Path(__file__).parent / "data"

# ────────────────────────────────── Taxonomy
class Taxonomy:
    def __init__(self, tree: dict):
        self.parent: Dict[str, str] = {}
        self.children: Dict[str, List[str]] = {}
        self._build(tree, None)

    def _add(self, node: str, parent: Optional[str]):
        self.children.setdefault(node, [])
        if parent is not None:
            self.parent[node] = parent
            self.children.setdefault(parent, []).append(node)

    def _build(self, subtree, parent):
        if isinstance(subtree, dict):
            for n, kids in subtree.items():
                self._add(n, parent)
                self._build(kids, n)
        elif isinstance(subtree, (list, set, tuple)):
            for n in subtree:
                self._add(str(n), parent)
        else:                               # scalar leaf
            self._add(str(subtree), parent)

    @property
    def roots(self):        return sorted([n for n in self.children if n not in self.parent])
    def descendants(self, n): return [c for ch in self.children.get(n, []) for c in (ch, *self.descendants(ch))]
    def inclusive(self, n):   return {n, *self.descendants(n)}

# ────────────────────────────────── Navigator
class FacetedNavigator:
    def __init__(self, df: pd.DataFrame, tax: Dict[str, Taxonomy]):
        self.df, self.tax = df, tax
        self.roles = ["verb", "object", "purpose", "method"]

    def _mask(self, sel):
        m = pd.Series(True, index=self.df.index)
        for r, node in sel.items():
            if node:
                m &= self.df[r.capitalize()].isin(self.tax[r].inclusive(node))
        return m

    def view(self, sel): return self.df[self._mask(sel)]

    def valid_children(self, role, parent, allowed_leaves):
        tx = self.tax[role]
        cand = tx.roots if parent is None else tx.children.get(parent, [])
        return sorted(c for c in cand if tx.inclusive(c) & allowed_leaves)

# ────────────────────────────────── Cached loader
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_DIR / "tasks.tsv", sep="\t", dtype=str).fillna("")
    tax = {}
    for role in ["verb", "object", "purpose", "method"]:
        with open(Path(DATA_DIR / f"{role}_taxonomy.txt"), "r", encoding="utf-8") as fp:   # your file name
            text   = fp.read()
            data   = ast.literal_eval(text)
            tax[role] = Taxonomy(data)
    return df, tax
