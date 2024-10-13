"""operator base model

Revision ID: 2981df385f6c
Revises: 
Create Date: 2024-10-13 20:54:57.615145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2981df385f6c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('apitask',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('subscriber', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('evalresult',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('expression', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('operatorprecedence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('op_precedence', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('operatorprecedence')
    op.drop_table('evalresult')
    op.drop_table('apitask')
    # ### end Alembic commands ###
