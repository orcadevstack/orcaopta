from setuptools import setup, find_packages

setup(
    name="orcaopta",
    version="0.1.0",
    description="Cloud-native SRE automation framework with ML, MCP, observability, operator tooling, and intelligent remediation.",
    author="Samuel",
    author_email="orcaprojectstack@gmail.com",
    license="MIT",

    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.13.5",

    install_requires=[
        ##############################
        # ORCAOPTA CORE
        ##############################
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "pydantic",
        "requests",
        "SQLAlchemy",
        "cryptography",
        "ossaudit",
        "rich",
        "python-dotenv",
        "typer",
        "orjson",
        "pyyaml",
        "click",

        ##############################
        # OBSERVABILITY
        ##############################
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-otlp-proto-http",

        ##############################
        # DATA + ML / MCP
        ##############################
        "pandas",
        "numpy",
        "torch",
        "transformers",
        "scikit-learn",
        "joblib",

        ##############################
        # SPARK SUBSYSTEM
        ##############################
        "pyspark",

        ##############################
        # CLOUD SCANNERS
        ##############################
        "boto3",
        "google-auth",
        "google-cloud-storage",
        "google-cloud-compute",
        "azure-identity",
        "azure-mgmt-storage",
        "azure-mgmt-network",
        "openstacksdk",

        ##############################
        # SAAS SCANNERS
        ##############################
        "requests",

        ##############################
        # CVE / VULNERABILITY PIPELINE
        ##############################
        "cve-bin-tool",
        "nvdlib",
        "vulners",

        ##############################
        # SBOM PROCESSING
        ##############################
        "cyclonedx-python-lib",
        "spdx-tools",

        ##############################
        # ATTACK PATH GRAPHING
        ##############################
        "networkx",
        "graphviz",
        "pygraphviz",

        ##############################
        # YAML / JSON SECURITY
        ##############################
        "jsonschema",
        "ruamel.yaml",

        ##############################
        # CONTAINER / K8S
        ##############################
        "docker",
        "kubernetes",

        ##############################
        # Threat Intel / Blockchain
        ##############################
        "attackcti",
        "stix2",
        "taxii2-client",
        "web3"
    ],

    extras_require={
        "dashboard": [
            "matplotlib>=3.11",
            "seaborn",
            "plotly",
            "pyvis",
            "networkx",
            "streamlit"
        ],
        "cloud": [
            "openstacksdk",
            "kubernetes",
            "python-hcl2"
        ],
        "spark": [
            "py4j",
            "kafka-python"
        ],
        "explain": [
            "shap"
        ],
        "mlflow-legacy": [
            "mlflow",
            "protobuf",
            "sqlalchemy",
            "alembic"
        ],
        "notebooks": [
            "jupyter",
            "notebook",
            "jupyterlab",
            "ipython",
            "ipykernel",
            "pyzmq",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "plotly",
            "networkx",
            "pyvis",
            "scikit-learn",
            "joblib"
        ],
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy",
            "pre-commit"
        ]
    },

    include_package_data=True,
)
