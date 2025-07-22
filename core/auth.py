import pyotp
import bcrypt
from core.database import init_db
from mysql.connector import Error
from hashlib import sha256
from mysql.connector import IntegrityError 

class AuthManager:
    def __init__(self):
            print("Attempting database connection...")
            self.conn = init_db()
            print("Connected?", self.conn.is_connected() if self.conn else "Failed")
            self.current_user = None
            print(f"Connection result: {self.conn}")  
            if not self.conn:
                print("Database connection failed. Exiting...")
                raise SystemExit(1)
    
    def signup(self, username, email, password):
        cursor = self.conn.cursor()
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        totp_secret = pyotp.random_base32()

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, totp_secret)
                VALUES (%s, %s, %s, %s)
            """, (username, email, password_hash, totp_secret))
            self.conn.commit()
            return totp_secret
        except Error as e:
            print(f"🚨 Signup Error: {e}")
            return False

    
    def login(self, email, password):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, password_hash, totp_secret FROM users
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            self.current_user = (user["id"], user["username"])
            return user  # send back secret too
        return None
    
    def save_global_message(self, user_id, username, message):
        if not message.strip():
            return False
            
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO global_messages (user_id, username, message)
                VALUES (%s, %s, %s)
            """, (user_id, username, message.strip()))
            self.conn.commit()
            return True
        except Error as e:
            print(f"Error saving message: {e}")
            return False

    def get_global_messages(self, limit=100):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT username, message, 
                    DATE_FORMAT(sent_at, '%Y-%m-%d %H:%i') as timestamp
                FROM global_messages
                ORDER BY sent_at ASC  # Changed to ASC for chronological order
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching messages: {e}")
            return []
