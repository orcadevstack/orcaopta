import os
import json
import logging
import subprocess
import shutil

logger = logging.getLogger("orcaopta.wizard")

INSTALL_STATE = "/app/state/installed.json"


# ============================
# Low-level helpers
# ============================

def check_binary(name: str) -> bool:
    """Check if a binary exists in PATH."""
    return shutil.which(name) is not None


def get_output(cmd: str) -> str:
    """Run a shell command safely and return its output."""
    try:
        return subprocess.getoutput(cmd)
    except Exception:
        return "not available"


def pip_show(pkg: str) -> str:
    """Check if a Python package is installed."""
    return get_output(f"pip show {pkg} 2>&1")


# ============================
# Requirement definitions
# ============================

MANDATORY_BINARIES = {
    "python3": "Python 3 is required to run Orcaopta.",
    "java": "Java (JRE) is required for Spark/PySpark.",
    "docker": "Docker is required to run Orcaopta containers.",
}

OPTIONAL_BINARIES = {
    "openstack": "OpenStack CLI is optional but recommended for cloud integration.",
    "terraform": "Terraform is optional but recommended for IaC integration.",
    "kubectl": "kubectl is optional but recommended for Kubernetes integration.",
    "ceph": "Ceph CLI is optional but recommended for storage integration.",
    "spark-submit": "spark-submit is optional but recommended for Spark jobs.",
}

MANDATORY_PY_PACKAGES = {
    "pyspark": "PySpark is required for Spark integration.",
}

OPTIONAL_PY_PACKAGES = {
    "attackcti": "attackcti is optional but recommended for MITRE ATT&CK integration.",
    "stix2": "stix2 is optional but recommended for ATT&CK/STIX processing.",
}


# ============================
# Suggestion helpers
# ============================

def suggest_install_binary(name: str) -> str:
    if name == "python3":
        return "Install Python 3 via your OS package manager (e.g., apt, yum, brew)."
    if name == "java":
        return "Install OpenJDK 17: apt-get install openjdk-17-jre."
    if name == "docker":
        return "Install Docker from https://docs.docker.com/get-docker/."
    if name == "openstack":
        return "Install OpenStack CLI: pip install python-openstackclient."
    if name == "terraform":
        return "Install Terraform from https://developer.hashicorp.com/terraform/downloads."
    if name == "kubectl":
        return "Install kubectl from https://kubernetes.io/docs/tasks/tools/."
    if name == "ceph":
        return "Install Ceph CLI via your distro packages."
    if name == "spark-submit":
        return "Install Apache Spark from https://spark.apache.org/downloads.html."
    return f"Install {name} via your OS package manager or official docs."


def suggest_install_package(pkg: str) -> str:
    return f"Install Python package '{pkg}' via: pip install {pkg}"


# ============================
# Core wizard logic
# ============================

def run_checks() -> dict:
    """
    Run all environment checks and return a structured result.
    """
    result = {
        "timestamp": get_output("date"),
        "version": "1.0.0",
        "languages": {},
        "binaries": {},
        "python_packages": {},
        "warnings": [],
        "errors": [],
        "suggestions": [],
    }

    # Languages / runtimes
    result["languages"]["python"] = get_output("python3 --version")
    result["languages"]["java"] = get_output("java -version 2>&1")
    result["languages"]["node"] = get_output("node --version")
    result["languages"]["go"] = get_output("go version")
    result["languages"]["rust"] = get_output("rustc --version")
    result["languages"]["ruby"] = get_output("ruby --version")
    result["languages"]["php"] = get_output("php --version")

    # Mandatory binaries
    for name, desc in MANDATORY_BINARIES.items():
        present = check_binary(name)
        result["binaries"][name] = present
        if not present:
            msg = f"MANDATORY missing binary: {name}. {desc}"
            result["errors"].append(msg)
            result["suggestions"].append(suggest_install_binary(name))

    # Optional binaries
    for name, desc in OPTIONAL_BINARIES.items():
        present = check_binary(name)
        result["binaries"][name] = present
        if not present:
            msg = f"Optional binary missing: {name}. {desc}"
            result["warnings"].append(msg)
            result["suggestions"].append(suggest_install_binary(name))

    # Mandatory Python packages
    for pkg, desc in MANDATORY_PY_PACKAGES.items():
        info = pip_show(pkg)
        installed = "Name:" in info
        result["python_packages"][pkg] = installed
        if not installed:
            msg = f"MANDATORY missing Python package: {pkg}. {desc}"
            result["errors"].append(msg)
            result["suggestions"].append(suggest_install_package(pkg))

    # Optional Python packages
    for pkg, desc in OPTIONAL_PY_PACKAGES.items():
        info = pip_show(pkg)
        installed = "Name:" in info
        result["python_packages"][pkg] = installed
        if not installed:
            msg = f"Optional Python package missing: {pkg}. {desc}"
            result["warnings"].append(msg)
            result["suggestions"].append(suggest_install_package(pkg))

    return result


def save_state(state: dict):
    os.makedirs("/app/state", exist_ok=True)
    with open(INSTALL_STATE, "w") as f:
        json.dump(state, f, indent=2)


def wizard():
    """
    Full installation wizard for Orcaopta.
    - Runs environment checks
    - Logs errors and warnings
    - Saves state
    - Can be extended to be interactive
    """

    # If already installed, just log and return
    if os.path.exists(INSTALL_STATE):
        logger.info("Orcaopta already installed. Skipping wizard.")
        return True

    logger.info("Running Orcaopta installation wizard...")

    state = run_checks()

    # Log errors and warnings
    for err in state["errors"]:
        logger.error(err)
    for warn in state["warnings"]:
        logger.warning(warn)

    # Log suggestions
    for sug in state["suggestions"]:
        logger.info(f"Suggestion: {sug}")

    # Save state
    save_state(state)

    if state["errors"]:
        logger.error("Orcaopta environment has mandatory missing components.")
        logger.error("Please address the above errors and suggestions before production use.")
        # We still return True so the system can start in degraded mode.
        return False

    logger.info("Orcaopta installation wizard completed successfully.")
    return True
