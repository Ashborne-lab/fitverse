import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_from_scratch():
    """Create the database with the updated schema directly using SQL commands"""
    # Connect to MySQL server
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', '127.0.0.1'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '@Hum42')
        )
        cursor = conn.cursor()
        print("Connected to MySQL server successfully!")
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS fitness_manager_system")
        cursor.execute("USE fitness_manager_system")
        print("Database 'fitness_manager_system' selected")
        
        # Create tables
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS Fitness_Manager(
                 AppID INT PRIMARY KEY,
                 Name_ VARCHAR(100) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Admin (
                Admin_id INT PRIMARY KEY AUTO_INCREMENT,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Email VARCHAR(100) NOT NULL UNIQUE,
                Phone_no BIGINT UNIQUE,
                Password_ VARCHAR(20) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS User (
                User_Id INT PRIMARY KEY AUTO_INCREMENT,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Email VARCHAR(100) NOT NULL UNIQUE,
                Phone_no BIGINT UNIQUE,
                Password_ VARCHAR(20) NOT NULL,
                RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Challenge (
                ChallengeID INT PRIMARY KEY AUTO_INCREMENT,
                Name_ VARCHAR(100) NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ChallengeParticipation (
                ParticipationID INT PRIMARY KEY AUTO_INCREMENT,
                User_Id INT,
                ChallengeID INT,
                ParticipationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (User_Id) REFERENCES User(User_Id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ChallengeID) REFERENCES Challenge(ChallengeID) ON DELETE CASCADE ON UPDATE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ActivityLog (
                LogID INT PRIMARY KEY AUTO_INCREMENT,
                User_Id INT,
                ChallengeID INT,
                ActivityType VARCHAR(50) NOT NULL,
                ActivityData FLOAT NOT NULL,
                LogTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (User_Id) REFERENCES User(User_Id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ChallengeID) REFERENCES Challenge(ChallengeID) ON DELETE CASCADE ON UPDATE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS LeaderBoard (
                LeaderBoardID INT PRIMARY KEY AUTO_INCREMENT,
                Points FLOAT NOT NULL,
                Rank_ INT NOT NULL,
                User_Id INT,
                ChallengeId INT,
                FOREIGN KEY (User_Id) REFERENCES User(User_Id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ChallengeId) REFERENCES Challenge(ChallengeID) ON DELETE CASCADE ON UPDATE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Rewards (
                RewardID INT PRIMARY KEY AUTO_INCREMENT,
                RewardType VARCHAR(255) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Medals (
                MedalID INT PRIMARY KEY AUTO_INCREMENT,
                Rank_ INT NOT NULL UNIQUE,
                MedalType VARCHAR(50) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS MedalRewards (
                MedalRewardID INT PRIMARY KEY AUTO_INCREMENT,
                MedalID INT,
                RewardID INT,
                FOREIGN KEY (MedalID) REFERENCES Medals(MedalID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (RewardID) REFERENCES Rewards(RewardID) ON DELETE CASCADE ON UPDATE CASCADE
            )
            """
        ]
        
        # Execute table creation
        for command in sql_commands:
            cursor.execute(command)
            print("Table created successfully")
        
        # Create trigger
        try:
            cursor.execute("""
            DROP TRIGGER IF EXISTS trg_insert_participation
            """)
            
            cursor.execute("""
            CREATE TRIGGER trg_insert_participation
            BEFORE INSERT ON ActivityLog
            FOR EACH ROW
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM ChallengeParticipation 
                    WHERE User_Id = NEW.User_Id AND ChallengeID = NEW.ChallengeID
                ) THEN
                    INSERT INTO ChallengeParticipation (User_Id, ChallengeID) 
                    VALUES (NEW.User_Id, NEW.ChallengeID);
                END IF;
            END
            """)
            print("Trigger created successfully")
        except Exception as e:
            print(f"Error creating trigger: {e}")
        
        # Create stored procedure
        try:
            cursor.execute("""
            DROP PROCEDURE IF EXISTS RegisterUser
            """)
            
            cursor.execute("""
            CREATE PROCEDURE RegisterUser(
                IN p_FirstName VARCHAR(50),
                IN p_LastName VARCHAR(50),
                IN p_Email VARCHAR(100),
                IN p_Phone BIGINT,
                IN p_Password VARCHAR(20)
            )
            BEGIN
                INSERT INTO User (FirstName, LastName, Email, Phone_no, Password_) 
                VALUES (p_FirstName, p_LastName, p_Email, p_Phone, p_Password);
            END
            """)
            print("Stored procedure created successfully")
        except Exception as e:
            print(f"Error creating stored procedure: {e}")
        
        # Create views
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
                print("View created successfully")
            except Exception as e:
                print(f"Error creating view: {e}")
        
        # Create indexes
        index_commands = [
            "CREATE INDEX idx_user_challenge ON LeaderBoard(User_Id, ChallengeId)",
            "CREATE INDEX idx_challenge_dates ON Challenge(StartDate, EndDate)",
            "CREATE INDEX idx_activity_user ON ActivityLog(User_Id)"
        ]
        
        for command in index_commands:
            try:
                cursor.execute(command)
                print("Index created successfully")
            except Exception as e:
                print(f"Error creating index: {e}")
        
        # Insert data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM Admin")
        if cursor.fetchone()[0] == 0:
            # Insert admins
            cursor.execute("""
            INSERT INTO Admin (FirstName, LastName, Email, Phone_no, Password_) VALUES
            ('Rahul', 'Kapoor', 'rahul.kapoor@fitadmin.com', 9991112222, 'admin123'),
            ('Anjali', 'Deshmukh', 'anjali.deshmukh@fitadmin.com', 9991113333, 'admin456')
            """)
            print("Admin data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM User")
        if cursor.fetchone()[0] == 0:
            # Insert users
            cursor.execute("""
            INSERT INTO User (FirstName, LastName, Email, Phone_no, Password_) VALUES
            ('Aarav', 'Sharma', 'aarav.sharma@gmail.com', 9876543210, 'pass1234'),
            ('Diya', 'Mehra', 'diya.mehra@yahoo.com', 9876543211, 'diya2025'),
            ('Rohan', 'Verma', 'rohan.verma@gmail.com', 9876543212, 'rohan@123'),
            ('Sneha', 'Iyer', 'sneha.iyer@hotmail.com', 9876543213, 'sneha456'),
            ('Vikram', 'Choudhary', 'vikram.c@gmail.com', 9876543214, 'vikram789')
            """)
            print("User data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM Challenge")
        if cursor.fetchone()[0] == 0:
            # Insert challenges
            cursor.execute("""
            INSERT INTO Challenge (Name_, StartDate, EndDate) VALUES
            ('10K Steps Daily', '2025-04-01', '2025-04-30'),
            ('Home Workout Streak', '2025-04-05', '2025-05-05'),
            ('Cycling Distance Challenge', '2025-04-05', '2025-04-30'),
            ('Push-up Progression', '2025-04-10', '2025-05-10'),
            ('Daily Yoga Habit', '2025-04-15', '2025-05-15')
            """)
            print("Challenge data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM Rewards")
        if cursor.fetchone()[0] == 0:
            # Insert rewards
            cursor.execute("""
            INSERT INTO Rewards (RewardType) VALUES
            ('Amazon Gift Card ₹500'),
            ('Free Gym Membership - 1 Month'),
            ('Fitness Tracker Band'),
            ('Protein Supplement Pack'),
            ('Digital Certificate of Completion')
            """)
            print("Rewards data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM Medals")
        if cursor.fetchone()[0] == 0:
            # Insert medals
            cursor.execute("""
            INSERT INTO Medals (Rank_, MedalType) VALUES
            (1, 'Gold'),
            (2, 'Silver'),
            (3, 'Bronze')
            """)
            print("Medals data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM MedalRewards")
        if cursor.fetchone()[0] == 0:
            # Insert medal rewards
            cursor.execute("""
            INSERT INTO MedalRewards (MedalID, RewardID) VALUES
            (1, 3), -- Fitness Tracker
            (1, 5), -- Certificate
            (2, 2), -- Gym Membership
            (3, 1), -- Amazon Gift Card
            (3, 5)  -- Certificate
            """)
            print("Medal rewards data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM LeaderBoard")
        if cursor.fetchone()[0] == 0:
            # Insert leaderboards
            cursor.execute("""
            INSERT INTO LeaderBoard (Points, Rank_, User_Id, ChallengeId) VALUES
            (88.5, 1, 1, 1), -- Aarav in 10K Steps
            (75.0, 2, 2, 1), -- Diya in 10K Steps
            (69.5, 3, 3, 1), -- Rohan in 10K Steps
            (91.0, 1, 4, 2), -- Sneha in Workout Streak
            (79.2, 2, 5, 2), -- Vikram in Workout Streak
            (72.4, 3, 1, 2)  -- Aarav again
            """)
            print("Leaderboard data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM ActivityLog")
        if cursor.fetchone()[0] == 0:
            # Insert activity logs
            cursor.execute("""
            INSERT INTO ActivityLog (User_Id, ChallengeID, ActivityType, ActivityData) VALUES
            (1, 1, 'Steps', 10500),   -- Aarav in 10K Steps
            (2, 1, 'Steps', 9700),    -- Diya in 10K Steps
            (3, 1, 'Steps', 8800),    -- Rohan in 10K Steps
            (4, 2, 'Workout (minutes)', 45), -- Sneha in Workout Streak
            (5, 2, 'Workout (minutes)', 38), -- Vikram in Workout Streak
            (1, 2, 'Workout (minutes)', 40)  -- Aarav in Workout Streak
            """)
            print("Activity log data inserted")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database created and populated successfully!")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == '__main__':
    create_database_from_scratch() 