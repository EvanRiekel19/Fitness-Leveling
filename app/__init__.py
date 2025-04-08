from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Default config settings
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_123'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///fitness_leveling.db').replace('postgres://', 'postgresql://'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # Update with test config if provided
    if test_config:
        app.config.from_mapping(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Import models for migrations
    from app.models.user import User
    from app.models.workout import Workout
    from app.models.exercise import Exercise
    from app.models.exercise_set import ExerciseSet
    from app.models.challenge import Challenge, ChallengeParticipant
    from app.models.friendship import Friendship
    
    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        # Create tables if they don't exist
        try:
            # Check if the exercise tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'workout' not in tables:
                db.create_all()
            else:
                # Check for new tables that might be missing
                if 'exercise' not in tables:
                    Exercise.__table__.create(db.engine)
                    app.logger.info("Created Exercise table")
                
                if 'exercise_set' not in tables:
                    ExerciseSet.__table__.create(db.engine)
                    app.logger.info("Created ExerciseSet table")
                
                if 'challenge' not in tables:
                    Challenge.__table__.create(db.engine)
                    app.logger.info("Created Challenge table")
                
                if 'challenge_participant' not in tables:
                    ChallengeParticipant.__table__.create(db.engine)
                    app.logger.info("Created ChallengeParticipant table")
                
                # Check if we need to add the subtype column to the workout table
                workout_columns = [c['name'] for c in inspector.get_columns('workout')]
                if 'subtype' not in workout_columns:
                    db.session.execute("ALTER TABLE workout ADD COLUMN subtype VARCHAR(50)")
                    db.session.commit()
                    app.logger.info("Added subtype column to Workout table")
        except Exception as e:
            app.logger.error(f"Error creating tables: {e}")
    
    # Register error handlers
    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        error_traceback = traceback.format_exc()
        print(f"500 Error: {error_traceback}")
        
        # Only return detailed error information in debug mode
        if app.debug:
            return f"""
            <h1>Internal Server Error (500)</h1>
            <h2>The server encountered an error and could not complete your request.</h2>
            <pre>{error_traceback}</pre>
            """, 500
        else:
            return "Internal Server Error", 500
    
    # Register blueprints
    from app.routes import auth, main, workout, profile, friends, challenges
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(workout.bp)
    app.register_blueprint(profile.bp)
    # app.register_blueprint(strava.bp)  # Temporarily disabled
    app.register_blueprint(friends.bp)
    app.register_blueprint(challenges.bp)
    
    return app
