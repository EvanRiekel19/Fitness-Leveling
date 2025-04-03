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

    # Create workout table
    op.create_table('workout',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('subtype', sa.String(length=50), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create exercise table
    op.create_table('exercise',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['workout_id'], ['workout.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create exercise_set table
    op.create_table('exercise_set',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create friendship table
    op.create_table('friendship',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('friend_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['friend_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create challenge table
    op.create_table('challenge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create challenge_participant table
    op.create_table('challenge_participant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenge.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create achievement table
    op.create_table('achievement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

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