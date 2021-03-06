"""empty message

Revision ID: e6a26c208b3e
Revises: 72779a864e26
Create Date: 2020-08-06 14:28:33.152014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6a26c208b3e'
down_revision = '72779a864e26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('temporary_role_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('birthdate', sa.Date(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('contact_number', sa.Unicode(length=20), nullable=True),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.Column('gender', sa.String(length=15), nullable=True),
    sa.Column('work_timings', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('doctor_username', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['doctor_username'], ['user.username'], ),
    sa.ForeignKeyConstraint(['username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_temporary_role_users_username'), 'temporary_role_users', ['username'], unique=False)
    op.drop_table('roles')
    op.add_column('user_role', sa.Column('gender', sa.String(length=15), nullable=True))
    op.add_column('user_role', sa.Column('role', sa.String(length=20), nullable=False))
    op.drop_column('user_role', 'gender_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_role', sa.Column('gender_user', sa.VARCHAR(length=15), autoincrement=False, nullable=True))
    op.drop_column('user_role', 'role')
    op.drop_column('user_role', 'gender')
    op.create_table('roles',
    sa.Column('role_name', sa.VARCHAR(length=15), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('role_name', name='roles_pkey')
    )
    op.drop_index(op.f('ix_temporary_role_users_username'), table_name='temporary_role_users')
    op.drop_table('temporary_role_users')
    # ### end Alembic commands ###
