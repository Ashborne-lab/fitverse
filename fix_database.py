import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_database_schema():
    """Modify the database schema to match the updated requirements"""
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', '127.0.0.1'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '@Hum42'),
            database=os.getenv('MYSQL_DB', 'fitness_manager_system')
        )
        cursor = conn.cursor()
        print("Connected to the database successfully!")
        
        # Check if User table exists
        cursor.execute("SHOW TABLES LIKE 'User'")
        if cursor.fetchone():
            # Check if Name_ column exists
            cursor.execute("SHOW COLUMNS FROM User LIKE 'Name_'")
            if cursor.fetchone():
                # User table has Name_ column, need to update schema
                print("Updating User table schema...")
                
                # Add FirstName and LastName columns if they don't exist
                try:
                    cursor.execute("ALTER TABLE User ADD COLUMN FirstName VARCHAR(50)")
                    print("Added FirstName column")
                except Exception as e:
                    print(f"Column FirstName may already exist: {e}")
                
                try:
                    cursor.execute("ALTER TABLE User ADD COLUMN LastName VARCHAR(50)")
                    print("Added LastName column")
                except Exception as e:
                    print(f"Column LastName may already exist: {e}")
                
                # Split existing Name_ values into FirstName and LastName
                cursor.execute("SELECT User_Id, Name_ FROM User")
                users = cursor.fetchall()
                for user_id, full_name in users:
                    # Split name and handle edge cases
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Update the user record
                    cursor.execute(
                        "UPDATE User SET FirstName = %s, LastName = %s WHERE User_Id = %s",
                        (first_name, last_name, user_id)
                    )
                print(f"Updated {len(users)} user records with split names")
                
                # Modify FirstName and LastName to be NOT NULL
                try:
                    cursor.execute("ALTER TABLE User MODIFY COLUMN FirstName VARCHAR(50) NOT NULL")
                    cursor.execute("ALTER TABLE User MODIFY COLUMN LastName VARCHAR(50) NOT NULL")
                    print("Set FirstName and LastName to NOT NULL")
                except Exception as e:
                    print(f"Error setting NOT NULL constraint: {e}")
                
                # Drop the Name_ column
                try:
                    cursor.execute("ALTER TABLE User DROP COLUMN Name_")
                    print("Dropped Name_ column")
                except Exception as e:
                    print(f"Error dropping Name_ column: {e}")
            else:
                print("User table already has the updated schema.")
        
        # Check if Admin table exists
        cursor.execute("SHOW TABLES LIKE 'Admin'")
        if cursor.fetchone():
            # Check if Name_ column exists
            cursor.execute("SHOW COLUMNS FROM Admin LIKE 'Name_'")
            if cursor.fetchone():
                # Admin table has Name_ column, need to update schema
                print("Updating Admin table schema...")
                
                # Add FirstName and LastName columns if they don't exist
                try:
                    cursor.execute("ALTER TABLE Admin ADD COLUMN FirstName VARCHAR(50)")
                    print("Added FirstName column")
                except Exception as e:
                    print(f"Column FirstName may already exist: {e}")
                
                try:
                    cursor.execute("ALTER TABLE Admin ADD COLUMN LastName VARCHAR(50)")
                    print("Added LastName column")
                except Exception as e:
                    print(f"Column LastName may already exist: {e}")
                
                # Split existing Name_ values into FirstName and LastName
                cursor.execute("SELECT Admin_id, Name_ FROM Admin")
                admins = cursor.fetchall()
                for admin_id, full_name in admins:
                    # Split name and handle edge cases
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Update the admin record
                    cursor.execute(
                        "UPDATE Admin SET FirstName = %s, LastName = %s WHERE Admin_id = %s",
                        (first_name, last_name, admin_id)
                    )
                print(f"Updated {len(admins)} admin records with split names")
                
                # Modify FirstName and LastName to be NOT NULL
                try:
                    cursor.execute("ALTER TABLE Admin MODIFY COLUMN FirstName VARCHAR(50) NOT NULL")
                    cursor.execute("ALTER TABLE Admin MODIFY COLUMN LastName VARCHAR(50) NOT NULL")
                    print("Set FirstName and LastName to NOT NULL")
                except Exception as e:
                    print(f"Error setting NOT NULL constraint: {e}")
                
                # Drop the Name_ column
                try:
                    cursor.execute("ALTER TABLE Admin DROP COLUMN Name_")
                    print("Dropped Name_ column")
                except Exception as e:
                    print(f"Error dropping Name_ column: {e}")
            else:
                print("Admin table already has the updated schema.")
        
        # Update LeaderBoard table if needed (UserId -> User_Id)
        cursor.execute("SHOW COLUMNS FROM LeaderBoard LIKE 'UserId'")
        if cursor.fetchone():
            print("Updating LeaderBoard table schema...")
            
            # Add User_Id column if it doesn't exist
            try:
                cursor.execute("ALTER TABLE LeaderBoard ADD COLUMN User_Id INT")
                print("Added User_Id column")
            except Exception as e:
                print(f"Column User_Id may already exist: {e}")
            
            # Copy data from UserId to User_Id
            cursor.execute("UPDATE LeaderBoard SET User_Id = UserId")
            print("Copied data from UserId to User_Id")
            
            # Add foreign key constraint
            try:
                cursor.execute("""
                ALTER TABLE LeaderBoard 
                ADD CONSTRAINT fk_leaderboard_user 
                FOREIGN KEY (User_Id) REFERENCES User(User_Id) 
                ON DELETE CASCADE ON UPDATE CASCADE
                """)
                print("Added foreign key constraint to User_Id")
            except Exception as e:
                print(f"Error adding foreign key constraint: {e}")
            
            # Drop the UserId column
            try:
                cursor.execute("ALTER TABLE LeaderBoard DROP COLUMN UserId")
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
                cursor.execute(command)
                print("View created/updated successfully")
            except Exception as e:
                print(f"Error creating/updating view: {e}")
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        print("Database schema updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating database schema: {e}")
        return False

if __name__ == '__main__':
    fix_database_schema() 