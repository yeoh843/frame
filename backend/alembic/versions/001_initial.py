"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.String(), default='free'),
        sa.Column('credits', sa.Integer(), default=10),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('image_urls', postgresql.JSON(), nullable=False),
        sa.Column('aspect_ratios', postgresql.JSON(), default=['9:16', '1:1', '16:9']),
        sa.Column('options', postgresql.JSON(), default={}),
        sa.Column('video_urls', postgresql.JSON()),
        sa.Column('thumbnail_url', sa.String()),
        sa.Column('metadata', postgresql.JSON(), default={}),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table('jobs')
    op.drop_table('users')













