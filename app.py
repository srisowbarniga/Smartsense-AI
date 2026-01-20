import streamlit as st
import pandas as pd
import altair as alt
import json
import os

from iot_agent import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SmartSense AI – IoT Dashboard",
    layout="wide",
    page_icon="🤖"
)

# ---------------- TITLE ----------------
st.title("📡 SmartSense AI – Industrial IoT Monitoring")
st.caption("Autonomous Agent-driven sensor monitoring and safety auditing")

# ---------------- LOAD DATA ----------------
CSV_PATH = "data/processed/sensor_data_cleaned.csv"

if not os.path.exists(CSV_PATH):
    st.error("❌ Sensor data file not found. Please upload sensor_data_cleaned.csv")
    st.stop()

df = pd.read_csv(CSV_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---------------- KPI METRICS ----------------
st.subheader("📊 System Health Overview")

col1, col2, col3 = st.columns(3)

col1.metric("🌡 Avg Temperature", f"{df['temperature'].mean():.2f} °C")
col2.metric("💧 Avg Humidity", f"{df['humidity'].mean():.2f} %")
col3.metric("⚡ Avg Voltage", f"{df['voltage'].mean():.2f} V")

st.divider()

# ---------------- MAIN LAYOUT ----------------
left_col, right_col = st.columns([2, 1])

# --------- LEFT : CHARTS ----------
with left_col:
    st.subheader("📈 Sensor Trends")

    temp_chart = alt.Chart(df).mark_line(color="red").encode(
        x="timestamp:T",
        y="temperature:Q",
        tooltip=["timestamp", "temperature"]
    ).properties(height=250)

    st.altair_chart(temp_chart, use_container_width=True)

    voltage_chart = alt.Chart(df).mark_line(color="orange").encode(
        x="timestamp:T",
        y="voltage:Q",
        tooltip=["timestamp", "voltage"]
    ).properties(height=250)

    st.altair_chart(voltage_chart, use_container_width=True)

# --------- RIGHT : AI AGENT ----------
with right_col:
    st.subheader("🤖 AI Safety Agent")
    st.write("Click below to run an autonomous safety audit on the sensor data.")

    if st.button("🚀 Run AI Safety Audit"):
        with st.spinner("🧠 Agent analyzing sensor data..."):
            report_data = run_agent()
        st.success("✅ Audit completed successfully")

    REPORT_PATH = "output/report.json"

    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            report = json.load(f)

        status = report.get("status", "UNKNOWN")

        color_map = {
            "CRITICAL": "red",
            "WARNING": "orange",
            "NORMAL": "green"
        }

        st.markdown(
            f"### Status: <span style='color:{color_map.get(status, 'gray')}'>{status}</span>",
            unsafe_allow_html=True
        )

        st.markdown("**📄 Summary**")
        st.write(report.get("summary", "N/A"))

        st.markdown("**📌 Insights**")
        st.info(report.get("insights", "N/A"))

        st.markdown("**🛠 Recommendation**")
        st.success(report.get("recommendation", "N/A"))

    else:
        st.info("ℹ️ No report available. Click 'Run AI Safety Audit' to generate one.")

# ---------------- FOOTER ----------------
st.divider()
st.caption(f"🔄 Last data update: {df['timestamp'].max()}")
