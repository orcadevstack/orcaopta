import json
import pandas as pd
from orcaopta.ai.llm import OrcaLLM
from orcaopta.ml import (
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
    model_utils,
)

llm = OrcaLLM(default_model="qwen2.5")


def analyze_anomalies(records):
    m = model_utils.load_anomaly()
    df = pd.DataFrame(records)
    preds = anomaly_detection.predict_anomaly(m, df)
    return {"records": records, "predictions": preds.tolist()}

def analyze_forecast(records):
    m = model_utils.load_forecast()
    df = pd.DataFrame(records)
    preds = forecasting.predict_future(m, df)
    return {"records": records, "predictions": preds.tolist()}

def analyze_resource_opt(records):
    m = model_utils.load_resource_opt()
    df = pd.DataFrame(records)
    preds = resource_optimization.optimize_resources(m, df)
    return {"records": records, "predictions": preds.tolist()}

def analyze_autoscale(records):
    m = model_utils.load_autoscale()
    df = pd.DataFrame(records)
    preds = autoscaling.autoscale_decision(m, df)
    return {"records": records, "decisions": preds.tolist()}

TOOLS = {
    "analyze_anomalies": analyze_anomalies,
    "analyze_forecast": analyze_forecast,
    "analyze_resource_opt": analyze_resource_opt,
    "analyze_autoscale": analyze_autoscale,
}


def run_agent(prompt: str, records: list[dict], tool_name: str):
    tool = TOOLS[tool_name]
    tool_output = tool(records)

    final_prompt = (
        f"{prompt}\n\n"
        f"Here is the structured data from the ML tool:\n"
        f"{json.dumps(tool_output, indent=2)}\n\n"
        f"Now produce your final explanation."
    )

    return llm.run(final_prompt)


def ai_explain_anomaly(records):
    prompt = (
        "You are the AI brain of Orcaopta. "
        "Explain detected anomalies, root causes, and remediation actions."
    )
    return run_agent(prompt, records, "analyze_anomalies")

def ai_explain_forecast(records):
    prompt = (
        "You are the AI brain of Orcaopta. "
        "Explain future risks, load predictions, and preparation strategy."
    )
    return run_agent(prompt, records, "analyze_forecast")

def ai_explain_autoscale(records):
    prompt = (
        "You are the AI brain of Orcaopta. "
        "Explain autoscaling decisions and improvements."
    )
    return run_agent(prompt, records, "analyze_autoscale")

def ai_self_heal_plan(records):
    prompt = (
        "You are the AI brain of Orcaopta. "
        "Generate a unified self-healing plan using anomalies, forecasts, "
        "resource optimization, and autoscaling."
    )
    return run_agent(prompt, records, "analyze_anomalies")
