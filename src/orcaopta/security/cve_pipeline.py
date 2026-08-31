
import nvdlib
from vulners import Vulners
from orcaopta.vunescaning.engine.results import Issue

class CVEPipeline:
    """
    Enriches CVEs with NVD + Vulners metadata.
    """

    def __init__(self):
        self.vulners = Vulners()

    def enrich(self, issue: Issue) -> Issue:
        if not issue.id.startswith("CVE"):
            return issue

        try:
            nvd = nvdlib.searchCVE(cveId=issue.id)
            if nvd:
                issue.metadata["nvd"] = nvd[0].__dict__
        except Exception:
            pass

        try:
            vul = self.vulners.document(issue.id)
            issue.metadata["vulners"] = vul
        except Exception:
            pass

        return issue
