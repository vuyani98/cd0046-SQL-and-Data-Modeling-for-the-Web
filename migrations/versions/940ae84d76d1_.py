"""empty message

Revision ID: 940ae84d76d1
Revises: 2e619ae5087c
Create Date: 2022-08-19 18:49:27.106738

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '940ae84d76d1'
down_revision = '2e619ae5087c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_tim', sa.String(), nullable=True))
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('shows', 'start_tim')
    # ### end Alembic commands ###
