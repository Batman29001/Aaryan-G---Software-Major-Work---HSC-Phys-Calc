import sys
from datetime import datetime, timezone
from core.database import init_db

def verify_email_token(token: str):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, expires_at FROM email_verifications
        WHERE token = %s
    """, (token,))
    result = cursor.fetchone()

    if not result:
        print("❌ Invalid token")
        return

    user_id, expires_at = result
    if datetime.now(timezone.utc) > expires_at:
        print("❌ Token expired")
        return

    # Delete verification entry = mark user as verified
    cursor.execute("DELETE FROM email_verifications WHERE user_id = %s", (user_id,))
    conn.commit()
    print("✅ Email verified!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_email.py <verification_token>")
    else:
        verify_email_token(sys.argv[1])
