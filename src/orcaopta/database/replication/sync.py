import requests

def sync_db(node_url, db_path="/app/orcaopta.db"):
    with open(db_path, "rb") as f:
        data = f.read()
    requests.post(f"{node_url}/sync", files={"db": data})
