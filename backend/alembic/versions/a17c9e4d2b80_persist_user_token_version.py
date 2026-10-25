"""Persist user token version for durable logout.

Revision ID: a17c9e4d2b80
Revises: 6d4a8f9b2c31
Create Date: 2026-10-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a17c9e4d2b80"
down_revision: Union[str, None] = "6d4a8f9b2c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "token_version")
