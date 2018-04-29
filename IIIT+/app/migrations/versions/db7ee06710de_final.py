"""final

Revision ID: db7ee06710de
Revises: 
Create Date: 2018-04-29 06:30:44.236921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db7ee06710de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userid', sa.Integer(), nullable=True),
    sa.Column('groupname', sa.String(length=64), nullable=True),
    sa.Column('adminId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['userid'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_groupname'), 'group', ['groupname'], unique=False)
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.String(length=64), nullable=True),
    sa.Column('msg', sa.String(length=700), nullable=True),
    sa.Column('reciever', sa.String(length=64), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['reciever'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_msg'), 'message', ['msg'], unique=False)
    op.create_index(op.f('ix_message_timestamp'), 'message', ['timestamp'], unique=False)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('us', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['us'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_timestamp'), 'comment', ['timestamp'], unique=False)
    op.create_table('ingroup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('myuser', sa.Integer(), nullable=True),
    sa.Column('gp', sa.String(length=64), nullable=True),
    sa.Column('pg', sa.String(length=140), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['gp'], ['group.groupname'], ),
    sa.ForeignKeyConstraint(['myuser'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingroup_time'), 'ingroup', ['time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ingroup_time'), table_name='ingroup')
    op.drop_table('ingroup')
    op.drop_index(op.f('ix_comment_timestamp'), table_name='comment')
    op.drop_table('comment')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_message_timestamp'), table_name='message')
    op.drop_index(op.f('ix_message_msg'), table_name='message')
    op.drop_table('message')
    op.drop_index(op.f('ix_group_groupname'), table_name='group')
    op.drop_table('group')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
