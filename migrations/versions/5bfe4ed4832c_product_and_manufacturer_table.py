"""product and manufacturer table

Revision ID: 5bfe4ed4832c
Revises: 
Create Date: 2021-02-18 14:34:32.011726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bfe4ed4832c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('manufacturer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('stock', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('stock', sa.String(), nullable=True),
    sa.Column('manufacturer', sa.String(), nullable=True),
    sa.Column('color', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_category'), 'product', ['category'], unique=False)
    op.create_index(op.f('ix_product_manufacturer'), 'product', ['manufacturer'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_manufacturer'), table_name='product')
    op.drop_index(op.f('ix_product_category'), table_name='product')
    op.drop_table('product')
    op.drop_table('manufacturer')
    # ### end Alembic commands ###
