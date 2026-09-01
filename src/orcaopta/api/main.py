import logging
import subprocess
import pandas as pd

from fastapi import FastAPI, Request, UploadFile, File, Form, Response, APIRouter
from pydantic import BaseModel

from orcaopta.bootstrap.handshake import handshake
from orcaopta.bootstrap.wizard import wizard
from orcaopta.ai.llm import llm
from orcaopta.security.attack_mapping import analyze_cloud_graph
from orcaopta.tracking.client import OrcaoptaTracker
from orcaopta.tracing.setup import setup_tracing
from orcaopta.core.mode import detect_mode
from orcaopta.core.config import load_config
from orcaopta.core.events import get_events
from orcaopta.cloud.detect.graph import build_cloud_graph
from orcaopta.security.encryption import encrypt, decrypt
from orcaopta.api.routes import system
from orcaopta.cloud.detect.detect import detect_all
from orcaopta.cloud.detect.autofix import auto_fix_configs

from orcaopta.supervisor.supervisor import start_supervisor, get_supervisor

# Optional RL autoscale
try:
    from orcaopta.rl.training.train_autoscale import train_autoscale_rl
except Exception:
    def train_autoscale_rl(*args, **kwargs):
        return {"status": "rl_autoscale_unavailable"}

# Optional PPO agent
try:
    from orcaopta.rl.agents.ppo_agent import PPOAgent
except Exception:
    PPOAgent = None

# AI explanation modules
from orcaopta.ai.agent import (
    ai_self_heal_plan,
    ai_explain_anomaly,
    ai_explain_forecast,
    ai_explain_autoscale,
)

# ML stack
from orcaopta.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)

from orcaopta.ml.model_utils import (
    deploy_versioned_model,
    load_versioned_model,
)

logger = logging.getLogger("orcaopta")

# Globals
config = None
model = None
tracer = None
tracker = OrcaoptaTracker()

# ============================================================
# OpenAPI Tags
# ============================================================

tags_metadata = [
    {"name": "Core ML", "description": "Prediction, anomaly detection, forecasting, autoscale ML."},
    {"name": "Model Lifecycle", "description": "Deploy, reload, and manage versioned ML models."},
    {"name": "Secrets", "description": "Encrypted secret storage and retrieval."},
    {"name": "AI Explanations", "description": "AI-driven anomaly, forecast, autoscale explanations."},
    {"name": "Self-Healing", "description": "Cloud graph analysis and automated healing plans."},
    {"name": "Dashboard", "description": "Cloud graph, detection, and healing event dashboards."},
    {"name": "Supervisor", "description": "Autoscale supervisor health and Prometheus metrics."},
]

app = FastAPI(
    title="Orcaopta ML API",
    version="1.0.0",
    openapi_tags=tags_metadata
)

# Versioned API router
v1 = APIRouter(prefix="/v1")

# Attach system routes
v1.include_router(system.router)


class Payload(BaseModel):
    records: list[dict]


def load_model():
    global model
    logger.info("Loading Orcaopta core model...")
    model = model_utils.load_core_model()
    logger.info("Core model loaded successfully")


# ============================================================
# Auth Middleware (API Key)
# ============================================================

API_KEY = "CHANGE_ME"

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = {
        "/health",
        "/metrics/supervisor",
        "/metrics/supervisor/prometheus",
        "/docs",
        "/openapi.json",
    }

    if request.url.path in public_paths:
        return await call_next(request)

    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return Response(
            content='{"error": "Unauthorized"}',
            status_code=401,
            media_type="application/json"
        )

    return await call_next(request)


# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
async def startup_event():
    global config, tracer

    logger.info("Starting ORCAOPTA API...")

    config = load_config()
    tracer = setup_tracing()

    try:
        load_model()
    except Exception as e:
        logger.error(f"Model load failed: {e}")

    try:
        audit_results = subprocess.check_output(["ossaudit", "scan", "."]).decode()
        ai_self_heal_plan([{"audit": audit_results}])
    except Exception as e:
        logger.warning(f"Security audit failed: {e}")

    tracker.log_event("startup", "system", {"mode": detect_mode()})

    handshake()
    wizard()

    start_supervisor(interval=10)


# ============================================================
# Core ML Routes
# ============================================================

@v1.get("/predict", tags=["Core ML"])
def predict(x: float):
    tracker.log_event("predict", "api", {"input": x})
    y = model.predict([[x]])[0]
    return {"input": x, "output": float(y)}


def to_df(payload: Payload):
    return pd.DataFrame(payload.records)


