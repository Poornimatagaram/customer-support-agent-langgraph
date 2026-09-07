"""
check_checkpoints.py

Diagnostic: query the checkpoints table directly to see if data
was actually saved for our thread_id during the paused run.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

thread_id = sys.argv[1] if len(sys.argv) > 1 else None

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'checkpoint%'")
print("Checkpoint-related tables found:", cursor.fetchall())

if thread_id:
    cursor.execute("SELECT thread_id, checkpoint_id FROM checkpoints WHERE thread_id = %s", (thread_id,))
    rows = cursor.fetchall()
    print(f"\nRows found for thread_id={thread_id}: {len(rows)}")
    for r in rows:
        print(r)
else:
    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    print("\nAll thread_ids currently in checkpoints table:", cursor.fetchall())

cursor.close()
conn.close()