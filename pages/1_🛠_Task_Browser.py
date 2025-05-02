import streamlit as st
from utils import load_data, FacetedNavigator

df, tax = load_data()
nav = FacetedNavigator(df, tax)

# ──────────────────────────────────────────────────────────────────────────
# Pretty breadcrumb: one line per level, growing number of ">" prefixes.
# The leaf gets a ✅ in front of it.
# ──────────────────────────────────────────────────────────────────────────
def ladder(role: str, leaf: str, tax) -> str:
    """
    Return a markdown string formatted like:
        root
        > child
        >> child2
        >>> ✅leaf
    """
    tx = tax[role]
    if not leaf:
        return "—"

    # Build ancestor chain  (root … leaf)
    chain = [leaf]
    node = leaf
    while node in tx.parent:
        node = tx.parent[node]
        chain.append(node)
    chain.reverse()

    lines = []
    for depth, node in enumerate(chain):
        prefix = "> " * depth               # "", "> ", ">> ", …
        bullet = f"✅{node}" if depth == len(chain) - 1 else node
        lines.append(prefix + bullet)
    return "\n".join(lines)



# session-state dict of current selections
if "sel" not in st.session_state:
    st.session_state.sel = {r: None for r in nav.roles}
sel = st.session_state.sel

st.header("🛠 Task Browser")

# ── sidebar filters
with st.sidebar:
    st.subheader("Filters")
    def cascade(role):
        keyp = f"{role}_path"
        st.session_state.setdefault(keyp, [])
        path = st.session_state[keyp]

        leaves = set(nav.view({k: v for k, v in sel.items() if k != role})[role.capitalize()])
        parent, depth = None, 0
        while True:
            opts = nav.valid_children(role, parent, leaves)
            if not opts: break
            choice = st.selectbox(
                f"{role.capitalize()} ▸ level {depth+1}",
                ["— Any —"] + opts,
                index=(["— Any —"] + opts).index(path[depth]) if depth < len(path) and path[depth] in opts else 0,
            )
            if choice == "— Any —":
                path[:] = path[:depth]; break
            if depth < len(path): path[depth] = choice
            else: path.append(choice)
            parent, depth = choice, depth + 1
            if depth > 10: break
        sel[role] = path[-1] if path else None

    for r in nav.roles:
        with st.expander(r.capitalize(), True):
            cascade(r)
            if st.button(f"Clear {r}", key=f"clr_{r}"):
                st.session_state[f"{r}_path"] = []; sel[r] = None
    if st.button("Clear ALL"):
        for r in nav.roles:
            st.session_state[f"{r}_path"] = []; sel[r] = None

# ── results

# Interactive grid  •  click a row → show details underneath
# ──────────────────────────────────────────────────────────────────────────────
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

hits = nav.view(sel)
st.write(f"**{len(hits)} task(s)** match")

grid_df = hits.reset_index(drop=False)  # keep original row index

# Build grid options
gb = GridOptionsBuilder.from_dataframe(grid_df)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_grid_options(domLayout="normal")   # let grid resize responsively

grid_res = AgGrid(
    grid_df,
    gridOptions=gb.build(),
    height=300,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    key="task_grid",
)
st.download_button("Download CSV", hits.to_csv(index=False).encode(), "matching_tasks.csv", "text/csv")

# ----------------------------------------------------------------------
# Robust check for “did the user click a row?”
# ----------------------------------------------------------------------
selected = grid_res["selected_rows"]         # may be list OR DataFrame
if (isinstance(selected, list) and selected) or (
    isinstance(selected, pd.DataFrame) and not selected.empty
):
    # Normalise to a Python dict
    if isinstance(selected, list):
        row_dict = selected[0]
    else:  # DataFrame
        row_dict = selected.iloc[0].to_dict()

    st.markdown("---")
    st.subheader("Task details")

    # free-text task sentence
    st.write(f"**Description:** {row_dict['Task']}")

    # ladder for each semantic role
    for role in ["Verb", "Object", "Purpose", "Method"]:
        path_md = ladder(role.lower(), row_dict.get(role, ""), tax)
        st.markdown(f"**{role}:**\n{path_md}")
