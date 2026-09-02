import os
import subprocess
import json
import shutil


# ---------------------------------------------------------
# SaaS (Terraform) AUDIT MODULE — STRICT + SAFE
# ---------------------------------------------------------

def _load_saas_config():
    """
    Load Orcaopta SaaS config.
    Returns None if missing.
    """
    try:
        from orcaopta.config import config
        return config.get("saas", None)
    except Exception:
        return None


def _terraform_installed():
    """
    Check if Terraform binary exists.
    """
    return shutil.which("terraform") is not None


def _saas_process_running():
    """
    Detect SaaS/Terraform process running on the system.
    Example: terraform apply, terraform plan, terraform init.
    """
    try:
        out = subprocess.check_output(["ps", "aux"]).decode().lower()
        return "terraform" in out or "saas" in out
    except Exception:
        return False


def _run_plan_json(working_dir):
    """
    Run terraform plan -json safely.
    """
    try:
        result = subprocess.check_output(
            ["terraform", "plan", "-json"],
            cwd=working_dir,
            stderr=subprocess.STDOUT
        )
        return json.loads(result.decode())
    except Exception as e:
        return {"error": str(e)}


def _extract_plan_issues(plan_json):
    """
    Extract resource changes from plan JSON.
    """
    if not plan_json or "error" in plan_json:
        return []

    issues = []

    for change in plan_json.get("resource_changes", []):
        address = change.get("address")
        actions = change.get("change", {}).get("actions", [])

        if "delete" in actions:
            issues.append({
                "resource": address,
                "action": "delete",
                "type": "saas_delete",
                "message": f"SaaS will delete {address}"
            })

        if "create" in actions:
            issues.append({
                "resource": address,
                "action": "create",
                "type": "saas_create",
                "message": f"SaaS will create {address}"
            })

        if "update" in actions:
            issues.append({
                "resource": address,
                "action": "update",
                "type": "saas_update",
                "message": f"SaaS will update {address}"
            })

    return issues


def audit_saas():
    """
    Full SaaS audit.
    Returns strict + safe structured result.
    """

    cfg = _load_saas_config()

    # CONFIG MISSING
    if cfg is None:
        return {
            "saas_detected": False,
            "status": "CONFIG_MISSING",
            "issues": [],
            "message": "SaaS config missing in Orcaopta config."
        }

    working_dir = cfg.get("working_dir")

    # WORKING DIR MISSING
    if not working_dir or not os.path.isdir(working_dir):
        return {
            "saas_detected": False,
            "status": "DIR_MISSING",
            "working_dir": working_dir,
            "issues": [],
            "message": f"SaaS working directory missing: {working_dir}"
        }

    # TERRAFORM NOT INSTALLED
    if not _terraform_installed():
        return {
            "saas_detected": False,
            "status": "TERRAFORM_NOT_INSTALLED",
            "working_dir": working_dir,
            "issues": [],
            "message": "Terraform binary not found on system."
        }

    # SAAS PROCESS NOT RUNNING
    if not _saas_process_running():
        process_status = "SAAS_PROCESS_NOT_RUNNING"
    else:
        process_status = "SAAS_PROCESS_RUNNING"

    # RUN PLAN
    plan_json = _run_plan_json(working_dir)

    if "error" in plan_json:
        return {
            "saas_detected": True,
            "status": "PLAN_FAILED",
            "working_dir": working_dir,
            "issues": [],
            "message": f"Terraform plan failed: {plan_json['error']}"
        }

    # EXTRACT ISSUES
    issues = _extract_plan_issues(plan_json)

    return {
        "saas_detected": True,
        "status": process_status,
        "working_dir": working_dir,
        "issues": issues,
        "message": "SaaS plan analyzed successfully."
    }
