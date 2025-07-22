from core.database import init_db

def create_schema_if_missing(conn):
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        totp_secret VARCHAR(32)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        username VARCHAR(50),
        message TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    print("✅ Tables created or already exist.")

if __name__ == "__main__":
    conn = init_db()
    if conn:
        create_schema_if_missing(conn)
        conn.close()
    else:
        print("❌ Could not connect to database.")
