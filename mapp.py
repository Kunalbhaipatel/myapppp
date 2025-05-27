
import pandas as pd
import streamlit as st
import plotly.express as px
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Rig Comparison Dashboard", page_icon="📊")

# ---------- Branding Header ----------
LOGO_PATH = "prodigy_logo.png"
DATA_PATH = "sample_rig_dashboard_data.csv"

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

# ---------- METRICS ----------
st.markdown("### 📈 Key Performance Metrics")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Avg Total Dilution", f"{filtered['Total_Dil'].mean():,.2f} BBLs")
with m2:
    st.metric("Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
with m3:
    st.metric("Avg DSRE", f"{filtered['DSRE'].mean()*100:.1f}%")

# ---------- TABS ----------
tabs = st.tabs(["🧾 Well Overview", "📋 Summary & Charts", "📊 Statistical Insights", "📈 Advanced Analytics", "🧮 Multi-Well Comparison"])

# ---------- TAB 1 ----------
with tabs[0]:
    st.markdown("### 🧾 Well Overview")
    numeric_cols = [
        "DSRE", "SCE_Loss_Ratio", "Total_SCE", "Total_Dil", "ROP", "Temp", "DOW", "AMW",
        "Drilling_Hours", "Haul_OFF", "Base_Oil", "Water", "Weight_Material",
        "Chemicals", "Dilution_Ratio", "Solids_Generated"
    ]
    available_cols = [col for col in numeric_cols if col in filtered.columns]
    melted_df = filtered[["Well_Name"] + available_cols].melt(id_vars="Well_Name", var_name="Metric", value_name="Value")
    if not melted_df.empty:
        fig = px.bar(melted_df, x="Well_Name", y="Value", color="Metric", barmode="group", title="Well Name vs Key Metrics", height=600)
        st.plotly_chart(fig, use_container_width=True)

# ---------- TAB 2 ----------
with tabs[1]:
    st.markdown("### 📋 Summary & Charts")
    subset = filtered.dropna(subset=["Well_Name"])
    if "Depth" in subset.columns and "DOW" in subset.columns:
        fig1 = px.bar(subset, x="Well_Name", y=["Depth", "DOW"], barmode='group')
        st.plotly_chart(fig1, use_container_width=True)
    if "Base_Oil" in subset.columns and "Water" in subset.columns:
        fig2 = px.bar(subset, x="Well_Name", y=["Base_Oil", "Water", "Weight_Material", "Chemicals"], barmode="stack")
        st.plotly_chart(fig2, use_container_width=True)

# ---------- TAB 3 ----------
with tabs[2]:
    st.markdown("### 📊 Statistical Insights")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Mean DSRE", f"{filtered['DSRE'].mean()*100:.2f}%")
    k2.metric("Max Haul Off", f"{filtered['Haul_OFF'].max():,.0f}")
    k3.metric("Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
    k4.metric("Avg Dilution", f"{filtered['Total_Dil'].mean():,.2f}")
    if 'DSRE' in filtered.columns:
        high_eff = filtered[filtered['DSRE'] > 0.9]
        low_eff = filtered[filtered['DSRE'] < 0.6]
        st.markdown(f"✅ **High Efficiency Wells (DSRE > 90%)**: {len(high_eff)}")
        st.markdown(f"⚠️ **Low Efficiency Wells (DSRE < 60%)**: {len(low_eff)}")

# ---------- TAB 4 ----------
with tabs[3]:
    st.markdown("### 📈 Advanced Analytics")
    if "ROP" in filtered.columns and "Temp" in filtered.columns:
        fig3 = px.scatter(filtered, x="ROP", y="Temp", color="Well_Name", title="ROP vs Temperature")
        st.plotly_chart(fig3, use_container_width=True)
    if "Base_Oil" in filtered.columns and "Water" in filtered.columns:
        fig4 = px.scatter(filtered, x="Base_Oil", y="Water", size="Total_Dil", color="Well_Name", title="Base Oil vs Water")
        st.plotly_chart(fig4, use_container_width=True)
    try:
        corr_cols = ["DSRE", "Total_SCE", "Total_Dil", "SCE_Loss_Ratio", "Dilution_Ratio", "ROP", "AMW", "Haul_OFF"]
        corr_data = filtered[corr_cols].dropna()
        corr_matrix = corr_data.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='Blues')
        st.plotly_chart(fig_corr, use_container_width=True)
    except Exception as e:
        st.error(f"Correlation error: {e}")

# ---------- TAB 5 ----------
with tabs[4]:
    st.markdown("### 🧮 Derrick vs Non-Derrick Comparison")
    if "flowline_Shakers" in filtered.columns:
        filtered["Shaker_Type"] = filtered["flowline_Shakers"].apply(
            lambda x: "Derrick" if isinstance(x, str) and "derrick" in x.lower() else "Non-Derrick"
        )
        selected_metrics = st.multiselect("Select Metrics", ["DSRE", "ROP", "Total_Dil"], default=["DSRE", "ROP"])
        if selected_metrics:
            melted_df = filtered[["Well_Name", "Shaker_Type"] + selected_metrics].melt(
                id_vars=["Well_Name", "Shaker_Type"], var_name="Metric", value_name="Value"
            )
            fig = px.bar(melted_df, x="Well_Name", y="Value", color="Shaker_Type", facet_col="Metric",
                         color_discrete_map={"Derrick": "#007635", "Non-Derrick": "lightgrey"})
            st.plotly_chart(fig, use_container_width=True)

# ---------- Footer ----------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(LOGO_PATH, width=100)
    st.caption("© 2025 Prodigy IQ")
