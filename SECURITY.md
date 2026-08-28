# Security Policy

Orcaopta is an autonomous multi‑cloud SRE and healing platform that interacts with critical cloud infrastructure.  
Security is a top priority, and we take all vulnerability reports seriously.

---

## Supported Versions

We provide security updates for the most recent stable releases.

| Version   | Status              |
|---------- |---------------------|
| v0.1.x    | ✔ Supported         |
| v0.0.x    | ✖ Not supported     |
| < v0.0    | ✖ Not supported     |

As the project grows, additional long‑term support (LTS) versions may be introduced.

---

## Reporting a Vulnerability

If you discover a security vulnerability, **do not open a public issue**.

Instead, please report it privately:

**Email:** `security@orcaopta.dev`  
(If you don’t have this email yet, replace with your personal email temporarily.)

When reporting a vulnerability, include:

- A clear description of the issue  
- Steps to reproduce  
- Affected versions  
- Potential impact  
- Any logs, screenshots, or proof‑of‑concept  
- Suggested fixes (optional)

We will acknowledge your report within **48 hours** and provide:

- A confirmation of receipt  
- An initial assessment  
- A timeline for remediation  
- Notification when the fix is released  

---

## Handling of Security Issues

Once a vulnerability is confirmed:

1. The issue is assigned a severity level  
2. A fix is developed privately  
3. A patch release is prepared  
4. Security notes are added to the changelog  
5. The reporter is credited (unless anonymity is requested)

We do **not** disclose vulnerabilities until a fix is available.

---

## Best Practices for Contributors

When contributing to Orcaopta:

- Avoid hard‑coded secrets  
- Use environment variables for credentials  
- Follow secure coding practices  
- Validate all external inputs  
- Avoid unsafe shell execution  
- Ensure cloud actions are idempotent  
- Review PRs for potential security risks  

---

## Responsible Disclosure

We follow a responsible disclosure model.  
Please give us reasonable time to address the issue before making it public.
