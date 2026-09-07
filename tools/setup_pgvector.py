"""
setup_pgvector.py

Enables the pgvector extension (if not already) and creates a table
to store policy document chunks along with their embeddings.

384 dimensions matches all-MiniLM-L6-v2's output size.
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# Defensive -- makes sure the extension is enabled even if the
# dashboard toggle didn't fully take effect.
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

cursor.execute("DROP TABLE IF EXISTS policy_chunks")
cursor.execute("""
CREATE TABLE policy_chunks (
    id SERIAL PRIMARY KEY,
    source TEXT,
    chunk_text TEXT,
    embedding VECTOR(384)
)
""")

conn.commit()
cursor.close()
conn.close()

print("pgvector extension enabled and policy_chunks table created.")