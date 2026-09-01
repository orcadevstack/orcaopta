from .client import client

def write_metric(name, value):
    write_api = client.write_api()
    write_api.write(
        bucket="metrics",
        record={"measurement": name, "fields": {"value": value}}
    )
