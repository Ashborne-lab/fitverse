import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='@Hum42',
            database='fitness_manager_system2'
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database.")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def check_table_structure(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        
        print(f"\n{table_name} table structure:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Total entries in {table_name}: {count}")
        
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample = cursor.fetchone()
            print(f"Sample entry from {table_name}:")
            for i, col in enumerate(cursor.column_names):
                print(f"  {col}: {sample[i]}")
        
        return True
    except Error as e:
        print(f"Error checking {table_name} table: {e}")
        return False

def check_table_relationships(connection):
    try:
        cursor = connection.cursor()
        
        # Check if UserLandingPage query would work
        print("\nChecking user_landing_page query compatibility...")
        user_id = 1  # Test with user ID 1
        
        # Check Users table field names
        cursor.execute("SHOW COLUMNS FROM Users")
        users_columns = [column[0] for column in cursor.fetchall()]
        print(f"Users table columns: {', '.join(users_columns)}")
        
        # Check LeaderBoard table field names
        cursor.execute("SHOW COLUMNS FROM LeaderBoard")
        leaderboard_columns = [column[0] for column in cursor.fetchall()]
        print(f"LeaderBoard table columns: {', '.join(leaderboard_columns)}")
        
        # Check Medals table field names
        cursor.execute("SHOW COLUMNS FROM Medals")
        medals_columns = [column[0] for column in cursor.fetchall()]
        print(f"Medals table columns: {', '.join(medals_columns)}")
        
        # Look for user ID fields in LeaderBoard
        print("\nChecking for user ID fields in LeaderBoard table:")
        for col in leaderboard_columns:
            if 'user' in col.lower() or 'id' in col.lower():
                print(f"  Potential user ID field: {col}")
        
        # Test if medals count query would work
        print("\nTesting medals count query...")
        try:
            cursor.execute(f"SELECT COUNT(*) FROM Medals WHERE UserId = {user_id}")
            count = cursor.fetchone()[0]
            print(f"Found {count} medals for user ID {user_id}")
            print("Medals query works with 'UserId' field")
        except Error as e:
            print(f"Error with 'UserId' field in Medals table: {e}")
            # Try alternative field names
            for field in medals_columns:
                if field != 'UserId' and ('user' in field.lower() or 'id' in field.lower()):
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM Medals WHERE {field} = {user_id}")
                        count = cursor.fetchone()[0]
                        print(f"Alternative query using '{field}' field works! Found {count} medals.")
                    except Error as e2:
                        print(f"  Alternative field '{field}' also failed: {e2}")
    
    except Error as e:
        print(f"Error checking table relationships: {e}")

def main():
    connection = get_connection()
    if connection:
        try:
            check_table_structure(connection, "Users")
            check_table_structure(connection, "LeaderBoard")
            check_table_structure(connection, "Medals")
            check_table_structure(connection, "Challenges")
            check_table_relationships(connection)
        except Error as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                connection.close()
                print("\nMySQL connection closed.")

if __name__ == "__main__":
    main() 