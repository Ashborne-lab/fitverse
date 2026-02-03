import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# ✅ DB Connection Function
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="@Hum42",
        database="fitness_manager_system"  # Updated database name
    )

# This is an alternative version of the app that works with the new schema
# without requiring changes to the MedalRewards table

# Function to check if the database has correct tables
def check_database_setup():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if necessary tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0].lower() for table in cursor.fetchall()]
        required_tables = ['user', 'challenge', 'challengeparticipation', 
                          'activitylog', 'leaderboard', 'medals', 'rewards']
        
        missing_tables = [table for table in required_tables if table.lower() not in tables]
        
        if missing_tables:
            st.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return False

# The rest of the file would be similar to streamlit_app.py but with
# adapted queries for the new schema. For brevity, I'm only including
# the key functions that need to change.

# Function to update leaderboard based on user activities
def update_leaderboard():
    # Connect to the database
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all challenge participants with their activities
    cursor.execute("""
        SELECT CP.User_Id, CP.ChallengeID, SUM(AL.ActivityData) as TotalPoints
        FROM ActivityLog AL
        JOIN ChallengeParticipation CP ON AL.User_Id = CP.User_Id AND AL.ChallengeID = CP.ChallengeID
        GROUP BY CP.User_Id, CP.ChallengeID
    """)
    
    participants = cursor.fetchall()
    
    for participant in participants:
        user_id, challenge_id, total_points = participant

        # Check if entry exists in leaderboard
        cursor.execute(
            "SELECT LeaderBoardID FROM LeaderBoard WHERE User_Id = %s AND ChallengeId = %s",
            (user_id, challenge_id)
        )
        leaderboard_entry = cursor.fetchone()
        
        if leaderboard_entry:
            # Update existing entry
            cursor.execute(
                "UPDATE LeaderBoard SET Points = %s WHERE LeaderBoardID = %s",
                (total_points, leaderboard_entry[0])
            )
        else:
            # Create new entry (rank will be updated later)
            cursor.execute(
                "INSERT INTO LeaderBoard (Points, Rank_, User_Id, ChallengeId) VALUES (%s, 999, %s, %s)",
                (total_points, user_id, challenge_id)
            )
    
    # Update all ranks for all challenges
    cursor.execute("""
        SELECT DISTINCT ChallengeId FROM LeaderBoard
    """)
    challenges = cursor.fetchall()
    
    for challenge in challenges:
        challenge_id = challenge[0]
        cursor.execute("""
            SET @rank = 0;
            UPDATE LeaderBoard
            JOIN (
                SELECT LeaderBoardID, (@rank := @rank + 1) as new_rank
                FROM LeaderBoard
                WHERE ChallengeId = %s
                ORDER BY Points DESC
            ) as ranked ON LeaderBoard.LeaderBoardID = ranked.LeaderBoardID
            SET LeaderBoard.Rank_ = ranked.new_rank
            WHERE LeaderBoard.ChallengeId = %s;
        """, (challenge_id, challenge_id))
    
    conn.commit()
    conn.close()

