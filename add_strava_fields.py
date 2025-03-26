from app import create_app, db
from sqlalchemy import text

def add_strava_fields():
    app = create_app()
    with app.app_context():
        # Add Strava fields to the user table
        with db.engine.connect() as conn:
            # Add each column separately
            conn.execute(text("ALTER TABLE user ADD COLUMN strava_access_token VARCHAR(100)"))
            conn.execute(text("ALTER TABLE user ADD COLUMN strava_refresh_token VARCHAR(100)"))
            conn.execute(text("ALTER TABLE user ADD COLUMN strava_token_expires_at DATETIME"))
            conn.execute(text("ALTER TABLE user ADD COLUMN strava_last_sync DATETIME"))
            conn.commit()

if __name__ == '__main__':
    add_strava_fields()
    print("Successfully added Strava fields to the database.") 