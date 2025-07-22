import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        db = os.getenv("DB_NAME")

        print(f"Connecting to DB at {host}:{port} as {user}, DB: {db}")

        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=os.getenv("DB_PASS"),
            database=db,
            connection_timeout=5,
            ssl_disabled=True,
            use_pure=True
        )

        # REMOVE THIS LINE:
        # if conn.is_connected():
        print("✅ Connection created.")
        return conn

    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return None


# Test the connection (optional)
if __name__ == "__main__":
    conn = init_db()
    if conn:
        conn.close()