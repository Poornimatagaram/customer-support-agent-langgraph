"""
test_db_connection.py

Quick sanity check: can we actually connect to the Supabase Postgres
database using the DATABASE_URL from .env?
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL not found in .env")
    exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # A trivial query just to prove the connection actually works
    cursor.execute("SELECT version();")
    version = cursor.fetchone()

    print("Connected successfully!")
    print(f"Postgres version: {version[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Connection FAILED: {e}")