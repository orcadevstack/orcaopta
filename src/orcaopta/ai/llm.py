import requests
import json
import logging
from typing import Optional, Dict, Any, Generator, Callable

logger = logging.getLogger("orcaopta.llm")


class OrcaLLM:
    """
    Unified LLM engine for Orcaopta.
    Supports:
    - Ollama generate
    - Streaming
    - Tool calling
    - Routing
    """

    def __init__(
        self,
        default_model: str = "qwen2.5",
        endpoint: str = "http://127.0.0.1:11434/api/generate",
        timeout: int = 60,
    ):
        self.default_model = default_model
        self.endpoint = endpoint
        self.timeout = timeout

    # ============================================================
    # BASIC CALL
    # ============================================================

    def run(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:

        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        try:
            res = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            data = res.json()
            return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"[LLM] Error: {e}")
            return f"[LLM Error: {e}]"

    # ============================================================
    # STREAMING
    # ============================================================

    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Generator[str, None, None]:

        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        try:
            with requests.post(self.endpoint, json=payload, timeout=self.timeout, stream=True) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line.decode())
                        token = data.get("response", "")
                        if token:
                            yield token
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"[LLM] Stream error: {e}")
            yield f"[LLM Stream Error: {e}]"

    # ============================================================
    # TOOL CALLING
    # ============================================================

    def run_with_tools(
        self,
        prompt: str,
        tools: Dict[str, Callable],
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:

        response = self.run(prompt, model=model, system=system)

        try:
            cmd = json.loads(response)
        except Exception:
            return {"error": "LLM did not return valid JSON", "raw": response}

        tool_name = cmd.get("tool")
        args = cmd.get("args", {})

        if tool_name not in tools:
            return {"error": f"Unknown tool '{tool_name}'", "raw": cmd}

        try:
            result = tools[tool_name](**args)
            return {"tool": tool_name, "result": result}
        except Exception as e:
            return {"error": f"Tool execution failed: {e}", "tool": tool_name}

    # ============================================================
    # ROUTING
    # ============================================================

    def route(
        self,
        task: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> str:

        task = task.lower()

        if "security" in task:
            model = "llama3-sec"
        elif "cloud" in task:
            model = "qwen2.5-cloud"
        elif "rl" in task:
            model = "orca-rl"
        else:
            model = self.default_model

        return self.run(prompt, model=model, system=system)


# ============================================================
# SIMPLE WRAPPERS (Optional)
# ============================================================

llm = OrcaLLM()

def generate(prompt: str, model: str = "qwen2.5"):
    return llm.run(prompt, model=model)

def stream(prompt: str, model: str = "qwen2.5"):
    return llm.stream(prompt, model=model)

def route(task: str, prompt: str):
    return llm.route(task, prompt)

