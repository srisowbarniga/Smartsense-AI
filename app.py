import streamlit as st
import pandas as pd
import altair as alt
import json
import os
import subprocess
import sys

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
csv_path = "data/processed/sensor_data_cleaned.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
else:
    st.error(f"Data file not found at {csv_path}")
    st.stop()

# ---------------- KPI METRICS ----------------
st.subheader("📊 System Health Overview")
col1, col2, col3 = st.columns(3)
col1.metric("🌡 Avg Temperature", f"{df['temperature'].mean():.2f}°C")
col2.metric("💧 Avg Humidity", f"{df['humidity'].mean():.2f}%")
col3.metric("⚡ Avg Voltage", f"{df['voltage'].mean():.2f}V")

st.divider()

# ---------------- MAIN LAYOUT ----------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📈 Sensor Trends")
    
    # Temperature Chart
    temp_chart = alt.Chart(df).mark_line(color='red').encode(
        x='timestamp:T',
        y='temperature:Q',
        tooltip=['timestamp', 'temperature']
    ).properties(height=200)
    st.altair_chart(temp_chart, use_container_width=True)

    # Voltage Chart
    volt_chart = alt.Chart(df).mark_line(color='orange').encode(
        x='timestamp:T',
        y='voltage:Q',
        tooltip=['timestamp', 'voltage']
    ).properties(height=200)
    st.altair_chart(volt_chart, use_container_width=True)

with right_col:
    st.subheader("🤖 AI Safety Agent")
    st.write("Trigger the autonomous reasoning loop to audit machine safety.")

    if st.button("🚀 Run AI Safety Audit"):
        with st.spinner("🧠 Agent reasoning..."):
            # Run your agent script
            subprocess.run([sys.executable, "iot_agent.py"])
        st.success("🔧 Audit Complete!")

    # ---------------- DISPLAY AGENT REPORT ----------------
    report_path = "output/report.json"  # Use JSON for safety
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            try:
                report_data = json.load(f)

                # Dynamic Styling based on Status
                status_color = {
                    "CRITICAL": "red",
                    "WARNING": "orange",
                    "NORMAL": "green"
                }.get(report_data.get("status"), "gray")

                st.markdown(f"### Status: <span style='color:{status_color}'>{report_data.get('status')}</span>", unsafe_allow_html=True)
                
                with st.container():
                    st.markdown("**Summary**")
                    st.write(report_data.get("summary"))
                    
                    st.markdown("**Insights**")
                    st.info(report_data.get("insights"))
                    
                    st.markdown("**Recommendation**")
                    st.success(report_data.get("recommendation"))
            except json.JSONDecodeError:
                st.warning("Agent report found, but format is invalid. Run audit again.")
    else:
        st.info("No report generated. Click 'Run AI Safety Audit' to start.")

# ---------------- FOOTER ----------------
st.divider()
st.caption(f"🔄 Last data sync: {df['timestamp'].max()}")
