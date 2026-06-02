"""add user theme preference

Revision ID: 0001
Revises:
Create Date: 2026-06-01

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "theme",
            sa.String(length=10),
            nullable=False,
            server_default="light",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "theme")
