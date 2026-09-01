import requests

def replicate_artifact(node_url: str, artifact_path: str):
    with open(artifact_path, "rb") as f:
        data = f.read()

    requests.post(
        f"{node_url}/replicate/artifact",
        files={"artifact": data}
    )
