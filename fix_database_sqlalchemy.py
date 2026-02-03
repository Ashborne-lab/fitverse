from dotenv import load_dotenv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sys

# Load environment variables
load_dotenv()

# Create a Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def fix_database_schema():
    """Fix the database schema using SQLAlchemy"""
    with app.app_context():
        try:
            # Check if User table has Name_ column
            result = db.session.execute(text("SHOW COLUMNS FROM User LIKE 'Name_'"))
            if result.rowcount > 0:
                print("Updating User table schema...")
                
                # Add FirstName and LastName columns if they don't exist
                try:
                    db.session.execute(text("ALTER TABLE User ADD COLUMN FirstName VARCHAR(50)"))
                    print("Added FirstName column")
                except Exception as e:
                    print(f"Column FirstName may already exist: {e}")
                
                try:
                    db.session.execute(text("ALTER TABLE User ADD COLUMN LastName VARCHAR(50)"))
                    print("Added LastName column")
                except Exception as e:
                    print(f"Column LastName may already exist: {e}")
                
                # Split existing Name_ values into FirstName and LastName
                results = db.session.execute(text("SELECT User_Id, Name_ FROM User"))
                users = results.fetchall()
                for user_id, full_name in users:
                    # Split name and handle edge cases
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Update the user record
                    db.session.execute(
                        text("UPDATE User SET FirstName = :first, LastName = :last WHERE User_Id = :id"),
                        {"first": first_name, "last": last_name, "id": user_id}
                    )
                print(f"Updated {len(users)} user records with split names")
                
                # Modify FirstName and LastName to be NOT NULL
                try:
                    db.session.execute(text("ALTER TABLE User MODIFY COLUMN FirstName VARCHAR(50) NOT NULL"))
                    db.session.execute(text("ALTER TABLE User MODIFY COLUMN LastName VARCHAR(50) NOT NULL"))
                    print("Set FirstName and LastName to NOT NULL")
                except Exception as e:
                    print(f"Error setting NOT NULL constraint: {e}")
                
                # Drop the Name_ column
                try:
                    db.session.execute(text("ALTER TABLE User DROP COLUMN Name_"))
                    print("Dropped Name_ column")
                except Exception as e:
                    print(f"Error dropping Name_ column: {e}")
            else:
                print("User table already has the updated schema.")
            
            # Check if Admin table has Name_ column
            result = db.session.execute(text("SHOW COLUMNS FROM Admin LIKE 'Name_'"))
            if result.rowcount > 0:
                print("Updating Admin table schema...")
                
                # Add FirstName and LastName columns if they don't exist
                try:
                    db.session.execute(text("ALTER TABLE Admin ADD COLUMN FirstName VARCHAR(50)"))
                    print("Added FirstName column")
                except Exception as e:
                    print(f"Column FirstName may already exist: {e}")
                
                try:
                    db.session.execute(text("ALTER TABLE Admin ADD COLUMN LastName VARCHAR(50)"))
                    print("Added LastName column")
                except Exception as e:
                    print(f"Column LastName may already exist: {e}")
                
                # Split existing Name_ values into FirstName and LastName
                results = db.session.execute(text("SELECT Admin_id, Name_ FROM Admin"))
                admins = results.fetchall()
                for admin_id, full_name in admins:
                    # Split name and handle edge cases
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Update the admin record
                    db.session.execute(
                        text("UPDATE Admin SET FirstName = :first, LastName = :last WHERE Admin_id = :id"),
                        {"first": first_name, "last": last_name, "id": admin_id}
                    )
                print(f"Updated {len(admins)} admin records with split names")
                
                # Modify FirstName and LastName to be NOT NULL
                try:
                    db.session.execute(text("ALTER TABLE Admin MODIFY COLUMN FirstName VARCHAR(50) NOT NULL"))
                    db.session.execute(text("ALTER TABLE Admin MODIFY COLUMN LastName VARCHAR(50) NOT NULL"))
                    print("Set FirstName and LastName to NOT NULL")
                except Exception as e:
                    print(f"Error setting NOT NULL constraint: {e}")
                
                # Drop the Name_ column
                try:
                    db.session.execute(text("ALTER TABLE Admin DROP COLUMN Name_"))
                    print("Dropped Name_ column")
                except Exception as e:
                    print(f"Error dropping Name_ column: {e}")
            else:
                print("Admin table already has the updated schema.")
            
            # Check if LeaderBoard table has UserId column
            result = db.session.execute(text("SHOW COLUMNS FROM LeaderBoard LIKE 'UserId'"))
            if result.rowcount > 0:
                print("Updating LeaderBoard table schema...")
                
                # Add User_Id column if it doesn't exist
                try:
                    db.session.execute(text("ALTER TABLE LeaderBoard ADD COLUMN User_Id INT"))
                    print("Added User_Id column")
                except Exception as e:
                    print(f"Column User_Id may already exist: {e}")
                
                # Copy data from UserId to User_Id
                db.session.execute(text("UPDATE LeaderBoard SET User_Id = UserId"))
                print("Copied data from UserId to User_Id")
                
                # Add foreign key constraint
                try:
                    db.session.execute(text("""
                    ALTER TABLE LeaderBoard 
                    ADD CONSTRAINT fk_leaderboard_user 
                    FOREIGN KEY (User_Id) REFERENCES User(User_Id) 
                    ON DELETE CASCADE ON UPDATE CASCADE
                    """))
                    print("Added foreign key constraint to User_Id")
                except Exception as e:
                    print(f"Error adding foreign key constraint: {e}")
                
                # Drop the UserId column
                try:
                    db.session.execute(text("ALTER TABLE LeaderBoard DROP COLUMN UserId"))
                    print("Dropped UserId column")
                except Exception as e:
                    print(f"Error dropping UserId column: {e}")
            else:
                print("LeaderBoard table already has the updated schema.")
            
            # Create views with updated schema
            view_commands = [
                """
                CREATE OR REPLACE VIEW AdminDetails AS
                SELECT Admin_id, CONCAT(FirstName, ' ', LastName) AS FullName, Email, Phone_no FROM Admin
                """,
                """
                CREATE OR REPLACE VIEW UserChallengeLog AS
                SELECT U.User_Id, CONCAT(U.FirstName, ' ', U.LastName) AS UserName, 
                       C.Name_ AS ChallengeName, A.ActivityType, A.ActivityData, A.LogTimestamp
                FROM ActivityLog A
                JOIN User U ON A.User_Id = U.User_Id
                JOIN Challenge C ON A.ChallengeID = C.ChallengeID
                """,
                """
                CREATE OR REPLACE VIEW LeaderBoardSummary AS
                SELECT L.LeaderBoardID, CONCAT(U.FirstName, ' ', U.LastName) AS UserName, 
                       C.Name_ AS ChallengeName, L.Points, L.Rank_
                FROM LeaderBoard L
                JOIN User U ON L.User_Id = U.User_Id
                JOIN Challenge C ON L.ChallengeId = C.ChallengeID
                """,
                """
                CREATE OR REPLACE VIEW ChallengeParticipationView AS
                SELECT CP.ParticipationID, CONCAT(U.FirstName, ' ', U.LastName) AS UserName, 
                       C.Name_ AS ChallengeName, CP.ParticipationDate
                FROM ChallengeParticipation CP
                JOIN User U ON U.User_Id = CP.User_Id
                JOIN Challenge C ON C.ChallengeID = CP.ChallengeID
                """
            ]
            
            for command in view_commands:
                try:
                    db.session.execute(text(command))
                    print("View created/updated successfully")
                except Exception as e:
                    print(f"Error creating/updating view: {e}")
            
            # Commit all changes
            db.session.commit()
            print("Database schema updated successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating database schema: {e}")
            return False

if __name__ == '__main__':
    print("Starting database schema fix...")
    success = fix_database_schema()
    sys.exit(0 if success else 1) 