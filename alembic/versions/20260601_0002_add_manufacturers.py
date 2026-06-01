"""add manufacturers table and items.manufacturer_id FK

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manufacturers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
    )
    # batch_alter_table is required for SQLite (it rebuilds the table to add the
    # FK); on MySQL it compiles to a plain ALTER TABLE. Adding a NOT NULL column
    # assumes the items table is empty — true on a fresh `alembic upgrade head`.
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("manufacturer_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_items_manufacturer_id_manufacturers", "manufacturers", ["manufacturer_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_constraint("fk_items_manufacturer_id_manufacturers", type_="foreignkey")
        batch_op.drop_column("manufacturer_id")
    op.drop_table("manufacturers")
