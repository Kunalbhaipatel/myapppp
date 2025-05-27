
import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

from pathlib import Path

st.set_page_config(layout="wide", page_title="Rig Comparison Dashboard", page_icon="📊")

# Load logo image
LOGO_PATH = "prodigy_logo.png"
DATA_PATH = "sample_rig_dashboard_data.csv"

# ---------- Branding Header ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(LOGO_PATH, width=180)
    st.markdown("<h1 style='text-align: center; color: #004578;'>Rig Comparison Dashboard</h1>", unsafe_allow_html=True)

# ---------- Load Data ----------
try:
    data = pd.read_csv(DATA_PATH, quotechar='"', skipinitialspace=True, engine="python")
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# ---------- Filters ----------
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_operator = st.selectbox("Select Operator", ["All"] + sorted(data["Operator"].dropna().unique().tolist()))
    with col2:
        filtered_by_op = data if selected_operator == "All" else data[data["Operator"] == selected_operator]
        selected_contractor = st.selectbox("Select Contractor", ["All"] + sorted(filtered_by_op["Contractor"].dropna().unique().tolist()))
    with col3:
        filtered_by_contractor = filtered_by_op if selected_contractor == "All" else filtered_by_op[filtered_by_op["Contractor"] == selected_contractor]
        selected_shaker = st.selectbox("Select Shaker", ["All"] + sorted(filtered_by_contractor["flowline_Shakers"].dropna().unique().tolist()))
    with col4:
        filtered_by_shaker = filtered_by_contractor if selected_shaker == "All" else filtered_by_contractor[filtered_by_contractor["flowline_Shakers"] == selected_shaker]
        selected_hole = st.selectbox("Select Hole Size", ["All"] + sorted(filtered_by_shaker["Hole_Size"].dropna().unique().tolist()))
    filtered = filtered_by_shaker if selected_hole == "All" else filtered_by_shaker[filtered_by_shaker["Hole_Size"] == selected_hole]

# ---------- Metrics ----------
st.markdown("### 📈 Key Performance Metrics")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Avg Total Dilution", f"{filtered['Total_Dil'].mean():,.2f} BBLs")
with m2:
    st.metric("Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
with m3:
    st.metric("Avg DSRE", f"{filtered['DSRE'].mean()*100:.1f}%")

# ---------- Footer ----------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(LOGO_PATH, width=100)
    st.caption("© 2025 Prodigy IQ")
