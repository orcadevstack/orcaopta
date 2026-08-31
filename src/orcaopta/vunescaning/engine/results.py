from dataclasses import dataclass, field
from typing import Any, Dict, List
import json

@dataclass
class Issue:
    id: str
    title: str
    severity: str
    description: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScanResult:
    trivy: List[Issue] = field(default_factory=list)
    kube: List[Issue] = field(default_factory=list)
    cloud: List[Issue] = field(default_factory=list)
    saas: List[Issue] = field(default_factory=list)
    runtime: List[Issue] = field(default_factory=list)

    def all(self) -> List[Issue]:
        return (
            self.trivy +
            self.kube +
            self.cloud +
            self.saas +
            self.runtime
        )

    def by_severity(self, level: str) -> List[Issue]:
        return [i for i in self.all() if i.severity.lower() == level.lower()]

    def to_json(self) -> str:
        return json.dumps([i.__dict__ for i in self.all()], indent=2)

    def add_issue(self, issue: Issue):
        if issue.source == "trivy":
            self.trivy.append(issue)
        elif issue.source == "kube":
            self.kube.append(issue)
        elif issue.source == "cloud":
            self.cloud.append(issue)
        elif issue.source == "saas":
            self.saas.append(issue)
        elif issue.source == "runtime":
            self.runtime.append(issue)
