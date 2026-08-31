
from orcaopta.vunescaning.engine.orchestrator import VulnerabilityOrchestrator
from orcaopta.vunescaning.engine.results import ScanResult, Issue

class SecurityPipeline:
    """
    Unified security pipeline for Orcaopta.
    Runs:
    - Trivy (image, repo, IaC)
    - Kubescape (cluster, CIS, NSA, MITRE)
    - Cloud scanners (AWS, GCP, Azure)
    - SaaS scanners (GitHub, GitLab, Okta)
    - Falco runtime
    """

    def __init__(self):
        self.orch = VulnerabilityOrchestrator()

    def run_all(self) -> ScanResult:
        result = ScanResult()

        # Trivy repo scan
        trivy_raw = self.orch.trivy.scan_repo(".")
        for issue in self.orch.trivy.convert(trivy_raw):
            result.add_issue(Issue(**issue))

        # Kubescape cluster scan
        kube_raw = self.orch.kube.scan_cluster()
        for issue in self.orch.kube.convert(kube_raw):
            result.add_issue(Issue(**issue))

        # Cloud scan
        cloud_raw = self.orch.cloud.scan_all()
        for issue in cloud_raw["issues"]:
            result.add_issue(Issue(**issue))

        # SaaS scan
        saas_raw = self.orch.saas.scan_github()
        for issue in saas_raw["issues"]:
            result.add_issue(Issue(**issue))

        # Runtime scan
        runtime_issues = self.orch.runtime.collect_issues()
        for issue in runtime_issues:
            result.add_issue(Issue(**issue))

        return result
