import pandas as pd
import requests
import json
import os

# ===============================
# CONFIG
# ===============================
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:latest" 

CSV_FILE = "data/processed/sensor data cleaned.csv"

# ===============================
# TOOLS (THE AGENT'S HANDS)
# ===============================

def analyze_sensor_data():
    """Reads IoT CSV and returns statistics and risk level."""
    if not os.path.exists(CSV_FILE):
        return {"error": f"File not found at {CSV_FILE}"}
    try:
        df = pd.read_csv(CSV_FILE)
        avg_temp = df["temperature"].mean()
        max_temp = df["temperature"].max()
        # Logic: Risk is HIGH if max temp exceeds 75
        risk = "HIGH" if max_temp > 75 else "NORMAL"
        return {
            "avg_temp": round(avg_temp, 2),
            "max_temp": round(max_temp, 2),
            "risk_level": risk
        }
    except Exception as e:
        return {"error": str(e)}

def check_maintenance_logs():
    """Returns maintenance status."""
    return {
        "last_maintenance_days": 45,
        "recommended_interval": 30,
        "status": "OVERDUE"
    }

TOOLS = {
    "analyze_sensor_data": analyze_sensor_data,
    "check_maintenance_logs": check_maintenance_logs
}

# ===============================
# AGENT LOOP (THE BRAIN)
# ===============================

def run_agent(user_query):
    # The message history acts as the Agent's Short-Term Memory
    messages = [
        {
            "role": "system",
            "content": """You are an IoT Safety Agent. 
            Follow this EXACT sequence:
            1. Call 'analyze_sensor_data'.
            2. Call 'check_maintenance_logs'.
            3. Provide a final summary report based on those results.

            To use a tool, respond ONLY with: {"tool": "tool_name"}
            To finish, respond ONLY with this JSON structure: 
            {"status": "CRITICAL/WARNING/NORMAL", "summary": "...", "insights": "...", "recommendation": "..."}

            Do NOT repeat tools. Output MUST be valid JSON."""
        },
        {"role": "user", "content": user_query}
    ]

    print(f"🚀 Starting Agent Task: {user_query}")

    # The loop allows the agent to think and act multiple times
    for step in range(1, 6):
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "format": "json" # Forces Llama to speak in JSON
            }
        )

        ai_message = response.json()["message"]
        messages.append(ai_message) # Agent remembers its own thought

        try:
            decision = json.loads(ai_message["content"])
        except json.JSONDecodeError:
            print(f"⚠️ Step {step}: AI output was not valid JSON. Retrying...")
            continue

        # ACTION: Agent decides to use a tool
        if "tool" in decision:
            tool_name = decision["tool"]
            print(f"🔧 [Step {step}] Executing: {tool_name}")

            if tool_name in TOOLS:
                observation = TOOLS[tool_name]()
                # Feedback: Give the result back to the AI
                messages.append({
                    "role": "user",
                    "content": f"Observation from {tool_name}: {json.dumps(observation)}"
                })
            else:
                messages.append({"role": "user", "content": f"Error: {tool_name} not found."})

        # FINAL: Agent decides it has enough info to finish
        elif "status" in decision:
            print("\n📊 FINAL AGENT REPORT:\n")
            report = json.dumps(decision, indent=4)
            print(report)

            # Save the report to a file
            os.makedirs("output", exist_ok=True)
            with open("output/report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            
            print("\n✅ Report successfully saved to output/report.txt")
            return

    print("❌ Failure: Agent timed out without finishing.")

# ===============================
# EXECUTION
# ===============================
if __name__ == "__main__":
    run_agent("Evaluate machine safety. Analyze sensor trends and check maintenance status.")