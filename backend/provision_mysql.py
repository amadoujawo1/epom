import pymysql

db_creds = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'epom_dev'
}

tables = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        role VARCHAR(50) DEFAULT 'Staff',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        priority VARCHAR(20) DEFAULT 'Medium',
        user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        status VARCHAR(50) DEFAULT 'Draft',
        category VARCHAR(50) DEFAULT 'Internal',
        uploaded_by INTEGER NOT NULL,
        doc_type VARCHAR(50) DEFAULT 'Official',
        content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS document_audit (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        document_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        action VARCHAR(100) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        status VARCHAR(50) DEFAULT 'Pending',
        priority VARCHAR(20) DEFAULT 'Medium',
        due_date DATETIME,
        assigned_to INTEGER NOT NULL,
        document_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        message VARCHAR(255) NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        link VARCHAR(255),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    ) ENGINE=InnoDB;
    """
]

try:
    conn = pymysql.connect(**db_creds)
    cursor = conn.cursor()
    print("Connecting to MySQL...")
    for sql in tables:
        try:
            cursor.execute(sql)
            print(f"Table checked/created.")
        except Exception as table_err:
            print(f"Error creating table: {table_err}")
    conn.commit()
    conn.close()
    print("Manual Database Provisioning Complete.")
except Exception as e:
    print(f"Failed to connect and provision: {e}")
