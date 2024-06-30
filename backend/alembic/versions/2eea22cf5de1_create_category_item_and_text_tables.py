"""Create Category, Item and Text tables

Revision ID: 2eea22cf5de1
Revises: 
Create Date: 2024-06-29 18:06:49.768960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

# revision identifiers, used by Alembic.
revision: str = '2eea22cf5de1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Entity sets
    op.create_table(
        "category",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("desc", sa.String(200), nullable=False),
    )

    op.create_table(
        "item",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("desc", sa.String(100)),
    )

    op.create_table(
        "text",
        sa.Column("id", sa.Integer, ForeignKey("item.id"), primary_key=True),
        sa.Column("txt", sa.Text(), nullable=False),
    )

    # Relations
    op.create_table(
        "category_text",
        sa.Column("cat_id", sa.Integer, ForeignKey("category.id"), primary_key=True),
        sa.Column("text_id", sa.Integer, ForeignKey("text.id"), primary_key=True),
    )


def downgrade() -> None:
    pass
