"""
seed_crm.py

Creates a mock CRM database (SQLite) with fake customer records,
so our search_crm node has real data to query against.

Run this file ONCE to create/reset data/crm.db.
"""

import sqlite3
import os

# Make sure the data/ folder exists
os.makedirs("data", exist_ok=True)

# Connect -- this creates the file data/crm.db if it doesn't exist yet
conn = sqlite3.connect("data/crm.db")
cursor = conn.cursor()

# --- Define the table structure ---
# DROP TABLE first so re-running this script gives a clean slate each time
cursor.execute("DROP TABLE IF EXISTS customers")

cursor.execute("""
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    order_id TEXT,
    order_amount REAL,
    order_date TEXT,
    account_status TEXT
)
""")

# --- Insert fake sample data ---
fake_customers = [
    ("cust_001", "Priya Sharma", "priya@example.com", "4521", 89.99, "2026-08-15", "active"),
    ("cust_002", "James Miller", "james@example.com", "4522", 249.50, "2026-08-18", "active"),
    ("cust_003", "Aiko Tanaka", "aiko@example.com", "4523", 15.00, "2026-08-20", "active"),
    ("cust_004", "Carlos Diaz", "carlos@example.com", "4524", 500.00, "2026-08-10", "flagged"),
]

cursor.executemany("""
INSERT INTO customers (customer_id, name, email, order_id, order_amount, order_date, account_status)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", fake_customers)

conn.commit()
conn.close()

print("data/crm.db created and seeded with 4 fake customers.")