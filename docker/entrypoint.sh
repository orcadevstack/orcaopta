#!/bin/bash

echo ""
echo "==============================================="
echo "   ORCAOPTA CLOUD BRAIN — AUTO START"
echo "==============================================="
echo ""

# -----------------------------
# Auto-detect environment
# -----------------------------
echo " Orcaopta Auto-Detect Mode Starting..."

if openstack --version >/dev/null 2>&1; then
    export ORCAOPTA_OPENSTACK_AVAILABLE=true
    echo " OpenStack detected"
else
    export ORCAOPTA_OPENSTACK_AVAILABLE=false
    echo " OpenStack NOT detected"
fi

if ceph --version >/dev/null 2>&1; then
    export ORCAOPTA_CEPH_AVAILABLE=true
    echo " Ceph detected"
else
    export ORCAOPTA_CEPH_AVAILABLE=false
    echo " Ceph NOT detected"
fi

if kubectl version --client >/dev/null 2>&1; then
    export ORCAOPTA_K8S_AVAILABLE=true
    echo " Kubernetes detected"
else
    export ORCAOPTA_K8S_AVAILABLE=false
    echo " Kubernetes NOT detected"
fi

if terraform version >/dev/null 2>&1; then
    export ORCAOPTA_TERRAFORM_AVAILABLE=true
    echo " Terraform detected"
else
    export ORCAOPTA_TERRAFORM_AVAILABLE=false
    echo " Terraform NOT detected"
fi

# -----------------------------
# Decide mode
# -----------------------------
if [ "$ORCAOPTA_OPENSTACK_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_CEPH_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_K8S_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_TERRAFORM_AVAILABLE" = true ]; then

    export ORCAOPTA_MODE=cluster
    echo " Running in CLUSTER MODE"

else
    export ORCAOPTA_MODE=standalone
    echo " Running in STANDALONE MODE"
fi

# -----------------------------
# Startup Banner
# -----------------------------
python - << 'EOF'
from datetime import datetime
import os

mode = os.getenv("ORCAOPTA_MODE", "standalone")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"""
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
""")
EOF

# -----------------------------
# Start API + MCP server
# -----------------------------
echo " Starting API on port 8000..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

echo " Starting MCP server..."
python -m src.orcaopta.mcp_server.server
