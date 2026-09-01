from .client import client

def query_metric(name):
    query_api = client.query_api()
    return query_api.query(f'from(bucket:"metrics") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "{name}")')
