import os
import datetime

def print_banner():
    mode = os.getenv("ORCAOPTA_MODE", "standalone")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    banner = f"""
===========================================================

    ██████╗   ██████╗   ██████╗    ██████╗    ██████╗   ███████╗  ████████╗   ██████╗ 
██╔═══██╗ ██╔═══██╗ ██╔═══██╗  ██╔═══██╗  ██╔══██╗  ██╔════╝  ╚══██╔══╝  ██╔═══██╗
██║   ██║ ██║   ██║ ██║   ██║  ██║   ██║  ██████╔╝  ███████╗     ██║     ██║   ██║
██║   ██║ ██║   ██║ ██║   ██║  ██║   ██║  ██╔══██╗  ██╔═══██╗    ██║     ██║   ██║
╚██████╔╝ ╚██████╔╝ ╚██████╔╝  ╚██████╔╝  ██║  ██║  ███████║    ██║     ╚██████╔╝
 ╚═════╝   ╚═════╝   ╚═════╝    ╚═════╝   ╚═╝  ╚═╝  ╚══════╝    ╚═╝      ╚═════╝ 

                 ORCAOPTA CLOUD BRAIN
-----------------------------------------------------------
 Mode: {mode}
 Started: {now}
===========================================================
"""
    print(banner)

openstack = os.getenv("ORCAOPTA_OPENSTACK_AVAILABLE", "false")
ceph = os.getenv("ORCAOPTA_CEPH_AVAILABLE", "false")
k8s = os.getenv("ORCAOPTA_K8S_AVAILABLE", "false")
terraform = os.getenv("ORCAOPTA_TERRAFORM_AVAILABLE", "false")
