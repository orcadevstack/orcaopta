import requests

def get_cluster_nodes():
    try:
        resp = requests.get("http://orcaopta-control-plane/nodes")
        return resp.json()["nodes"]
    except:
        return []
