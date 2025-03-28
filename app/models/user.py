from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.friendship import Friendship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    try:
        last_workout_at = db.Column(db.DateTime, nullable=True)
    except:
        pass  # If column doesn't exist, don't fail
    xp_decay_rate = db.Column(db.Float, default=0.05)  # 5% decay per day after grace period
    xp_decay_grace_days = db.Column(db.Integer, default=3)  # Days before decay starts
    
    # Avatar customization fields
    avatar_style = db.Column(db.String(20), default='adventurer')  # adventurer, identicon, bottts, etc.
    avatar_seed = db.Column(db.String(50))  # Used to generate consistent avatars
    avatar_background = db.Column(db.String(7), default='#b6e3f4')  # Hex color code
    
    # Strava integration fields
    strava_access_token = db.Column(db.String(100))
    strava_refresh_token = db.Column(db.String(100))
    strava_token_expires_at = db.Column(db.DateTime)
    strava_last_sync = db.Column(db.DateTime)
    
    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy='dynamic')
    
    # Friend relationships
    sent_friend_requests = db.relationship(
        'Friendship',
        foreign_keys='Friendship.user_id',
        backref='sender',
        lazy='dynamic'
    )
    received_friend_requests = db.relationship(
        'Friendship',
        foreign_keys='Friendship.friend_id',
        backref='receiver',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar_url(self):
        """Generate avatar URL using DiceBear API."""
        # Default values
        style = 'adventurer'
        seed = self.username
        bg_color = 'b6e3f4'  # Default without #
        
        # Check if fields exist and have values
        if hasattr(self, 'avatar_style') and self.avatar_style:
            style = self.avatar_style
        if hasattr(self, 'avatar_seed') and self.avatar_seed:
            seed = self.avatar_seed
        if hasattr(self, 'avatar_background') and self.avatar_background:
            # Remove the # from hex color
            bg_color = self.avatar_background.lstrip('#')
            
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}&backgroundColor={bg_color}"
    
    def calculate_level(self):
        """Calculate the user's level based on their XP."""
        remaining_xp = self.xp
        level = 1
        threshold = 300  # Base XP needed for level 2
        increase = 400   # Initial increase

        while remaining_xp >= threshold:
            remaining_xp -= threshold
            level += 1
            threshold = increase
            increase += 100

        return level
    
    def add_xp(self, amount):
        """Add XP and update level if necessary."""
        old_level = self.level
        self.xp += amount
        new_level = self.calculate_level()
        if new_level > self.level:
            self.level = new_level
            return True
        return False
    
    def update_level(self):
        """Update the user's level based on current XP."""
        self.level = self.calculate_level()
        db.session.commit()
        
    def get_next_level_xp(self):
        """Calculate XP needed for next level."""
        # First ensure level is up to date
        current_level = self.calculate_level()
        if current_level != self.level:
            self.level = current_level
            db.session.commit()
            
        # Calculate XP needed for next level
        total_for_next_level = 0
        threshold = 300
        increase = 400
        
        # Calculate total XP needed up to next level
        for level in range(1, self.level + 1):
            total_for_next_level += threshold
            threshold = increase
            increase += 100
            
        return total_for_next_level - self.xp
    
    def get_level_progress(self):
        """Calculate progress towards next level (0-100)."""
        if self.level == 1:
            return min(100, (self.xp / 300) * 100)

        current_level_start = 0
        threshold = 300
        increase = 400

        # Calculate XP at start of current level
        for _ in range(1, self.level):
            current_level_start += threshold
            threshold = increase
            increase += 100

        # Calculate progress within current level
        xp_in_level = self.xp - current_level_start
        return min(100, (xp_in_level / threshold) * 100)
    
    def get_rank(self):
        """Get the user's rank based on total XP."""
        xp = self.xp
        if xp < 2000:
            return "Bronze"
        elif xp < 5000:
            return "Silver"
        elif xp < 10000:
            return "Gold"
        elif xp < 20000:
            return "Platinum"
        elif xp < 35000:
            return "Diamond"
        elif xp < 55000:
            return "Master"
        elif xp < 80000:
            return "Grandmaster"
        elif xp < 110000:
            return "Elite"
        elif xp < 150000:
            return "Legend"
        elif xp < 200000:
            return "Mythic"
        else:
            return "GOAT"
    
    def send_friend_request(self, friend):
        """Send a friend request to another user."""
        if friend.id == self.id:
            return False, "You cannot add yourself as a friend."
            
        # Check if friendship already exists
        existing = Friendship.query.filter(
            ((Friendship.user_id == self.id) & (Friendship.friend_id == friend.id)) |
            ((Friendship.user_id == friend.id) & (Friendship.friend_id == self.id))
        ).first()
        
        if existing:
            if existing.status == 'accepted':
                return False, "You are already friends with this user."
            elif existing.status == 'pending':
                return False, "A friend request is already pending."
            
        friendship = Friendship(user_id=self.id, friend_id=friend.id)
        db.session.add(friendship)
        db.session.commit()
        return True, "Friend request sent successfully!"
        
    def accept_friend_request(self, friendship_id):
        """Accept a friend request."""
        friendship = Friendship.query.get(friendship_id)
        if not friendship or friendship.friend_id != self.id:
            return False, "Invalid friend request."
            
        friendship.status = 'accepted'
        db.session.commit()
        return True, "Friend request accepted!"
        
    def reject_friend_request(self, friendship_id):
        """Reject a friend request."""
        friendship = Friendship.query.get(friendship_id)
        if not friendship or friendship.friend_id != self.id:
            return False, "Invalid friend request."
            
        friendship.status = 'rejected'
        db.session.commit()
        return True, "Friend request rejected."
        
    def remove_friend(self, friend_id):
        """Remove a friend."""
        friendship = Friendship.query.filter(
            ((Friendship.user_id == self.id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == self.id))
        ).first()
        
        if friendship:
            db.session.delete(friendship)
            db.session.commit()
            return True, "Friend removed successfully."
        return False, "Friendship not found."
        
    def get_friends(self):
        """Get all accepted friends."""
        sent_friendships = Friendship.query.filter_by(
            user_id=self.id, status='accepted'
        ).all()
        received_friendships = Friendship.query.filter_by(
            friend_id=self.id, status='accepted'
        ).all()
        
        friends = []
        for friendship in sent_friendships:
            friends.append(User.query.get(friendship.friend_id))
        for friendship in received_friendships:
            friends.append(User.query.get(friendship.user_id))
        
        return friends
        
    def get_pending_friend_requests(self):
        """Get pending friend requests received by the user."""
        return self.received_friend_requests.filter_by(status='pending').all()
    
    def calculate_xp_decay(self):
        """Calculate how much XP will be lost due to inactivity."""
        if not self.last_workout_at:
            return 0, None
            
        days_since_workout = (datetime.utcnow() - self.last_workout_at).days
        if days_since_workout <= self.xp_decay_grace_days:
            return 0, self.xp_decay_grace_days - days_since_workout
            
        days_in_decay = days_since_workout - self.xp_decay_grace_days
        decay_multiplier = 1 - pow(1 - self.xp_decay_rate, days_in_decay)
        xp_to_lose = int(self.xp * decay_multiplier)
        
        return xp_to_lose, self.xp_decay_grace_days - days_since_workout
    
    def apply_xp_decay(self):
        """Apply XP decay if necessary."""
        xp_to_lose, _ = self.calculate_xp_decay()
        if xp_to_lose > 0:
            self.xp = max(0, self.xp - xp_to_lose)
            self.update_level()
            return xp_to_lose
        return 0
    
    def update_last_workout(self):
        """Update the last workout timestamp."""
        self.last_workout_at = datetime.utcnow()
        db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 