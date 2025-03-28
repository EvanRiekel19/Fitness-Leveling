"""
Script to add all missing columns to the user table
"""

from sqlalchemy import create_engine, text
import os

# Get the DATABASE_URL from environment
database_url = os.environ.get('DATABASE_URL')

# If it starts with postgres://, replace with postgresql://
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if not database_url:
    print("DATABASE_URL not found in environment")
    exit(1)

# Create engine
engine = create_engine(database_url)

# Add all missing columns
with engine.begin() as conn:
    print("Adding missing columns to user table...")
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_workout_at TIMESTAMP'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS xp_decay_rate FLOAT DEFAULT 0.05'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS xp_decay_grace_days INTEGER DEFAULT 3'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar_style VARCHAR(20) DEFAULT \'adventurer\''))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar_seed VARCHAR(50)'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar_background VARCHAR(7) DEFAULT \'#b6e3f4\''))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS strava_access_token VARCHAR(100)'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS strava_refresh_token VARCHAR(100)'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS strava_token_expires_at TIMESTAMP'))
    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS strava_last_sync TIMESTAMP'))
    print("All columns added successfully")

print("Done!") 