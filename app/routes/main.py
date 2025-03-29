from flask import Blueprint, render_template, flash, jsonify
from flask_login import login_required, current_user
from app.models.workout import Workout
from datetime import datetime, timedelta
from app import db
from sqlalchemy import inspect
from flask import current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('main/landing.html')
    
    # Check and apply XP decay
    xp_to_lose, days_until_decay = current_user.calculate_xp_decay()
    if xp_to_lose > 0:
        xp_lost = current_user.apply_xp_decay()
        if xp_lost > 0:
            flash(f'You lost {xp_lost} XP due to inactivity! Work out to stop losing XP.', 'error')
            db.session.commit()
    
    # Get recent workouts
    recent_workouts = Workout.query.filter_by(user_id=current_user.id)\
        .order_by(Workout.created_at.desc())\
        .limit(5)\
        .all()
    
    # Get weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.created_at >= week_ago
    ).all()
    
    total_xp_this_week = sum(workout.xp_earned for workout in weekly_workouts)
    workout_count_this_week = len(weekly_workouts)
    
    return render_template('main/dashboard.html',
                         recent_workouts=recent_workouts,
                         total_xp_this_week=total_xp_this_week,
                         workout_count_this_week=workout_count_this_week)

@bp.route('/debug')
def debug():
    """Debug endpoint to check database schema."""
    from app import db
    from sqlalchemy import inspect
    from flask import jsonify, current_app
    
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        result = {'tables': tables, 'columns': {}}
        
        for table in tables:
            result['columns'][table] = [col['name'] for col in inspector.get_columns(table)]
        
        # Also check if our problematic column exists
        user_columns = result['columns'].get('user', [])
        workout_columns = result['columns'].get('workout', [])
        
        # Add specific checks
        result['has_last_workout_at'] = 'last_workout_at' in user_columns
        result['has_subtype'] = 'subtype' in workout_columns
        
        # Add environment info
        result['env'] = {
            'ENV': current_app.config.get('ENV', 'unknown'),
            'DEBUG': current_app.config.get('DEBUG', False),
            'TESTING': current_app.config.get('TESTING', False),
            'DB_URI_TYPE': db.engine.url.drivername
        }
        
        # Try to modify the database (if possible)
        try:
            db.session.execute("SELECT 1")
            db.session.commit()
            result['db_connection'] = 'ok'
            
            # Try to add columns if they don't exist
            if not result['has_last_workout_at']:
                try:
                    db.session.execute("ALTER TABLE \"user\" ADD COLUMN last_workout_at TIMESTAMP")
                    db.session.commit()
                    result['added_last_workout_at'] = True
                except Exception as e:
                    result['add_column_error'] = str(e)
            
            if not result['has_subtype']:
                try:
                    db.session.execute("ALTER TABLE workout ADD COLUMN subtype VARCHAR(50)")
                    db.session.commit()
                    result['added_subtype'] = True
                except Exception as e:
                    result['add_subtype_error'] = str(e)
                    
        except Exception as e:
            result['db_connection'] = f'error: {str(e)}'
            
        # Test user operations
        try:
            from app.models.user import User
            test_user = User.query.first()
            if test_user:
                result['user_test'] = {
                    'id': test_user.id,
                    'username': test_user.username,
                    'has_last_workout_attr': hasattr(test_user, 'last_workout_at'),
                    'last_workout': str(test_user.last_workout_at) if hasattr(test_user, 'last_workout_at') and test_user.last_workout_at else None
                }
        except Exception as e:
            result['user_test_error'] = str(e)
            
        # Test workout operations
        try:
            from app.models.workout import Workout
            test_workout = Workout.query.first()
            if test_workout:
                result['workout_test'] = {
                    'id': test_workout.id,
                    'name': test_workout.name,
                    'type': test_workout.type,
                    'has_subtype_attr': hasattr(test_workout, 'subtype'),
                    'subtype': test_workout.subtype if hasattr(test_workout, 'subtype') else None
                }
                
                # Test workout calculations
                try:
                    xp = test_workout.calculate_xp()
                    result['workout_xp_test'] = xp
                except Exception as e:
                    result['workout_xp_error'] = str(e)
        except Exception as e:
            result['workout_test_error'] = str(e)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}) 