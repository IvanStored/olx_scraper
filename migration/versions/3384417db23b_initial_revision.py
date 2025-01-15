"""Initial revision

Revision ID: 3384417db23b
Revises: 
Create Date: 2025-01-15 20:31:11.610453

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3384417db23b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "publication_date", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("title", sa.String(length=70), nullable=False),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column(
            "user_registration", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("business", sa.Boolean(), nullable=False),
        sa.Column("olx_delivery", sa.Boolean(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False),
        sa.Column("user_rating", sa.Float(), nullable=False),
        sa.Column("_image_urls", sa.String(), nullable=False),
        sa.Column("_params", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("ads")
    # ### end Alembic commands ###