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

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Set up login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Ensure database tables exist
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            # Ensure required columns exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Check if user table has last_workout_at column
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            if 'last_workout_at' not in user_columns:
                db.session.execute("ALTER TABLE \"user\" ADD COLUMN last_workout_at TIMESTAMP")
            
            # Check if workout table has subtype column
            if inspector.has_table('workout'):
                workout_columns = [col['name'] for col in inspector.get_columns('workout')]
                if 'subtype' not in workout_columns:
                    db.session.execute("ALTER TABLE workout ADD COLUMN subtype VARCHAR(50)")
            
            db.session.commit()
        except Exception as e:
            print(f"Database initialization error (non-fatal): {e}")
            db.session.rollback()
    
    # Register blueprints
    from app.routes import auth, main, workout, profile, strava, friends
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(workout.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(strava.bp)
    app.register_blueprint(friends.bp)
    
    return app
