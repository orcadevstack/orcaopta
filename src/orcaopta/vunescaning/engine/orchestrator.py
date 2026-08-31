from typing import List, Dict, Any
from .results import ScanResult, Issue
from ..vunescaning.scanners.trivy_scanner import TrivyScanner
from ..vunescaning.scanners.kubescape_scanner import KubescapeScanner
from ..vunescaning.scanners.cloud_scanner import CloudScanner
from ..vunescaning.scanners.saas_scanner import SaaSScanner
from ..vunescaning.scanners.falco_runtime import FalcoRuntime


class VulnerabilityOrchestrator:
    """
    Main orchestrator that runs all scanners and converts raw output
    into unified Issue objects for the ScanResult model.
    """

    def __init__(self):
        self.trivy = TrivyScanner()
        self.kube = KubescapeScanner()
        self.cloud = CloudScanner()
        self.saas = SaaSScanner()
        self.runtime = FalcoRuntime()

    # -------------------------------------------------------------
    # Helper: normalize severity
    # -------------------------------------------------------------
    def normalize_severity(self, sev: str) -> str:
        sev = sev.lower()
        if sev in ["critical", "high", "medium", "low"]:
            return sev
        return "unknown"

    # -------------------------------------------------------------
    # Helper: convert raw scanner output into Issue objects
    # -------------------------------------------------------------
    def convert(self, raw: Dict[str, Any], source: str) -> List[Issue]:
        issues = []

        if not raw:
            return issues

        # Trivy-style results
        if source == "trivy":
            for vuln in raw.get("Results", []):
                for v in vuln.get("Vulnerabilities", []):
                    issues.append(Issue(
                        id=v.get("VulnerabilityID", "UNKNOWN"),
                        title=v.get("Title", "No title"),
                        severity=self.normalize_severity(v.get("Severity", "unknown")),
                        description=v.get("Description", "No description"),
                        source="trivy",
                        metadata=v
                    ))

        # Kubescape-style results
        elif source == "kube":
            for ctrl in raw.get("controls", []):
                issues.append(Issue(
                    id=ctrl.get("controlID", "UNKNOWN"),
                    title=ctrl.get("name", "Unknown control"),
                    severity=self.normalize_severity(ctrl.get("severity", "unknown")),
                    description=ctrl.get("description", "No description"),
                    source="kube",
                    metadata=ctrl
                ))

        # Cloud scanner (your custom engine)
        elif source == "cloud":
            for issue in raw.get("issues", []):
                issues.append(Issue(
                    id=issue.get("id", "CLOUD-ISSUE"),
                    title=issue.get("title", "Cloud Misconfiguration"),
                    severity=self.normalize_severity(issue.get("severity", "medium")),
                    description=issue.get("description", ""),
                    source="cloud",
                    metadata=issue
                ))

        # SaaS scanner
        elif source == "saas":
            for issue in raw.get("issues", []):
                issues.append(Issue(
                    id=issue.get("id", "SAAS-ISSUE"),
                    title=issue.get("title", "SaaS Misconfiguration"),
                    severity=self.normalize_severity(issue.get("severity", "medium")),
                    description=issue.get("description", ""),
                    source="saas",
                    metadata=issue
                ))

        return issues

    # -------------------------------------------------------------
    # Main scan functions
    # -------------------------------------------------------------
    def scan_all(self) -> ScanResult:
        result = ScanResult()

        # Trivy repo scan
        trivy_raw = self.trivy.scan_repo(".")
        for issue in self.convert(trivy_raw, "trivy"):
            result.add_issue(issue)

        # Kubescape cluster scan
        kube_raw = self.kube.scan_cluster()
        for issue in self.convert(kube_raw, "kube"):
            result.add_issue(issue)

        # Cloud scan
        cloud_raw = self.cloud.scan_aws()
        for issue in self.convert(cloud_raw, "cloud"):
            result.add_issue(issue)

        # SaaS scan
        saas_raw = self.saas.scan_github()
        for issue in self.convert(saas_raw, "saas"):
            result.add_issue(issue)

        return result
