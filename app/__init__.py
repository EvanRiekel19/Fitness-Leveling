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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'fitness_leveling.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
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
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
