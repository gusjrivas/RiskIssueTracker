"""soft delete risks and issues

Revision ID: 9dcf00d01c37
Revises: 0001
Create Date: 2026-06-06 21:05:59.621848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9dcf00d01c37'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_risks_deleted_at', 'risks', ['deleted_at'])
    op.add_column('issues', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_issues_deleted_at', 'issues', ['deleted_at'])


def downgrade() -> None:
    op.drop_index('ix_issues_deleted_at', table_name='issues')
    op.drop_column('issues', 'deleted_at')
    op.drop_index('ix_risks_deleted_at', table_name='risks')
    op.drop_column('risks', 'deleted_at')
