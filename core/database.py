import mysql.connector
from mysql.connector import Error

def init_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dolphinboi29001",
            database="physics_chat",
            connect_timeout=5  # Add timeout
        )
        if conn.is_connected():
            print("✅ Connected to MySQL!")
            return conn
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        # Add more specific error handling
        if "Access denied" in str(e):
            print("Check your username/password")
        elif "Unknown database" in str(e):
            print("Database 'PhysCalc' doesn't exist")
        return None

# Test the connection (optional)
if __name__ == "__main__":
    conn = init_db()
    if conn:
        conn.close()