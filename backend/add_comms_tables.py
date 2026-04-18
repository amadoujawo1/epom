import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Extract database name from connection string if possible, or use fallback
# database_url usually looks like mysql+pymysql://root:root@localhost/epom_dev
db_url = os.getenv("DATABASE_URL", "")
db_name = db_url.split('/')[-1] if '/' in db_url else 'epom_dev'

db_creds = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': db_name
}

tables = [
    """
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description VARCHAR(255),
        is_private BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        content TEXT NOT NULL,
        message_type VARCHAR(20) DEFAULT 'text',
        file_path VARCHAR(255),
        file_name VARCHAR(255),
        user_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(channel_id) REFERENCES channels(id)
    ) ENGINE=InnoDB;
    """
]

try:
    conn = pymysql.connect(**db_creds)
    cursor = conn.cursor()
    print(f"Provisioning communication tables in {db_name}...")
    for sql in tables:
        cursor.execute(sql)
    
    # Seed default channels
    defaults = [
        ("General", "Global tactical coordination channel"),
        ("Announcements", "Official briefings and directives"),
        ("Technical Hub", "IT and systems support")
    ]
    
    for name, desc in defaults:
        cursor.execute("SELECT id FROM channels WHERE name = %s", (name,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO channels (name, description) VALUES (%s, %s)", (name, desc))
    
    conn.commit()
    conn.close()
    print("Communication Hub provisioned successfully.")
except Exception as e:
    print(f"Provisioning failed: {e}")
