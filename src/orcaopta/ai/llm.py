import requests
import logging
from typing import Optional, Dict, Any, Generator, Callable

logger = logging.getLogger("orcaopta.llm")


class OrcaLLM:
    def __init__(
        self,
        default_model: str = "qwen2.5",
        endpoint: str = "http://localhost:11434/api/generate",
        timeout: int = 30,
    ):
        self.default_model = default_model
        self.endpoint = endpoint
        self.timeout = timeout

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
            logger.error(f"LLM error: {e}")
            return f"[LLM Error: {e}]"


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
            logger.error(f"Streaming LLM error: {e}")
            yield f"[LLM Stream Error: {e}]"

    def run_with_tools(
        self,
        prompt: str,
        tools: Dict[str, Callable],
        model: Optional[str] = None,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:

        """
        LLM returns a JSON command like:
        {
            "tool": "terraform_audit",
            "args": {}
        }
        """

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

    def route(
        self,
        task: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> str:

        """
        Example routing:
        - security tasks → "llama3-sec"
        - cloud tasks → "qwen2.5-cloud"
        - RL tasks → "orca-rl"
        """

        if "security" in task.lower():
            model = "llama3-sec"
        elif "cloud" in task.lower():
            model = "qwen2.5-cloud"
        elif "rl" in task.lower():
            model = "orca-rl"
        else:
            model = self.default_model

        return self.run(prompt, model=model, system=system)
