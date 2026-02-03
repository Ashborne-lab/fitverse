import mysql.connector
import pandas as pd

# Database connection function
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="@Hum42",
        database="fitness_manager_system2"
    )

def main():
    print("=== Database Diagnostic Tool ===")
    
    try:
        # Check database connection
        conn = get_connection()
        print("✅ Connected to database successfully!")
        
        # Check database version
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL version: {version[0]}")
        
        # Check if User table exists
        cursor.execute("SHOW TABLES LIKE 'User'")
        if not cursor.fetchone():
            print("❌ User table does not exist!")
            return
        
        print("✅ User table exists")
        
        # Check User table structure
        cursor.execute("DESCRIBE User")
        columns = cursor.fetchall()
        print("\nUser table structure:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        # Check for any users in the database
        cursor.execute("SELECT COUNT(*) FROM User")
        user_count = cursor.fetchone()[0]
        print(f"\nUser count: {user_count}")
        
        if user_count > 0:
            # List all users
            cursor.execute("SELECT User_Id, Name_, Email, Phone_no, RegistrationDate FROM User")
            users = cursor.fetchall()
            
            print("\nUser list:")
            for user in users:
                print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Phone: {user[3]}, Registered: {user[4]}")
            
            # Test case-insensitive email query (for one sample user)
            if users:
                sample_email = users[0][2]
                upper_email = sample_email.upper()
                
                print(f"\nTesting case-insensitive email query for: {sample_email}")
                print(f"Uppercase version: {upper_email}")
                
                # Test normal query
                cursor.execute("SELECT User_Id FROM User WHERE Email = %s", (sample_email,))
                normal_result = cursor.fetchone()
                
                # Test uppercase query
                cursor.execute("SELECT User_Id FROM User WHERE Email = %s", (upper_email,))
                upper_result = cursor.fetchone()
                
                # Test lowercase query
                cursor.execute("SELECT User_Id FROM User WHERE LOWER(Email) = LOWER(%s)", (upper_email,))
                lower_case_result = cursor.fetchone()
                
                print(f"Normal query result: {normal_result}")
                print(f"Uppercase query result: {upper_result}")
                print(f"Case-insensitive query result: {lower_case_result}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 