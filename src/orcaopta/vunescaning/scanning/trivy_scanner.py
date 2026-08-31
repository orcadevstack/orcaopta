import subprocess
import json
from typing import Dict, Any, List


class TrivyScanner:
    """
    Full Trivy scanner for Orcaopta.
    Supports:
    - Image scanning
    - Filesystem scanning
    - IaC scanning (Terraform, Helm, K8s YAML)
    - Secret scanning
    - SBOM generation
    - License scanning
    - SBOM → CVE correlation
    """

    # -------------------------------------------------------------
    # Internal runner
    # -------------------------------------------------------------
    def _run(self, cmd: List[str]) -> Dict[str, Any]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": result.stderr, "issues": []}
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e), "issues": []}

    # -------------------------------------------------------------
    # Image scanning
    # -------------------------------------------------------------
    def scan_image(self, image: str):
        cmd = [
            "trivy", "image",
            "--format", "json",
            "--scanners", "vuln,secret,misconfig,license",
            image
        ]
        return self._run(cmd)

    # -------------------------------------------------------------
    # IaC scanning
    # -------------------------------------------------------------
    def scan_iac(self, path: str):
        cmd = [
            "trivy", "config",
            "--format", "json",
            "--scanners", "misconfig,secret",
            path
        ]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Filesystem scanning
    # -------------------------------------------------------------
    def scan_repo(self, repo_path: str):
        cmd = [
            "trivy", "fs",
            "--format", "json",
            "--scanners", "vuln,secret,misconfig,license",
            repo_path
        ]
        return self._run(cmd)

    # -------------------------------------------------------------
    # SBOM generation
    # -------------------------------------------------------------
    def scan_sbom(self, image: str):
        cmd = ["trivy", "sbom", "--format", "json", image]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Severity scoring
    # -------------------------------------------------------------
    def severity_score(self, severity: str) -> int:
        mapping = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "unknown": 0,
        }
        return mapping.get(severity.lower(), 0)

    # -------------------------------------------------------------
    # SBOM → CVE correlation
    # -------------------------------------------------------------
    def correlate_sbom_with_vulns(self, sbom: Dict[str, Any], vulns: Dict[str, Any]) -> List[Dict[str, Any]]:
        packages = {}

        for comp in sbom.get("components", []):
            name = comp.get("name")
            version = comp.get("version")
            if name:
                packages[name] = {"name": name, "version": version}

        issues = []

        for result in vulns.get("Results", []):
            for v in result.get("Vulnerabilities", []):
                pkg_name = v.get("PkgName")
                pkg_meta = packages.get(pkg_name, {})

                issues.append({
                    "id": v.get("VulnerabilityID", "UNKNOWN"),
                    "title": v.get("Title", "Unknown vulnerability"),
                    "severity": v.get("Severity", "unknown"),
                    "severity_score": self.severity_score(v.get("Severity", "unknown")),
                    "description": v.get("Description", ""),
                    "source": "trivy",
                    "metadata": {
                        "vuln": v,
                        "package": pkg_meta,
                    },
                })

        return issues

    # -------------------------------------------------------------
    # Convert Trivy results → Orcaopta Issue objects
    # -------------------------------------------------------------
    def convert(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []

        if "error" in raw:
            issues.append({
                "id": "TRIVY-ERROR",
                "title": "Trivy scan error",
                "severity": "unknown",
                "description": raw["error"],
                "source": "trivy",
                "metadata": raw
            })
            return issues

        # Vulnerabilities
        for result in raw.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                issues.append({
                    "id": vuln.get("VulnerabilityID", "UNKNOWN"),
                    "title": vuln.get("Title", "Unknown vulnerability"),
                    "severity": vuln.get("Severity", "unknown"),
                    "severity_score": self.severity_score(vuln.get("Severity", "unknown")),
                    "description": vuln.get("Description", ""),
                    "source": "trivy",
                    "metadata": vuln
                })

        # Misconfigurations
        for result in raw.get("Results", []):
            for mis in result.get("Misconfigurations", []):
                issues.append({
                    "id": mis.get("ID", "MISCONFIG"),
                    "title": mis.get("Title", "Misconfiguration"),
                    "severity": mis.get("Severity", "unknown"),
                    "severity_score": self.severity_score(mis.get("Severity", "unknown")),
                    "description": mis.get("Description", ""),
                    "source": "trivy",
                    "metadata": mis
                })

        # Secrets
        for result in raw.get("Results", []):
            for sec in result.get("Secrets", []):
                issues.append({
                    "id": sec.get("RuleID", "SECRET"),
                    "title": "Secret detected",
                    "severity": "critical",
                    "severity_score": 4,
                    "description": sec.get("Title", "Secret found"),
                    "source": "trivy",
                    "metadata": sec
                })

        # License issues
        for result in raw.get("Results", []):
            for lic in result.get("Licenses", []):
                issues.append({
                    "id": lic.get("Key", "LICENSE"),
                    "title": "License violation",
                    "severity": "medium",
                    "severity_score": 2,
                    "description": lic.get("Title", "License issue"),
                    "source": "trivy",
                    "metadata": lic
                })

        return issues
