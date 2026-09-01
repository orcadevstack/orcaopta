
from orcaopta.database.artifacts.storage.ceph import CephStorage

def replicate_ceph_multisite(src_object: str, sites: list[dict]):
    """
    sites: [
      {"cluster_conf": "/etc/ceph/ceph-eu.conf", "pool": "artifacts", "cluster_name": "ceph-eu"},
      {"cluster_conf": "/etc/ceph/ceph-us.conf", "pool": "artifacts", "cluster_name": "ceph-us"},
    ]
    """
    # read from primary (assume local ceph)
    primary = CephStorage()
    data = primary.load(src_object)

    for site in sites:
        target = CephStorage(
            cluster_conf=site["cluster_conf"],
            pool=site["pool"],
            cluster_name=site.get("cluster_name", "ceph"),
        )
        target.ioctx.write(src_object, data)
