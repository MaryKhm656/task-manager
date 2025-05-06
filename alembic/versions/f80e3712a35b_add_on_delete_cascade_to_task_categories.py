"""Add ON DELETE CASCADE to task_categories

Revision ID: f80e3712a35b
Revises: 49f80c164eac
Create Date: 2025-04-23 21:36:56.341571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f80e3712a35b'
down_revision: Union[str, None] = '49f80c164eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('task_categories')

    op.create_table(
        'task_categories',
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    )


def downgrade() -> None:
    op.drop_table('task_categories')
    op.create_table(
        'task_categories',
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id')),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'))
    )