@v1.post("/anomaly", tags=["Core ML"])
def anomaly(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_anomaly()
    preds = anomaly_detection.predict_anomaly(m, df)
    return {"predictions": preds.tolist()}


@v1.post("/forecast", tags=["Core ML"])
def forecast(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_forecast()
    preds = forecasting.predict_future(m, df)
    return {"predictions": preds.tolist()}


@v1.post("/resource-opt", tags=["Core ML"])
def resource_opt(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_resource_opt()
    preds = resource_optimization.optimize_resources(m, df)
    return {"predictions": preds.tolist()}


@v1.post("/autoscale", tags=["Core ML"])
def autoscale_route(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_autoscale()
    preds = autoscaling.autoscale_decision(m, df)
    return {"decisions": preds.tolist()}


# ============================================================
# Model Lifecycle
# ============================================================

@v1.post("/model/deploy", tags=["Model Lifecycle"])
async def deploy_model(
    family: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
):
    allowed = {"anomaly", "forecast", "resource", "autoscale"}
    if family not in allowed:
        return {"error": f"Invalid family '{family}'"}

    model_bytes = await file.read()
    path = deploy_versioned_model(model_bytes, family, version)

    try:
        load_versioned_model({version: path}, version)
    except Exception as e:
        return {"error": f"Model deployed but reload failed: {e}"}

    return {"status": "success", "family": family, "version": version}


# ============================================================
# Secrets
# ============================================================

@v1.post("/store-secret", tags=["Secrets"])
def store_secret(payload: dict):
    encrypted = encrypt(payload["value"].encode())
    return {"token": encrypted.decode()}


@v1.post("/read-secret", tags=["Secrets"])
def read_secret(payload: dict):
    decrypted = decrypt(payload["token"].encode())
    return {"value": decrypted.decode()}


# ============================================================
# AI Explanations
# ============================================================

@v1.post("/ai/anomaly-explain", tags=["AI Explanations"])
def ai_anomaly_explain(payload: Payload):
    return {"explanation": ai_explain_anomaly(payload.records)}


@v1.post("/ai/forecast-explain", tags=["AI Explanations"])
def ai_forecast_explain(payload: Payload):
    return {"explanation": ai_explain_forecast(payload.records)}


@v1.post("/ai/autoscale-explain", tags=["AI Explanations"])
def ai_autoscale_explain(payload: Payload):
    return {"explanation": ai_explain_autoscale(payload.records)}


# ============================================================
# Self-Healing
# ============================================================

@v1.post("/ai/self-heal-plan", tags=["Self-Healing"])
def ai_self_heal(payload: Payload):
    return {"self_heal_plan": ai_self_heal_plan(payload.records)}


@v1.get("/ai/global-self-heal", tags=["Self-Healing"])
def ai_global_self_heal():
    graph = build_cloud_graph()
    findings = analyze_cloud_graph(graph)
    plan = ai_self_heal_plan([{"cloud_graph": graph}, {"security_findings": findings}])
    return {"global_self_heal_plan": plan, "security_findings": findings}


# ============================================================
# Dashboard
# ============================================================

@v1.get("/dashboard/cloud-graph", tags=["Dashboard"])
def dashboard_cloud_graph():
    return {"graph": build_cloud_graph()}


@v1.get("/dashboard/healing-events", tags=["Dashboard"])
def dashboard_healing_events():
    return {"events": get_events()}


@v1.get("/dashboard/cloud-detection", tags=["Dashboard"])
def dashboard_cloud_detection():
    detection = detect_all()
    detection = auto_fix_configs(detection)
    return {"cloud_detection": detection}


# ============================================================
# Supervisor Metrics
# ============================================================

@v1.get("/health/supervisor", tags=["Supervisor"])
def supervisor_health():
    sup = get_supervisor()
    return sup.get_health() if sup else {"status": "not_running"}


@v1.get("/metrics/supervisor", tags=["Supervisor"])
def supervisor_metrics_json():
    sup = get_supervisor()
    return sup.get_metrics() if sup else {}


@v1.get("/metrics/supervisor/prometheus", tags=["Supervisor"])
def supervisor_metrics_prometheus():
    sup = get_supervisor()
    if not sup:
        return Response("# orcaopta supervisor not running\n", media_type="text/plain")
    return Response(sup.get_metrics_prometheus(), media_type="text/plain")


@v1.post("/ai/anomaly-explain-llm", tags=["AI Explanations"])
def ai_anomaly_explain_llm(payload: Payload):
    prompt = f"Explain these anomaly detection results:\n{payload.records}"
    explanation = llm.run(prompt)
    return {"explanation": explanation}

@v1.post("/ai/forecast-explain-llm", tags=["AI Explanations"])
def ai_forecast_explain_llm(payload: Payload):
    prompt = f"Explain this forecast output:\n{payload.records}"
    explanation = llm.run(prompt)
    return {"explanation": explanation}

@v1.post("/ai/autoscale-explain-llm", tags=["AI Explanations"])
def ai_autoscale_explain_llm(payload: Payload):
    prompt = f"Explain this autoscale decision context:\n{payload.records}"
    explanation = llm.run(prompt)
    return {"explanation": explanation}

@v1.get("/ai/cloud-explain-llm", tags=["AI Explanations"])
def ai_cloud_explain_llm():
    graph = build_cloud_graph()
    prompt = f"Analyze this cloud graph and describe risks:\n{graph}"
    explanation = llm.run(prompt)
    return {"cloud_graph": graph, "explanation": explanation}

@v1.post("/ai/self-heal-plan-llm", tags=["AI Explanations"])
def ai_self_heal_llm(payload: Payload):
    plan = ai_self_heal_plan(payload.records)
    prompt = f"Explain this self-healing plan:\n{plan}"
    explanation = llm.run(prompt)
    return {"self_heal_plan": plan, "explanation": explanation}

@v1.post("/ai/llm-stream", tags=["AI Explanations"])
def ai_llm_stream(payload: dict):
    prompt = payload.get("prompt", "")
    output = ""
    for token in llm.stream(prompt):
        output += token
    return {"response": output}

@v1.post("/ai/llm-route", tags=["AI Explanations"])
def ai_llm_route(payload: dict):
    task = payload.get("task", "general")
    prompt = payload.get("prompt", "")
    response = llm.route(task, prompt)
    return {"task": task, "response": response}


# Attach versioned router
app.include_router(v1)
