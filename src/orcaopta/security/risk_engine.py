
from dataclasses import dataclass
from typing import List
from orcaopta.vunescaning.engine.results import ScanResult, Issue


@dataclass
class RiskScore:
    issue_id: str
    score: float
    label: str


class RiskEngine:
    """
    ML-friendly risk scoring engine for Orcaopta.
    Combines:
    - Severity
    - CVE presence
    - Source (cloud / k8s / saas / runtime)
    - Optional exploitability (from metadata)
    """

    SEVERITY_BASE = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4,
        "unknown": 0.2,
    }

    SOURCE_WEIGHT = {
        "cloud": 1.0,
        "kube": 0.9,
        "saas": 0.8,
        "runtime": 1.0,
        "trivy": 0.7,
        "default": 0.5,
    }

    def _severity_factor(self, issue: Issue) -> float:
        return self.SEVERITY_BASE.get(issue.severity.lower(), 0.2)

    def _source_factor(self, issue: Issue) -> float:
        return self.SOURCE_WEIGHT.get(issue.source, self.SOURCE_WEIGHT["default"])

    def _cve_factor(self, issue: Issue) -> float:
        return 1.0 if issue.id.startswith("CVE") else 0.5

    def _exploitability_factor(self, issue: Issue) -> float:
        nvd = issue.metadata.get("nvd", {})
        try:
            metrics = nvd.get("metrics", {}).get("cvssMetricV31", [{}])[0]
            exploit = metrics.get("exploitabilityScore", 0.0)
            return min(exploit / 10.0, 1.0)
        except Exception:
            return 0.5

    def score_issue(self, issue: Issue) -> RiskScore:
        sev = self._severity_factor(issue)
        src = self._source_factor(issue)
        cve = self._cve_factor(issue)
        expl = self._exploitability_factor(issue)

        # Simple weighted combination
        raw = (sev * 0.4) + (src * 0.2) + (cve * 0.2) + (expl * 0.2)

        if raw >= 0.85:
            label = "very_high"
        elif raw >= 0.7:
            label = "high"
        elif raw >= 0.5:
            label = "medium"
        elif raw >= 0.3:
            label = "low"
        else:
            label = "very_low"

        return RiskScore(issue_id=issue.id, score=raw, label=label)

    def score_all(self, results: ScanResult) -> List[RiskScore]:
        scores = []
        for issue in results.all():
            scores.append(self.score_issue(issue))
        return scores

    def attach_scores(self, results: ScanResult) -> ScanResult:
        """
        Adds risk_score + risk_label into issue.metadata.
        """
        scored = ScanResult()
        for issue in results.all():
            rs = self.score_issue(issue)
            issue.metadata["risk_score"] = rs.score
            issue.metadata["risk_label"] = rs.label
            scored.add_issue(issue)
        return scored
