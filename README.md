# FitVerse - Fitness Challenge Web Application

A complete web app for managing fitness challenges, tracking activities, and ranking participants on leaderboards.

## Features

- User Registration and Authentication
- Create and Join Fitness Challenges
- Log Fitness Activities
- View Leaderboards and Rankings
- Admin Dashboard for Managing Users and Challenges
- Reward System with Medals

## Screenshots
(Add screenshots here once the app is running)

## Database Schema

This application is built on a normalized MySQL database schema (3NF) with the following tables:

- User: Store user information
- Admin: Store admin users
- Challenge: Store fitness challenges
- ChallengeParticipation: Track which users join which challenges
- ActivityLog: Record user activities for challenges
- LeaderBoard: Store rankings and points
- Rewards & Medals: Manage rewards based on rankings

## Technology Stack

- Flask: Web Framework
- SQLAlchemy: ORM for database interactions
- Flask-Login: User authentication
- Bootstrap 5: Front-end UI components
- MySQL: Database

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitverse.git
cd fitverse
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your database:
   - Edit the `.env` file with your MySQL credentials
   - Make sure the MySQL database `fitness_manager_system2` exists

5. Initialize the database with sample data:
```bash
python init_db.py
```

6. Run the application:
```bash
python app.py
```

7. Access the application:
   - Open your web browser and go to `http://localhost:5000`

## Default Credentials

### Admin:
- Email: admin@fitverse.com
- Password: admin123

### Sample Users:
- Email: john@example.com
- Password: password123

- Email: jane@example.com
- Password: password123

- Email: mike@example.com
- Password: password123

## Project Structure

```
fitverse/
├── app.py              # Main application file
├── models.py           # SQLAlchemy models
├── forms.py            # Form definitions
├── init_db.py          # Database initialization script
├── requirements.txt    # Dependencies
├── .env                # Environment configuration
├── static/             # Static files (CSS, JS)
│   └── css/
│       └── style.css   # Custom CSS
└── templates/          # HTML templates
    ├── base.html       # Base template
    ├── index.html      # Home page
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── dashboard.html  # User dashboard
    ├── challenges.html # Challenges page
    └── ...             # Other templates
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

[MIT License](LICENSE) 