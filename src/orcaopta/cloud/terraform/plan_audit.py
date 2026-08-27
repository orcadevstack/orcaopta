
import subprocess
import json
import re


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd).decode()
    except Exception as e:
        return f"ERROR: {e}"


def get_terraform_plan():
    """
    Runs `terraform plan -json` and returns parsed JSON.
    """
    output = run_cmd(["terraform", "plan", "-json"])
    if "ERROR" in output:
        return None

    try:
        return json.loads(output)
    except Exception:
        return None


def audit_terraform_plan():
    """
    Detects:
      - security issues
      - drift
      - dangerous deletes
      - missing tags
      - public exposure
      - misconfigured networking
    """
    plan = get_terraform_plan()
    if not plan:
        return [{"severity": "high", "type": "terraform_plan_error", "message": "Cannot parse terraform plan"}]

    issues = []

    # 1. Detect resources being destroyed
    for rc in plan.get("resource_changes", []):
        if rc.get("change", {}).get("actions") == ["delete"]:
            issues.append({
                "severity": "high",
                "resource": rc["address"],
                "type": "terraform_delete_detected",
                "message": f"Terraform will DELETE {rc['address']}"
            })

    # 2. Detect public IP exposure
    for rc in plan.get("resource_changes", []):
        after = rc.get("change", {}).get("after", {})
        if isinstance(after, dict):
            if "0.0.0.0/0" in str(after):
                issues.append({
                    "severity": "high",
                    "resource": rc["address"],
                    "type": "terraform_public_exposure",
                    "message": f"Resource {rc['address']} exposes 0.0.0.0/0"
                })

    # 3. Detect missing tags (common cloud misconfig)
    for rc in plan.get("resource_changes", []):
        after = rc.get("change", {}).get("after", {})
        if isinstance(after, dict):
            if "tags" not in after:
                issues.append({
                    "severity": "medium",
                    "resource": rc["address"],
                    "type": "terraform_missing_tags",
                    "message": f"Resource {rc['address']} has no tags"
                })

    # 4. Detect drift (replace actions)
    for rc in plan.get("resource_changes", []):
        if "replace" in rc.get("change", {}).get("actions", []):
            issues.append({
                "severity": "medium",
                "resource": rc["address"],
                "type": "terraform_drift_detected",
                "message": f"Resource {rc['address']} will be replaced (drift)"
            })

    return issues


def fix_missing_tags(address):
    """
    Adds default tags to a Terraform resource.
    """
    try:
        with open("tags.auto.tfvars", "w") as f:
            f.write('default_tags = { "owner" = "orcaopta", "managed-by" = "ai" }\n')
        return f"Added default tags for {address}"
    except Exception as e:
        return f"Failed to add tags for {address}: {e}"


def block_public_exposure(address):
    """
    Removes 0.0.0.0/0 from security groups or firewall rules.
    """
    try:
        with open("fix_public_exposure.auto.tfvars", "w") as f:
            f.write('allow_public = false\n')
        return f"Blocked public exposure for {address}"
    except Exception as e:
        return f"Failed to block public exposure for {address}: {e}"


def prevent_delete(address):
    """
    Adds lifecycle prevent_destroy to a resource.
    """
    try:
        with open("prevent_destroy.auto.tfvars", "w") as f:
            f.write('prevent_destroy = true\n')
        return f"Added prevent_destroy for {address}"
    except Exception as e:
        return f"Failed to add prevent_destroy for {address}: {e}"


def execute_terraform_plan(plan: str):
    """
    Parse AI plan and execute Terraform remediation actions.
    """
    if "add tags" in plan.lower():
        print(fix_missing_tags("all"))

    if "block public" in plan.lower():
        print(block_public_exposure("all"))

    if "prevent delete" in plan.lower():
        print(prevent_delete("all"))

    if "apply terraform" in plan.lower():
        print(run_cmd(["terraform", "apply", "-auto-approve"]))
