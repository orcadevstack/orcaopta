import os
import yaml
import json
import logging

logger = logging.getLogger("orcaopta.cloud.detect")


# ============================================================
# SAFE LOADERS
# ============================================================

def safe_load_yaml(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Failed to load YAML {path}: {e}")
        return None


def safe_load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load JSON {path}: {e}")
        return None


# ============================================================
# OPENSTACK DETECTION
# ============================================================

def detect_openstack():
    """
    Detect OpenStack by reading clouds.yaml.
    Extract auth_url and cloud name.
    """
    paths = [
        "/etc/openstack/clouds.yaml",
        os.path.expanduser("~/.config/openstack/clouds.yaml"),
        os.path.expanduser("~/.config/openstack/clouds.yml"),
    ]

    for path in paths:
        data = safe_load_yaml(path)
        if data and "clouds" in data:
            try:
                cloud_name = list(data["clouds"].keys())[0]
                auth_url = data["clouds"][cloud_name]["auth"]["auth_url"]
                return {
                    "detected": True,
                    "type": "openstack",
                    "config_path": path,
                    "cloud_name": cloud_name,
                    "auth_url": auth_url,
                }
            except Exception:
                continue

    return {"detected": False, "type": "openstack", "reason": "clouds.yaml missing"}


# ============================================================
# CLOUDSTACK DETECTION (Apache CloudStack)
# ============================================================

def detect_cloudstack():
    """
    Detect Apache CloudStack by reading cloudstack.json or api config.
    """
    paths = [
        "/etc/cloudstack/cloudstack.json",
        "/etc/cloudstack/management-server.json",
        os.path.expanduser("~/.cloudstack/cloudstack.json"),
    ]

    for path in paths:
        data = safe_load_json(path)
        if data:
            try:
                endpoint = data.get("endpoint") or data.get("api_url")
                api_key = data.get("api_key")
                return {
                    "detected": True,
                    "type": "cloudstack",
                    "config_path": path,
                    "endpoint": endpoint,
                    "api_key_present": bool(api_key),
                }
            except Exception:
                continue

    return {"detected": False, "type": "cloudstack", "reason": "cloudstack.json missing"}


# ============================================================
# KUBERNETES DETECTION
# ============================================================

def detect_kubernetes():
    """
    Detect Kubernetes by reading ~/.kube/config.
    Extract cluster server URL.
    """
    path = os.path.expanduser("~/.kube/config")
    data = safe_load_yaml(path)

    if not data:
        return {"detected": False, "type": "kubernetes", "reason": "kubeconfig missing"}

    try:
        cluster = data["clusters"][0]
        server = cluster["cluster"]["server"]
        return {
            "detected": True,
            "type": "kubernetes",
            "config_path": path,
            "cluster_name": cluster["name"],
            "server_url": server,
        }
    except Exception:
        return {"detected": False, "type": "kubernetes", "reason": "invalid kubeconfig"}


# ============================================================
# CNI DETECTION (Calico, Flannel, Cilium)
# ============================================================

def detect_cni():
    """
    Detect CNI by checking common CNI config directories.
    """
    paths = [
        "/etc/cni/net.d/calico.conf",
        "/etc/cni/net.d/10-calico.conf",
        "/etc/cni/net.d/flannel.conf",
        "/etc/cni/net.d/cilium.conf",
    ]

    for path in paths:
        data = safe_load_json(path) or safe_load_yaml(path)
        if data:
            return {
                "detected": True,
                "type": "cni",
                "config_path": path,
                "plugin": os.path.basename(path).replace(".conf", ""),
            }

    return {"detected": False, "type": "cni", "reason": "no CNI config found"}


# ============================================================
# TERRAFORM DETECTION
# ============================================================

def detect_terraform():
    """
    Detect Terraform by checking terraform.tfvars or main.tf.
    """
    tfvars = "terraform.tfvars"
    main_tf = "main.tf"

    if os.path.exists(tfvars):
        return {
            "detected": True,
            "type": "terraform",
            "config_path": tfvars,
            "endpoint": "unknown",
        }

    if os.path.exists(main_tf):
        try:
            with open(main_tf) as f:
                content = f.read()
                if "endpoint" in content:
                    return {
                        "detected": True,
                        "type": "terraform",
                        "config_path": main_tf,
                        "endpoint": "endpoint found",
                    }
        except Exception:
            pass

        return {
            "detected": True,
            "type": "terraform",
            "config_path": main_tf,
            "endpoint": "unknown",
        }

    return {"detected": False, "type": "terraform", "reason": "no terraform config"}


# ============================================================
# CEPH DETECTION
# ============================================================

def detect_ceph():
    """
    Detect Ceph by reading /etc/ceph/ceph.conf.
    """
    path = "/etc/ceph/ceph.conf"
    if not os.path.exists(path):
        return {"detected": False, "type": "ceph", "reason": "ceph.conf missing"}

    try:
        with open(path) as f:
            lines = f.readlines()
            mons = [l for l in lines if "mon_host" in l]
            if mons:
                return {
                    "detected": True,
                    "type": "ceph",
                    "config_path": path,
                    "mon_host": mons[0].split("=")[1].strip(),
                }
    except Exception:
        pass

    return {"detected": True, "type": "ceph", "config_path": path, "mon_host": "unknown"}


# ============================================================
# SPARK DETECTION
# ============================================================

def detect_spark():
    paths = [
        "/etc/spark/conf/spark-defaults.conf",
        "/usr/local/spark/conf/spark-defaults.conf",
        "/opt/spark/conf/spark-defaults.conf",
    ]

    for path in paths:
        if os.path.exists(path):
            return {
                "detected": True,
                "type": "spark",
                "config_path": path,
            }

    return {"detected": False, "type": "spark", "reason": "spark-defaults.conf missing"}


# ============================================================
# UNIFIED DETECTOR
# ============================================================

def detect_all():
    return {
        "openstack": detect_openstack(),
        "cloudstack": detect_cloudstack(),
        "kubernetes": detect_kubernetes(),
        "cni": detect_cni(),
        "terraform": detect_terraform(),
        "ceph": detect_ceph(),
        "spark": detect_spark(),
    }
