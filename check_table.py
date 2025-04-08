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
    
    # Get table structure
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'exercise_set'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    print("\nExercise Set Table Structure:")
    print("----------------------------")
    for col in columns:
        print(f"Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}, Default: {col[3]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error checking table structure: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close() 