# Function to assign medals based on rank - modified for the new schema
def assign_medals():
    # Connect to the database
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all challenges
    cursor.execute("SELECT DISTINCT ChallengeId FROM LeaderBoard")
    challenges = cursor.fetchall()
    
    for challenge in challenges:
        challenge_id = challenge[0]
        
        # Get top 3 users in this challenge
        cursor.execute("""
            SELECT User_Id, Rank_ 
            FROM LeaderBoard 
            WHERE ChallengeId = %s AND Rank_ <= 3
            ORDER BY Rank_
        """, (challenge_id,))
        
        top_users = cursor.fetchall()
        
        for user_data in top_users:
            user_id, rank = user_data
            
            # Determine medal type
            if rank == 1:
                medal_type = 'Gold'
            elif rank == 2:
                medal_type = 'Silver'
            elif rank == 3:
                medal_type = 'Bronze'
            else:
                continue  # Skip if rank > 3
                
            # Create temporary table to track medal assignments if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temp_medal_assignments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    challenge_id INT,
                    medal_id INT,
                    UNIQUE KEY (user_id, challenge_id, medal_id)
                )
            """)
                
            # Check if medal type exists in Medals table
            cursor.execute("""
                SELECT MedalID 
                FROM Medals 
                WHERE Rank_ = %s AND MedalType = %s
            """, (rank, medal_type))
            
            medal_record = cursor.fetchone()
            
            if not medal_record:
                # Insert new medal type
                cursor.execute("""
                    INSERT INTO Medals (Rank_, MedalType) 
                    VALUES (%s, %s)
                """, (rank, medal_type))
                
                # Get the medal ID
                cursor.execute("SELECT LAST_INSERT_ID()")
                medal_id = cursor.fetchone()[0]
            else:
                medal_id = medal_record[0]
                
            # Check if this user already has this medal for this challenge in our temporary table
            cursor.execute("""
                SELECT id 
                FROM temp_medal_assignments 
                WHERE user_id = %s AND challenge_id = %s AND medal_id = %s
            """, (user_id, challenge_id, medal_id))
            
            medal_assignment_exists = cursor.fetchone() is not None
            
            if not medal_assignment_exists:
                # Record this medal assignment
                cursor.execute("""
                    INSERT IGNORE INTO temp_medal_assignments (user_id, challenge_id, medal_id)
                    VALUES (%s, %s, %s)
                """, (user_id, challenge_id, medal_id))
                
                # Get reward ID based on medal type
                cursor.execute("SELECT RewardID FROM Rewards WHERE RewardType = %s", (medal_type,))
                reward_data = cursor.fetchone()
                
                if reward_data:
                    reward_id = reward_data[0]
                    # Link medal to reward
                    cursor.execute("""
                        INSERT INTO MedalRewards (MedalID, RewardID) 
                        VALUES (%s, %s)
                    """, (medal_id, reward_id))
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to get medal count for a user using the temporary table approach
def get_user_medal_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if our temporary table exists
    cursor.execute("SHOW TABLES LIKE 'temp_medal_assignments'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT COUNT(DISTINCT medal_id) 
            FROM temp_medal_assignments 
            WHERE user_id = %s
        """, (user_id,))
    else:
        # If temporary table doesn't exist, return 0
        cursor.execute("SELECT 0")
    
    count = cursor.fetchone()[0] or 0
    cursor.close()
    conn.close()
    return count

# Function to get medals for a challenge
def get_challenge_medals(challenge_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if our temporary table exists
    cursor.execute("SHOW TABLES LIKE 'temp_medal_assignments'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT ta.user_id, m.MedalType 
            FROM temp_medal_assignments ta
            JOIN Medals m ON ta.medal_id = m.MedalID
            WHERE ta.challenge_id = %s
        """, (challenge_id,))
        medals = cursor.fetchall()
    else:
        medals = []
    
    cursor.close()
    conn.close()
    return medals

# Function to get user medals across all challenges
def get_user_medals(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if our temporary table exists
    cursor.execute("SHOW TABLES LIKE 'temp_medal_assignments'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT m.MedalType, c.Name_
            FROM temp_medal_assignments ta
            JOIN Medals m ON ta.medal_id = m.MedalID
            JOIN Challenge c ON ta.challenge_id = c.ChallengeID
            WHERE ta.user_id = %s
        """, (user_id,))
        medals = cursor.fetchall()
    else:
        medals = []
    
    cursor.close()
    conn.close()
    return medals

# Function to get all medal assignments
def get_all_medal_assignments():
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if our temporary table exists
    cursor.execute("SHOW TABLES LIKE 'temp_medal_assignments'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT m.MedalID, u.Name_, c.Name_, m.MedalType, m.Rank_
            FROM temp_medal_assignments ta
            JOIN Medals m ON ta.medal_id = m.MedalID
            JOIN User u ON ta.user_id = u.User_Id
            JOIN Challenge c ON ta.challenge_id = c.ChallengeID
            ORDER BY c.Name_, m.Rank_
        """)
        medals = cursor.fetchall()
    else:
        medals = []
    
    cursor.close()
    conn.close()
    return medals

# The rest of the app would follow a similar pattern, replacing direct Medal table queries with
# these helper functions that use the temporary tracking table. 