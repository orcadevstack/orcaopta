
from graphviz import Digraph
from pathlib import Path


def generate_architecture_diagram(output: str = "orcaopta_architecture"):
    """
    Generates a full architecture diagram for Orcaopta.
    Output: orcaopta_architecture.png
    """

    dot = Digraph(comment="Orcaopta Architecture", format="png")

    # Core components
    dot.node("api", "FastAPI API")
    dot.node("trainer", "Trainer (ML/RL)")
    dot.node("mlflow", "MLflow Server")
    dot.node("minio", "MinIO (S3 Storage)")
    dot.node("postgres", "Postgres (MLflow DB)")
    dot.node("redis", "Redis (Queue)")
    dot.node("cloud", "Cloud Stack\n(OpenStack / K8s / Ceph / Terraform)")

    # Relationships
    dot.edges([
        ("api", "mlflow"),
        ("trainer", "mlflow"),
        ("mlflow", "minio"),
        ("mlflow", "postgres"),
        ("api", "redis"),
        ("api", "cloud"),
        ("trainer", "cloud"),
    ])

    # Render
    output_path = Path(output)
    dot.render(str(output_path), cleanup=True)

    return f"{output}.png"
