from orcaopta.pipeline.log_pipeline import run_log_pipeline

if __name__ == "__main__":
    config_state = {
        "open_ports": 12,
        "num_pools": 8,
        "replication_factor": 3,
    }

    run_log_pipeline(
        kafka_bootstrap="localhost:9092",
        kafka_topic="orcaopta-logs",
        config_state=config_state,
    )
