"""event

Revision ID: 5951e4c7a5d0
Revises: db7ee06710de
Create Date: 2018-04-29 06:33:36.964056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5951e4c7a5d0'
down_revision = 'db7ee06710de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gr', sa.String(length=64), nullable=True),
    sa.Column('ev', sa.String(length=140), nullable=True),
    sa.Column('Participants', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['gr'], ['group.groupname'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event')
    # ### end Alembic commands ###
