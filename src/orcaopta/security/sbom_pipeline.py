
from orcaopta.vunescaning.scanners.trivy_scanner import TrivyScanner
from orcaopta.vunescaning.engine.results import ScanResult, Issue

class SBOMPipeline:
    """
    SBOM → CVE correlation pipeline.
    """

    def __init__(self):
        self.trivy = TrivyScanner()

    def run(self, image: str) -> ScanResult:
        sbom = self.trivy.scan_sbom(image)
        vulns = self.trivy.scan_image(image)
        correlated = self.trivy.correlate_sbom_with_vulns(sbom, vulns)

        result = ScanResult()
        for item in correlated:
            result.add_issue(Issue(**item))

        return result
