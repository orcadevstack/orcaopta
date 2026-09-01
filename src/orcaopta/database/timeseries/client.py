from influxdb_client import InfluxDBClient

client = InfluxDBClient(
    url="http://localhost:8086",
    token="orcaopta",
    org="orcaopta"
)
