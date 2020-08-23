"""empty message

Revision ID: d3428c53b46b
Revises: d84627383210
Create Date: 2020-08-23 16:43:16.519142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3428c53b46b'
down_revision = 'd84627383210'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('upload_medical_records', sa.Column('username', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('upload_medical_records', 'username')
    # ### end Alembic commands ###