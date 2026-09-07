"""
setup_pgvector.py

Enables pgvector and creates the policy_chunks table.
768 dimensions matches Gemini's gemini-embedding-001 output size
(configured via output_dimensionality).
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

cursor.execute("DROP TABLE IF EXISTS policy_chunks")
cursor.execute("""
CREATE TABLE policy_chunks (
    id SERIAL PRIMARY KEY,
    source TEXT,
    chunk_text TEXT,
    embedding VECTOR(768)
)
""")

conn.commit()
cursor.close()
conn.close()

print("pgvector table recreated with 768 dimensions (Gemini embeddings).")