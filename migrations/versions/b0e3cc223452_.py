"""empty message

Revision ID: b0e3cc223452
Revises: bfbe171e7b2e
Create Date: 2020-04-23 11:56:06.548914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b0e3cc223452'
down_revision = 'bfbe171e7b2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('deleted_doctors', 'visiting_hours')
    op.drop_column('deleted_doctors', 'consultant_fee')
    op.drop_column('deleted_doctors', 'timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deleted_doctors', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('deleted_doctors', sa.Column('consultant_fee', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('deleted_doctors', sa.Column('visiting_hours', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
