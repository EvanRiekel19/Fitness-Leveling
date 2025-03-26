from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.friendship import Friendship
from app.models.workout import Workout

bp = Blueprint('friends', __name__)

@bp.route('/friends')
@login_required
def index():
    friends = current_user.get_friends()
    pending_requests = current_user.get_pending_friend_requests()
    return render_template('friends/index.html', friends=friends, pending_requests=pending_requests)

@bp.route('/friends/profile/<username>')
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if the current user is friends with this user
    if user.id != current_user.id:
        friendship = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user.id)) |
            ((Friendship.user_id == user.id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if not friendship or friendship.status != 'accepted':
            flash('You must be friends with this user to view their profile.', 'error')
            return redirect(url_for('friends.index'))
    
    # Get user's recent workouts
    recent_workouts = user.workouts.order_by(Workout.created_at.desc()).limit(5).all()
    
    # Calculate some stats
    total_workouts = user.workouts.count()
    total_distance = sum(w.distance or 0 for w in user.workouts.all())
    total_duration = sum(w.duration or 0 for w in user.workouts.all())
    
    # Get workout type distribution
    workout_types = {}
    for workout in user.workouts.all():
        workout_types[workout.type] = workout_types.get(workout.type, 0) + 1
    
    return render_template('friends/profile.html', 
                         user=user,
                         recent_workouts=recent_workouts,
                         total_workouts=total_workouts,
                         total_distance=total_distance,
                         total_duration=total_duration,
                         workout_types=workout_types)

@bp.route('/friends/add', methods=['POST'])
@login_required
def add_friend():
    username = request.form.get('username')
    if not username:
        flash('Please enter a username.', 'error')
        return redirect(url_for('friends.index'))
        
    friend = User.query.filter_by(username=username).first()
    if not friend:
        flash('User not found.', 'error')
        return redirect(url_for('friends.index'))
        
    success, message = current_user.send_friend_request(friend)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('friends.index'))

@bp.route('/friends/accept/<int:friendship_id>', methods=['POST'])
@login_required
def accept_friend(friendship_id):
    success, message = current_user.accept_friend_request(friendship_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('friends.index'))

@bp.route('/friends/reject/<int:friendship_id>', methods=['POST'])
@login_required
def reject_friend(friendship_id):
    success, message = current_user.reject_friend_request(friendship_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('friends.index'))

@bp.route('/friends/remove/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    success, message = current_user.remove_friend(friend_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('friends.index'))

@bp.route('/friends/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if len(query) < 3:
        return jsonify([])
        
    users = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.id != current_user.id
    ).limit(5).all()
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'avatar_url': user.get_avatar_url(),
        'level': user.level,
        'rank': user.get_rank()
    } for user in users]) 