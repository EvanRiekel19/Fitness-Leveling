"""
Script to add last_workout_at column if it doesn't exist
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

# Check if column exists
with engine.connect() as conn:
    result = conn.execute(text("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='user' AND column_name='last_workout_at'
    """))
    
    exists = result.fetchone() is not None
    
    if not exists:
        print("Adding last_workout_at column to user table...")
        conn.execute(text("ALTER TABLE \"user\" ADD COLUMN last_workout_at TIMESTAMP"))
        conn.commit()
        print("Column added successfully")
    else:
        print("last_workout_at column already exists")

print("Done!") 