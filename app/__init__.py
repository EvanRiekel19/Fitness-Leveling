from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from app.config import Config
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
scheduler = APScheduler()

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
    
    # Register blueprints
    from app.routes import auth, main, workout, profile, strava, friends
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(workout.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(strava.bp)
    app.register_blueprint(friends.bp)
    
    # Set up scheduler
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.init_app(app)
        scheduler.start()
        
        # Import and schedule tasks
        from app.tasks import apply_xp_decay_to_all_users
        scheduler.add_job(
            id='apply_xp_decay',
            func=apply_xp_decay_to_all_users,
            trigger='interval',
            hours=24,  # Run once per day
            next_run_time=None  # Start on next interval
        )
    
    return app
