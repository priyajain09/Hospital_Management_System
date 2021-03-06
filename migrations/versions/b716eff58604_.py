"""empty message

Revision ID: b716eff58604
Revises: 1b94af8c1f99
Create Date: 2020-04-25 20:20:39.623658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b716eff58604'
down_revision = '1b94af8c1f99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('upload_medical_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('treat_id', sa.Integer(), nullable=True),
    sa.Column('type_doc', sa.Enum('Invoice', 'Prescription', 'Report', name='type_enum'), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('File', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('upload_medical_records')
    # ### end Alembic commands ###
