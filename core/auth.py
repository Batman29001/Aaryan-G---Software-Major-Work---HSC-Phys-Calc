from core.database import init_db
from mysql.connector import Error
from hashlib import sha256
from mysql.connector import IntegrityError  # Add this import

class AuthManager:
    def __init__(self):
            print("Attempting database connection...")
            self.conn = init_db()
            self.current_user = None
            print(f"Connection result: {self.conn}")  
            if not self.conn:
                print("Database connection failed. Exiting...")
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
        
        user = cursor.fetchone()
        if user:
            self.current_user = user  # Store as (id, username)
        return user
    
    def save_global_message(self, user_id, username, message):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO global_messages (user_id, username, message)
            VALUES (%s, %s, %s)
        """, (user_id, username, message))
        self.conn.commit()

    def get_global_messages(self, limit=50):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT username, message, 
                DATE_FORMAT(sent_at, '%Y-%m-%d %H:%i') as timestamp
            FROM global_messages
            ORDER BY sent_at DESC
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()