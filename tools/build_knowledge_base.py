"""
build_knowledge_base.py

Reads all .txt policy documents from data/knowledge_base/, splits them
into paragraph-level chunks, embeds them, and stores them in a
persistent ChromaDB vector store.

Run this ONCE (or whenever policy documents change) to (re)build the
vector store that search_knowledge_base.py will query.
"""

import os
import glob
import chromadb

KNOWLEDGE_BASE_DIR = "data/knowledge_base"
CHROMA_PERSIST_DIR = "data/chroma_db"
COLLECTION_NAME = "policies"


def chunk_document(text: str) -> list[str]:
    """
    Splits a document into chunks by blank-line-separated paragraphs.
    This is "semantic chunking" -- we split at natural meaning
    boundaries (paragraphs) rather than an arbitrary character count.
    """
    # Split on double newlines (blank lines between paragraphs)
    raw_chunks = text.split("\n\n")
    # Clean up whitespace, drop any empty chunks
    chunks = [c.strip() for c in raw_chunks if c.strip()]
    return chunks


def build_knowledge_base():
    # PersistentClient saves the vector store to disk, so it survives
    # between script runs -- we don't want to re-embed everything
    # every single time our agent runs.
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # If the collection already exists from a previous run, delete it
    # so we get a clean rebuild (avoids duplicate/stale chunks).
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    # Creating the collection with NO embedding_function specified
    # means Chroma uses its default: all-MiniLM-L6-v2, running locally.
    collection = client.create_collection(name=COLLECTION_NAME)

    all_chunks = []
    all_ids = []
    all_metadatas = []

    txt_files = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.txt"))

    for file_path in txt_files:
        source_name = os.path.basename(file_path)
        with open(file_path, "r") as f:
            text = f.read()

        chunks = chunk_document(text)

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{source_name}_chunk_{i}")
            # metadata lets us trace which document a chunk came from --
            # useful for debugging and for showing "source" in answers
            all_metadatas.append({"source": source_name})

    # This is where the actual embedding happens -- Chroma automatically
    # runs each chunk through the embedding model and stores the
    # resulting vectors, indexed for fast similarity search.
    collection.add(
        documents=all_chunks,
        ids=all_ids,
        metadatas=all_metadatas,
    )

    print(f"Knowledge base built: {len(all_chunks)} chunks from {len(txt_files)} documents.")
    for source in set(m["source"] for m in all_metadatas):
        count = sum(1 for m in all_metadatas if m["source"] == source)
        print(f"  - {source}: {count} chunks")


if __name__ == "__main__":
    build_knowledge_base()