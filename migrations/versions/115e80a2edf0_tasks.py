"""tasks

Revision ID: 115e80a2edf0
Revises: c1ae693488f1
Create Date: 2021-02-24 17:15:20.610734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '115e80a2edf0'
down_revision = 'c1ae693488f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    # ### end Alembic commands ###
