"""empty message

Revision ID: 72779a864e26
Revises: 3e507a43fcd8
Create Date: 2020-08-06 07:31:04.195901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72779a864e26'
down_revision = '3e507a43fcd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('past_user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('doctor_username', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('birthdate', sa.Date(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('contact_number', sa.Unicode(length=20), nullable=True),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.Column('gender_user', sa.String(length=15), nullable=True),
    sa.Column('work_timings', sa.String(length=50), nullable=True),
    sa.Column('date_of_joining', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('role_name', sa.String(length=15), nullable=False),
    sa.PrimaryKeyConstraint('role_name')
    )
    op.create_table('user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('birthdate', sa.Date(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('contact_number', sa.Unicode(length=20), nullable=True),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.Column('gender_user', sa.String(length=15), nullable=True),
    sa.Column('work_timings', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('doctor_username', sa.String(length=64), nullable=True),
    sa.Column('date_of_joining', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_username'], ['user.username'], ),
    sa.ForeignKeyConstraint(['username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_role_username'), 'user_role', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_role_username'), table_name='user_role')
    op.drop_table('user_role')
    op.drop_table('roles')
    op.drop_table('past_user_role')
    # ### end Alembic commands ###