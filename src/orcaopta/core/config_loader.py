import yaml
from pathlib import Path

from orcaopta.core.config_schema import (
    FullConfig,
    OrcaoptaConfig,
    APIConfig,
    DatabaseConfig,
    ModelsConfig,
    ModelVersionSet,
    DataConfig,
    CloudStorageConfig,
    QueueConfig,
    AIConfig,
    LLMConfig,
    AutoscalingConfig,
    AutoscalingPolicy,
    MLConfig,
    SecurityConfig,
    LoggingConfig,
    TerraformConfig,
    OpenStackConfig,
    K8sConfig,
    SparkConfig,
    TelemetryConfig,
    AttackConfig,
)


def load_config(path: str | Path = "orcaopta.yaml") -> FullConfig:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    return FullConfig(
        orcaopta=OrcaoptaConfig(**cfg["orcaopta"]),
        api=APIConfig(**cfg["api"]),
        database=DatabaseConfig(**cfg["database"]),
        models=ModelsConfig(
            directory=cfg["models"]["directory"],
            core_model=cfg["models"]["core_model"],
            anomaly=ModelVersionSet(**cfg["models"]["anomaly"]),
            forecast=ModelVersionSet(**cfg["models"]["forecast"]),
            resource_opt=ModelVersionSet(**cfg["models"]["resource_opt"]),
            autoscale=ModelVersionSet(**cfg["models"]["autoscale"]),
        ),
        data=DataConfig(**cfg["data"]),
        cloud_storage=CloudStorageConfig(**cfg["cloud_storage"]),
        queue=QueueConfig(**cfg["queue"]),
        ai=AIConfig(llm=LLMConfig(**cfg["ai"]["llm"])),
        autoscaling=AutoscalingConfig(
            enabled=cfg["autoscaling"]["enabled"],
            min_replicas=cfg["autoscaling"]["min_replicas"],
            max_replicas=cfg["autoscaling"]["max_replicas"],
            cooldown_seconds=cfg["autoscaling"]["cooldown_seconds"],
            policy=AutoscalingPolicy(**cfg["autoscaling"]["policy"]),
        ),
        ml=MLConfig(**cfg["ml"]),
        security=SecurityConfig(**cfg["security"]),
        logging=LoggingConfig(**cfg["logging"]),
        terraform=TerraformConfig(**cfg["terraform"]),
        openstack=OpenStackConfig(**cfg["openstack"]),
        k8s=K8sConfig(**cfg["k8s"]),
        spark=SparkConfig(**cfg["spark"]),
        telemetry=TelemetryConfig(**cfg["telemetry"]),
        attack=AttackConfig(**cfg["attack"]),
    )
