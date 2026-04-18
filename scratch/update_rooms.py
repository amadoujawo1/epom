import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='epom_db'
)
cur = conn.cursor()

# Show current
cur.execute("SELECT id, name, type, capacity FROM resources")
rows = cur.fetchall()
print(f"Current resources ({len(rows)}):")
for r in rows:
    print(f"  {r}")

# Disable FK checks, clear, re-enable
cur.execute("SET FOREIGN_KEY_CHECKS=0")
cur.execute("DELETE FROM resources")
cur.execute("SET FOREIGN_KEY_CHECKS=1")

# Insert new rooms
cur.execute("INSERT INTO resources (name, type, capacity, is_available) VALUES (%s, %s, %s, %s)",
            ('Board Room', 'Room', 20, True))
cur.execute("INSERT INTO resources (name, type, capacity, is_available) VALUES (%s, %s, %s, %s)",
            ('Conference Room', 'Room', 12, True))

conn.commit()

# Confirm
cur.execute("SELECT id, name, type, capacity FROM resources")
updated = cur.fetchall()
print(f"\nUpdated resources ({len(updated)}):")
for r in updated:
    print(f"  ID:{r[0]} | Name:{r[1]} | Type:{r[2]} | Capacity:{r[3]}")

cur.close()
conn.close()
