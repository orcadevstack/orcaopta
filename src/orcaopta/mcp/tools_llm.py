import logging
from orcaopta.ai.llm import llm

logger = logging.getLogger("orcaopta.mcp.tools.llm")


# ============================================================
# BASIC LLM GENERATION
# ============================================================

def tool_llm_generate(prompt: str, model: str | None = None):
    """
    Basic LLM text generation.
    """
    try:
        logger.info(f"[LLMTool] generate: model={model or llm.default_model}")
        response = llm.run(prompt, model=model)
        return {"status": "ok", "response": response}
    except Exception as e:
        logger.error(f"[LLMTool] generate failed: {e}")
        return {"status": "error", "error": str(e)}


# ============================================================
# STREAMING LLM
# ============================================================

def tool_llm_stream(prompt: str, model: str | None = None):
    """
    Streaming LLM output (aggregated into a single string).
    """
    try:
        logger.info(f"[LLMTool] stream: model={model or llm.default_model}")
        output = ""
        for token in llm.stream(prompt, model=model):
            output += token
        return {"status": "ok", "response": output}
    except Exception as e:
        logger.error(f"[LLMTool] stream failed: {e}")
        return {"status": "error", "error": str(e)}


# ============================================================
# ROUTED LLM (TASK-AWARE)
# ============================================================

def tool_llm_route(task: str, prompt: str):
    """
    Route prompt to best model based on task type.
    """
    try:
        logger.info(f"[LLMTool] route: task={task}")
        response = llm.route(task, prompt)
        return {"status": "ok", "task": task, "response": response}
    except Exception as e:
        logger.error(f"[LLMTool] route failed: {e}")
        return {"status": "error", "task": task, "error": str(e)}


# ============================================================
# TOOL-CALLING LLM
# ============================================================

def tool_llm_tools(prompt: str, tools: dict):
    """
    LLM returns JSON:
    {
        "tool": "terraform_audit",
        "args": {}
    }
    Then we execute the tool.
    """
    try:
        logger.info("[LLMTool] tools: tool-calling request")
        result = llm.run_with_tools(prompt, tools)
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"[LLMTool] tools failed: {e}")
        return {"status": "error", "error": str(e)}


# ============================================================
# EXPLANATION HELPERS (OPTIONAL)
# ============================================================

def tool_llm_explain_autoscale(context: dict):
    """
    Explain autoscale decision context using LLM.
    """
    prompt = f"Explain this autoscale decision context:\n{context}"
    try:
        logger.info("[LLMTool] explain_autoscale")
        response = llm.run(prompt)
        return {"status": "ok", "explanation": response}
    except Exception as e:
        logger.error(f"[LLMTool] explain_autoscale failed: {e}")
        return {"status": "error", "error": str(e)}


def tool_llm_explain_anomaly(records: list):
    """
    Explain anomaly detection results using LLM.
    """
    prompt = f"Explain these anomaly detection results:\n{records}"
    try:
        logger.info("[LLMTool] explain_anomaly")
        response = llm.run(prompt)
        return {"status": "ok", "explanation": response}
    except Exception as e:
        logger.error(f"[LLMTool] explain_anomaly failed: {e}")
        return {"status": "error", "error": str(e)}
