

from fastapi import APIRouter, HTTPException
from orcaopta.security.security_orchestrator import SecurityOrchestrator
from orcaopta.security.report_generator import ReportGenerator
from orcaopta.vunescaning.engine.results import ScanResult, Issue

router = APIRouter(prefix="/security", tags=["security"])

orch = SecurityOrchestrator()
reports = ReportGenerator()


# -------------------------------------------------------------
# Full vulnerability scan
# -------------------------------------------------------------
@router.get("/scan/all")
def scan_all():
    try:
        results = orch.scan_all()
        return results.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Scan container image
# -------------------------------------------------------------
@router.get("/scan/image/{image}")
def scan_image(image: str):
    try:
        raw = orch.vuln.trivy.scan_image(image)
        issues = orch.vuln.trivy.convert(raw)

        result = ScanResult()
        for i in issues:
            result.add_issue(Issue(**i))

        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Scan repository filesystem
# -------------------------------------------------------------
@router.get("/scan/repo")
def scan_repo(path: str = "."):
    try:
        raw = orch.vuln.trivy.scan_repo(path)
        issues = orch.vuln.trivy.convert(raw)

        result = ScanResult()
        for i in issues:
            result.add_issue(Issue(**i))

        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# SBOM → CVE correlation
# -------------------------------------------------------------
@router.get("/scan/sbom/{image}")
def scan_sbom(image: str):
    try:
        results = orch.scan_sbom(image)
        return results.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# CVE enrichment (NVD + Vulners)
# -------------------------------------------------------------
@router.post("/enrich/cves")
def enrich_cves(payload: dict):
    try:
        result = ScanResult.from_dict(payload)
        enriched = orch.enrich_cves(result)
        return enriched.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Attack graph generation
# -------------------------------------------------------------
@router.post("/attack-graph")
def attack_graph(payload: dict, path: str = "attack.graphml"):
    try:
        result = ScanResult.from_dict(payload)
        orch.build_attack_graph(result, path)
        return {"status": "ok", "graph_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# HTML report
# -------------------------------------------------------------
@router.post("/report/html")
def report_html(payload: dict):
    try:
        result = ScanResult.from_dict(payload)
        html = reports.to_html(result)
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# Markdown report
# -------------------------------------------------------------
@router.post("/report/markdown")
def report_markdown(payload: dict):
    try:
        result = ScanResult.from_dict(payload)
        md = reports.to_markdown(result)
        return {"markdown": md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# JSON report
# -------------------------------------------------------------
@router.post("/report/json")
def report_json(payload: dict):
    try:
        result = ScanResult.from_dict(payload)
        return reports.to_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
