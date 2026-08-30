import os
from pathlib import Path
import yaml



DEFAULT_MODE = "cluster"          # cluster | local | hybrid | edge
DEFAULT_CONFIG_PATH = "/app/configs/orcaopta.yaml"
DEFAULT_SECRETS_PATH = "/app/secrets/orcaopta-secrets.yaml"



def get_mode() -> str:
    """
    Determine MCP runtime mode.
    Priority:
        1. ORCAOPTA_MODE env
        2. Kubernetes detection
        3. Local dev fallback
    """
    env_mode = os.getenv("ORCAOPTA_MODE")
    if env_mode:
        return env_mode.lower()

    # Auto-detect Kubernetes
    if Path("/var/run/secrets/kubernetes.io").exists():
        return "cluster"

    # Auto-detect local dev
    if Path(".devcontainer").exists() or Path(".local").exists():
        return "local"

    return DEFAULT_MODE



def get_config_path() -> Path:
    """
    Resolve the path to orcaopta.yaml.
    Priority:
        1. ORCAOPTA_CONFIG env
        2. Default enterprise path
        3. Local fallback
    """
    env_path = os.getenv("ORCAOPTA_CONFIG")
    if env_path:
        return Path(env_path)

    default_path = Path(DEFAULT_CONFIG_PATH)
    if default_path.exists():
        return default_path

    # Local fallback for dev
    local_path = Path("orcaopta.yaml")
    if local_path.exists():
        return local_path

    raise FileNotFoundError(
        "No configuration file found. "
        "Set ORCAOPTA_CONFIG or place orcaopta.yaml in project root."
    )



def get_secrets_path() -> Path:
    """
    Resolve the path to secrets file.
    Priority:
        1. ORCAOPTA_SECRETS env
        2. Default enterprise secrets path
        3. Optional local fallback
    """
    env_path = os.getenv("ORCAOPTA_SECRETS")
    if env_path:
        return Path(env_path)

    default_path = Path(DEFAULT_SECRETS_PATH)
    if default_path.exists():
        return default_path

    # Optional local fallback
    local_path = Path("orcaopta-secrets.yaml")
    if local_path.exists():
        return local_path

    # Secrets are optional — return None
    return None



def load_mcp_config() -> dict:
    """
    Load MCP configuration from YAML.
    Includes:
        - MCP server settings
        - tool registry settings
        - cloud audit settings
        - ML/RL runtime settings
        - logging
        - security
    """
    path = get_config_path()

    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    return cfg.get("mcp", {})  # Only return MCP section



def load_mcp_secrets() -> dict:
    """
    Load MCP secrets (optional).
    """
    path = get_secrets_path()
    if not path:
        return {}

    with open(path, "r") as f:
        return yaml.safe_load(f)
