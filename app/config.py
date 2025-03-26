import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'fitness_leveling.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Strava API Configuration
    STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET') 