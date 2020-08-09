"""empty message

Revision ID: b8a2bf42b347
Revises: b716eff58604
Create Date: 2020-04-26 23:37:37.155614

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b8a2bf42b347'
down_revision = 'b716eff58604'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('upload_medical_records', sa.Column('filename', sa.String(length=50), nullable=False))
    op.alter_column('upload_medical_records', 'File',
               existing_type=postgresql.BYTEA(),
               nullable=False)
    op.alter_column('upload_medical_records', 'date',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('upload_medical_records', 'treat_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('upload_medical_records', 'type_doc',
               existing_type=postgresql.ENUM('Invoice', 'Prescription', 'Report', name='type_enum'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('upload_medical_records', 'type_doc',
               existing_type=postgresql.ENUM('Invoice', 'Prescription', 'Report', name='type_enum'),
               nullable=True)
    op.alter_column('upload_medical_records', 'treat_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('upload_medical_records', 'date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('upload_medical_records', 'File',
               existing_type=postgresql.BYTEA(),
               nullable=True)
    op.drop_column('upload_medical_records', 'filename')
    # ### end Alembic commands ###