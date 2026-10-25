"""Add normalized prescription and RAG metadata, and exact lab numerics.

Revision ID: 6d4a8f9b2c31
Revises: e912bba8f6d2
Create Date: 2026-10-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "6d4a8f9b2c31"
down_revision: Union[str, None] = "e912bba8f6d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ocr_results") as batch_op:
        batch_op.alter_column(
            "extracted_text",
            existing_type=sa.Text(),
            type_=sa.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"),
            existing_nullable=False,
        )

    with op.batch_alter_table("laboratory_values") as batch_op:
        batch_op.alter_column(
            "numeric_value",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=20, scale=8),
            existing_nullable=True,
        )

    op.create_table(
        "prescription_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("prescriber", sa.String(length=255), nullable=True),
        sa.Column("prescription_date", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", name="uq_prescription_records_document_id"),
    )
    with op.batch_alter_table("prescription_items") as batch_op:
        batch_op.add_column(sa.Column("prescription_id", sa.String(length=36), nullable=True))
        batch_op.create_index(
            "ix_prescription_items_prescription_id",
            ["prescription_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_prescription_items_prescription_id",
            "prescription_records",
            ["prescription_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.create_table(
        "rag_document_metadata",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reference_document_id", sa.String(length=36), nullable=False),
        sa.Column("retrieval_backend", sa.String(length=50), nullable=False),
        sa.Column("vector_index_key", sa.String(length=255), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("index_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["reference_document_id"],
            ["reference_documents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_document_id"),
    )


def downgrade() -> None:
    op.drop_table("rag_document_metadata")
    with op.batch_alter_table("prescription_items") as batch_op:
        batch_op.drop_constraint("fk_prescription_items_prescription_id", type_="foreignkey")
        batch_op.drop_index("ix_prescription_items_prescription_id")
        batch_op.drop_column("prescription_id")
    op.drop_table("prescription_records")
    with op.batch_alter_table("laboratory_values") as batch_op:
        batch_op.alter_column(
            "numeric_value",
            existing_type=sa.Numeric(precision=20, scale=8),
            type_=sa.Float(),
            existing_nullable=True,
        )
    with op.batch_alter_table("ocr_results") as batch_op:
        batch_op.alter_column(
            "extracted_text",
            existing_type=sa.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"),
            type_=sa.Text(),
            existing_nullable=False,
        )
