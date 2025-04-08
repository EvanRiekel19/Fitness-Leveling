import os
import psycopg2
from urllib.parse import urlparse

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    exit(1)

# Parse the database URL
url = urlparse(DATABASE_URL)

try:
    # Connect to the database
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    # Check if column exists
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'exercise_set' 
        AND column_name = 'set_number'
    """)
    
    if not cur.fetchone():
        # Add the column if it doesn't exist
        cur.execute("""
            ALTER TABLE exercise_set 
            ADD COLUMN set_number INTEGER NOT NULL DEFAULT 1
        """)
        conn.commit()
        print("Successfully added set_number column to exercise_set table")
    else:
        print("set_number column already exists in exercise_set table")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error adding set_number column: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close() 