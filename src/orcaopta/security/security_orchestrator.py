

from orcaopta.vunescaning.engine.orchestrator import VulnerabilityOrchestrator
from orcaopta.vunescaning.engine.results import ScanResult, Issue

from orcaopta.security.cve_pipeline import CVEPipeline
from orcaopta.security.sbom_pipeline import SBOMPipeline
from orcaopta.security.attack_graph import AttackGraph


class SecurityOrchestrator:
    """
    Central orchestrator for Orcaopta's security subsystem.
    Coordinates:
    - Vulnerability scanning (Trivy, Kubescape, Cloud, SaaS, Runtime)
    - SBOM → CVE correlation
    - CVE enrichment (NVD + Vulners)
    - Attack graph generation
    """

    def __init__(self):
        self.vuln = VulnerabilityOrchestrator()
        self.cve = CVEPipeline()
        self.sbom = SBOMPipeline()
        self.attack = AttackGraph()

    # -------------------------------------------------------------
    # Run full vulnerability scan
    # -------------------------------------------------------------
    def scan_all(self) -> ScanResult:
        result = ScanResult()

        # Trivy repo scan
        trivy_raw = self.vuln.trivy.scan_repo(".")
        for issue in self.vuln.trivy.convert(trivy_raw):
            result.add_issue(Issue(**issue))

        # Kubescape cluster scan
        kube_raw = self.vuln.kube.scan_cluster()
        for issue in self.vuln.kube.convert(kube_raw):
            result.add_issue(Issue(**issue))

        # Cloud scan
        cloud_raw = self.vuln.cloud.scan_all()
        for issue in cloud_raw["issues"]:
            result.add_issue(Issue(**issue))

        # SaaS scan
        saas_raw = self.vuln.saas.scan_github()
        for issue in saas_raw["issues"]:
            result.add_issue(Issue(**issue))

        # Runtime scan
        runtime_issues = self.vuln.runtime.collect_issues()
        for issue in runtime_issues:
            result.add_issue(Issue(**issue))

        return result

    # -------------------------------------------------------------
    # SBOM → CVE correlation
    # -------------------------------------------------------------
    def scan_sbom(self, image: str) -> ScanResult:
        return self.sbom.run(image)

    # -------------------------------------------------------------
    # Enrich CVEs with NVD + Vulners
    # -------------------------------------------------------------
    def enrich_cves(self, results: ScanResult) -> ScanResult:
        enriched = ScanResult()
        for issue in results.all():
            enriched_issue = self.cve.enrich(issue)
            enriched.add_issue(enriched_issue)
        return enriched

    # -------------------------------------------------------------
    # Build attack graph
    # -------------------------------------------------------------
    def build_attack_graph(self, results: ScanResult, path: str):
        self.attack.build(results)
        self.attack.export(path)

    # -------------------------------------------------------------
    # Full pipeline: scan → enrich → graph
    # -------------------------------------------------------------
    def full_pipeline(self, image: str, graph_path: str) -> ScanResult:
        # SBOM + CVE correlation
        sbom_results = self.scan_sbom(image)

        # CVE enrichment
        enriched = self.enrich_cves(sbom_results)

        # Attack graph
        self.build_attack_graph(enriched, graph_path)

        return enriched
