"""
build_knowledge_base.py (Postgres/pgvector version)

Reads all .txt policy documents, splits them into paragraph-level
chunks, generates embeddings explicitly using sentence-transformers,
and stores everything in the policy_chunks table in Postgres.
"""

import os
import glob
from dotenv import load_dotenv
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

KNOWLEDGE_BASE_DIR = "data/knowledge_base"

print("Loading embedding model (this may take a moment)...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_document(text: str) -> list[str]:
    raw_chunks = text.split("\n\n")
    chunks = [c.strip() for c in raw_chunks if c.strip()]
    return chunks


def build_knowledge_base():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM policy_chunks")

    txt_files = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.txt"))
    total_chunks = 0

    for file_path in txt_files:
        source_name = os.path.basename(file_path)
        with open(file_path, "r") as f:
            text = f.read()

        chunks = chunk_document(text)

        for chunk in chunks:
            embedding = embedding_model.encode(chunk)

            cursor.execute(
                "INSERT INTO policy_chunks (source, chunk_text, embedding) VALUES (%s, %s, %s)",
                (source_name, chunk, embedding),
            )
            total_chunks += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Knowledge base built: {total_chunks} chunks from {len(txt_files)} documents, stored in Postgres.")


if __name__ == "__main__":
    build_knowledge_base()