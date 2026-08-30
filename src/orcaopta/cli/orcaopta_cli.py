import json
import requests
import typer
import webbrowser

app = typer.Typer(help="Orcaopta Control Plane CLI")
spark_app = typer.Typer(help="Spark operations")
node_app = typer.Typer(help="Node operations")
autoscale_app = typer.Typer(help="Autoscale operations")
blockchain_app = typer.Typer(help="Blockchain operations")
supervisor_app = typer.Typer(help="Supervisor control")
cluster_app = typer.Typer(help="Cluster metrics")

app.add_typer(spark_app, name="spark")
app.add_typer(node_app, name="node")
app.add_typer(autoscale_app, name="autoscale")
app.add_typer(blockchain_app, name="blockchain")
app.add_typer(supervisor_app, name="supervisor")
app.add_typer(cluster_app, name="cluster")

DEFAULT_BASE_URL = "http://localhost:8000"


def _post_mcp(tool: str, arguments: dict | None = None, base_url: str = DEFAULT_BASE_URL):
    payload = {"tool": tool, "arguments": arguments or {}}
    resp = requests.post(f"{base_url}/v1/mcp", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# FULL HELP / COMMAND REFERENCE
# ============================================================

@app.command("help-all")
def help_all():
    """Show full CLI command reference."""
    typer.echo("""
============================================================
                ORCAOPTA CLI — COMMAND REFERENCE
============================================================

Core Commands:
  orcaopta info
  orcaopta health
  orcaopta tools
  orcaopta llm "<prompt>"
  orcaopta llm-stream "<prompt>"

------------------------------------------------------------
Spark Commands:
  orcaopta spark run <job>
  orcaopta spark pipeline <name>

------------------------------------------------------------
Node Commands:
  orcaopta node peers
  orcaopta node metrics

------------------------------------------------------------
Autoscale Commands:
  orcaopta autoscale status
  orcaopta autoscale simulate <minutes>

------------------------------------------------------------
Blockchain Commands:
  orcaopta blockchain log "<message>"
  orcaopta blockchain tail

------------------------------------------------------------
Supervisor Commands:
  orcaopta supervisor restart
  orcaopta supervisor status

------------------------------------------------------------
Cluster Commands:
  orcaopta cluster metrics

------------------------------------------------------------
Dashboard:
  orcaopta dashboard

------------------------------------------------------------
Autocomplete:
  orcaopta --install-completion bash
  orcaopta --install-completion zsh
  orcaopta --install-completion fish
  orcaopta --install-completion powershell

============================================================
""")


# ============================================================
# Core Commands
# ============================================================

@app.command()
def info(base_url: str = DEFAULT_BASE_URL):
    resp = requests.get(f"{base_url}/v1/info", timeout=10)
    typer.echo(json.dumps(resp.json(), indent=2))


@app.command()
def health(base_url: str = DEFAULT_BASE_URL):
    resp = requests.get(f"{base_url}/v1/health", timeout=10)
    typer.echo(json.dumps(resp.json(), indent=2))


@app.command()
def tools(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("list_tools", base_url=base_url)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def llm(prompt: str, model: str = None, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("llm", {"prompt": prompt, "model": model}, base_url=base_url)
    typer.echo(result["result"]["response"])


@app.command()
def llm_stream(prompt: str, model: str = None, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("llm_stream", {"prompt": prompt, "model": model}, base_url=base_url)
    typer.echo(result["result"]["response"])


# ============================================================
# Spark Commands
# ============================================================

@spark_app.command("run")
def spark_run(job: str, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("spark_run_job", {"job_name": job}, base_url)
    typer.echo(json.dumps(result, indent=2))


@spark_app.command("pipeline")
def spark_pipeline(name: str, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("spark_run_pipeline", {"pipeline_name": name}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Node Commands
# ============================================================

@node_app.command("peers")
def node_peers(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("node_list_peers", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


@node_app.command("metrics")
def node_metrics(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("node_metrics", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Autoscale Commands
# ============================================================

@autoscale_app.command("status")
def autoscale_status(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("ml_signals", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


@autoscale_app.command("simulate")
def autoscale_simulate(minutes: int, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("autoscale_simulate", {"minutes": minutes}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Blockchain Commands
# ============================================================

@blockchain_app.command("log")
def blockchain_log(message: str, base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("blockchain_log", {"message": message}, base_url)
    typer.echo(json.dumps(result, indent=2))


@blockchain_app.command("tail")
def blockchain_tail(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("blockchain_tail", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Supervisor Commands
# ============================================================

@supervisor_app.command("restart")
def supervisor_restart(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("supervisor_restart", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


@supervisor_app.command("status")
def supervisor_status(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("supervisor_status", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Cluster Commands
# ============================================================

@cluster_app.command("metrics")
def cluster_metrics(base_url: str = DEFAULT_BASE_URL):
    result = _post_mcp("cluster_metrics", {}, base_url)
    typer.echo(json.dumps(result, indent=2))


# ============================================================
# Dashboard
# ============================================================

@app.command()
def dashboard(base_url: str = DEFAULT_BASE_URL):
    """Open the Orcaopta dashboard in a browser."""
    url = f"{base_url}/ui"
    typer.echo(f"Opening dashboard at {url}")
    webbrowser.open(url)


# ============================================================
# Autocomplete
# ============================================================

@app.command()
def install_completion():
    typer.echo("Run one of the following:")
    typer.echo("  orcaopta --install-completion bash")
    typer.echo("  orcaopta --install-completion zsh")
    typer.echo("  orcaopta --install-completion fish")
    typer.echo("  orcaopta --install-completion powershell")


if __name__ == "__main__":
    app()
