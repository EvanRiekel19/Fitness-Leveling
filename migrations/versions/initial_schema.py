"""Initial database schema

Revision ID: initial_schema
Revises: 
Create Date: 2025-03-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This migration doesn't make changes because all tables already exist in the database
    pass


def downgrade():
    # This migration is just to establish a base for future migrations
    pass 