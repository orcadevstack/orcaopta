
from openstack import connection


def get_conn():
    """
    Central OpenStack connection factory.
    Replace hard-coded values with env vars or config later.
    """
    return connection.Connection(
        auth_url="https://your-keystone:5000/v3",
        project_name="admin",
        username="admin",
        password="secret",
        region_name="RegionOne",
        user_domain_name="Default",
        project_domain_name="Default",
    )
