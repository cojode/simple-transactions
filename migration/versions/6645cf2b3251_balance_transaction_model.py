"""balance+transaction model

Revision ID: 6645cf2b3251
Revises: 0b67dfae96bf
Create Date: 2024-12-13 18:22:31.029501

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6645cf2b3251"
down_revision: Union[str, None] = "0b67dfae96bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("balance", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "balance")
    # ### end Alembic commands ###
