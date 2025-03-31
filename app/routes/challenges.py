from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.challenge import Challenge, ChallengeParticipant
from app.models.user import User

bp = Blueprint('challenges', __name__)

@bp.route('/challenges')
@login_required
def index():
    # Get challenges the user has created or joined
    user_challenges = Challenge.query.join(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user.id
    ).all()
    
    # Get public challenges the user hasn't joined
    available_challenges = Challenge.query.filter(
        Challenge.is_public == True,
        ~Challenge.participants.any(ChallengeParticipant.user_id == current_user.id)
    ).all()
    
    return render_template('challenges/index.html',
                         user_challenges=user_challenges,
                         available_challenges=available_challenges)

@bp.route('/challenges/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            challenge = Challenge(
                title=request.form['title'],
                description=request.form['description'],
                creator_id=current_user.id,
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
                goal_type=request.form['goal_type'],
                goal_value=float(request.form['goal_value']),
                goal_unit=request.form['goal_unit'],
                workout_type=request.form['workout_type'],
                is_public=bool(request.form.get('is_public', True))
            )
            
            # Creator automatically joins their own challenge
            participant = ChallengeParticipant(user_id=current_user.id)
            challenge.participants.append(participant)
            
            db.session.add(challenge)
            db.session.commit()
            
            flash('Challenge created successfully!', 'success')
            return redirect(url_for('challenges.view', challenge_id=challenge.id))
        except Exception as e:
            flash('Error creating challenge. Please try again.', 'error')
            return redirect(url_for('challenges.new'))
            
    return render_template('challenges/new.html')

@bp.route('/challenges/<int:challenge_id>')
@login_required
def view(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    participants = challenge.participants.all()
    
    # Calculate progress for each participant
    participant_progress = []
    for participant in participants:
        progress_data = challenge.calculate_progress(participant.user_id)
        
        # Get workout count for this participant in the challenge period
        # Handle different workout type mappings
        workout_type_filter = ""
        workout_params = {
            'user_id': participant.user_id,
            'start_date': challenge.start_date,
            'end_date': challenge.end_date
        }
        
        if challenge.workout_type == 'cardio':
            workout_type_filter = "type = 'cardio'"
        elif challenge.workout_type == 'strength':
            workout_type_filter = "type = 'strength'"
        elif challenge.workout_type.startswith('strength_'):
            # For specific strength workout types (e.g., strength_upper, strength_push)
            workout_type_filter = "(type = 'strength' AND subtype = :subtype)"
            workout_params['subtype'] = challenge.workout_type
        
        query = f"""
            SELECT COUNT(*) 
            FROM workout 
            WHERE user_id = :user_id 
            AND {workout_type_filter}
            AND created_at BETWEEN :start_date AND :end_date
        """
        
        workout_count = db.session.execute(query, workout_params).scalar()
        
        participant_progress.append({
            'user': participant.user,
            'progress': progress_data['progress'],
            'current_value': progress_data['current_value'],
            'completed': participant.completed,
            'workout_count': workout_count
        })
    
    # Sort by progress descending
    participant_progress.sort(key=lambda x: x['progress'], reverse=True)
    
    return render_template('challenges/view.html',
                         challenge=challenge,
                         participant_progress=participant_progress)

@bp.route('/challenges/<int:challenge_id>/join', methods=['POST'])
@login_required
def join(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if challenge.get_participant(current_user.id):
        flash('You are already participating in this challenge.', 'error')
        return redirect(url_for('challenges.view', challenge_id=challenge_id))
    
    participant = ChallengeParticipant(user_id=current_user.id)
    challenge.participants.append(participant)
    
    db.session.commit()
    flash('You have joined the challenge!', 'success')
    return redirect(url_for('challenges.view', challenge_id=challenge_id))

@bp.route('/challenges/<int:challenge_id>/leave', methods=['POST'])
@login_required
def leave(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if challenge.creator_id == current_user.id:
        flash('Challenge creator cannot leave the challenge.', 'error')
        return redirect(url_for('challenges.view', challenge_id=challenge_id))
    
    participant = challenge.get_participant(current_user.id)
    if participant:
        db.session.delete(participant)
        db.session.commit()
        flash('You have left the challenge.', 'success')
    
    return redirect(url_for('challenges.index')) 