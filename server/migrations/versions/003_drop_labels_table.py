"""drop legacy labels table

Revision ID: 003_drop_labels_table
Revises: 002_richer_videos
Create Date: 2026-06-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "003_drop_labels_table"
down_revision: Union[str, Sequence[str], None] = "002_richer_videos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "labels" in inspector.get_table_names():
        op.drop_table("labels")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "labels" not in inspector.get_table_names():
        op.create_table(
            "labels",
            sa.Column("pk", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("start_time", sa.Float(), nullable=False),
            sa.Column("label", sa.Integer(), nullable=False),
            sa.Column("video_fk", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(["video_fk"], ["videos.pk"]),
            sa.PrimaryKeyConstraint("pk"),
        )
