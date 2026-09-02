import os
import logging
from orcaopta.cloud.apis.detect.detect import detect_all

logger = logging.getLogger("orcaopta.autofix")


def ensure_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    logger.warning(f"[AutoFix] Created missing config: {path}")
    return path

def auto_fix_configs():
    detection = detect_all()

    # -----------------------------
    # OpenStack clouds.yaml
    # -----------------------------
    if not detection["openstack"]["detected"]:
        ensure_file(
            os.path.expanduser("~/.config/openstack/clouds.yaml"),
            """
clouds:
  default:
    auth:
      auth_url: http://openstack.local:5000/v3
      username: "CHANGE_ME"
      password: "CHANGE_ME"
      project_name: "CHANGE_ME"
      user_domain_name: "Default"
      project_domain_name: "Default"
""",
        )

    # -----------------------------
    # Kubernetes kubeconfig
    # -----------------------------
    if not detection["kubernetes"]["detected"]:
        ensure_file(
            os.path.expanduser("~/.kube/config"),
            """
apiVersion: v1
clusters: []
contexts: []
current-context: ""
kind: Config
preferences: {}
users: []
""",
        )

    # -----------------------------
    # Terraform main.tf
    # -----------------------------
    if not detection["terraform"]["detected"]:
        ensure_file(
            "main.tf",
            """
terraform {
  required_version = ">= 1.0.0"
}

provider "null" {}
""",
        )

    # -----------------------------
    # Ceph config
    # -----------------------------
    if not detection["ceph"]["detected"]:
        ensure_file(
            "/etc/ceph/ceph.conf",
            """
[global]
fsid = CHANGE_ME
mon_host = 127.0.0.1
""",
        )

    # -----------------------------
    # Spark config
    # -----------------------------
    if not detection["spark"]["detected"]:
        ensure_file(
            "/etc/spark/conf/spark-defaults.conf",
            """
spark.master local[*]
spark.app.name Orcaopta
""",
        )

    return detect_all()
