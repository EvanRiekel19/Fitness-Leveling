from app import create_app, db
from sqlalchemy import text

def fix_database():
    app = create_app()
    with app.app_context():
        # SQL commands to add missing columns
        sql_commands = """
        DO $$
        BEGIN
            -- Basic user fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'username') THEN
                ALTER TABLE "user" ADD COLUMN username VARCHAR(120);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'email') THEN
                ALTER TABLE "user" ADD COLUMN email VARCHAR(120);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'password_hash') THEN
                ALTER TABLE "user" ADD COLUMN password_hash VARCHAR(255);
            END IF;

            -- Stats and leveling fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'xp') THEN
                ALTER TABLE "user" ADD COLUMN xp INTEGER DEFAULT 0;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'level') THEN
                ALTER TABLE "user" ADD COLUMN level INTEGER DEFAULT 1;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'created_at') THEN
                ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'last_workout_date') THEN
                ALTER TABLE "user" ADD COLUMN last_workout_date TIMESTAMP;
            END IF;

            -- XP decay settings
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'xp_decay_rate') THEN
                ALTER TABLE "user" ADD COLUMN xp_decay_rate FLOAT DEFAULT 0;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'xp_decay_grace_days') THEN
                ALTER TABLE "user" ADD COLUMN xp_decay_grace_days INTEGER DEFAULT 0;
            END IF;

            -- Workout statistics
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'total_workouts') THEN
                ALTER TABLE "user" ADD COLUMN total_workouts INTEGER DEFAULT 0;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'total_distance') THEN
                ALTER TABLE "user" ADD COLUMN total_distance FLOAT DEFAULT 0;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'total_duration') THEN
                ALTER TABLE "user" ADD COLUMN total_duration FLOAT DEFAULT 0;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'total_calories') THEN
                ALTER TABLE "user" ADD COLUMN total_calories FLOAT DEFAULT 0;
            END IF;

            -- Avatar customization
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'avatar_style') THEN
                ALTER TABLE "user" ADD COLUMN avatar_style VARCHAR(100);
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'avatar_seed') THEN
                ALTER TABLE "user" ADD COLUMN avatar_seed VARCHAR(100);
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'avatar_background') THEN
                ALTER TABLE "user" ADD COLUMN avatar_background VARCHAR(100);
            END IF;

            -- Strava integration
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'strava_access_token') THEN
                ALTER TABLE "user" ADD COLUMN strava_access_token TEXT;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'strava_refresh_token') THEN
                ALTER TABLE "user" ADD COLUMN strava_refresh_token TEXT;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'strava_token_expires_at') THEN
                ALTER TABLE "user" ADD COLUMN strava_token_expires_at TIMESTAMP;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'strava_last_sync') THEN
                ALTER TABLE "user" ADD COLUMN strava_last_sync TIMESTAMP;
            END IF;
        END $$;
        """
        
        try:
            # Execute the SQL commands
            db.session.execute(text(sql_commands))
            db.session.commit()
            print("Successfully added missing columns to the database.")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    fix_database() 