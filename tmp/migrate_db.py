import sqlite3
import os

db_path = 'backend/instance/epom_dev.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns in documents table
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if 'uploaded_by' not in columns:
        print("Adding uploaded_by column...")
        cursor.execute("ALTER TABLE documents ADD COLUMN uploaded_by INTEGER REFERENCES users(id)")
    
    if 'doc_type' not in columns:
        print("Adding doc_type column...")
        cursor.execute("ALTER TABLE documents ADD COLUMN doc_type VARCHAR(50) DEFAULT 'Official'")
        
    if 'content' not in columns:
        print("Adding content column...")
        cursor.execute("ALTER TABLE documents ADD COLUMN content TEXT")
        
    conn.commit()
    conn.close()
    print("Database check/migration completed.")
else:
    print(f"Database {db_path} not found. It will be created on next app run.")
