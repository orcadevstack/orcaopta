import subprocess
import json
from typing import Dict, Any, List


class KubescapeScanner:
    """
    Full Kubescape scanner for Orcaopta.
    Supports:
    - Cluster posture scanning
    - CIS benchmark scanning
    - NSA hardening
    - MITRE ATT&CK
    - YAML/IaC manifest scanning
    - Image scanning
    - Runtime scanning (Kubescape v4)
    """

    # -------------------------------------------------------------
    # Internal: run kubescape command
    # -------------------------------------------------------------
    def _run(self, cmd: List[str]) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return {
                    "error": result.stderr,
                    "issues": []
                }
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e), "issues": []}

    # -------------------------------------------------------------
    # Cluster scan (default)
    # -------------------------------------------------------------
    def scan_cluster(self):
        cmd = ["kubescape", "scan", "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # CIS benchmark scan
    # -------------------------------------------------------------
    def scan_cis(self, version="cis-v1.23"):
        cmd = ["kubescape", "scan", "framework", version, "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # NSA hardening
    # -------------------------------------------------------------
    def scan_nsa(self):
        cmd = ["kubescape", "scan", "framework", "nsa", "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # MITRE ATT&CK
    # -------------------------------------------------------------
    def scan_mitre(self):
        cmd = ["kubescape", "scan", "framework", "mitre", "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Scan YAML/IaC manifests
    # -------------------------------------------------------------
    def scan_manifest(self, path: str):
        cmd = ["kubescape", "scan", "manifest", path, "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Scan container image
    # -------------------------------------------------------------
    def scan_image(self, image: str):
        cmd = ["kubescape", "scan", "image", image, "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Runtime scan (Kubescape v4)
    # -------------------------------------------------------------
    def scan_runtime(self):
        cmd = ["kubescape", "runtime", "scan", "--format", "json"]
        return self._run(cmd)

    # -------------------------------------------------------------
    # Convert Kubescape results → Orcaopta Issue objects
    # -------------------------------------------------------------
    def convert(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []

        if "error" in raw:
            issues.append({
                "id": "KUBESCAPE-ERROR",
                "title": "Kubescape scan error",
                "severity": "unknown",
                "description": raw["error"],
                "source": "kube",
                "metadata": raw
            })
            return issues

        controls = raw.get("controls", [])
        for ctrl in controls:
            issues.append({
                "id": ctrl.get("controlID", "KUBE-CONTROL"),
                "title": ctrl.get("name", "Unknown control"),
                "severity": ctrl.get("severity", "unknown"),
                "description": ctrl.get("description", ""),
                "source": "kube",
                "metadata": ctrl
            })

        return issues
