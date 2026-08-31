# src/orcaopta/cli/vscan_cli.py
import typer
from orcaopta.vunescaning.engine.orchestrator import VulnerabilityOrchestrator
from orcaopta.vunescaning.engine.formatter import ResultFormatter
from orcaopta.vunescaning.engine.results import Issue, ScanResult

app = typer.Typer(help="Orcaopta Vulnerability Scanning CLI")

@app.command()
def image(name: str, html: str = None):
    """Scan a container image using Trivy."""
    orch = VulnerabilityOrchestrator()
    raw = orch.trivy.scan_image(name)
    issues = orch.trivy.convert(raw)

    result = ScanResult()
    for i in issues:
        result.add_issue(Issue(**i))

    formatter = ResultFormatter()
    formatter.to_table(result)

    if html:
        with open(html, "w") as f:
            f.write(formatter.to_html(result))
        typer.echo(f"HTML report written to {html}")

@app.command()
def repo(path: str, html: str = None):
    """Scan a repository filesystem."""
    orch = VulnerabilityOrchestrator()
    raw = orch.trivy.scan_repo(path)
    issues = orch.trivy.convert(raw)

    result = ScanResult()
    for i in issues:
        result.add_issue(Issue(**i))

    formatter = ResultFormatter()
    formatter.to_table(result)

    if html:
        with open(html, "w") as f:
            f.write(formatter.to_html(result))
        typer.echo(f"HTML report written to {html}")

@app.command()
def sbom(image: str, html: str = None):
    """Generate SBOM + correlate CVEs."""
    orch = VulnerabilityOrchestrator()
    sbom = orch.trivy.scan_sbom(image)
    vulns = orch.trivy.scan_image(image)
    correlated = orch.trivy.correlate_sbom_with_vulns(sbom, vulns)

    result = ScanResult()
    for item in correlated:
        result.add_issue(Issue(**item))

    formatter = ResultFormatter()
    formatter.to_table(result)

    if html:
        with open(html, "w") as f:
            f.write(formatter.to_html(result))
        typer.echo(f"HTML report written to {html}")

if __name__ == "__main__":
    app()
