"""empty message

Revision ID: f7151fd2f78e
Revises: 91c4538ecc67
Create Date: 2020-08-07 13:41:51.891625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7151fd2f78e'
down_revision = '91c4538ecc67'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_temporary_role_users_username', table_name='temporary_role_users')
    op.create_index(op.f('ix_temporary_role_users_username'), 'temporary_role_users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_temporary_role_users_username'), table_name='temporary_role_users')
    op.create_index('ix_temporary_role_users_username', 'temporary_role_users', ['username'], unique=False)
    # ### end Alembic commands ###
