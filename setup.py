from setuptools import setup, find_packages

setup(
    name="orcaopta",
    version="0.1.0",
    description="Cloud-native SRE automation framework with ML, RL, observability, and intelligent remediation.",
    author="Samuel",
    author_email="orcaprojectstack@gmail.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.14",

    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "pydantic",
        "requests",
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib",
        "stable-baselines3",
        "gymnasium",
        "SQLAlchemy",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-otlp-proto-http",
        "cryptography",
        "ossaudit",
        "hoppr-cop",
        "rich",
        "python-dotenv",
        "typer",
        "orjson",
        "pyyaml",
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
            "pyspark",
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
