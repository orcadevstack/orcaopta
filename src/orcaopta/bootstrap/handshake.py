import os
import json
import logging
import subprocess
import shutil

logger = logging.getLogger("orcaopta.handshake")

INSTALL_STATE = "/app/state/installed.json"


def check_binary(name):
    """Check if a binary exists in PATH."""
    return shutil.which(name) is not None


def get_version(cmd):
    """Run a version command safely."""
    try:
        return subprocess.getoutput(cmd)
    except Exception:
        return "not available"


def handshake():
    """
    First-run installation handshake for Orcaopta.
    Verifies all major languages, runtimes, and cloud tools.
    """

    # 1. Check if already installed
    if os.path.exists(INSTALL_STATE):
        logger.info("Orcaopta already installed. Skipping handshake.")
        return True

    logger.info("Running Orcaopta installation handshake...")

    state = {
        "timestamp": get_version("date"),
        "version": "1.0.0",

        # ============================
        # Programming Languages
        # ============================
        "python": get_version("python3 --version"),
        "java": get_version("java -version 2>&1"),
        "node": get_version("node --version"),
        "npm": get_version("npm --version"),
        "go": get_version("go version"),
        "rust": get_version("rustc --version"),
        "cargo": get_version("cargo --version"),
        "ruby": get_version("ruby --version"),
        "php": get_version("php --version"),
        "gcc": get_version("gcc --version"),
        "g++": get_version("g++ --version"),
        "clang": get_version("clang --version"),
        "bash": get_version("bash --version"),
        "zsh": get_version("zsh --version"),

        # ============================
        # Python Libraries
        # ============================
        "pyspark": get_version("pip show pyspark 2>&1"),
        "attackcti": get_version("pip show attackcti 2>&1"),
        "stix2": get_version("pip show stix2 2>&1"),

        # ============================
        # Cloud / DevOps Tools
        # ============================
        "openstack_cli": check_binary("openstack"),
        "terraform": check_binary("terraform"),
        "kubectl": check_binary("kubectl"),
        "ceph": check_binary("ceph"),
        "docker": check_binary("docker"),
        "docker_compose": check_binary("docker-compose"),

        # ============================
        # Spark / Hadoop Ecosystem
        # ============================
        "spark_submit": check_binary("spark-submit"),
        "hadoop": check_binary("hadoop"),
    }

    # 2. Save installation state
    os.makedirs("/app/state", exist_ok=True)
    with open(INSTALL_STATE, "w") as f:
        json.dump(state, f, indent=2)

    logger.info("Orcaopta handshake completed.")
    return True
