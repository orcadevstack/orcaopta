from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OrcaoptaConfig:
    name: str
    version: str
    environment: str
    mode: str


@dataclass
class APIConfig:
    host: str
    port: int
    log_level: str


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class ModelVersionSet:
    default: str
    versions: List[str]


@dataclass
class ModelsConfig:
    directory: str
    core_model: str
    anomaly: ModelVersionSet
    forecast: ModelVersionSet
    resource_opt: ModelVersionSet
    autoscale: ModelVersionSet


@dataclass
class DataConfig:
    directory: str


@dataclass
class CloudStorageConfig:
    enabled: bool
    endpoint: str
    bucket: str
    access_key: str
    secret_key: str


@dataclass
class QueueConfig:
    backend: str
    redis_url: str


@dataclass
class LLMConfig:
    provider: str
    model: str
    endpoint: str


@dataclass
class AIConfig:
    llm: LLMConfig


@dataclass
class AutoscalingPolicy:
    gpu_utilization_scale_up_threshold: int
    gpu_utilization_scale_down_threshold: int
    ml_autoscale_scale_up_threshold: float
    ml_autoscale_scale_down_threshold: float
    hysteresis_margin: float


@dataclass
class AutoscalingConfig:
    enabled: bool
    min_replicas: int
    max_replicas: int
    cooldown_seconds: int
    policy: AutoscalingPolicy


@dataclass
class MLConfig:
    autoscale: str


@dataclass
class SecurityConfig:
    encryption_key: str
    allow_public_api: bool


@dataclass
class LoggingConfig:
    level: str
    file: str


@dataclass
class TerraformConfig:
    enabled: bool
    working_dir: str


@dataclass
class OpenStackConfig:
    enabled: bool
    group_name: str


@dataclass
class K8sConfig:
    enabled: bool
    namespace: str
    deployment: str


@dataclass
class SparkConfig:
    enabled: bool


@dataclass
class TelemetryConfig:
    enabled: bool


@dataclass
class AttackConfig:
    enabled: bool


@dataclass
class FullConfig:
    orcaopta: OrcaoptaConfig
    api: APIConfig
    database: DatabaseConfig
    models: ModelsConfig
    data: DataConfig
    cloud_storage: CloudStorageConfig
    queue: QueueConfig
    ai: AIConfig
    autoscaling: AutoscalingConfig
    ml: MLConfig
    security: SecurityConfig
    logging: LoggingConfig
    terraform: TerraformConfig
    openstack: OpenStackConfig
    k8s: K8sConfig
    spark: SparkConfig
    telemetry: TelemetryConfig
    attack: AttackConfig
