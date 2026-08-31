from rich.table import Table
from rich.console import Console
from .results import Issue, ScanResult

console = Console()

class ResultFormatter:

    # -------------------------------------------------------------
    # Rich table output
    # -------------------------------------------------------------
    def to_table(self, results: ScanResult):
        table = Table(title="Orcaopta Vulnerability Report")

        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Severity", style="red")
        table.add_column("Title", style="white")
        table.add_column("Source", style="green")
        table.add_column("Description", style="yellow")

        for issue in results.all():
            table.add_row(
                issue.id,
                issue.severity.upper(),
                issue.title,
                issue.source,
                issue.description
            )

        console.print(table)

    # -------------------------------------------------------------
    # Markdown output
    # -------------------------------------------------------------
    def to_markdown(self, results: ScanResult) -> str:
        md = "# Orcaopta Vulnerability Report\n\n"
        for issue in results.all():
            md += f"## {issue.title}\n"
            md += f"- **ID:** {issue.id}\n"
            md += f"- **Severity:** {issue.severity}\n"
            md += f"- **Source:** {issue.source}\n"
            md += f"- **Description:** {issue.description}\n\n"
        return md

    # -------------------------------------------------------------
    # JSON output
    # -------------------------------------------------------------
    def to_json(self, results: ScanResult) -> str:
        return results.to_json()

    # -------------------------------------------------------------
    # HTML output
    # -------------------------------------------------------------
    def to_html(self, results: ScanResult) -> str:
        rows = []
        for issue in results.all():
            rows.append(
                f"<tr>"
                f"<td>{issue.id}</td>"
                f"<td>{issue.severity.upper()}</td>"
                f"<td>{issue.title}</td>"
                f"<td>{issue.source}</td>"
                f"<td>{issue.description}</td>"
                f"</tr>"
            )

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Orcaopta Vulnerability Report</title>
  <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; font-family: sans-serif; }}
    th {{ background: #222; color: #fff; }}
  </style>
</head>
<body>
  <h1>Orcaopta Vulnerability Report</h1>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Severity</th>
        <th>Title</th>
        <th>Source</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
        return html
