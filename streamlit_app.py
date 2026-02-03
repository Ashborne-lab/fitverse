import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import time

# ✅ DB Connection Function
def get_connection():
    # Use Streamlit secrets for database credentials
    # If specifically running locally with no secrets.toml, you might want a fallback,
    # but for cloud deployment, secrets are best.
    if "mysql" in st.secrets:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    else:
        # Fallback for local testing if secrets aren't set up
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="@Hum42",
            database="fitness_manager_system"
        )

# Add custom CSS styling
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            padding: 1rem;
        }

        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #202040, #543864);
        }

        /* Make the standard buttons invisible but clickable where we use custom buttons */
        .custom-button-container .stButton {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 10;
        }
        
        .custom-button-container {
            position: relative;
            margin-bottom: 15px;
        }

        /* From Uiverse.io by FColombati */
        .button {
          all: unset;
          cursor: pointer;
          -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
          position: relative;
          border-radius: 100em;
          background-color: rgba(0, 0, 0, 0.75);
          box-shadow:
            -0.15em -0.15em 0.15em -0.075em rgba(5, 5, 5, 0.25),
            0.0375em 0.0375em 0.0675em 0 rgba(5, 5, 5, 0.1);
        }

        .button::after {
          content: "";
          position: absolute;
          z-index: 0;
          width: calc(100% + 0.3em);
          height: calc(100% + 0.3em);
          top: -0.15em;
          left: -0.15em;
          border-radius: inherit;
          background: linear-gradient(
            -135deg,
            rgba(5, 5, 5, 0.5),
            transparent 20%,
            transparent 100%
          );
          filter: blur(0.0125em);
          opacity: 0.25;
          mix-blend-mode: multiply;
        }

        .button .button-outer {
          position: relative;
          z-index: 1;
          border-radius: inherit;
          transition: box-shadow 300ms ease;
          will-change: box-shadow;
          box-shadow:
            0 0.05em 0.05em -0.01em rgba(5, 5, 5, 1),
            0 0.01em 0.01em -0.01em rgba(5, 5, 5, 0.5),
            0.15em 0.3em 0.1em -0.01em rgba(5, 5, 5, 0.25);
        }

        .button:hover .button-outer {
          box-shadow:
            0 0 0 0 rgba(5, 5, 5, 1),
            0 0 0 0 rgba(5, 5, 5, 0.5),
            0 0 0 0 rgba(5, 5, 5, 0.25);
        }

        .button-inner {
          --inset: 0.035em;
          position: relative;
          z-index: 1;
          border-radius: inherit;
          padding: 1em 1.5em;
          background-image: linear-gradient(
            135deg,
            rgba(230, 230, 230, 1),
            rgba(180, 180, 180, 1)
          );
          transition:
            box-shadow 300ms ease,
            clip-path 250ms ease,
            background-image 250ms ease,
            transform 250ms ease;
          will-change: box-shadow, clip-path, background-image, transform;
          overflow: clip;
          clip-path: inset(0 0 0 0 round 100em);
          box-shadow:
                /* 1 */
            0 0 0 0 inset rgba(5, 5, 5, 0.1),
            /* 2 */ -0.05em -0.05em 0.05em 0 inset rgba(5, 5, 5, 0.25),
            /* 3 */ 0 0 0 0 inset rgba(5, 5, 5, 0.1),
            /* 4 */ 0 0 0.05em 0.2em inset rgba(255, 255, 255, 0.25),
            /* 5 */ 0.025em 0.05em 0.1em 0 inset rgba(255, 255, 255, 1),
            /* 6 */ 0.12em 0.12em 0.12em inset rgba(255, 255, 255, 0.25),
            /* 7 */ -0.075em -0.25em 0.25em 0.1em inset rgba(5, 5, 5, 0.25);
        }

        .button:hover .button-inner {
          clip-path: inset(
            clamp(1px, 0.0625em, 2px) clamp(1px, 0.0625em, 2px)
              clamp(1px, 0.0625em, 2px) clamp(1px, 0.0625em, 2px) round 100em
          );
          box-shadow:
                /* 1 */
            0.1em 0.15em 0.05em 0 inset rgba(5, 5, 5, 0.75),
            /* 2 */ -0.025em -0.03em 0.05em 0.025em inset rgba(5, 5, 5, 0.5),
            /* 3 */ 0.25em 0.25em 0.2em 0 inset rgba(5, 5, 5, 0.5),
            /* 4 */ 0 0 0.05em 0.5em inset rgba(255, 255, 255, 0.15),
            /* 5 */ 0 0 0 0 inset rgba(255, 255, 255, 1),
            /* 6 */ 0.12em 0.12em 0.12em inset rgba(255, 255, 255, 0.25),
            /* 7 */ -0.075em -0.12em 0.2em 0.1em inset rgba(5, 5, 5, 0.25);
        }

        .button .button-inner span {
          position: relative;
          z-index: 4;
          font-family: "Inter", sans-serif;
          letter-spacing: -0.05em;
          font-weight: 500;
          color: rgba(0, 0, 0, 0);
          background-image: linear-gradient(
            135deg,
            rgba(25, 25, 25, 1),
            rgba(75, 75, 75, 1)
          );
          -webkit-background-clip: text;
          background-clip: text;
          transition: transform 250ms ease;
          display: block;
          will-change: transform;
          text-shadow: rgba(0, 0, 0, 0.1) 0 0 0.1em;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }

        .button:hover .button-inner span {
          transform: scale(0.975);
        }

        .button:active .button-inner {
          transform: scale(0.975);
        }

        /* Challenge card styling */
        .card {
          position: relative;
          width: 220px;
          height: 320px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 25px;
          font-weight: bold;
          border-radius: 15px;
          cursor: pointer;
          overflow: hidden;
          box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }

        .card::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, #43cea2, #185a9d);
          opacity: 0.9;
          z-index: -1;
          transition: all 0.5s;
        }

        .card:hover::before {
          transform: scale(1.1);
        }

        .challenge-card {
          position: relative;
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: bold;
          border-radius: 15px;
          cursor: pointer;
          padding: 20px;
          margin-bottom: 20px;
          min-height: 200px;
          box-sizing: border-box;
          overflow: hidden;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
          background: white;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .challenge-card::before {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, #ff9a8b, #ff6a88, #ff99ac);
          opacity: 0.85;
          z-index: 0;
          transition: all 0.5s;
        }

        .challenge-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }

        .challenge-card:hover::before {
          opacity: 0.95;
        }

        .challenge-card-content {
          position: relative;
          z-index: 1;
          text-align: center;
          width: 100%;
          color: white;
          text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        }

        /* Loading animation */
        .wrapper {
          width: 200px;
          height: 60px;
          position: relative;
          z-index: 1;
          margin: 0 auto;
        }

        .circle {
          width: 20px;
          height: 20px;
          position: absolute;
          border-radius: 50%;
          background-color: #fff;
          left: 15%;
          transform-origin: 50%;
          animation: circle7124 .5s alternate infinite ease;
        }

        @keyframes circle7124 {
          0% {
            top: 60px;
            height: 5px;
            border-radius: 50px 50px 25px 25px;
            transform: scaleX(1.7);
          }

          40% {
            height: 20px;
            border-radius: 50%;
            transform: scaleX(1);
          }

          100% {
            top: 0%;
          }
        }

        .circle:nth-child(2) {
          left: 45%;
          animation-delay: .2s;
        }

        .circle:nth-child(3) {
          left: auto;
          right: 15%;
          animation-delay: .3s;
        }

        .shadow {
          width: 20px;
          height: 4px;
          border-radius: 50%;
          background-color: rgba(0,0,0,0.9);
          position: absolute;
          top: 62px;
          transform-origin: 50%;
          z-index: -1;
          left: 15%;
          filter: blur(1px);
          animation: shadow046 .5s alternate infinite ease;
        }

        @keyframes shadow046 {
          0% {
            transform: scaleX(1.5);
          }

          40% {
            transform: scaleX(1);
            opacity: .7;
          }

          100% {
            transform: scaleX(.2);
            opacity: .4;
          }
        }

        .shadow:nth-child(4) {
          left: 45%;
          animation-delay: .2s
        }

        .shadow:nth-child(5) {
          left: auto;
          right: 15%;
          animation-delay: .3s;
        }

        .stButton>button {
            color: white;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(0, 0, 0, 0.2);
            background: linear-gradient(135deg, #764ba2, #667eea);
        }

        .stTextInput>div>input {
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #ddd;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .stSelectbox>div {
            border-radius: 8px;
        }
        
        h1, h2, h3 {
            color: #333;
            font-weight: 600;
        }
        
        h1 {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            font-weight: 700;
        }
        
        .user-welcome {
            background: linear-gradient(135deg, #a18cd1, #fbc2eb);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            color: white;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        .sidebar-content {
            padding: 15px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            margin-bottom: 15px;
            color: white;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Leaderboard styling */
        .leaderboard-card {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }

        .leaderboard-card h2, .leaderboard-card h3 {
            color: white;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }

        .podium-card {
            text-align: center;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            transform: perspective(1000px);
        }

        .podium-card:hover {
            transform: perspective(1000px) translateY(-5px) rotateX(5deg);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
        }

        .gold-card {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #333;
        }

        .silver-card {
            background: linear-gradient(135deg, #E0E0E0, #A0A0A0);
            color: #333;
        }

        .bronze-card {
            background: linear-gradient(135deg, #CD7F32, #A0522D);
            color: white;
        }
        
        /* Dashboard Cards */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
        }
        
        .metric-card .value {
            font-size: 32px;
            font-weight: 700;
            color: #6a11cb;
            margin: 10px 0;
        }
        
        .metric-card .label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-card .icon {
            font-size: 28px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Activity card */
        .activity-card {
            background: white;
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 10px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
            transition: all 0.2s ease;
            border-left: 4px solid #764ba2;
        }
        
        .activity-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.12);
        }
        
        .activity-type {
            font-weight: 600;
            color: #333;
        }
        
        .activity-points {
            color: #6a11cb;
            font-weight: 600;
        }
        
        .activity-challenge {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #a18cd1, #fbc2eb);
            color: white;
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div {
            background-color: #6a11cb;
            background-image: linear-gradient(135deg, #667eea, #764ba2);
        }
    </style>
    """, unsafe_allow_html=True)

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
            "SELECT LeaderBoardID FROM LeaderBoard WHERE User_Id = %s AND ChallengeID = %s",
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
                "INSERT INTO LeaderBoard (Points, Rank_, User_Id, ChallengeID) VALUES (%s, 999, %s, %s)",
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
                WHERE ChallengeID = %s
                ORDER BY Points DESC
            ) as ranked ON LeaderBoard.LeaderBoardID = ranked.LeaderBoardID
            SET LeaderBoard.Rank_ = ranked.new_rank
            WHERE LeaderBoard.ChallengeID = %s;
        """, (challenge_id, challenge_id))
    
    conn.commit()
    conn.close()

# Function to assign medals based on rank
def assign_medals():
    try:
        # Connect to the database
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch all challenges
        cursor.execute("SELECT DISTINCT ChallengeID FROM LeaderBoard")
        challenges = cursor.fetchall()
        
        for challenge in challenges:
            challenge_id = challenge[0]
            
            # Get top 3 users in this challenge
            cursor.execute("""
                SELECT User_Id, Rank_ 
                FROM LeaderBoard 
                WHERE ChallengeID = %s AND Rank_ <= 3
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
                
                try:
                    # Check if this user already has this medal for this challenge
                    cursor.execute("""
                        SELECT MedalRewardID 
                        FROM MedalRewards 
                        WHERE User_Id = %s AND ChallengeID = %s AND MedalID = %s
                    """, (user_id, challenge_id, medal_id))
                    
                    medal_reward_exists = cursor.fetchone() is not None
                except Exception as e:
                    # If MedalRewards doesn't have User_Id, try different approach
                    try:
                        cursor.execute("""
                            SELECT MedalRewardID 
                            FROM MedalRewards mr
                            JOIN LeaderBoard lb ON mr.ChallengeID = lb.ChallengeID AND lb.User_Id = %s
                            WHERE mr.ChallengeID = %s AND mr.MedalID = %s
                        """, (user_id, challenge_id, medal_id))
                        
                        medal_reward_exists = cursor.fetchone() is not None
                    except Exception as e2:
                        # If all checks fail, assume medal doesn't exist
                        medal_reward_exists = False
                
                if not medal_reward_exists:
                    # Get reward ID based on medal type
                    cursor.execute("SELECT RewardID FROM Rewards WHERE RewardType = %s", (medal_type,))
                    reward_data = cursor.fetchone()
                    
                    if reward_data:
                        reward_id = reward_data[0]
                        try:
                            # Try to insert with User_Id
                            cursor.execute("""
                                INSERT INTO MedalRewards (MedalID, RewardID, User_Id, ChallengeID) 
                                VALUES (%s, %s, %s, %s)
                            """, (medal_id, reward_id, user_id, challenge_id))
                        except Exception as e:
                            # If that fails, insert without User_Id
                            cursor.execute("""
                                INSERT INTO MedalRewards (MedalID, RewardID, ChallengeID) 
                                VALUES (%s, %s, %s)
                            """, (medal_id, reward_id, challenge_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        # If the entire function fails, log the error but don't crash
        print(f"Error assigning medals: {e}")

# Log activity and update leaderboard
def log_activity_and_update_leaderboard(user_id, challenge_id, activity_type, activity_data):
    # Log the activity
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ActivityLog (User_Id, ChallengeID, ActivityType, ActivityData)
        VALUES (%s, %s, %s, %s)
    """, (user_id, challenge_id, activity_type, activity_data))
    
    conn.commit()
    cursor.close()
    conn.close()

    # Update leaderboard and assign medals
    update_leaderboard()
    assign_medals()
    
    return True

# Admin Challenge Creator UI
def create_challenge_ui():
    st.subheader("🗓️ Create New Challenge")
    name = st.text_input("Challenge Description (No spaces)")  # Normalized format
    start = st.date_input("Start Date")
    end = st.date_input("End Date")

    if st.button("Create Challenge"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Challenge (Name_, StartDate, EndDate) VALUES (%s, %s, %s)",
                (name.strip().replace(" ", "_"), start, end)
            )
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Challenge created successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# User Activity Logger UI
def activity_logger_ui(user_id):
    st.subheader("📌 Log Your Activity")

    # Get active challenges
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ChallengeID, Name_ FROM Challenge")
    challenges = cursor.fetchall()
    cursor.close()
    conn.close()

    if not challenges:
        st.warning("No challenges found.")
        return

    challenge_dict = {name: cid for cid, name in challenges}
    selected_challenge = st.selectbox("Select Challenge", list(challenge_dict.keys()))
    activity_type = st.text_input("Activity Type (e.g., Running, Cycling)")
    activity_data = st.number_input("Activity Data (e.g., distance in km)", min_value=0.0)

    if st.button("Submit Activity"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Remove LogTimestamp from the insert since it's not in the table
            cursor.execute("""
                INSERT INTO ActivityLog (User_Id, ChallengeID, ActivityType, ActivityData) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, challenge_dict[selected_challenge], activity_type, activity_data))
            conn.commit()
            
            # Update leaderboard and assign medals
            update_leaderboard()
            assign_medals()
            
            cursor.close()
            conn.close()
            st.success("✅ Activity logged successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Create separate landing pages for different user types
def user_landing_page(user_id, user_name):
    # Header with welcome message
    st.markdown(f"""
    <div class="user-welcome">
        <h2 style="color:white; margin:0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">Welcome to FitVerse, <span style="font-weight:700;">{user_name}</span>! 👋</h2>
        <p style="margin-top:10px; font-size:16px; opacity:0.9;">Track your fitness journey and compete in challenges</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats 
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get user stats
    cursor.execute("SELECT COUNT(*) FROM ActivityLog WHERE User_Id = %s", (user_id,))
    activity_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(ActivityData) FROM ActivityLog WHERE User_Id = %s", (user_id,))
    total_points = cursor.fetchone()[0] or 0
    
    # Check medals count with error handling
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM MedalRewards mr
            WHERE mr.User_Id = %s
        """, (user_id,))
        medals_count = cursor.fetchone()[0] or 0
    except Exception as e:
        # Fallback if MedalRewards doesn't have User_Id column
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM MedalRewards mr
                JOIN LeaderBoard l ON mr.ChallengeID = l.ChallengeID
                WHERE l.User_Id = %s
            """, (user_id,))
            medals_count = cursor.fetchone()[0] or 0
        except Exception as e2:
            # If all queries fail, set medals to 0
            medals_count = 0
    
    cursor.execute("SELECT COUNT(*) FROM ChallengeParticipation WHERE User_Id = %s", (user_id,))
    challenges_joined = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    # Display stats in a visually appealing way
    st.markdown("### Your Fitness Dashboard")
    
    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🏆</div>
            <div class="value">{challenges_joined}</div>
            <div class="label">Challenges</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📊</div>
            <div class="value">{activity_count}</div>
            <div class="label">Activities</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">⭐</div>
            <div class="value">{f"{total_points:.1f}" if total_points else "0"}</div>
            <div class="label">Points</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🏅</div>
            <div class="value">{medals_count}</div>
            <div class="label">Medals</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area in tabs
    tab1, tab2, tab3 = st.tabs(["Active Challenges", "Recent Activities", "Quick Log"])
    
    with tab1:
        st.subheader("Active Challenges")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ChallengeID, c.Name_, c.StartDate, c.EndDate, 
                   CASE WHEN cp.ParticipationID IS NOT NULL THEN 1 ELSE 0 END as Joined
            FROM Challenge c
            LEFT JOIN ChallengeParticipation cp ON c.ChallengeID = cp.ChallengeID AND cp.User_Id = %s
            WHERE c.EndDate >= CURDATE()
            ORDER BY c.StartDate ASC
        """, (user_id,))
        
        active_challenges = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if active_challenges:
            # Display challenges in a grid
            challenge_cols = st.columns(3)
            for i, challenge in enumerate(active_challenges):
                with challenge_cols[i % 3]:
                    joined_status = "✅ Joined" if challenge[4] else "⭕ Not Joined"
                    joined_color = "#00796b" if challenge[4] else "#f44336"
                    
                    st.markdown(f"""
                    <div class="challenge-card">
                        <div class="challenge-card-content">
                            <h4 style="margin:0 0 10px 0; font-weight:700;">{challenge[1]}</h4>
                            <p style="margin:0; font-size:14px;">📅 {challenge[2].strftime('%b %d')} - {challenge[3].strftime('%b %d, %Y')}</p>
                            <p style="margin:8px 0 0 0; font-weight:bold;">{joined_status}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not challenge[4]:  # If not joined
                        if st.button("Join Now", key=f"join_{challenge[0]}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO ChallengeParticipation (User_Id, ChallengeID) VALUES (%s, %s)",
                                (user_id, challenge[0])
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success("Challenge joined successfully!")
                            st.rerun()
                    else:  # If already joined
                        if st.button("Log Activity", key=f"log_{challenge[0]}"):
                            st.session_state.selected_challenge = challenge[0]
                            st.session_state.selected_challenge_name = challenge[1]
                            st.session_state.show_activity_logger = True
                            st.rerun()
        else:
            st.info("No active challenges available. Check back soon!")
    
    with tab2:
        st.subheader("Your Recent Activities")
        conn = get_connection()
        cursor = conn.cursor()
        # Note: Don't select LogTimestamp if it doesn't exist in the table
        cursor.execute("""
            SELECT a.ActivityType, a.ActivityData, c.Name_
            FROM ActivityLog a
            JOIN Challenge c ON a.ChallengeID = c.ChallengeID
            WHERE a.User_Id = %s
            ORDER BY a.LogID DESC
            LIMIT 5
        """, (user_id,))
        
        recent_activities = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if recent_activities:
            for activity in recent_activities:
                st.markdown(f"""
                <div class="activity-card">
                    <div class="activity-type">{activity[0]}</div>
                    <div class="activity-points">{activity[1]} points</div>
                    <div class="activity-challenge">Challenge: {activity[2]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't logged any activities yet. Start your fitness journey today!")
            
            if st.button("Log Your First Activity"):
                st.session_state.show_activity_logger = True
                st.rerun()
    
    with tab3:
        st.subheader("Quick Activity Log")
        
        # Get user's enrolled challenges
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ChallengeID, c.Name_ 
            FROM Challenge c
            JOIN ChallengeParticipation cp ON c.ChallengeID = cp.ChallengeID
            WHERE cp.User_Id = %s
        """, (user_id,))
        user_challenges = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if user_challenges:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                selected_challenge = st.selectbox(
                    "Select Challenge",
                    options=user_challenges,
                    format_func=lambda x: x[1]
                )
            with col2:
                quick_activity = st.selectbox("Activity Type", ["Running", "Walking", "Cycling", "Weightlifting", "Swimming", "Other"])
            with col3:
                quick_value = st.number_input("Value", min_value=0.1, step=0.1, value=1.0)
            
            if st.button("Log Activity", key="quick_log"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO ActivityLog (User_Id, ChallengeID, ActivityType, ActivityData) 
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, selected_challenge[0], quick_activity, quick_value))
                    conn.commit()
                    
                    # Update leaderboard and assign medals
                    update_leaderboard()
                    assign_medals()
                    
                    cursor.close()
                    conn.close()
                    st.success("Activity logged successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("You need to join a challenge before logging activities.")
            if st.button("See Available Challenges"):
                st.rerun()

def admin_landing_page(admin_id, admin_name):
    # Header with welcome message
    st.markdown(f"""
    <div style="background-color:#b3e5fc; padding:20px; border-radius:10px; margin-bottom:30px;">
        <h2 style="color:#01579b; margin:0;">Admin Dashboard - Welcome, <span style="color:#0277bd">{admin_name}</span>! 🧑‍💼</h2>
        <p style="margin-top:5px; font-size:16px;">Manage challenges, users and monitor activity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats 
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get admin stats
    cursor.execute("SELECT COUNT(*) FROM User")
    user_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM Challenge")
    challenge_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM ActivityLog")
    activity_count = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(ActivityData) FROM ActivityLog
    """)
    total_points = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    # Display stats in a visually appealing way
    st.markdown("### System Overview")
    
    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", user_count)
    with col2:
        st.metric("🏆 Challenges", challenge_count)
    with col3:
        st.metric("📊 Activities", activity_count)
    with col4:
        st.metric("⭐ Total Points", f"{total_points:.1f}" if total_points else "0")
    
    # Main content area in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Manage Challenges", "User Management", "Activity Logs", "Create Challenge"])
    
    with tab1:
        st.subheader("All Challenges")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ChallengeID, c.Name_, c.StartDate, c.EndDate, 
                   COUNT(DISTINCT cp.User_Id) as Participants,
                   SUM(a.ActivityData) as TotalPoints
            FROM Challenge c
            LEFT JOIN ChallengeParticipation cp ON c.ChallengeID = cp.ChallengeID
            LEFT JOIN ActivityLog a ON c.ChallengeID = a.ChallengeID
            GROUP BY c.ChallengeID
            ORDER BY c.StartDate DESC
        """)
        
        all_challenges = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if all_challenges:
            # Create a DataFrame for better display
            challenge_df = pd.DataFrame(
                all_challenges, 
                columns=["ID", "Name", "Start Date", "End Date", "Participants", "Total Points"]
            )
            challenge_df["Total Points"] = challenge_df["Total Points"].fillna(0)
            
            # Add status column
            today = datetime.now().date()
            challenge_df["Status"] = challenge_df.apply(
                lambda x: "Active" if x["Start Date"] <= today <= x["End Date"] 
                else ("Upcoming" if x["Start Date"] > today else "Completed"),
                axis=1
            )
            
            st.dataframe(challenge_df)
            
            # Challenge selection for leaderboard update
            st.subheader("Update Challenge Leaderboard")
            selected_challenge_id = st.selectbox(
                "Select challenge",
                options=all_challenges,
                format_func=lambda x: x[1]
            )[0]
            
            if st.button("Update Leaderboard & Assign Medals"):
                try:
                    update_leaderboard()
                    assign_medals()
                    st.success("Leaderboard updated and medals assigned successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No challenges found. Create your first challenge!")
    
    with tab2:
        st.subheader("User Management")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.User_Id, u.FirstName, u.LastName, u.Email, u.RegistrationDate,
                   COUNT(DISTINCT cp.ChallengeID) as JoinedChallenges,
                   COUNT(DISTINCT a.LogID) as Activities,
                   IFNULL(SUM(a.ActivityData), 0) as TotalPoints
            FROM User u
            LEFT JOIN ChallengeParticipation cp ON u.User_Id = cp.User_Id
            LEFT JOIN ActivityLog a ON u.User_Id = a.User_Id
            GROUP BY u.User_Id
            ORDER BY u.RegistrationDate DESC
        """)
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if users:
            # Create a DataFrame for better display
            users_df = pd.DataFrame(
                users, 
                columns=["ID", "First Name", "Last Name", "Email", "Registration Date", "Challenges", "Activities", "Points"]
            )
            st.dataframe(users_df)
            
            # Registration trend
            st.subheader("User Registration Trend")
            users_df['Month'] = pd.to_datetime(users_df['Registration Date']).dt.strftime('%Y-%m')
            registration_counts = users_df.groupby('Month').size().reset_index(name='Count')
            st.bar_chart(registration_counts.set_index('Month'))
        else:
            st.info("No users found in the system.")
    
    with tab3:
        st.subheader("Recent Activity Logs")
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT a.LogID, u.FirstName, u.LastName, c.Name_, a.ActivityType, a.ActivityData, a.LogTimestamp
                FROM ActivityLog a
                JOIN User u ON a.User_Id = u.User_Id
                JOIN Challenge c ON a.ChallengeID = c.ChallengeID
                ORDER BY a.LogTimestamp DESC
                LIMIT 50
            """)
            logs = cursor.fetchall()
            column_names = ["ID", "First Name", "Last Name", "Challenge", "Activity Type", "Value", "Timestamp"]
        except Exception as e:
            # If LogTimestamp doesn't exist, use LogID for ordering
            cursor.execute("""
                SELECT a.LogID, u.FirstName, u.LastName, c.Name_, a.ActivityType, a.ActivityData
                FROM ActivityLog a
                JOIN User u ON a.User_Id = u.User_Id
                JOIN Challenge c ON a.ChallengeID = c.ChallengeID
                ORDER BY a.LogID DESC
                LIMIT 50
            """)
            logs = cursor.fetchall()
            column_names = ["ID", "First Name", "Last Name", "Challenge", "Activity Type", "Value"]
            
        cursor.close()
        conn.close()
        
        if logs:
            logs_df = pd.DataFrame(logs, columns=column_names)
            st.dataframe(logs_df)
            
            # Activity distribution by type
            st.subheader("Activity Type Distribution")
            try:
                activity_counts = logs_df.groupby('Activity Type')['Value'].sum().reset_index()
                st.bar_chart(activity_counts.set_index('Activity Type'))
            except Exception as e:
                st.error(f"Error displaying activity chart: {e}")
        else:
            st.info("No activity logs found.")

    with tab4:
        create_challenge_ui()

# Set page config
st.set_page_config(page_title="FitVerse - Fitness Challenge App", page_icon="🏋️", layout="wide")

# Apply custom CSS
local_css()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.is_admin = False
    st.session_state.show_challenge_creator = False
    st.session_state.show_activity_logger = False
    st.session_state.show_profile = False

# Sidebar for navigation
st.sidebar.title("FitVerse")

# Change menu options based on login status
if st.session_state.logged_in:
    menu_options = ["Home", "Challenges", "Log Activity", "Leaderboard", "Admin"]
else:
    menu_options = ["Home", "Login", "Register", "Challenges", "Leaderboard", "Admin"]

menu = st.sidebar.selectbox("Menu", menu_options)

# Show logged-in user info
if st.session_state.logged_in:
    st.sidebar.markdown(f"""
    <div class="sidebar-content">
        <p>Logged in as: <b>{st.session_state.user_name}</b></p>
        <p>{'Admin Account' if st.session_state.is_admin else 'User Account'}</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Display quick action buttons based on user role
    if st.session_state.is_admin:
        if st.sidebar.button("➕ Create Challenge"):
            st.session_state.show_challenge_creator = True
            st.session_state.show_activity_logger = False
            st.session_state.show_profile = False
            st.rerun()
    else:
        if st.sidebar.button("📝 Log Activity"):
            st.session_state.show_activity_logger = True
            st.session_state.show_challenge_creator = False
            st.session_state.show_profile = False
            st.rerun()
    
    # Profile button for all users
    if st.sidebar.button("👤 My Profile"):
        st.session_state.show_profile = True
        st.session_state.show_activity_logger = False
        st.session_state.show_challenge_creator = False
        st.rerun()
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.is_admin = False
        st.session_state.show_challenge_creator = False
        st.session_state.show_activity_logger = False
        st.session_state.show_profile = False
        st.query_params.update(menu="Home")
        st.rerun()

# Add database connection test at the bottom of sidebar
st.sidebar.markdown("---")
with st.sidebar.expander("Database Connection Test"):
    if st.button("Test Connection"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            st.success(f"✅ Connected to MySQL version: {version[0]}")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
            st.info("Check your database credentials in the connection function.")
    
    # Show connection details
    st.write("**Connection Details:**")
    st.code("""
    host: 127.0.0.1
    user: root
    password: @Hum42
    database: fitness_manager_system
    """)

# Helper function to show challenge cards
def show_challenge_cards(challenges):
    cols = st.columns(3)
    for i, challenge in enumerate(challenges):
        with cols[i % 3]:
            with st.container():
                card_id = f"card_{challenge[0]}"
                challenge_name = challenge[1]
                start_date = challenge[2].strftime('%b %d, %Y')
                end_date = challenge[3].strftime('%b %d, %Y')
                
                # Use the new card styling with hover effects
                st.markdown(f"""
                <div class="challenge-card" id="{card_id}">
                    <div class="challenge-card-content">
                        <h3 style="color: #1e6091; font-weight: bold;">{challenge_name}</h3>
                        <p style="color: #333333; font-size: 16px; font-weight: 500;">
                            📅 {start_date} - {end_date}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.logged_in:
                    # Check if user already joined this challenge
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT * FROM ChallengeParticipation WHERE User_Id = %s AND ChallengeID = %s", 
                        (st.session_state.user_id, challenge[0])
                    )
                    already_joined = cursor.fetchone() is not None
                    cursor.close()
                    conn.close()
                    
                    # Custom button styling using the button class
                    if already_joined:
                        st.markdown("""
                        <div style="margin-bottom: 10px;">
                            <span style="background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px;">
                                ✅ Joined
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Log Activity", key=f"log_{challenge[0]}"):
                            st.session_state.selected_challenge = challenge[0]
                            st.session_state.selected_challenge_name = challenge[1]
                            # Show loading animation before page transition
                            show_loading_animation()
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        if st.button("Join Challenge", key=f"join_{challenge[0]}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO ChallengeParticipation (User_Id, ChallengeID) VALUES (%s, %s)",
                                (st.session_state.user_id, challenge[0])
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success("Challenge joined successfully!")
                            # Show loading animation
                            show_loading_animation()
                            time.sleep(0.5)
                            st.rerun()
                else:
                    st.info("Login to join this challenge")
                
                # Wrap the "View Leaderboard" button in custom styling
                st.markdown("""
                <div class="custom-button-container">
                    <button class="button">
                      <div class="button-outer">
                        <div class="button-inner">
                          <span>View Leaderboard</span>
                        </div>
                      </div>
                    </button>
                </div>
                """, unsafe_allow_html=True)
                
                # Since we can't directly handle clicks on custom HTML elements, 
                # we still need a regular button, but we can hide it with CSS
                if st.button("View Leaderboard", key=f"view_{challenge[0]}", help="View the leaderboard for this challenge"):
                    st.session_state.selected_challenge = challenge[0]
                    st.session_state.selected_challenge_name = challenge[1]
                    # Update the menu in session state
                    st.query_params.update(menu="Leaderboard")
                    show_loading_animation()
                    time.sleep(0.5)  # A brief delay
                    st.rerun()

# Add a loading animation component function
def show_loading_animation():
    st.markdown("""
    <div class="wrapper">
        <div class="circle"></div>
        <div class="circle"></div>
        <div class="circle"></div>
        <div class="shadow"></div>
        <div class="shadow"></div>
        <div class="shadow"></div>
    </div>
    """, unsafe_allow_html=True)

# Home Page
if menu == "Home":
    # Check if user is logged in, show proper landing page
    if st.session_state.logged_in:
        if st.session_state.is_admin:
            # Show admin landing page
            admin_landing_page(st.session_state.user_id, st.session_state.user_name)
        else:
            # Show user landing page
            user_landing_page(st.session_state.user_id, st.session_state.user_name)
            
            # Show activity logger if requested
            if st.session_state.get('show_activity_logger', False):
                activity_logger_ui(st.session_state.user_id)
    # If not logged in, show regular home page
    else:
        st.title("🏋️ Welcome to FitVerse")
        st.write("Join fitness challenges, track your progress, and compete with friends!")
        
        # Display some active challenges
        st.subheader("Active Challenges")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT ChallengeID, Name_, StartDate, EndDate FROM Challenge")
            challenges = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if challenges:
                show_challenge_cards(challenges)
            else:
                st.info("No active challenges at the moment.")
        except Exception as e:
            st.error(f"Error connecting to database: {e}")

# Login Page
elif menu == "Login":
    st.title("Login")
    
    with st.form("login_form"):
        # Use strip() to remove whitespace and lower() for case-insensitive matching
        email = st.text_input("Email").strip().lower()
        password = st.text_input("Password", type="password").strip()
        
        admin_login = st.checkbox("Login as Admin")
        
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                if admin_login:
                    # Use LOWER() in SQL to make case-insensitive comparison
                    cursor.execute("SELECT Admin_id, FirstName, LastName, Password_ FROM Admin WHERE LOWER(Email) = %s", (email,))
                else:
                    # Use LOWER() in SQL to make case-insensitive comparison
                    cursor.execute("SELECT User_Id, FirstName, LastName, Password_ FROM User WHERE LOWER(Email) = %s", (email,))
                
                user = cursor.fetchone()
                
                # Debug information in a collapsible section
                with st.expander("Debug Info (Click to expand)"):
                    st.write(f"Email entered: {email}")
                    st.write(f"Admin login: {admin_login}")
                    if user:
                        st.write(f"User found: ID={user[0]}, Name={user[1]} {user[2]}")
                        st.write(f"Password match: {user[3] == password}")
                    else:
                        st.write("No user found with this email.")
                
                cursor.close()
                conn.close()
                
                if user and user[3] == password:  # Simple password check (no hashing for demo)
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = f"{user[1]} {user[2]}"
                    st.session_state.is_admin = admin_login
                    st.session_state.show_profile = True  # Show profile after login
                    
                    # Show loading animation
                    show_loading_animation()
                    
                    # Redirect to home page after a short delay
                    st.success("Login successful! Redirecting to home page...")
                    time.sleep(1)  # Short delay for loading animation
                    st.query_params.update(menu="Home")  # Set menu to Home explicitly
                    st.rerun()  # Redirect to home page after login
                else:
                    if not user:
                        st.error(f"No account found with email: {email}")
                    else:
                        st.error("Invalid password. Please try again.")
            except Exception as e:
                st.error(f"Error during login: {e}")
                st.error("Please check your database connection settings.")
    
    # Register option with a clear call-to-action button
    st.write("Don't have an account?")
    if st.button("Register a New Account"):
        st.query_params.update(menu="Register")
        st.rerun()

# Register Page
elif menu == "Register":
    # Redirect logged-in users away from Register page
    if st.session_state.logged_in:
        st.query_params.update(menu="Home")
        st.rerun()
    
    st.title("Create an Account")
    
    with st.form("register_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        # Use strip() and lower() for consistent email storage
        email = st.text_input("Email").strip().lower()
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password").strip()
        confirm_password = st.text_input("Confirm Password", type="password").strip()
        
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match")
            elif not first_name or not last_name or not email or not phone or not password:
                st.error("All fields are required")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # Check if email already exists - case insensitive
                    cursor.execute("SELECT COUNT(*) FROM User WHERE LOWER(Email) = %s", (email,))
                    if cursor.fetchone()[0] > 0:
                        st.error("Email is already registered")
                    else:
                        # Show loading animation while registering
                        show_loading_animation()
                        st.info("Creating your account... Please wait.")
                        
                        # Add registration date as current date
                        current_date = datetime.now().strftime('%Y-%m-%d')
                        
                        # Debug the values being inserted
                        with st.expander("Debug Registration Data"):
                            st.write(f"First Name: {first_name}")
                            st.write(f"Last Name: {last_name}")
                            st.write(f"Email: {email}")
                            st.write(f"Phone: {phone}")
                            st.write(f"Registration Date: {current_date}")
                        
                        try:
                            cursor.execute(
                                "INSERT INTO User (FirstName, LastName, Email, Phone_no, Password_, RegistrationDate) VALUES (%s, %s, %s, %s, %s, %s)",
                                (first_name, last_name, email, phone, password, current_date)
                            )
                            conn.commit()
                            
                            # Get the newly created user_id
                            user_id = cursor.lastrowid
                            
                            # Set login session
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.user_name = f"{first_name} {last_name}"
                            st.session_state.is_admin = False
                            
                            # Show success message with loading animation
                            st.success("Registration successful! Redirecting to home page...")
                            show_loading_animation()
                            time.sleep(1)  # Delay for animation
                            
                            # Redirect to home
                            st.query_params.update(menu="Home")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error during registration: {e}")
                            st.info("Please try different information or contact support.")
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Error connecting to database: {e}")
                    st.info("Please try again later or contact support for assistance.")
    
    # Show the SQL structure for debugging
    with st.expander("User Table Structure (For Admin Reference)"):
        st.code("""
        CREATE TABLE User (
            User_Id INT PRIMARY KEY AUTO_INCREMENT,
            FirstName VARCHAR(50) NOT NULL,
            LastName VARCHAR(50) NOT NULL,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Phone_no BIGINT,
            Password_ VARCHAR(20) NOT NULL,
            RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """, language="sql")

# Challenges Page
elif menu == "Challenges":
    st.title("Fitness Challenges")
    
    if st.session_state.logged_in and not st.session_state.is_admin:
        # Create new challenge button
        if st.button("Create New Challenge"):
            st.session_state.creating_challenge = True
    
    # Create Challenge Form
    if st.session_state.logged_in and st.session_state.get('creating_challenge', False):
        st.subheader("Create New Challenge")
        with st.form("challenge_form"):
            name = st.text_input("Challenge Name")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            submit = st.form_submit_button("Create Challenge")
            
            if submit:
                if not name or end_date <= start_date:
                    st.error("Please check your inputs")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Challenge (Name_, StartDate, EndDate) VALUES (%s, %s, %s)",
                            (name, start_date, end_date)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Challenge created successfully!")
                        st.session_state.creating_challenge = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    # Display challenges
    st.subheader("All Challenges")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ChallengeID, Name_, StartDate, EndDate FROM Challenge")
        challenges = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if challenges:
            show_challenge_cards(challenges)
        else:
            st.info("No challenges found.")
    except Exception as e:
        st.error(f"Error: {e}")

# Log Activity Page
elif menu == "Log Activity":
    st.title("Log Fitness Activity")
    
    if not st.session_state.logged_in:
        st.warning("Please login to log your activities")
    else:
        # Get user's challenges
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ChallengeID, c.Name_ 
            FROM Challenge c
            JOIN ChallengeParticipation cp ON c.ChallengeID = cp.ChallengeID
            WHERE cp.User_Id = %s
        """, (st.session_state.user_id,))
        user_challenges = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not user_challenges:
            st.warning("You haven't joined any challenges yet. Join a challenge first!")
        else:
            # Display progress for challenges
            st.subheader("Your Challenge Progress")
            progress_cols = st.columns(len(user_challenges))
            
            for i, challenge in enumerate(user_challenges):
                with progress_cols[i % len(progress_cols)]:
                    st.markdown(f"#### {challenge[1]}")
                    
                    # Get user's total points for this challenge
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT SUM(ActivityData) FROM ActivityLog 
                        WHERE User_Id = %s AND ChallengeID = %s
                    """, (st.session_state.user_id, challenge[0]))
                    total = cursor.fetchone()[0] or 0
                    cursor.close()
                    conn.close()
                    
                    # Set target points (this could be configurable in the future)
                    target = 1000
                    progress = min(total/target, 1.0)
                    st.progress(progress)
                    st.caption(f"Your progress: {total:.1f} / {target} points")
            
            # Activity logging form
            st.subheader("Log New Activity")
            with st.form("activity_form"):
                # Pre-select challenge if coming from a challenge card
                if 'selected_challenge' in st.session_state:
                    default_idx = next((i for i, c in enumerate(user_challenges) if c[0] == st.session_state.selected_challenge), 0)
                else:
                    default_idx = 0
                
                challenge = st.selectbox(
                    "Select Challenge", 
                    options=user_challenges,
                    format_func=lambda x: x[1],
                    index=default_idx
                )
                
                activity_type = st.text_input("Activity Type (e.g., Steps, Distance, Reps)")
                activity_data = st.number_input("Activity Value", min_value=0.1, step=0.1)
                
                submit = st.form_submit_button("Log Activity")
                
                if submit:
                    if not activity_type or activity_data <= 0:
                        st.error("Please check your inputs")
                    else:
                        try:
                            # Use the new function to log activity and update leaderboard
                            success = log_activity_and_update_leaderboard(
                                st.session_state.user_id, 
                                challenge[0], 
                                activity_type, 
                                activity_data
                            )
                            
                            if success:
                                st.success("Activity logged successfully!")
                                if 'selected_challenge' in st.session_state:
                                    del st.session_state.selected_challenge
                                    del st.session_state.selected_challenge_name
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            # Activity trend chart
            st.subheader("Your Activity Trend")
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT DATE(LogTimestamp) as date, SUM(ActivityData) as total
                    FROM ActivityLog
                    WHERE User_Id = %s
                    GROUP BY DATE(LogTimestamp)
                    ORDER BY date
                """, (st.session_state.user_id,))
                activity_data = cursor.fetchall()
            except Exception as e:
                # If LogTimestamp column doesn't exist, use LogID as a proxy for time ordering
                cursor.execute("""
                    SELECT LogID as date_proxy, ActivityData as total
                    FROM ActivityLog
                    WHERE User_Id = %s
                    ORDER BY LogID
                """, (st.session_state.user_id,))
                activity_data = cursor.fetchall()
            
            cursor.close()
            conn.close()

            if activity_data:
                try:
                    chart_data = pd.DataFrame(
                        activity_data,
                        columns=['Date', 'Activity']
                    )
                    st.line_chart(chart_data.set_index('Date'))
                except Exception as e:
                    st.error(f"Error displaying activity chart: {e}")
                    st.info("Activity data might be in an unexpected format.")
            else:
                st.info("Start logging activities to see your trend!")
            
            # Activity examples
            st.subheader("Activity Examples")
            cols = st.columns(3)
            with cols[0]:
                st.markdown("### 🚶 Steps")
                st.write("Record your daily step count")
            with cols[1]:
                st.markdown("### 🏃 Distance")
                st.write("Log your running/walking distance (km)")
            with cols[2]:
                st.markdown("### 🏋️ Weight Training")
                st.write("Track weight lifted or reps completed")

# Leaderboard Page
elif menu == "Leaderboard":
    st.title("Leaderboard")
    
    # Get challenges for the dropdown
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ChallengeID, Name_ FROM Challenge")
    all_challenges = cursor.fetchall()
    
    if not all_challenges:
        st.warning("No challenges found")
    else:
        # Select challenge
        if 'selected_challenge' in st.session_state:
            default_idx = next((i for i, c in enumerate(all_challenges) if c[0] == st.session_state.selected_challenge), 0)
            selected_challenge = st.selectbox(
                "Select Challenge",
                options=all_challenges,
                format_func=lambda x: x[1],
                index=default_idx
            )
            del st.session_state.selected_challenge
            del st.session_state.selected_challenge_name
        else:
            selected_challenge = st.selectbox(
                "Select Challenge",
                options=all_challenges,
                format_func=lambda x: x[1]
            )
        
        # Get leaderboard data
        cursor.execute("""
            SELECT l.Rank_, u.FirstName, u.LastName, l.Points, l.User_Id
            FROM LeaderBoard l
            JOIN User u ON l.User_Id = u.User_Id
            WHERE l.ChallengeID = %s
            ORDER BY l.Rank_
        """, (selected_challenge[0],))
        leaderboard_data = cursor.fetchall()
        
        # Get challenge dates
        cursor.execute("SELECT StartDate, EndDate FROM Challenge WHERE ChallengeID = %s", (selected_challenge[0],))
        challenge_dates = cursor.fetchone()
        
        if challenge_dates:
            st.caption(f"📅 Challenge Period: {challenge_dates[0].strftime('%b %d, %Y')} - {challenge_dates[1].strftime('%b %d, %Y')}")
        
        # Display leaderboard
        if not leaderboard_data:
            st.info("No data available for this challenge yet. Start logging activities to appear on the leaderboard!")
            if st.session_state.logged_in:
                if st.button("Log Activity for this Challenge"):
                    st.session_state.selected_challenge = selected_challenge[0]
                    st.session_state.selected_challenge_name = selected_challenge[1]
                    st.query_params.update(menu="Log Activity")
                    show_loading_animation()
                    time.sleep(0.5)  # A brief delay
                    st.rerun()
        else:
            # Top 3 winners with improved visualization
            st.subheader("Top Performers")
            
            # Create a visually appealing podium
            podium_cols = st.columns([2, 3, 2])
            
            # Get medal data for this challenge
            cursor.execute("""
                SELECT m.MedalType, c.Name_
                FROM Medals m
                JOIN LeaderBoard l ON m.Rank_ = l.Rank_
                JOIN Challenge c ON l.ChallengeId = c.ChallengeID
                WHERE l.User_Id = %s AND l.ChallengeId = %s AND m.Rank_ <= 3
            """, (st.session_state.user_id, selected_challenge[0]))
            medal_data = cursor.fetchall()
            
            if medal_data:
                medal_type, challenge_name = medal_data[0]
                st.success(f"🏅 You have earned a {medal_type} medal in the {challenge_name} challenge!")
            
            # Display top 3 as a podium
            if len(leaderboard_data) >= 2:
                with podium_cols[1]:  # First place (center)
                    if len(leaderboard_data) >= 1:
                        st.markdown(f"""
                        <div class="podium-card gold-card">
                            <h2>🥇 {leaderboard_data[0][1]} {leaderboard_data[0][2]}</h2>
                            <p style="font-size:24px; font-weight:bold;">{leaderboard_data[0][3]} points</p>
                            <p>1st Place</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with podium_cols[0]:  # Second place (left)
                    if len(leaderboard_data) >= 2:
                        st.markdown(f"""
                        <div class="podium-card silver-card">
                            <h3>🥈 {leaderboard_data[1][1]} {leaderboard_data[1][2]}</h3>
                            <p style="font-size:18px; font-weight:bold;">{leaderboard_data[1][3]} points</p>
                            <p>2nd Place</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with podium_cols[2]:  # Third place (right)
                    if len(leaderboard_data) >= 3:
                        st.markdown(f"""
                        <div class="podium-card bronze-card">
                            <h3>🥉 {leaderboard_data[2][1]} {leaderboard_data[2][2]}</h3>
                            <p style="font-size:18px; font-weight:bold;">{leaderboard_data[2][3]} points</p>
                            <p>3rd Place</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Medals legend
            st.markdown("""
            <div style="display:flex; justify-content:center; margin:20px 0;">
                <div style="margin:0 15px;"><span style="font-size:24px;">🥇</span> Gold Medal</div>
                <div style="margin:0 15px;"><span style="font-size:24px;">🥈</span> Silver Medal</div>
                <div style="margin:0 15px;"><span style="font-size:24px;">🥉</span> Bronze Medal</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Full leaderboard with medal icons
            st.subheader("Full Rankings")
            
            # Create DataFrame for display
            leaderboard_list = []
            for rank, first_name, last_name, points, user_id in leaderboard_data:
                # Add medal emoji if applicable
                medal = ""
                if rank == 1:
                    medal = "🥇"
                elif rank == 2:
                    medal = "🥈"
                elif rank == 3:
                    medal = "🥉"
                
                leaderboard_list.append([rank, f"{medal} {first_name} {last_name}", points])
            
            df = pd.DataFrame(leaderboard_list, columns=["Rank", "Name", "Points"])
            
            # Highlight current user
            if st.session_state.logged_in:
                user_entry = next((entry for entry in leaderboard_data if entry[4] == st.session_state.user_id), None)
                
                if user_entry:
                    st.info(f"Your current rank: {user_entry[0]} with {user_entry[3]} points")
            
            st.table(df)
            
            # If user is logged in, show their achievements
            if st.session_state.logged_in:
                st.subheader("Your Achievements")
                
                # Get user medals across all challenges
                cursor.execute("""
                    SELECT m.MedalType, c.Name_
                    FROM MedalRewards mr
                    JOIN Medals m ON mr.MedalID = m.MedalID
                    JOIN LeaderBoard l ON m.Rank_ = l.Rank_
                    JOIN Challenge c ON l.ChallengeId = c.ChallengeID
                    WHERE l.User_Id = %s
                """, (st.session_state.user_id,))
                
                user_medals = cursor.fetchall()
                
                if user_medals:
                    medal_cols = st.columns(min(4, len(user_medals)))
                    for i, (medal_type, challenge_name) in enumerate(user_medals):
                        with medal_cols[i % len(medal_cols)]:
                            medal_icon = "🥇" if medal_type == "Gold" else "🥈" if medal_type == "Silver" else "🥉"
                            st.markdown(f"### {medal_icon}")
                            st.write(f"{medal_type} Medal")
                            st.caption(f"Challenge: {challenge_name}")
                else:
                    st.info("Keep participating to earn medals!")
        
        cursor.close()
        conn.close()

# Admin Page
elif menu == "Admin":
    st.title("Admin Dashboard")
    
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("Please login as admin to access this page")
    else:
        tabs = st.tabs(["Users", "Challenges", "Activity Logs", "Medals"])
        
        with tabs[0]:
            st.header("User Management")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT User_Id, FirstName, LastName, Email, Phone_no, RegistrationDate FROM User")
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if users:
                users_df = pd.DataFrame(users, columns=["ID", "First Name", "Last Name", "Email", "Phone", "Registration Date"])
                st.dataframe(users_df)
                
                # Display registration trend
                st.subheader("User Registration Trend")
                users_df['Month'] = pd.to_datetime(users_df['Registration Date']).dt.strftime('%Y-%m')
                registration_counts = users_df.groupby('Month').size().reset_index(name='Count')
                st.bar_chart(registration_counts.set_index('Month'))
            else:
                st.info("No users found")
        
        with tabs[1]:
            st.header("Challenge Management")
            
            # Add new challenge button
            if st.button("Add New Challenge"):
                st.session_state.admin_adding_challenge = True
            
            if getattr(st.session_state, 'admin_adding_challenge', False):
                with st.form("admin_challenge_form"):
                    name = st.text_input("Challenge Name")
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date")
                    
                    submit = st.form_submit_button("Create Challenge")
                    
                    if submit:
                        if not name or end_date <= start_date:
                            st.error("Please check your inputs")
                        else:
                            try:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO Challenge (Name_, StartDate, EndDate) VALUES (%s, %s, %s)",
                                    (name, start_date, end_date)
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Challenge created successfully!")
                                st.session_state.admin_adding_challenge = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            # Display challenges
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.ChallengeID, c.Name_, c.StartDate, c.EndDate, COUNT(cp.ParticipationID) AS Participants
                FROM Challenge c
                LEFT JOIN ChallengeParticipation cp ON c.ChallengeID = cp.ChallengeID
                GROUP BY c.ChallengeID
            """)
            challenges = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if challenges:
                challenges_df = pd.DataFrame(challenges, columns=["ID", "Name", "Start Date", "End Date", "Participants"])
                st.dataframe(challenges_df)
                
                # Challenge selection for recalculating leaderboard
                selected_challenge = st.selectbox(
                    "Select challenge to update leaderboard",
                    options=[(c[0], c[1]) for c in challenges],
                    format_func=lambda x: x[1]
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Leaderboard"):
                        # Use the new functions to update leaderboard and assign medals
                        update_leaderboard()
                        assign_medals()
                        st.success("Leaderboard and medals updated successfully!")
                with col2:
                    if st.button("View Leaderboard Details"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT l.Rank_, u.FirstName, u.LastName, l.Points
                            FROM LeaderBoard l
                            JOIN User u ON l.User_Id = u.User_Id
                            WHERE l.ChallengeID = %s
                            ORDER BY l.Rank_
                        """, (selected_challenge[0],))
                        leaderboard_details = cursor.fetchall()
                        cursor.close()
                        conn.close()
                        
                        if leaderboard_details:
                            st.subheader(f"Leaderboard for {selected_challenge[1]}")
                            leaderboard_df = pd.DataFrame(leaderboard_details, columns=["Rank", "First Name", "Last Name", "Points"])
                            st.dataframe(leaderboard_df)
                        else:
                            st.info("No leaderboard data for this challenge yet")
            else:
                st.info("No challenges found")
        
        with tabs[2]:
            st.header("Activity Logs")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.LogID, u.FirstName, u.LastName, c.Name_, a.ActivityType, a.ActivityData, a.LogTimestamp
                FROM ActivityLog a
                JOIN User u ON a.User_Id = u.User_Id
                JOIN Challenge c ON a.ChallengeID = c.ChallengeID
                ORDER BY a.LogTimestamp DESC
                LIMIT 50
            """)
            logs = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if logs:
                logs_df = pd.DataFrame(logs, columns=["ID", "First Name", "Last Name", "Challenge", "Activity Type", "Value", "Timestamp"])
                st.dataframe(logs_df)
                
                # Activity trend visualization
                st.subheader("Activity Trend")
                logs_df['Date'] = pd.to_datetime(logs_df['Timestamp']).dt.date
                daily_activity = logs_df.groupby('Date')['Value'].sum().reset_index()
                st.line_chart(daily_activity.set_index('Date'))
            else:
                st.info("No activity logs found")
        
        with tabs[3]:
            st.header("Medal Management")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.MedalID, u.FirstName, u.LastName, c.Name_, m.MedalType, m.Rank_
                FROM MedalRewards mr
                JOIN Medals m ON mr.MedalID = m.MedalID
                JOIN LeaderBoard l ON m.Rank_ = l.Rank_
                JOIN User u ON l.User_Id = u.User_Id
                JOIN Challenge c ON l.ChallengeId = c.ChallengeID
                ORDER BY c.Name_, m.Rank_
            """)
            medals = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if medals:
                medals_df = pd.DataFrame(medals, columns=["ID", "First Name", "Last Name", "Challenge", "Medal Type", "Rank"])
                st.dataframe(medals_df)
                
                # Medal distribution visualization
                st.subheader("Medal Distribution")
                medal_counts = medals_df.groupby('Medal Type').size().reset_index(name='Count')
                st.bar_chart(medal_counts.set_index('Medal Type'))
            else:
                st.info("No medals awarded yet")
                
                if st.button("Initialize Medals"):
                    try:
                        # Update leaderboard and assign medals for all challenges
                        update_leaderboard()
                        assign_medals()
                        st.success("Medals initialized successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error initializing medals: {e}")

def display_user_profile(user_id, user_name, is_admin):
    # Get user stats
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get activity count
    cursor.execute("SELECT COUNT(*) FROM ActivityLog WHERE User_Id = %s", (user_id,))
    activity_count = cursor.fetchone()[0] or 0
    
    # Get total points
    cursor.execute("SELECT SUM(ActivityData) FROM ActivityLog WHERE User_Id = %s", (user_id,))
    total_points = cursor.fetchone()[0] or 0
    
    # Check medals count with error handling
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM MedalRewards mr
            WHERE mr.User_Id = %s
        """, (user_id,))
        medals_count = cursor.fetchone()[0] or 0
    except Exception as e:
        # Fallback if MedalRewards doesn't have User_Id column
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM MedalRewards mr
                JOIN LeaderBoard l ON mr.ChallengeID = l.ChallengeID
                WHERE l.User_Id = %s
            """, (user_id,))
            medals_count = cursor.fetchone()[0] or 0
        except Exception as e2:
            # If all queries fail, set medals to 0
            medals_count = 0
    
    cursor.execute("SELECT COUNT(*) FROM ChallengeParticipation WHERE User_Id = %s", (user_id,))
    challenges_joined = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    # Welcome header
    st.markdown(f"""
    <div class="user-welcome">
        <h3>Welcome, <span style="color:#00695c">{user_name}</span> 👋</h3>
        <p>{'Admin Dashboard' if is_admin else 'User Dashboard'} | Last login: {datetime.now().strftime('%b %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User stats display with metrics
    st.subheader("Your Fitness Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="🏆 Challenges Joined", value=challenges_joined)
    
    with col2:
        st.metric(label="📊 Activities Logged", value=activity_count)
    
    with col3:
        st.metric(label="⭐ Total Points", value=f"{total_points:.1f}")
    
    with col4:
        st.metric(label="🥇 Medals Earned", value=medals_count)
    
    # Recent activities or challenges
    st.subheader("Recent Activity")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if is_admin:
            # For admin, show recent user registrations
            cursor.execute("""
                SELECT FirstName, LastName, Email, RegistrationDate 
                FROM User 
                ORDER BY RegistrationDate DESC 
                LIMIT 5
            """)
            recent_users = cursor.fetchall()
            
            if recent_users:
                st.markdown("##### Recent User Registrations")
                for user in recent_users:
                    st.markdown(f"""
                    <div style="padding:10px; background-color:white; border-radius:5px; margin:5px 0;">
                        <strong>{user[0]} {user[1]}</strong> • {user[2]} • {user[3].strftime('%b %d, %Y') if user[3] else 'N/A'}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent user registrations")
                
        else:
            # For regular users, show their recent activities
            cursor.execute("""
                SELECT a.ActivityType, a.ActivityData, c.Name_
                FROM ActivityLog a
                JOIN Challenge c ON a.ChallengeID = c.ChallengeID
                WHERE a.User_Id = %s
                ORDER BY a.LogID DESC
                LIMIT 5
            """, (user_id,))
            
            recent_activities = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if recent_activities:
                for activity in recent_activities:
                    st.markdown(f"""
                    <div style="padding:10px; background-color:white; border-radius:5px; margin:5px 0;">
                        <strong>{activity[0]}</strong> • {activity[1]} points • Challenge: {activity[2]}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activities. Start logging your fitness activities!")
                
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error loading recent activity: {e}") 