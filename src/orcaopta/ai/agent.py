from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, Tool
import json

# Use your existing ML functions as tools
from src.ml import (
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
    model_utils,
)

# -----------------------------
# Tools wrapping your ML logic
# -----------------------------

def analyze_anomalies(records: list[dict]):
    m = model_utils.load_anomaly()
    import pandas as pd
    df = pd.DataFrame(records)
    preds = anomaly_detection.predict_anomaly(m, df)
    return json.dumps({"records": records, "predictions": preds.tolist()}, indent=2)


def analyze_forecast(records: list[dict]):
    m = model_utils.load_forecast()
    import pandas as pd
    df = pd.DataFrame(records)
    preds = forecasting.predict_future(m, df)
    return json.dumps({"records": records, "predictions": preds.tolist()}, indent=2)


def analyze_resource_opt(records: list[dict]):
    m = model_utils.load_resource_opt()
    import pandas as pd
    df = pd.DataFrame(records)
    preds = resource_optimization.optimize_resources(m, df)
    return json.dumps({"records": records, "predictions": preds.tolist()}, indent=2)


def analyze_autoscale(records: list[dict]):
    m = model_utils.load_autoscale()
    import pandas as pd
    df = pd.DataFrame(records)
    preds = autoscaling.autoscale_decision(m, df)
    return json.dumps({"records": records, "decisions": preds.tolist()}, indent=2)


# -----------------------------
# LLM (Ollama)
# -----------------------------

llm = OllamaLLM(model="qwen2.5")

tools = [
    Tool(
        name="analyze_anomalies",
        func=analyze_anomalies,
        description="Run anomaly detection on records and return predictions + context."
    ),
    Tool(
        name="analyze_forecast",
        func=analyze_forecast,
        description="Run forecasting on records and return future predictions."
    ),
    Tool(
        name="analyze_resource_opt",
        func=analyze_resource_opt,
        description="Run resource optimization and return recommended allocations."
    ),
    Tool(
        name="analyze_autoscale",
        func=analyze_autoscale,
        description="Run autoscaling decision logic and return decisions."
    ),
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)


# -----------------------------
# Public functions for FastAPI
# -----------------------------

def ai_explain_anomaly(records: list[dict]):
    prompt = (
        "You are the AI brain of a self-healing cloud platform called Orcaopta. "
        "Use the anomaly analysis tool to understand the records and explain: "
        "1) What anomalies exist, "
        "2) Why they might be happening, "
        "3) What remediation actions Orcaopta should take."
    )
    return agent.run({"input": records, "prompt": prompt})


def ai_explain_forecast(records: list[dict]):
    prompt = (
        "You are the AI brain of Orcaopta. Use the forecasting tool to analyze "
        "future trends and explain how the platform should prepare (scaling, "
        "resource allocation, risk mitigation)."
    )
    return agent.run({"input": records, "prompt": prompt})


def ai_explain_autoscale(records: list[dict]):
    prompt = (
        "You are the AI brain of Orcaopta. Use the autoscaling analysis tool to "
        "explain whether the current autoscaling decisions are correct, and how "
        "to improve them for a self-healing, resilient system."
    )
    return agent.run({"input": records, "prompt": prompt})

def ai_self_heal_plan(records: list[dict]):
    """
    Combine anomaly detection, forecasting, autoscaling, and resource optimization
    into a unified self-healing plan for Orcaopta.
    """
    prompt = (
        "You are the AI brain of Orcaopta, a self-healing cloud platform. "
        "Analyze the provided records using all available tools: anomaly detection, "
        "forecasting, autoscaling decisions, and resource optimization. "
        "Produce a unified self-healing plan that includes:\n"
        "1. Current cluster health summary\n"
        "2. Detected anomalies and root causes\n"
        "3. Forecasted risks or upcoming load issues\n"
        "4. Resource optimization recommendations\n"
        "5. Autoscaling corrections or improvements\n"
        "6. Concrete healing actions (restart pods, scale workloads, adjust resources)\n"
        "7. Priority order of actions\n"
        "8. Final stability assessment\n\n"
        "Return the plan in clear structured sections."
    )

    return agent.run({"input": records, "prompt": prompt})
