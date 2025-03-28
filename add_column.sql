-- Add the last_workout_at column if it doesn't exist
DO $$
BEGIN
    BEGIN
        -- Try to add the column
        ALTER TABLE "user" ADD COLUMN last_workout_at TIMESTAMP;
    EXCEPTION
        -- If column already exists, do nothing
        WHEN duplicate_column THEN
            RAISE NOTICE 'Column last_workout_at already exists in user table.';
    END;

    -- Add the subtype column to the workout table if it doesn't exist
    BEGIN
        ALTER TABLE workout ADD COLUMN subtype VARCHAR(50);
    EXCEPTION
        WHEN duplicate_column THEN
            RAISE NOTICE 'Column subtype already exists in workout table.';
    END;
END $$; 