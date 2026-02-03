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
    print("=== LeaderBoard Table Check ===")
    
    try:
        # Check database connection
        conn = get_connection()
        print("✅ Connected to database successfully!")
        
        # Check if LeaderBoard table exists
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'LeaderBoard'")
        if not cursor.fetchone():
            print("❌ LeaderBoard table does not exist!")
            return
        
        print("✅ LeaderBoard table exists")
        
        # Check LeaderBoard table structure
        cursor.execute("DESCRIBE LeaderBoard")
        columns = cursor.fetchall()
        print("\nLeaderBoard table structure:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        # Check for any entries in the LeaderBoard
        cursor.execute("SELECT COUNT(*) FROM LeaderBoard")
        entry_count = cursor.fetchone()[0]
        print(f"\nLeaderBoard entry count: {entry_count}")
        
        if entry_count > 0:
            # Show a sample entry
            cursor.execute("SELECT * FROM LeaderBoard LIMIT 1")
            sample = cursor.fetchone()
            print("\nSample LeaderBoard entry:")
            cursor.execute("DESCRIBE LeaderBoard")
            cols = cursor.fetchall()
            for i, col_info in enumerate(cols):
                print(f"- {col_info[0]}: {sample[i]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 