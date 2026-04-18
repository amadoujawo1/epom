import sqlite3
import os

db_path = "epom_dev.db"
if not os.path.exists(db_path):
    db_path = "instance/epom_dev.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, col, typ, default):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ} DEFAULT {default}")
        print(f"Added {col} to {table}")
    except Exception as e:
        print(f"Skipping {col} on {table}: {e}")

# Users
add_column("users", "is_active", "BOOLEAN", "1")

# Actions
add_column("actions", "priority", "VARCHAR(20)", "'Medium'")
add_column("actions", "due_date", "DATETIME", "NULL")

# Events
add_column("events", "priority", "VARCHAR(20)", "'Medium'")

# Documents
add_column("documents", "status", "VARCHAR(50)", "'Draft'")
add_column("documents", "category", "VARCHAR(50)", "'Internal'")
add_column("documents", "doc_type", "VARCHAR(50)", "'Official'")
add_column("documents", "content", "TEXT", "NULL")

# Document Audit Table
try:
    cursor.execute('''CREATE TABLE document_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        action VARCHAR(100) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    print("Created document_audit table")
except Exception as e:
    print(f"Skipping document_audit table: {e}")

conn.commit()
conn.close()
