"""empty message

Revision ID: e431ecc52f0f
Revises: b12b5cc2055f
Create Date: 2020-04-23 11:18:10.428649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e431ecc52f0f'
down_revision = 'b12b5cc2055f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deleted_doctors',
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender_doctor', sa.String(length=15), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('blood_group', sa.String(length=15), nullable=True),
    sa.Column('contact_number', sa.String(length=15), nullable=False),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.Column('qualification', sa.String(length=100), nullable=False),
    sa.Column('experience', sa.String(length=15), nullable=False),
    sa.Column('specialization', sa.String(length=20), nullable=False),
    sa.Column('consultant_fee', sa.Float(), nullable=True),
    sa.Column('visiting_hours', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('date_of_joining', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('username')
    )
    op.create_index(op.f('ix_deleted_doctors_email'), 'deleted_doctors', ['email'], unique=True)
    op.create_index(op.f('ix_deleted_doctors_timestamp'), 'deleted_doctors', ['timestamp'], unique=False)
    op.create_table('deleted_patients',
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('blood_group', sa.String(length=15), nullable=True),
    sa.Column('contact_number', sa.Unicode(length=20), nullable=True),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.Column('gender_user', sa.String(length=15), nullable=True),
    sa.PrimaryKeyConstraint('username')
    )
    op.create_index(op.f('ix_deleted_patients_email'), 'deleted_patients', ['email'], unique=True)
    op.create_table('is_user_deleted',
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('is_user_deleted')
    op.drop_index(op.f('ix_deleted_patients_email'), table_name='deleted_patients')
    op.drop_table('deleted_patients')
    op.drop_index(op.f('ix_deleted_doctors_timestamp'), table_name='deleted_doctors')
    op.drop_index(op.f('ix_deleted_doctors_email'), table_name='deleted_doctors')
    op.drop_table('deleted_doctors')
    # ### end Alembic commands ###