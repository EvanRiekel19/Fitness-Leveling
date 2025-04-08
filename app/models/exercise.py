from app import db
from app.models.exercise_set import ExerciseSet

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Name of the exercise (e.g., "Bench Press")
    type = db.Column(db.String(50), nullable=False, default='strength')
    
    # Relationships
    sets = db.relationship('app.models.exercise_set.ExerciseSet', back_populates='exercise', lazy='dynamic', cascade="all, delete-orphan")
    workout = db.relationship('Workout', back_populates='exercises')

    def __repr__(self):
        return f'<Exercise {self.name}>'

# ExerciseSet is now imported from exercise_set.py 