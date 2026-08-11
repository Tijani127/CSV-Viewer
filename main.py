import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV data explorer", layout="wide")
st.title("CSV data explorer")
st.write("Look, Honey! A CSV!!")

data = st.file_uploader("Upload your CSV", type="csv")

if data is not None:
    @st.cache_data
    def load(file):
        return pd.read_csv(file)

    df = load(data)

    # --- Sidebar filters ---
    with st.sidebar:
        st.header("Filters")

        # Column selector
        all_cols = df.columns.tolist()
        visible_cols = st.multiselect("Columns to show", all_cols, default=all_cols)

        # Per-column value filters for low-cardinality columns
        filters = {}
        for col in visible_cols:
            if df[col].dtype == object and df[col].nunique() <= 20:
                options = sorted(df[col].dropna().unique().tolist())
                selected = st.multiselect(col, options, default=options)
                filters[col] = selected

        st.divider()
        st.caption(f"{len(df):,} rows · {len(df.columns)} columns")

    # Apply filters
    filtered = df[visible_cols].copy()
    for col, values in filters.items():
        if col in filtered.columns:
            filtered = filtered[filtered[col].isin(values)]

    # --- Summary metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{len(filtered):,}")
    col2.metric("Columns", len(filtered.columns))
    col3.metric("Missing values", f"{filtered.isna().sum().sum():,}")

    st.divider()

    # --- Tabs: Data / Stats / Chart ---
    tab_data, tab_stats, tab_chart = st.tabs([
        ":material/table: Data",
        ":material/bar_chart: Stats",
        ":material/show_chart: Chart",
    ])

    with tab_data:
        st.dataframe(filtered, hide_index=True)

    with tab_stats:
        numeric_cols = filtered.select_dtypes("number").columns.tolist()
        if numeric_cols:
            st.dataframe(
                filtered[numeric_cols].describe().T.round(2),
            )

            st.subheader("Null counts")
            null_counts = filtered.isna().sum().reset_index()
            null_counts.columns = ["Column", "Null count"]
            st.dataframe(null_counts, hide_index=True)
        else:
            st.info("No numeric columns found for statistics.")

    with tab_chart:
        numeric_cols = filtered.select_dtypes("number").columns.tolist()
        if len(numeric_cols) >= 1:
            with st.container(horizontal=True):
                x_col = st.selectbox("X axis", filtered.columns.tolist(), key="x")
                y_col = st.selectbox("Y axis", numeric_cols, key="y")
                chart_type = st.selectbox(
                    "Chart type",
                    ["Line", "Bar", "Scatter", "Area"],
                    key="chart_type",
                )

            chart_fns = {
                "Line": st.line_chart,
                "Bar": st.bar_chart,
                "Scatter": st.scatter_chart,
                "Area": st.area_chart,
            }
            chart_fns[chart_type](filtered, x=x_col, y=y_col)
        else:
            st.info("Need at least one numeric column to plot a chart.")
else:
    st.info("Upload a CSV file to get started.")
