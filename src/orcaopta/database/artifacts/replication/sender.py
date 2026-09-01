import requests

def send_artifact(node_url: str, artifact_path: str):
    with open(artifact_path, "rb") as f:
        data = f.read()

    resp = requests.post(
        f"{node_url}/replicate/artifact",
        files={"artifact": data}
    )

    return resp.status_code == 200
