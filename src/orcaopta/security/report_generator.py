

from orcaopta.vunescaning.engine.results import ScanResult, Issue
from datetime import datetime
import orjson
import markdown

class ReportGenerator:
    """
    Generates security reports for Orcaopta:
    - HTML
    - Markdown
    - JSON
    - Severity summary
    - CVE summary
    """

    # -------------------------------------------------------------
    # Summary helpers
    # -------------------------------------------------------------
    def severity_summary(self, results: ScanResult):
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        for issue in results.all():
            sev = issue.severity.lower()
            summary[sev] = summary.get(sev, 0) + 1
        return summary

    def cve_summary(self, results: ScanResult):
        cves = []
        for issue in results.all():
            if issue.id.startswith("CVE"):
                cves.append(issue.id)
        return sorted(set(cves))

    # -------------------------------------------------------------
    # JSON report
    # -------------------------------------------------------------
    def to_json(self, results: ScanResult) -> str:
        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "severity_summary": self.severity_summary(results),
            "cve_summary": self.cve_summary(results),
            "issues": [i.__dict__ for i in results.all()],
        }
        return orjson.dumps(payload, option=orjson.OPT_INDENT_2).decode()

    # -------------------------------------------------------------
    # Markdown report
    # -------------------------------------------------------------
    def to_markdown(self, results: ScanResult) -> str:
        md = f"# Orcaopta Security Report\nGenerated: {datetime.utcnow().isoformat()}\n\n"

        # Severity summary
        sev = self.severity_summary(results)
        md += "## Severity Summary\n"
        for k, v in sev.items():
            md += f"- **{k.capitalize()}**: {v}\n"
        md += "\n"

        # CVE summary
        cves = self.cve_summary(results)
        md += "## CVE Summary\n"
        if cves:
            for c in cves:
                md += f"- {c}\n"
        else:
            md += "- No CVEs detected\n"
        md += "\n"

        # Issues
        md += "## Issues\n"
        for issue in results.all():
            md += f"### {issue.title}\n"
            md += f"- **ID:** {issue.id}\n"
            md += f"- **Severity:** {issue.severity}\n"
            md += f"- **Source:** {issue.source}\n"
            md += f"- **Description:** {issue.description}\n\n"

        return md

    # -------------------------------------------------------------
    # HTML report
    # -------------------------------------------------------------
    def to_html(self, results: ScanResult) -> str:
        md = self.to_markdown(results)
        html_body = markdown.markdown(md)

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Orcaopta Security Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
    }}
    h1, h2, h3 {{
      color: #222;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 20px;
    }}
    th, td {{
      border: 1px solid #ccc;
      padding: 8px;
    }}
    th {{
      background: #333;
      color: #fff;
    }}
  </style>
</head>
<body>
{html_body}
</body>
</html>
"""
        return html

    # -------------------------------------------------------------
    # Optional PDF (requires WeasyPrint)
    # -------------------------------------------------------------
    def to_pdf(self, results: ScanResult, path: str):
        try:
            from weasyprint import HTML
            html = self.to_html(results)
            HTML(string=html).write_pdf(path)
        except Exception as e:
            raise RuntimeError(f"PDF generation failed: {e}")
