from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from dotenv import load_dotenv
import os
from models import db, User, Admin, Challenge, ChallengeParticipation, ActivityLog, LeaderBoard, Rewards, Medals, MedalRewards
from forms import LoginForm, RegisterForm, ChallengeForm, ActivityForm

# Load environment variables
load_dotenv()

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    challenges = Challenge.query.all()
    return render_template('index.html', challenges=challenges)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                FirstName=form.first_name.data,
                LastName=form.last_name.data,
                Email=form.email.data,
                Phone_no=form.phone.data,
                Password_=form.password.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}')
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_challenges = ChallengeParticipation.query.filter_by(User_Id=current_user.User_Id).all()
    activity_logs = ActivityLog.query.filter_by(User_Id=current_user.User_Id).all()
    
    return render_template('dashboard.html', 
                          user_challenges=user_challenges, 
                          activity_logs=activity_logs)

@app.route('/join_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def join_challenge(challenge_id):
    # Check if already joined
    existing = ChallengeParticipation.query.filter_by(
        User_Id=current_user.User_Id, 
        ChallengeID=challenge_id
    ).first()
    
    if not existing:
        new_participation = ChallengeParticipation(
            User_Id=current_user.User_Id,
            ChallengeID=challenge_id
        )
        db.session.add(new_participation)
        db.session.commit()
        flash('Successfully joined the challenge!')
    else:
        flash('You have already joined this challenge.')
    
    return redirect(url_for('dashboard'))

@app.route('/challenges')
def challenges():
    all_challenges = Challenge.query.all()
    return render_template('challenges.html', challenges=all_challenges)

@app.route('/add_challenge', methods=['GET', 'POST'])
@login_required
def add_challenge():
    form = ChallengeForm()
    if form.validate_on_submit():
        new_challenge = Challenge(
            Name_=form.name.data,
            StartDate=form.start_date.data,
            EndDate=form.end_date.data
        )
        db.session.add(new_challenge)
        db.session.commit()
        flash('Challenge created successfully!')
        return redirect(url_for('challenges'))
    
    return render_template('add_challenge.html', form=form)

@app.route('/log_activity', methods=['GET', 'POST'])
@login_required
def log_activity():
    form = ActivityForm()
    # Populate challenge choices
    user_participations = ChallengeParticipation.query.filter_by(User_Id=current_user.User_Id).all()
    challenge_ids = [p.ChallengeID for p in user_participations]
    challenges = Challenge.query.filter(Challenge.ChallengeID.in_(challenge_ids)).all()
    form.challenge.choices = [(c.ChallengeID, c.Name_) for c in challenges]
    
    if form.validate_on_submit():
        new_activity = ActivityLog(
            User_Id=current_user.User_Id,
            ChallengeID=form.challenge.data,
            ActivityType=form.activity_type.data,
            ActivityData=form.activity_data.data
        )
        db.session.add(new_activity)
        db.session.commit()
        flash('Activity logged successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('log_activity.html', form=form)

@app.route('/leaderboard/<int:challenge_id>')
def leaderboard(challenge_id):
    # Get challenge details
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Get leaderboard entries for this challenge
    leaderboard_entries = LeaderBoard.query.filter_by(ChallengeId=challenge_id).order_by(LeaderBoard.Rank_).all()
    
    return render_template('leaderboard.html', challenge=challenge, leaderboard_entries=leaderboard_entries)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(Email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            # Use a session variable to track admin login
            session['admin_id'] = admin.Admin_id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if admin is logged in
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    challenges = Challenge.query.all()
    activities = ActivityLog.query.all()
    
    return render_template('admin_dashboard.html', 
                          users=users, 
                          challenges=challenges,
                          activities=activities)

@app.route('/calculate_leaderboard/<int:challenge_id>')
def calculate_leaderboard(challenge_id):
    # For simplicity, we're calculating based on total activity data
    
    # Get all activity logs for this challenge
    activities = ActivityLog.query.filter_by(ChallengeID=challenge_id).all()
    
    # Calculate points per user
    user_points = {}
    for activity in activities:
        if activity.User_Id not in user_points:
            user_points[activity.User_Id] = 0
        user_points[activity.User_Id] += activity.ActivityData
    
    # Sort users by points (descending)
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    
    # Update leaderboard
    for rank, (user_id, points) in enumerate(sorted_users, 1):
        # Check if entry exists
        entry = LeaderBoard.query.filter_by(User_Id=user_id, ChallengeId=challenge_id).first()
        
        if entry:
            entry.Points = points
            entry.Rank_ = rank
        else:
            new_entry = LeaderBoard(
                Points=points,
                Rank_=rank,
                User_Id=user_id,
                ChallengeId=challenge_id
            )
            db.session.add(new_entry)
    
    db.session.commit()
    flash('Leaderboard updated successfully!')
    return redirect(url_for('leaderboard', challenge_id=challenge_id))

if __name__ == '__main__':
    app.run(debug=True) 