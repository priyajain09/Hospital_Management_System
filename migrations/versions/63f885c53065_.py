"""empty message

Revision ID: 63f885c53065
Revises: d5455000d948
Create Date: 2020-07-27 12:59:21.346416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63f885c53065'
down_revision = 'd5455000d948'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_temporary_users_timestamp', table_name='temporary_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_temporary_users_timestamp', 'temporary_users', ['timestamp'], unique=False)
    # ### end Alembic commands ###
