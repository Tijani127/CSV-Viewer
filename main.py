import streamlit as st
import pandas as pd

st.title("CSV viewer")
st.write("""
  Look at your CSV!
""")

data = st.file_uploader("Upload your CSV", type="csv")

if data is not None:
  processed = pd.read_csv(data)
  code = st.code(processed)