
set -e

echo "==============================================="
echo "   ORCAOPTA CLOUD BRAIN — AUTO START"
echo "==============================================="


export PYTHONPATH="/app/src"


echo "Running Alembic migrations..."

cd /app/src/orcaopta/database/core

alembic upgrade head || {
    echo "Alembic migration failed!"
    exit 1
}

export ORCAOPTA_OTLP_ENDPOINT=${ORCAOPTA_OTLP_ENDPOINT:-"http://localhost:5000/v1/traces"}
export ORCAOPTA_EXPERIMENT_ID=${ORCAOPTA_EXPERIMENT_ID:-"0"}


detect() {
    if $1 --version >/dev/null 2>&1; then
        echo " $2 detected"
        return 0
    else
        echo " $2 NOT detected"
        return 1
    fi
}

detect openstack "OpenStack" && export ORCAOPTA_OPENSTACK_AVAILABLE=true || export ORCAOPTA_OPENSTACK_AVAILABLE=false
detect ceph "Ceph" && export ORCAOPTA_CEPH_AVAILABLE=true || export ORCAOPTA_CEPH_AVAILABLE=false
detect kubectl "Kubernetes" && export ORCAOPTA_K8S_AVAILABLE=true || export ORCAOPTA_K8S_AVAILABLE=false
detect terraform "Terraform" && export ORCAOPTA_TERRAFORM_AVAILABLE=true || export ORCAOPTA_TERRAFORM_AVAILABLE=false
detect spark-submit "Spark" && export ORCAOPTA_SPARK_AVAILABLE=true || export ORCAOPTA_SPARK_AVAILABLE=false


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


python3 - << 'EOF'
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


echo "Initializing Orcaopta SQL database..."
python3 -c "from orcaopta.database.core.init_db import init_db; init_db()"

echo "Starting Artifact Replication Worker..."
python3 -m orcaopta.database.artifacts.replication.worker &

echo "Building FAISS index if needed..."
python3 - << 'EOF'
from orcaopta.database.vector.embeddings import embed_text
from orcaopta.database.vector.index import add_vectors
import numpy as np

vec = embed_text("bootstrap")
add_vectors(np.vstack([vec]))
EOF

echo "Starting API on port 8000..."
uvicorn orcaopta.api.main:app --host 0.0.0.0 --port 8000 &


echo "Starting MCP server..."
python3 -m orcaopta.mcp.server &


echo "Registering node with control plane..."
python3 - << 'EOF'
from orcaopta.cluster.discovery import register_node
register_node("http://localhost:8000")
EOF

echo "Starting node heartbeat..."
python3 - << 'EOF'
import time
from orcaopta.cluster.discovery import register_node

while True:
    register_node("http://localhost:8000")
    time.sleep(5)
EOF &


if [ "$ORCAOPTA_SPARK_AVAILABLE" = true ]; then
    echo "Starting Spark worker..."
    python3 -m orcaopta.spark.worker &
fi

echo "Starting Orcaopta Dashboard on port 3000..."
cd /app/orcaopta-dashboard
npm run start &


wait
