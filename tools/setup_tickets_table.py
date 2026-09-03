"""
setup_tickets_table.py

Adds a `tickets` table to our existing data/crm.db database.
Run this ONCE, after seed_crm.py has already created the database.
"""

import sqlite3

conn = sqlite3.connect("data/crm.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS tickets")

cursor.execute("""
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    category TEXT,
    issue_summary TEXT,
    resolution_plan TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("tickets table created in data/crm.db")