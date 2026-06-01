"""make names unique columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-01 15:49:36.624253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Names are required for SQLite batch mode (autogenerate left them as None).
    # They match the metadata naming convention in app/database.py.
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_items_name', ['name'])

    with op.batch_alter_table('manufacturers', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_manufacturers_name', ['name'])


def downgrade() -> None:
    with op.batch_alter_table('manufacturers', schema=None) as batch_op:
        batch_op.drop_constraint('uq_manufacturers_name', type_='unique')

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_constraint('uq_items_name', type_='unique')
