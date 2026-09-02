from orcaopta.core.config_loader import load_config

# Cloud API backends
from orcaopta.cloud.apis.openstack.api import OpenStackAPI
from orcaopta.cloud.apis.ceph.api import CephAPI
from orcaopta.cloud.apis.k8s.api import K8sAPI
from orcaopta.cloud.apis.minio.api import MinioAPI
from orcaopta.cloud.apis.spark.api import SparkAPI

# Your renamed Terraform backend → SAAS
from orcaopta.cloud.apis.saas.api import SaasAPI


def get_cloud_apis():
    """
    Returns a list of active cloud API backends based on config.
    Each backend implements the unified CloudBackend interface.
    """
    cfg = load_config()
    apis = []

    if cfg.openstack.enabled:
        apis.append(OpenStackAPI())

    if cfg.ceph.enabled:
        apis.append(CephAPI())

    if cfg.k8s.enabled:
        apis.append(K8sAPI())

    if cfg.cloud_storage.enabled:
        apis.append(MinioAPI())

    if cfg.spark.enabled:
        apis.append(SparkAPI())

    # Your renamed Terraform backend
    if cfg.saas.enabled:
        apis.append(SaasAPI())

    return apis
