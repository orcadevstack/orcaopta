import time
import requests

def heartbeat(node_url):
    while True:
        try:
            requests.post(f"{node_url}/heartbeat")
        except:
            pass
        time.sleep(5)
