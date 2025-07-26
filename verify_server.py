from flask import Flask, request
from core.database import init_db
from datetime import datetime, timezone

app = Flask(__name__)
conn = init_db()

@app.route("/verify-email")
def verify_email():
    token = request.args.get("token")

    if not token:
        return "❌ No token provided."

    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, expires_at FROM email_verifications
        WHERE token = %s
    """, (token,))
    result = cursor.fetchone()

    if not result:
        return "❌ Invalid or expired token."

    user_id, expires_at = result

    # Add this line to convert expires_at to aware datetime if naive:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        return "❌ Token expired. Please sign up again."

    cursor.execute("DELETE FROM email_verifications WHERE user_id = %s", (user_id,))
    conn.commit()
    return "✅ Email verified successfully. You can now log in to Phys Calc."

if __name__ == "__main__":
    app.run(debug=True)

