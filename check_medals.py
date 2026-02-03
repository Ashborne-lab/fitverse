import mysql.connector

# Database connection function
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="@Hum42",
        database="fitness_manager_system2"
    )

def main():
    print("=== Medals Table Check ===")
    
    try:
        # Check database connection
        conn = get_connection()
        print("✅ Connected to database successfully!")
        
        # Check if Medals table exists
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'Medals'")
        if not cursor.fetchone():
            print("❌ Medals table does not exist!")
            return
        
        print("✅ Medals table exists")
        
        # Check Medals table structure
        cursor.execute("DESCRIBE Medals")
        columns = cursor.fetchall()
        print("\nMedals table structure:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        # Check for any medals in the database
        cursor.execute("SELECT COUNT(*) FROM Medals")
        medal_count = cursor.fetchone()[0]
        print(f"\nMedal count: {medal_count}")
        
        # Check column names used in the LeaderBoard table
        print("\nLeaderBoard table structure:")
        cursor.execute("DESCRIBE LeaderBoard")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 