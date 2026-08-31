import boto3
import google.auth
from google.cloud import storage as gcp_storage
from google.cloud import compute_v1
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient


class CloudScanner:
    """
    Multi-cloud misconfiguration scanner for AWS, GCP, Azure.
    All checks run locally using cloud SDKs.
    """

    # -------------------------------------------------------------
    # INIT
    # -------------------------------------------------------------
    def __init__(self):
        # AWS
        self.aws_iam = boto3.client("iam")
        self.aws_s3 = boto3.client("s3")
        self.aws_ec2 = boto3.client("ec2")

        # GCP
        try:
            self.gcp_credentials, self.gcp_project = google.auth.default()
            self.gcp_storage = gcp_storage.Client()
            self.gcp_compute = compute_v1.FirewallsClient()
        except Exception:
            self.gcp_credentials = None

        # Azure
        try:
            self.az_cred = DefaultAzureCredential()
            self.az_storage = StorageManagementClient(self.az_cred, "<AZURE_SUBSCRIPTION_ID>")
            self.az_network = NetworkManagementClient(self.az_cred, "<AZURE_SUBSCRIPTION_ID>")
        except Exception:
            self.az_cred = None

    # -------------------------------------------------------------
    # MAIN ENTRY POINT
    # -------------------------------------------------------------
    def scan_all(self):
        issues = []
        issues += self.scan_aws()
        issues += self.scan_gcp()
        issues += self.scan_azure()
        return {"issues": issues}

    # -------------------------------------------------------------
    # AWS SCANNING
    # -------------------------------------------------------------
    def scan_aws(self):
        return (
            self.check_aws_iam() +
            self.check_aws_s3() +
            self.check_aws_ec2() +
            self.check_aws_cloudtrail() +
            self.check_aws_guardduty()
        )

    def check_aws_iam(self):
        issues = []
        users = self.aws_iam.list_users().get("Users", [])

        for user in users:
            mfa = self.aws_iam.list_mfa_devices(UserName=user["UserName"])
            if len(mfa.get("MFADevices", [])) == 0:
                issues.append({
                    "id": f"AWS-IAM-MFA-{user['UserName']}",
                    "title": "IAM user without MFA",
                    "severity": "high",
                    "description": f"User {user['UserName']} has no MFA device.",
                    "source": "cloud",
                    "metadata": user
                })

        return issues

    def check_aws_s3(self):
        issues = []
        buckets = self.aws_s3.list_buckets().get("Buckets", [])

        for bucket in buckets:
            name = bucket["Name"]
            acl = self.aws_s3.get_bucket_acl(Bucket=name)
            grants = acl.get("Grants", [])

            for grant in grants:
                grantee = grant.get("Grantee", {})
                if grantee.get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers":
                    issues.append({
                        "id": f"AWS-S3-PUBLIC-{name}",
                        "title": "Public S3 bucket",
                        "severity": "critical",
                        "description": f"Bucket {name} is publicly accessible.",
                        "source": "cloud",
                        "metadata": grant
                    })

        return issues

    def check_aws_ec2(self):
        issues = []
        groups = self.aws_ec2.describe_security_groups().get("SecurityGroups", [])

        for sg in groups:
            for rule in sg.get("IpPermissions", []):
                for ip_range in rule.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        issues.append({
                            "id": f"AWS-EC2-SG-OPEN-{sg['GroupId']}",
                            "title": "Open security group",
                            "severity": "high",
                            "description": f"Security group {sg['GroupId']} allows 0.0.0.0/0.",
                            "source": "cloud",
                            "metadata": sg
                        })

        return issues

    def check_aws_cloudtrail(self):
        issues = []
        ct = boto3.client("cloudtrail")
        trails = ct.describe_trails().get("trailList", [])

        for trail in trails:
            if not trail.get("LogFileValidationEnabled"):
                issues.append({
                    "id": f"AWS-CT-NOVALIDATION-{trail['Name']}",
                    "title": "CloudTrail log validation disabled",
                    "severity": "medium",
                    "description": f"CloudTrail {trail['Name']} does not validate logs.",
                    "source": "cloud",
                    "metadata": trail
                })

        return issues

    def check_aws_guardduty(self):
        issues = []
        gd = boto3.client("guardduty")
        detectors = gd.list_detectors().get("DetectorIds", [])

        if not detectors:
            issues.append({
                "id": "AWS-GD-DISABLED",
                "title": "GuardDuty disabled",
                "severity": "high",
                "description": "AWS GuardDuty is not enabled.",
                "source": "cloud",
                "metadata": {}
            })

        return issues

    # -------------------------------------------------------------
    # GCP SCANNING
    # -------------------------------------------------------------
    def scan_gcp(self):
        if not self.gcp_credentials:
            return []

        return (
            self.check_gcp_storage() +
            self.check_gcp_firewall()
        )

    def check_gcp_storage(self):
        issues = []
        buckets = self.gcp_storage.list_buckets()

        for bucket in buckets:
            policy = bucket.get_iam_policy()
            for binding in policy.bindings:
                if "allUsers" in binding.get("members", []):
                    issues.append({
                        "id": f"GCP-STORAGE-PUBLIC-{bucket.name}",
                        "title": "Public GCP bucket",
                        "severity": "critical",
                        "description": f"GCP bucket {bucket.name} is publicly accessible.",
                        "source": "cloud",
                        "metadata": binding
                    })

        return issues

    def check_gcp_firewall(self):
        issues = []
        firewalls = self.gcp_compute.list(project=self.gcp_project)

        for fw in firewalls:
            for rule in fw.allowed:
                for ip in fw.source_ranges:
                    if ip == "0.0.0.0/0":
                        issues.append({
                            "id": f"GCP-FW-OPEN-{fw.name}",
                            "title": "Open GCP firewall rule",
                            "severity": "high",
                            "description": f"Firewall {fw.name} allows 0.0.0.0/0.",
                            "source": "cloud",
                            "metadata": fw
                        })

        return issues

    # -------------------------------------------------------------
    # AZURE SCANNING
    # -------------------------------------------------------------
    def scan_azure(self):
        if not self.az_cred:
            return []

        return (
            self.check_azure_storage() +
            self.check_azure_nsg()
        )

    def check_azure_storage(self):
        issues = []
        accounts = self.az_storage.storage_accounts.list()

        for acc in accounts:
            if acc.allow_blob_public_access:
                issues.append({
                    "id": f"AZ-STORAGE-PUBLIC-{acc.name}",
                    "title": "Public Azure storage account",
                    "severity": "critical",
                    "description": f"Azure storage {acc.name} allows public blob access.",
                    "source": "cloud",
                    "metadata": acc.as_dict()
                })

        return issues

    def check_azure_nsg(self):
        issues = []
        nsgs = self.az_network.network_security_groups.list_all()

        for nsg in nsgs:
            for rule in nsg.security_rules:
                if rule.source_address_prefix == "0.0.0.0/0":
                    issues.append({
                        "id": f"AZ-NSG-OPEN-{nsg.name}",
                        "title": "Open Azure NSG rule",
                        "severity": "high",
                        "description": f"NSG {nsg.name} allows 0.0.0.0/0.",
                        "source": "cloud",
                        "metadata": rule.as_dict()
                    })

        return issues
