import os
import subprocess
import json

# ---------------------------------------------------------
#  OPTIONAL TERRAFORM AUDIT MODULE
#  - Never crashes if Terraform is missing
#  - Never crashes if config is missing
#  - Never crashes if working_dir is wrong
#  - Always returns a safe structure
# ---------------------------------------------------------

def _safe_load_config():
    """
    Load Orcaopta config safely.
    Returns {} if config or terraform section is missing.
    """
    try:
        from orcaopta.config import config
        return config
    except Exception:
        return {}


def _get_terraform_dir():
    """
    Resolve Terraform working directory safely.
    Returns None if not configured or missing.
    """
    cfg = _safe_load_config()

    try:
        return cfg.get("terraform", {}).get("working_dir", None)
    except Exception:
        return None


def _run_terraform_plan(tf_dir):
    """
    Run `terraform plan -json` safely.
    Returns None if terraform is missing or fails.
    """
    if not tf_dir or not os.path.isdir(tf_dir):
        return None

    try:
        result = subprocess.check_output(
            ["terraform", "plan", "-json"],
            cwd=tf_dir,
            stderr=subprocess.STDOUT
        )
        return json.loads(result.decode())
    except Exception:
        return None


def _extract_issues(plan_json):
    """
    Extract meaningful issues from terraform plan JSON.
    Returns a list of issue dictionaries.
    """
    if not plan_json:
        return []

    issues = []

    # Example: detect resource deletions
    for change in plan_json.get("resource_changes", []):
        action = change.get("change", {}).get("actions", [])
        if "delete" in action:
            issues.append({
                "resource": change.get("address"),
                "action": "delete",
                "message": f"Terraform will delete {change.get('address')}"
            })

    # Example: detect resource creations
    for change in plan_json.get("resource_changes", []):
        action = change.get("change", {}).get("actions", [])
        if "create" in action:
            issues.append({
                "resource": change.get("address"),
                "action": "create",
                "message": f"Terraform will create {change.get('address')}"
            })

    return issues


def audit_terraform_plan():
    """
    Main entry point.
    ALWAYS returns a safe dictionary:

    {
        "terraform_detected": bool,
        "working_dir": str or None,
        "issues": list,
        "message": str
    }
    """

    tf_dir = _get_terraform_dir()

    # Terraform not configured
    if not tf_dir:
        return {
            "terraform_detected": False,
            "working_dir": None,
            "issues": [],
            "message": "Terraform not configured in Orcaopta config."
        }

    # Terraform directory missing
    if not os.path.isdir(tf_dir):
        return {
            "terraform_detected": False,
            "working_dir": tf_dir,
            "issues": [],
            "message": f"Terraform directory not found: {tf_dir}"
        }

    # Try running terraform plan
    plan_json = _run_terraform_plan(tf_dir)

    if plan_json is None:
        return {
            "terraform_detected": False,
            "working_dir": tf_dir,
            "issues": [],
            "message": "Terraform plan failed or terraform binary missing."
        }

    # Extract issues
    issues = _extract_issues(plan_json)

    return {
        "terraform_detected": True,
        "working_dir": tf_dir,
        "issues": issues,
        "message": "Terraform plan analyzed successfully."
    }
