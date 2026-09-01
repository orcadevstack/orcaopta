import sys
import os
from logging.config import fileConfig
from alembic import context

# ---------------------------------------------------------
# Resolve project root for BOTH local + docker
# ---------------------------------------------------------

# Path of this file: .../src/orcaopta/database/core/migrations/env.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up to /src/orcaopta/database/core
CORE_DIR = os.path.dirname(CURRENT_DIR)

# Go up to /src/orcaopta/database
DATABASE_DIR = os.path.dirname(CORE_DIR)

# Go up to /src/orcaopta
ORCAOPTA_DIR = os.path.dirname(DATABASE_DIR)

# Go up to /src
SRC_DIR = os.path.dirname(ORCAOPTA_DIR)

# Add /src to PYTHONPATH (local + docker)
sys.path.insert(0, SRC_DIR)

# Docker fallback (if running inside container)
if os.path.exists("/app/src"):
    sys.path.insert(0, "/app/src")

# ---------------------------------------------------------
# Alembic config
# ---------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# SQLAlchemy imports
# ---------------------------------------------------------
from orcaopta.core.base import Base
from orcaopta.database.core.engine import engine
import orcaopta.database.core.models  # REQUIRED for autogenerate

target_metadata = Base.metadata

# ---------------------------------------------------------
# Migration runners
# ---------------------------------------------------------

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
