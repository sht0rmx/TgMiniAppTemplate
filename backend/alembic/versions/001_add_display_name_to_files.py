"""Add display_name column to storage_files table

Revision ID: 001_add_display_name
Revises: 
Create Date: 2026-04-09 00:00:00.000000

"""
from __future__ import with_statement

from alembic import op
import sqlalchemy as sa

revision = '001_add_display_name'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('storage_files', sa.Column('display_name', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('storage_files', 'display_name')
