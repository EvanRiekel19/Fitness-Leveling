import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Fix the old Heroku-style URL before it's used
db_url = os.environ.get("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'fitness_leveling.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Strava API Configuration
    STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET') 
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")