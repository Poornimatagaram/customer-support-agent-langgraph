"""
setup_postgres.py

Creates the customers and tickets tables in our Supabase Postgres
database, and seeds customers with the same fake data we used in
SQLite. Run this ONCE to initialize the database.
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# --- customers table ---
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

fake_customers = [
    ("cust_001", "Priya Sharma", "priya@example.com", "4521", 89.99, "2026-08-15", "active"),
    ("cust_002", "James Miller", "james@example.com", "4522", 249.50, "2026-08-18", "active"),
    ("cust_003", "Aiko Tanaka", "aiko@example.com", "4523", 15.00, "2026-08-20", "active"),
    ("cust_004", "Carlos Diaz", "carlos@example.com", "4524", 500.00, "2026-08-10", "flagged"),
]

# Note: psycopg2 uses %s as its placeholder (SQLite used ?) --
# this is one of the small syntax differences between the two libraries.
cursor.executemany("""
INSERT INTO customers (customer_id, name, email, order_id, order_amount, order_date, account_status)
VALUES (%s, %s, %s, %s, %s, %s, %s)
""", fake_customers)

# --- tickets table ---
cursor.execute("DROP TABLE IF EXISTS tickets")
cursor.execute("""
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    category TEXT,
    issue_summary TEXT,
    resolution_plan TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
cursor.close()
conn.close()

print("Postgres tables created and seeded: customers (4 rows), tickets (empty, ready for use).")