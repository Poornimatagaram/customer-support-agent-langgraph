"""
Node: search_knowledge_base (Postgres/pgvector version)

Embeds the issue_summary, then uses pgvector's cosine distance
operator directly in SQL to find the most similar policy chunks.
"""

import os
from dotenv import load_dotenv
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

from nodes.state import AgentState

load_dotenv()

TOP_K = 3

# Loaded once at import time, same reasoning as in build_knowledge_base.py
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def search_knowledge_base(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]

    query_embedding = embedding_model.encode(issue_summary)

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    cursor = conn.cursor()

    # The <=> operator is pgvector's COSINE DISTANCE operator --
    # this is the literal SQL equivalent of what ChromaDB was doing
    # internally. ORDER BY distance ascending + LIMIT TOP_K gives us
    # the K most similar chunks, exactly like collection.query() did.
    cursor.execute("""
        SELECT chunk_text, source, embedding <=> %s AS distance
        FROM policy_chunks
        ORDER BY distance ASC
        LIMIT %s
    """, (query_embedding, TOP_K))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    retrieved_docs = [r[0] for r in results]

    print(f"[search_knowledge_base] Retrieved {len(retrieved_docs)} chunks:")
    for chunk_text, source, distance in results:
        print(f"   ({source}, distance={distance:.3f}) {chunk_text[:80]}...")

    return {
        "retrieved_docs": retrieved_docs,
    }