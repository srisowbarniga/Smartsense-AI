import pandas as pd
import json
import os

CSV_FILE = "data/processed/sensor_data_cleaned.csv"

def analyze_sensor_data():
    if not os.path.exists(CSV_FILE):
        return {"error": "Sensor data file not found"}

    df = pd.read_csv(CSV_FILE)

    avg_temp = df["temperature"].mean()
    max_temp = df["temperature"].max()

    if max_temp > 75:
        status = "CRITICAL"
    elif max_temp > 60:
        status = "WARNING"
    else:
        status = "NORMAL"

    return {
        "status": status,
        "avg_temp": round(avg_temp, 2),
        "max_temp": round(max_temp, 2)
    }

def run_agent():
    analysis = analyze_sensor_data()

    if "error" in analysis:
        return analysis

    report = {
        "status": analysis["status"],
        "summary": f"Average temperature is {analysis['avg_temp']}°C.",
        "insights": f"Maximum temperature reached {analysis['max_temp']}°C.",
        "recommendation": (
            "Immediate maintenance required."
            if analysis["status"] == "CRITICAL"
            else "Monitor system regularly."
        )
    }

    os.makedirs("output", exist_ok=True)

    with open("output/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report
