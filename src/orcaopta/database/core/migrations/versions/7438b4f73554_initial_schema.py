"""initial schema

Revision ID: 7438b4f73554
Revises:
Create Date: 2026-09-01 04:37:47.316739
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "7438b4f73554"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Metrics
    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )

    # GPU Usage
    op.create_table(
        "gpu_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("utilization", sa.Float(), nullable=True),
        sa.Column("memory_allocated", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )

    # RL Rewards
    op.create_table(
        "rl_rewards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("episode", sa.Integer(), nullable=False),
        sa.Column("reward", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )

    # Spark Jobs
    op.create_table(
        "spark_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("stages", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )

    # Artifacts
    op.create_table(
        "artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # Node State
    op.create_table(
        "node_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=False),
    )

    # Replication Log
    op.create_table(
        "replication_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_node", sa.String(), nullable=False),
        sa.Column("target_node", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("replication_log")
    op.drop_table("node_state")
    op.drop_table("artifacts")
    op.drop_table("spark_jobs")
    op.drop_table("rl_rewards")
    op.drop_table("gpu_usage")
    op.drop_table("metrics")
