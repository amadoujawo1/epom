import mysql.connector
import os

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'epom_db'
}

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        print("Creating resources table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) DEFAULT 'Room',
                capacity INT,
                is_available BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Updating events table...")
        cols_to_add = [
            ("resource_id", "INT"),
            ("location", "VARCHAR(255)"),
            ("meeting_link", "VARCHAR(512)")
        ]
        
        for col_name, col_type in cols_to_add:
            try:
                cursor.execute(f"ALTER TABLE events ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Column {col_name} might already exist: {e}")

        try:
            cursor.execute("ALTER TABLE events ADD FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE SET NULL")
        except: pass

        # Seed initial rooms if empty
        cursor.execute("SELECT COUNT(*) FROM resources")
        if cursor.fetchone()[0] == 0:
            print("Seeding initial resources...")
            resources = [
                ('Main Conference Room', 'Room', 20),
                ('Cabinet Briefing Room', 'Room', 10),
                ('Presidential Suite', 'Room', 5),
                ('Strategic Planning Hub', 'Room', 15),
                ('Standard Office 01', 'Room', 2)
            ]
            cursor.executemany("INSERT INTO resources (name, type, capacity) VALUES (%s, %s, %s)", resources)

        conn.commit()
        print("Schema update complete!")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
