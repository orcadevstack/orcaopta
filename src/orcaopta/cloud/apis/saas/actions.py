import subprocess
from typing import Optional


def _run_tf(args, working_dir: str) -> str:
    """
    Internal helper to run Terraform commands safely.
    """
    try:
        out = subprocess.check_output(
            ["terraform"] + args,
            cwd=working_dir
        ).decode()
        return out.strip()
    except Exception as e:
        return f"ERROR: {e}"


# ---------------------------------------------------------
# Healing Actions
# ---------------------------------------------------------

def fix_drift(working_dir: str) -> str:
    """
    Fix infrastructure drift by running terraform apply.
    """
    return _run_tf(["apply", "-auto-approve"], working_dir)


def recreate_missing_resource(working_dir: str, resource_name: Optional[str] = None) -> str:
    """
    Recreate missing resources detected by ML/RL or audits.
    If no resource_name is provided, Terraform will recreate all missing resources.
    """
    if resource_name:
        return _run_tf(["apply", "-auto-approve", f"-target={resource_name}"], working_dir)
    return _run_tf(["apply", "-auto-approve"], working_dir)


def destroy_resource(working_dir: str, resource_name: str) -> str:
    """
    Destroy a specific Terraform-managed resource.
    """
    return _run_tf(["destroy", "-auto-approve", f"-target={resource_name}"], working_dir)


def scale_infra(working_dir: str, var_name: str, new_value: int) -> str:
    """
    Scale infrastructure by updating a Terraform variable.
    Example: scale_infra("replicas", 5)
    """
    return _run_tf(
        ["apply", "-auto-approve", f"-var={var_name}={new_value}"],
        working_dir
    )


def heal_storage_issue(working_dir: str, issue: dict) -> str:
    """
    Handle storage-related SaaS issues (buckets, volumes, etc.)
    """
    msg = issue.get("message", "").lower()

    if "bucket missing" in msg:
        return recreate_missing_resource(working_dir)

    if "volume missing" in msg:
        return recreate_missing_resource(working_dir)

    if "bucket drift" in msg or "volume drift" in msg:
        return fix_drift(working_dir)

    return "Storage issue noted — no automatic action taken"


def heal_network_issue(working_dir: str, issue: dict) -> str:
    """
    Handle network-related SaaS issues (VPC, subnets, routers).
    """
    msg = issue.get("message", "").lower()

    if "subnet missing" in msg:
        return recreate_missing_resource(working_dir)

    if "router missing" in msg:
        return recreate_missing_resource(working_dir)

    if "network drift" in msg:
        return fix_drift(working_dir)

    return "Network issue noted — no automatic action taken"


def heal_compute_issue(working_dir: str, issue: dict) -> str:
    """
    Handle compute-related SaaS issues (instances, autoscaling groups).
    """
    msg = issue.get("message", "").lower()

    if "instance missing" in msg:
        return recreate_missing_resource(working_dir)

    if "autoscaling drift" in msg:
        return fix_drift(working_dir)

    if "scale up" in msg:
        return scale_infra(working_dir, "replicas", issue.get("desired", 1))

    if "scale down" in msg:
        return scale_infra(working_dir, "replicas", issue.get("desired", 1))

    return "Compute issue noted — no automatic action taken"


# ---------------------------------------------------------
# Unified healing entrypoint
# ---------------------------------------------------------

def heal_saas_issue(working_dir: str, issue: dict) -> str:
    """
    Unified healing entrypoint for SaaS backend.
    ML/RL engine sends an issue dict with type + message.
    """
    issue_type = issue.get("type", "").lower()

    if "storage" in issue_type:
        return heal_storage_issue(working_dir, issue)

    if "network" in issue_type:
        return heal_network_issue(working_dir, issue)

    if "compute" in issue_type:
        return heal_compute_issue(working_dir, issue)

    if "drift" in issue_type:
        return fix_drift(working_dir)

    if "missing" in issue_type:
        return recreate_missing_resource(working_dir)

    if "destroy" in issue_type:
        return destroy_resource(working_dir, issue.get("resource"))

    return "SaaS issue noted — no automatic action taken"
