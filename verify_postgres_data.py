"""
verify_postgres_data.py

Quick check: query the customers table to confirm the data actually
landed correctly in Postgres.
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

cursor.execute("SELECT * FROM customers")
rows = cursor.fetchall()

print(f"Found {len(rows)} customers:")
for row in rows:
    print(row)

cursor.close()
conn.close()