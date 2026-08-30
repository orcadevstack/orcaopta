#!/bin/bash
set -e

echo ""
echo "==============================================="
echo "   ORCAOPTA CLOUD BRAIN — AUTO START"
echo "==============================================="
echo ""

echo " Orcaopta Auto-Detect Mode Starting..."

# ---------------------------------------------------------
# Ensure required directories exist
# ---------------------------------------------------------
mkdir -p /app/data/tracking
mkdir -p /app/data/artifacts
mkdir -p /app/models

# ---------------------------------------------------------
# Load tracing config (Python handles OTLP setup)
# ---------------------------------------------------------
export ORCAOPTA_OTLP_ENDPOINT=${ORCAOPTA_OTLP_ENDPOINT:-"http://localhost:5000/v1/traces"}
export ORCAOPTA_EXPERIMENT_ID=${ORCAOPTA_EXPERIMENT_ID:-"0"}

# ---------------------------------------------------------
# Detect Cloud Components
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Detect Spark (Optional Plugin)
# ---------------------------------------------------------
if spark-submit --version >/dev/null 2>&1; then
    export ORCAOPTA_SPARK_AVAILABLE=true
    echo " Spark detected"
else
    export ORCAOPTA_SPARK_AVAILABLE=false
    echo " Spark NOT detected"
fi

# ---------------------------------------------------------
# Decide Mode
# ---------------------------------------------------------
if [ "$ORCAOPTA_OPENSTACK_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_CEPH_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_K8S_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_TERRAFORM_AVAILABLE" = true ] || \
   [ "$ORCAOPTA_SPARK_AVAILABLE" = true ]; then

    export ORCAOPTA_MODE=cluster
    echo " Running in CLUSTER MODE"

else
    export ORCAOPTA_MODE=standalone
    echo " Running in STANDALONE MODE"
fi

# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------
python - << 'EOF'
from datetime import datetime
import os

mode = os.getenv("ORCAOPTA_MODE", "standalone")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"""
===========================================================
                 ORCAOPTA CLOUD BRAIN
-----------------------------------------------------------
 Mode: {mode}
 Started: {now}
===========================================================
""")
EOF

# ---------------------------------------------------------
# Start API
# ---------------------------------------------------------
echo " Starting API on port 8000..."
uvicorn orcaopta.api.main:app --host 0.0.0.0 --port 8000 &

# ---------------------------------------------------------
# Start MCP Server
# ---------------------------------------------------------
echo " Starting MCP server..."
python -m orcaopta.mcp.server &

# ---------------------------------------------------------
# Start Spark (Optional)
# ---------------------------------------------------------
if [ "$ORCAOPTA_SPARK_AVAILABLE" = true ]; then
    echo " Starting Spark worker..."
    python -m orcaopta.spark.worker &
fi

wait
