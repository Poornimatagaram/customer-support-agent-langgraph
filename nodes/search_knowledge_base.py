"""
Node: search_knowledge_base

Takes the issue_summary from state, embeds it, and searches ChromaDB
for the most relevant policy document chunks. This is the "R" (Retrieval)
in RAG -- the "Generation" happens later, in determine_resolution,
when the LLM uses these retrieved chunks to decide what to do.
"""

import chromadb

from nodes.state import AgentState

CHROMA_PERSIST_DIR = "data/chroma_db"
COLLECTION_NAME = "policies"
TOP_K = 3   # how many chunks to retrieve per query


def search_knowledge_base(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]

    # Connect to the SAME persistent vector store build_knowledge_base.py created
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    # This single call does everything: embeds issue_summary using the
    # same embedding model, then finds the TOP_K closest stored vectors
    # via cosine similarity, and returns their original text + metadata.
    results = collection.query(
        query_texts=[issue_summary],
        n_results=TOP_K,
    )

    # results["documents"][0] is the list of matched chunk texts
    # results["metadatas"][0] is the list of matching source info
    # results["distances"][0] is how "far" each match is (lower = more similar)
    retrieved_docs = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    distances = results["distances"][0]

    print(f"[search_knowledge_base] Retrieved {len(retrieved_docs)} chunks:")
    for doc, source, dist in zip(retrieved_docs, sources, distances):
        print(f"   ({source}, distance={dist:.3f}) {doc[:80]}...")

    return {
        "retrieved_docs": retrieved_docs,
    }