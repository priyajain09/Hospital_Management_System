"""empty message

Revision ID: b12b5cc2055f
Revises: 67cada913a00
Create Date: 2020-03-28 20:58:57.511181

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b12b5cc2055f'
down_revision = '67cada913a00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctor', sa.Column('date_of_joining', sa.Date(), nullable=True))
    op.add_column('doctor', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.alter_column('doctor', 'consultant_fee',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('doctor', 'contact_number',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.alter_column('doctor', 'username',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.create_index(op.f('ix_doctor_timestamp'), 'doctor', ['timestamp'], unique=False)
    op.alter_column('patient', 'username',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('user', 'role',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'role',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('patient', 'username',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.drop_index(op.f('ix_doctor_timestamp'), table_name='doctor')
    op.alter_column('doctor', 'username',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('doctor', 'contact_number',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('doctor', 'consultant_fee',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.drop_column('doctor', 'timestamp')
    op.drop_column('doctor', 'date_of_joining')
    # ### end Alembic commands ###
