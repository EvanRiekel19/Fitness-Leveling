from app import db

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Name of the exercise (e.g., "Bench Press")
    type = db.Column(db.String(50), nullable=False, default='strength')  # Type of exercise (e.g., 'strength', 'cardio')
    sets = db.relationship('app.models.exercise_set.ExerciseSet', back_populates='exercise', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Exercise {self.name}>'


class ExerciseSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)  # e.g., 1, 2, 3 for set 1, set 2, set 3
    reps = db.Column(db.Integer)  # Number of repetitions
    weight = db.Column(db.Float)  # Weight in kg
    notes = db.Column(db.String(200))  # Optional notes for the set

    def __repr__(self):
        return f'<Set {self.set_number}: {self.reps} reps at {self.weight} kg>' 