from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    
    User_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Phone_no = db.Column(db.BigInteger, unique=True)
    Password_ = db.Column(db.String(20), nullable=False)
    RegistrationDate = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge_participations = db.relationship('ChallengeParticipation', backref='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)
    leaderboard_entries = db.relationship('LeaderBoard', backref='user', lazy=True)
    
    def get_id(self):
        return str(self.User_Id)
        
    def check_password(self, password):
        return self.Password_ == password  # In production, use proper password hashing
    
    @property
    def full_name(self):
        """Return the user's full name for display purposes"""
        return f"{self.FirstName} {self.LastName}"

class Admin(db.Model):
    __tablename__ = 'Admin'
    
    Admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Phone_no = db.Column(db.BigInteger, unique=True)
    Password_ = db.Column(db.String(20), nullable=False)
    
    def check_password(self, password):
        return self.Password_ == password  # In production, use proper password hashing
    
    @property
    def full_name(self):
        """Return the admin's full name for display purposes"""
        return f"{self.FirstName} {self.LastName}"

class Challenge(db.Model):
    __tablename__ = 'Challenge'
    
    ChallengeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name_ = db.Column(db.String(100), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    
    # Relationships
    participations = db.relationship('ChallengeParticipation', backref='challenge', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='challenge', lazy=True)
    leaderboard_entries = db.relationship('LeaderBoard', backref='challenge', lazy=True)

class ChallengeParticipation(db.Model):
    __tablename__ = 'ChallengeParticipation'
    
    ParticipationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_Id = db.Column(db.Integer, db.ForeignKey('User.User_Id', ondelete='CASCADE', onupdate='CASCADE'))
    ChallengeID = db.Column(db.Integer, db.ForeignKey('Challenge.ChallengeID', ondelete='CASCADE', onupdate='CASCADE'))
    ParticipationDate = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    __tablename__ = 'ActivityLog'
    
    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_Id = db.Column(db.Integer, db.ForeignKey('User.User_Id', ondelete='CASCADE', onupdate='CASCADE'))
    ChallengeID = db.Column(db.Integer, db.ForeignKey('Challenge.ChallengeID', ondelete='CASCADE', onupdate='CASCADE'))
    ActivityType = db.Column(db.String(50), nullable=False)
    ActivityData = db.Column(db.Float, nullable=False)
    LogTimestamp = db.Column(db.DateTime, default=datetime.utcnow)

class LeaderBoard(db.Model):
    __tablename__ = 'LeaderBoard'
    
    LeaderBoardID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Points = db.Column(db.Float, nullable=False)
    Rank_ = db.Column(db.Integer, nullable=False)
    User_Id = db.Column(db.Integer, db.ForeignKey('User.User_Id', ondelete='CASCADE', onupdate='CASCADE'))
    ChallengeId = db.Column(db.Integer, db.ForeignKey('Challenge.ChallengeID', ondelete='CASCADE', onupdate='CASCADE'))

class Rewards(db.Model):
    __tablename__ = 'Rewards'
    
    RewardID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RewardType = db.Column(db.String(255), nullable=False)
    
    # Relationships
    medal_rewards = db.relationship('MedalRewards', backref='reward', lazy=True)

class Medals(db.Model):
    __tablename__ = 'Medals'
    
    MedalID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Rank_ = db.Column(db.Integer, nullable=False, unique=True)
    MedalType = db.Column(db.String(50), nullable=False)
    
    # Relationships
    medal_rewards = db.relationship('MedalRewards', backref='medal', lazy=True)

class MedalRewards(db.Model):
    __tablename__ = 'MedalRewards'
    
    MedalRewardID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MedalID = db.Column(db.Integer, db.ForeignKey('Medals.MedalID', ondelete='CASCADE', onupdate='CASCADE'))
    RewardID = db.Column(db.Integer, db.ForeignKey('Rewards.RewardID', ondelete='CASCADE', onupdate='CASCADE')) 