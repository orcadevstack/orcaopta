

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def customize_openapi(app: FastAPI):
    """
    Custom OpenAPI schema for Orcaopta Security API.
    Adds branding, descriptions, and security metadata.
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Orcaopta Security API",
        version="1.0.0",
        description=(
            "Enterprise-grade security scanning API for Orcaopta.\n\n"
            "Includes:\n"
            "- CVE scanning\n"
            "- SBOM correlation\n"
            "- Cloud posture\n"
            "- K8s posture\n"
            "- SaaS posture\n"
            "- Runtime detection\n"
            "- Attack graph generation\n"
        ),
        routes=app.routes,
    )

    # Branding
    openapi_schema["info"]["x-logo"] = {
        "url": "https://orcaopta.example/logo.png",
        "altText": "Orcaopta Security"
    }

    # Tag descriptions
    openapi_schema["tags"] = [
        {"name": "security", "description": "Full security scanning and reporting"},
        {"name": "sbom", "description": "SBOM → CVE correlation"},
        {"name": "attack-graph", "description": "Attack path graph generation"},
        {"name": "auth", "description": "API authentication"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
