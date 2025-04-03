from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.workout import Workout
from werkzeug.security import generate_password_hash

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html', Workout=Workout, user=current_user)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        current_user.bio = request.form.get('bio', current_user.bio)
        
        # Handle password change if provided
        password = request.form.get('password')
        if password:
            current_user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html', user=current_user)

@bp.route('/profile/avatar', methods=['GET', 'POST'])
@login_required
def customize_avatar():
    if request.method == 'POST':
        style = request.form.get('avatar_style')
        seed = request.form.get('avatar_seed')
        background = request.form.get('avatar_background')
        
        if style:
            current_user.avatar_style = style
        if seed:
            current_user.avatar_seed = seed
        if background:
            current_user.avatar_background = background
            
        db.session.commit()
        flash('Avatar updated successfully!', 'success')
        return redirect(url_for('profile.index'))
        
    # Available avatar styles from DiceBear
    avatar_styles = [
        'adventurer',
        'adventurer-neutral',
        'avataaars',
        'bottts',
        'fun-emoji',
        'icons',
        'identicon',
        'initials',
        'lorelei',
        'pixel-art',
        'shapes'
    ]
    
    return render_template('profile/customize_avatar.html', avatar_styles=avatar_styles)

@bp.route('/profile/workout/delete/<int:workout_id>', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash('You do not have permission to delete this workout.', 'error')
        return redirect(url_for('profile.index'))
    
    # Subtract XP from user
    current_user.xp -= workout.xp_earned
    # Recalculate level
    current_user.level = current_user.calculate_level()
    
    # Delete the workout
    db.session.delete(workout)
    db.session.commit()
    
    flash('Workout deleted successfully!', 'success')
    return redirect(url_for('profile.index'))

@bp.route('/profile/workouts/clear', methods=['POST'])
@login_required
def clear_workouts():
    # Delete all workouts for the current user
    Workout.query.filter_by(user_id=current_user.id).delete()
    
    # Reset user's XP and level
    current_user.xp = 0
    current_user.level = 1
    
    db.session.commit()
    flash('All workouts have been cleared!', 'success')
    return redirect(url_for('profile.index')) 