import requests

class SaaSScanner:
    """
    Multi-SaaS security scanner for Orcaopta.
    Supports:
    - GitHub security posture
    - GitLab security posture
    - Okta identity posture
    - Slack token exposure
    - CI/CD token scope checks
    """

    def __init__(self, github_token=None, gitlab_token=None, okta_token=None, slack_token=None):
        self.github_token = github_token
        self.gitlab_token = gitlab_token
        self.okta_token = okta_token
        self.slack_token = slack_token

    # -------------------------------------------------------------
    # GitHub scanning
    # -------------------------------------------------------------
    def scan_github(self):
        if not self.github_token:
            return {"issues": [{"id": "GH-NO-TOKEN", "title": "GitHub token missing", "severity": "low", "description": "No GitHub token provided", "source": "saas"}]}

        headers = {"Authorization": f"token {self.github_token}"}
        repos = requests.get("https://api.github.com/user/repos", headers=headers).json()

        issues = []

        for repo in repos:
            name = repo["name"]

            # Branch protection
            bp = requests.get(
                f"https://api.github.com/repos/{repo['owner']['login']}/{name}/branches/main/protection",
                headers=headers
            )

            if bp.status_code != 200:
                issues.append({
                    "id": f"GH-BRANCH-NO-PROTECTION-{name}",
                    "title": "Branch protection missing",
                    "severity": "high",
                    "description": f"Repository {name} has no branch protection on main.",
                    "source": "saas",
                    "metadata": repo
                })

            # Secret scanning enabled?
            if not repo.get("security_and_analysis", {}).get("secret_scanning", {}).get("status") == "enabled":
                issues.append({
                    "id": f"GH-SECRET-SCANNING-{name}",
                    "title": "Secret scanning disabled",
                    "severity": "medium",
                    "description": f"Secret scanning is not enabled for {name}.",
                    "source": "saas",
                    "metadata": repo
                })

        return {"issues": issues}

    # -------------------------------------------------------------
    # GitLab scanning
    # -------------------------------------------------------------
    def scan_gitlab(self):
        if not self.gitlab_token:
            return {"issues": [{"id": "GL-NO-TOKEN", "title": "GitLab token missing", "severity": "low", "description": "No GitLab token provided", "source": "saas"}]}

        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        projects = requests.get("https://gitlab.com/api/v4/projects?membership=true", headers=headers).json()

        issues = []

        for project in projects:
            pid = project["id"]

            # Check pipeline token scope
            variables = requests.get(
                f"https://gitlab.com/api/v4/projects/{pid}/variables",
                headers=headers
            ).json()

            for var in variables:
                if var.get("masked") is False:
                    issues.append({
                        "id": f"GL-UNMASKED-VAR-{pid}",
                        "title": "Unmasked CI/CD variable",
                        "severity": "critical",
                        "description": f"Variable {var['key']} in project {project['name']} is not masked.",
                        "source": "saas",
                        "metadata": var
                    })

        return {"issues": issues}

    # -------------------------------------------------------------
    # Okta scanning
    # -------------------------------------------------------------
    def scan_okta(self):
        if not self.okta_token:
            return {"issues": [{"id": "OKTA-NO-TOKEN", "title": "Okta token missing", "severity": "low", "description": "No Okta token provided", "source": "saas"}]}

        headers = {"Authorization": f"SSWS {self.okta_token}"}
        users = requests.get("https://your-okta-domain.okta.com/api/v1/users", headers=headers).json()

        issues = []

        for user in users:
            profile = user.get("profile", {})
            creds = user.get("credentials", {})

            # MFA check
            if not creds.get("provider", {}).get("type") == "MFA":
                issues.append({
                    "id": f"OKTA-MFA-{user['id']}",
                    "title": "User without MFA",
                    "severity": "high",
                    "description": f"User {profile.get('login')} does not have MFA enabled.",
                    "source": "saas",
                    "metadata": user
                })

        return {"issues": issues}

    # -------------------------------------------------------------
    # Slack scanning (token exposure)
    # -------------------------------------------------------------
    def scan_slack(self):
        if not self.slack_token:
            return {"issues": [{"id": "SLACK-NO-TOKEN", "title": "Slack token missing", "severity": "low", "description": "No Slack token provided", "source": "saas"}]}

        headers = {"Authorization": f"Bearer {self.slack_token}"}
        resp = requests.get("https://slack.com/api/auth.test", headers=headers).json()

        if not resp.get("ok"):
            return {"issues": [{
                "id": "SLACK-TOKEN-INVALID",
                "title": "Invalid Slack token",
                "severity": "critical",
                "description": "Slack token is invalid or expired.",
                "source": "saas",
                "metadata": resp
            }]}

        return {"issues": []}
