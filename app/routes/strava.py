from flask import Blueprint, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from app.services.strava import StravaService
from app import db
from datetime import datetime
import urllib.parse

bp = Blueprint('strava', __name__, url_prefix='/strava')

@bp.route('/connect')
@login_required
def connect():
    """Initiate Strava OAuth flow."""
    try:
        strava_service = StravaService(
            client_id=current_app.config['STRAVA_CLIENT_ID'],
            client_secret=current_app.config['STRAVA_CLIENT_SECRET']
        )
        
        # Use the BASE_URL from config for the redirect URI
        redirect_uri = f"{current_app.config['BASE_URL']}/strava/callback"
        print(f"Redirect URI: {redirect_uri}")
        
        auth_url = strava_service.get_authorization_url(redirect_uri)
        return redirect(auth_url)
    except Exception as e:
        print(f"Error in connect route: {str(e)}")
        flash('Failed to initiate Strava connection. Please try again.', 'error')
        return redirect(url_for('profile.index'))

@bp.route('/disconnect')
@login_required
def disconnect():
    """Disconnect Strava account."""
    current_user.strava_access_token = None
    current_user.strava_refresh_token = None
    current_user.strava_token_expires_at = None
    current_user.strava_last_sync = None
    db.session.commit()
    flash('Successfully disconnected from Strava.', 'success')
    return redirect(url_for('profile.index'))

@bp.route('/callback')
@login_required
def callback():
    """Handle Strava OAuth callback."""
    error = request.args.get('error')
    if error:
        print(f"Error in Strava callback: {error}")
        flash('Failed to connect to Strava. Please try again.', 'error')
        return redirect(url_for('profile.index'))

    code = request.args.get('code')
    scope = request.args.get('scope', '')
    print(f"Received code: {code[:10]}... with scope: {scope}")

    if not code:
        flash('Failed to connect to Strava. Please try again.', 'error')
        return redirect(url_for('profile.index'))
    
    strava_service = StravaService(
        client_id=current_app.config['STRAVA_CLIENT_ID'],
        client_secret=current_app.config['STRAVA_CLIENT_SECRET']
    )
    
    try:
        print("Attempting to exchange code for token...")
        token_response = strava_service.get_access_token(code)
        print(f"Token response received: {token_response.keys()}")
        
        current_user.strava_access_token = token_response['access_token']
        current_user.strava_refresh_token = token_response['refresh_token']
        # Convert Unix timestamp to datetime
        expires_at = datetime.fromtimestamp(token_response['expires_at'])
        current_user.strava_token_expires_at = expires_at
        db.session.commit()
        
        print("Starting activity sync...")
        # Sync activities immediately
        imported_workouts = strava_service.sync_activities(current_user)
        
        flash(f'Successfully connected to Strava! Imported {len(imported_workouts)} workouts.', 'success')
    except Exception as e:
        print(f"Strava connection error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash('Failed to connect to Strava. Please try again.', 'error')
    
    return redirect(url_for('profile.index'))

@bp.route('/sync')
@login_required
def sync():
    """Manually sync activities from Strava."""
    if not current_user.strava_access_token:
        flash('Please connect your Strava account first.', 'error')
        return redirect(url_for('profile.index'))
    
    strava_service = StravaService(
        client_id=current_app.config['STRAVA_CLIENT_ID'],
        client_secret=current_app.config['STRAVA_CLIENT_SECRET']
    )
    
    try:
        imported_workouts = strava_service.sync_activities(current_user)
        flash(f'Successfully imported {len(imported_workouts)} workouts from Strava!', 'success')
    except Exception as e:
        print(f"Error syncing activities: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash('Failed to sync activities from Strava. Please try again.', 'error')
    
    return redirect(url_for('profile.index')) 