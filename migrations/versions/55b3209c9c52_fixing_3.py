"""fixing 3

Revision ID: 55b3209c9c52
Revises: 
Create Date: 2021-02-28 12:28:13.372140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55b3209c9c52'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('caches',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=36), nullable=True),
    sa.Column('uptodate', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_caches_name'), 'caches', ['name'], unique=False)
    op.create_table('manufacturer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('received', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=18), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('stock', sa.String(), nullable=True),
    sa.Column('manufacturer', sa.String(length=64), nullable=True),
    sa.Column('color', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_category'), 'product', ['category'], unique=False)
    op.create_index(op.f('ix_product_manufacturer'), 'product', ['manufacturer'], unique=False)
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('recreate', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_product_manufacturer'), table_name='product')
    op.drop_index(op.f('ix_product_category'), table_name='product')
    op.drop_table('product')
    op.drop_table('manufacturer')
    op.drop_index(op.f('ix_caches_name'), table_name='caches')
    op.drop_table('caches')
    # ### end Alembic commands ###
