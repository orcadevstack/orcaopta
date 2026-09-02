#!/usr/bin/env bash
set -e

echo "====================================================="
echo "      ORCAOPTA CLOUD BRAIN — KEY GENERATOR"
echo "====================================================="

# ---------------------------------------------------------
# Helper: generate encrypted data key
# ---------------------------------------------------------
generate_data_key() {
python3 - <<EOF
from cryptography.fernet import Fernet
import os

master = os.getenv("ORCAOPTA_MASTER_KEY")
if not master:
    raise RuntimeError("ORCAOPTA_MASTER_KEY is not set")

master = Fernet(master.encode())
raw = Fernet.generate_key()
print(master.encrypt(raw).decode())
EOF
}

# ---------------------------------------------------------
# Generate master key
# ---------------------------------------------------------
echo "Generating ORCAOPTA_MASTER_KEY..."
export ORCAOPTA_MASTER_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "MASTER KEY: $ORCAOPTA_MASTER_KEY"
echo

# ---------------------------------------------------------
# Generate encrypted data keys
# ---------------------------------------------------------
echo "Generating encrypted data keys..."

export ORCAOPTA_DB_KEY=$(generate_data_key)
export ORCAOPTA_ARTIFACT_KEY=$(generate_data_key)
export ORCAOPTA_CLUSTER_KEY=$(generate_data_key)
export ORCAOPTA_REPLICATION_KEY=$(generate_data_key)
export ORCAOPTA_OTS_KEY=$(generate_data_key)
export ORCAOPTA_VECTOR_KEY=$(generate_data_key)

echo "DB KEY:          $ORCAOPTA_DB_KEY"
echo "ARTIFACT KEY:    $ORCAOPTA_ARTIFACT_KEY"
echo "CLUSTER KEY:     $ORCAOPTA_CLUSTER_KEY"
echo "REPLICATION KEY: $ORCAOPTA_REPLICATION_KEY"
echo "OTS KEY:         $ORCAOPTA_OTS_KEY"
echo "VECTOR KEY:      $ORCAOPTA_VECTOR_KEY"
echo

# ---------------------------------------------------------
# Write to .env
# ---------------------------------------------------------
echo "Writing keys to .env..."

cat > .env <<EOF
ORCAOPTA_MASTER_KEY=$ORCAOPTA_MASTER_KEY
ORCAOPTA_DB_KEY=$ORCAOPTA_DB_KEY
ORCAOPTA_ARTIFACT_KEY=$ORCAOPTA_ARTIFACT_KEY
ORCAOPTA_CLUSTER_KEY=$ORCAOPTA_CLUSTER_KEY
ORCAOPTA_REPLICATION_KEY=$ORCAOPTA_REPLICATION_KEY
ORCAOPTA_OTS_KEY=$ORCAOPTA_OTS_KEY
ORCAOPTA_VECTOR_KEY=$ORCAOPTA_VECTOR_KEY
EOF

echo ".env file created."
echo
echo "====================================================="
echo "   Orcaopta encryption keys generated successfully"
echo "====================================================="
