from core.database import init_db
from mysql.connector import Error
from hashlib import sha256
from mysql.connector import IntegrityError  # Add this import

class AuthManager:
    def __init__(self):
            self.conn = init_db()
            if not self.conn:
                print("❌ Database connection failed. Exiting...")
                raise SystemExit(1)
    
    def signup(self, username, email, password):
        cursor = self.conn.cursor()
        password_hash = sha256(password.encode()).hexdigest()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """, (username, email, password_hash))
            self.conn.commit()
            return True
        except Error as e:
            print(f"🚨 Signup Error: {e}")
            return False
    
    def login(self, email, password):
        cursor = self.conn.cursor()
        password_hash = sha256(password.encode()).hexdigest()
        cursor.execute("""
            SELECT id, username FROM users 
            WHERE email = %s AND password_hash = %s
        """, (email, password_hash))
        return cursor.fetchone()