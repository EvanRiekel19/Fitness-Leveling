from datetime import datetime
from app import db
from app.models.user import User
from app.models.workout import Workout

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # 'distance', 'workouts', etc.
    goal_value = db.Column(db.Float, nullable=False)  # The target value (e.g., 30 miles)
    goal_unit = db.Column(db.String(20))  # 'miles', 'km', 'workouts', etc.
    workout_type = db.Column(db.String(50))  # Type of workouts to track
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', backref='created_challenges')
    participants = db.relationship('ChallengeParticipant', backref='challenge', lazy='dynamic')

    def get_participant(self, user_id):
        return self.participants.filter_by(user_id=user_id).first()

    def calculate_progress(self, user_id):
        """Calculate a user's progress towards the challenge goal."""
        participant = self.get_participant(user_id)
        if not participant:
            return {'progress': 0, 'current_value': 0}

        # Get relevant workouts within the challenge timeframe
        workouts = Workout.query.filter(
            Workout.user_id == user_id,
            Workout.created_at >= self.start_date,
            Workout.created_at <= self.end_date
        )

        if self.workout_type:
            workouts = workouts.filter_by(type=self.workout_type)

        total = 0
        for workout in workouts:
            if self.goal_type == 'distance':
                total += workout.distance or 0
            elif self.goal_type == 'workouts':
                total += 1
            # Add more goal types as needed

        progress = (total / self.goal_value) * 100 if self.goal_value > 0 else 0
        
        # Update completion status
        if progress >= 100 and not participant.completed:
            participant.completed = True
            participant.completed_at = datetime.utcnow()
            db.session.commit()
        
        return {
            'progress': progress,
            'current_value': total
        }

class ChallengeParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='challenge_participations')

    __table_args__ = (
        db.UniqueConstraint('challenge_id', 'user_id', name='unique_challenge_participant'),
    ) 