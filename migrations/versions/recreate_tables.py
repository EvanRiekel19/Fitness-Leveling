"""Recreate all tables with correct schema

Revision ID: recreate_tables
Revises: initial_schema
Create Date: 2024-04-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'recreate_tables'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Drop all existing tables
    op.execute('DROP TABLE IF EXISTS "user" CASCADE')
    op.execute('DROP TABLE IF EXISTS workout CASCADE')
    op.execute('DROP TABLE IF EXISTS exercise CASCADE')
    op.execute('DROP TABLE IF EXISTS exercise_set CASCADE')
    op.execute('DROP TABLE IF EXISTS friendship CASCADE')
    op.execute('DROP TABLE IF EXISTS challenge CASCADE')
    op.execute('DROP TABLE IF EXISTS challenge_participant CASCADE')
    op.execute('DROP TABLE IF EXISTS achievement CASCADE')

    # Create user table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_workout_date', sa.DateTime(), nullable=True),
        sa.Column('xp_decay_rate', sa.Float(), nullable=True),
        sa.Column('xp_decay_grace_days', sa.Integer(), nullable=True),
        sa.Column('avatar_style', sa.String(length=20), nullable=True),
        sa.Column('avatar_seed', sa.String(length=50), nullable=True),
        sa.Column('avatar_background', sa.String(length=7), nullable=True),
        sa.Column('strava_access_token', sa.String(length=100), nullable=True),
        sa.Column('strava_refresh_token', sa.String(length=100), nullable=True),
        sa.Column('strava_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('strava_last_sync', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create other tables...
    # (Add other table creation statements here as needed)

def downgrade():
    # Drop all tables
    op.execute('DROP TABLE IF EXISTS "user" CASCADE')
    op.execute('DROP TABLE IF EXISTS workout CASCADE')
    op.execute('DROP TABLE IF EXISTS exercise CASCADE')
    op.execute('DROP TABLE IF EXISTS exercise_set CASCADE')
    op.execute('DROP TABLE IF EXISTS friendship CASCADE')
    op.execute('DROP TABLE IF EXISTS challenge CASCADE')
    op.execute('DROP TABLE IF EXISTS challenge_participant CASCADE')
    op.execute('DROP TABLE IF EXISTS achievement CASCADE') 