import pyotp
import bcrypt
import smtplib
import uuid
import os
from core.database import init_db
from mysql.connector import Error, IntegrityError
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from dotenv import load_dotenv



load_dotenv()

class AuthManager:
    def __init__(self):
        print("Attempting database connection...")
        self.conn = init_db()
        print("Connected?", self.conn.is_connected() if self.conn else "Failed")
        self.current_user = None

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

            # ✅ Fetch new user's ID
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]

            # ✅ Send them a verification email
            self.send_verification_email(user_id, email)

            # ✅ Continue generating TOTP as normal
            totp = pyotp.TOTP(totp_secret)
            uri = totp.provisioning_uri(name=email, issuer_name="Phys Calc")

            return { "secret": totp_secret, "uri": uri }
        except IntegrityError:
            print("🚨 Email or username already exists.")
            return False
        except Error as e:
            print(f"🚨 Signup Error: {e}")
            return False

    def login(self, email, password, totp_code=None):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, password_hash, totp_secret FROM users
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()

        if not user:
            return None

        cursor.execute("""
            SELECT COUNT(*) AS count FROM email_verifications
            WHERE user_id = %s
        """, (user["id"],))
        unverified = cursor.fetchone()["count"]

        if unverified > 0:
            print("❌ Email not verified")
            return None

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return None

        if totp_code:
            totp = pyotp.TOTP(user["totp_secret"])
            if not totp.verify(totp_code):
                print("❌ Invalid 2FA code")
                return None

        self.current_user = (user["id"], user["username"])
        return user

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
                ORDER BY sent_at ASC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching messages: {e}")
            return []
        
    def send_verification_email(self, user_id, email):
        cursor = self.conn.cursor()

        # ⏳ Check if existing token is still active
        cursor.execute("""
            SELECT expires_at FROM email_verifications WHERE user_id = %s
        """, (user_id,))
        row = cursor.fetchone()

        if row and datetime.now(timezone.utc) < row[0]:
            wait_time = (row[0] - datetime.now(timezone.utc)).seconds
            print(f"⏳ Wait {wait_time//60} min before resending verification.")
            return  # 🚫 Exit early — don't send new email

        # ✅ Token has expired or doesn't exist — generate a new one
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        cursor.execute("""
            INSERT INTO email_verifications (user_id, token, expires_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE token = VALUES(token), expires_at = VALUES(expires_at)
        """, (user_id, token, expires_at))
        self.conn.commit()

        # 📧 Send email
        link = f"http://localhost:5000/verify-email?token={token}"

        message = MIMEText(f"Welcome to Phys Calc!\n\nClick to verify your email:\n\n{link}")
        message["Subject"] = "Verify your Phys Calc Email"
        message["From"] = "sftwr.eng.aryn@gmail.com"
        message["To"] = email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
                server.send_message(message)
            print(f"✅ Verification email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def get_user_details(self, user_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT username, email, totp_secret FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        if not user:
            return None

        uri = pyotp.TOTP(user["totp_secret"]).provisioning_uri(name=user["email"], issuer_name="Phys Calc")
        return {
            "username": user["username"],
            "email": user["email"],
            "totp_uri": uri
        }

    def verify_password(self, user_id, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False
        return bcrypt.checkpw(password.encode(), row[0].encode())

    def update_user_details(self, user_id, username=None, email=None, password=None):
        cursor = self.conn.cursor()
        fields = []
        values = []

        if username:
            fields.append("username = %s")
            values.append(username)
        if email:
            fields.append("email = %s")
            values.append(email)
        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            fields.append("password_hash = %s")
            values.append(hashed)

        if not fields:
            return False

        values.append(user_id)

        try:
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(query, values)
            self.conn.commit()
            return True
        except Error as e:
            print(f"Update error: {e}")
            return False

