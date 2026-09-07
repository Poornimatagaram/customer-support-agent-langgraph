"""
Node: search_knowledge_base

Embeds the issue_summary via the Gemini API, then uses pgvector's
cosine distance operator to find the most similar policy chunks.
"""
import numpy as np
import os
from dotenv import load_dotenv
import psycopg2
from pgvector.psycopg2 import register_vector

from nodes.state import AgentState
from embeddings_util import get_embedding

load_dotenv()

TOP_K = 3


def search_knowledge_base(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]

    query_embedding = np.array(get_embedding(issue_summary, task_type="retrieval_query"))

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    cursor = conn.cursor()

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