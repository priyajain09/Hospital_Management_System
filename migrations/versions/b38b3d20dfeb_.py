"""empty message

Revision ID: b38b3d20dfeb
Revises: a7f8bce5d8e0
Create Date: 2020-08-14 16:33:16.167617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b38b3d20dfeb'
down_revision = 'a7f8bce5d8e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deleted_doctors', sa.Column('experience', sa.String(), nullable=False))
    op.add_column('deleted_doctors', sa.Column('qualification', sa.String(), nullable=False))
    op.add_column('doctor', sa.Column('address', sa.String(), nullable=True))
    op.add_column('doctor', sa.Column('experience', sa.String(), nullable=False))
    op.add_column('doctor', sa.Column('qualification', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('doctor', 'qualification')
    op.drop_column('doctor', 'experience')
    op.drop_column('doctor', 'address')
    op.drop_column('deleted_doctors', 'qualification')
    op.drop_column('deleted_doctors', 'experience')
    # ### end Alembic commands ###
