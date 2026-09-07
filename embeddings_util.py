"""
embeddings_util.py

Generates embeddings via the Gemini API instead of loading a local
model. This keeps the deployed app lightweight -- no PyTorch or other
heavy ML libraries need to be installed or held in memory.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 768


def get_embedding(text: str, task_type: str = "retrieval_document") -> list:
    """
    task_type differs for documents being stored ("retrieval_document")
    vs queries being searched ("retrieval_query") -- Gemini's embedding
    model produces vectors optimized for each role, which is a real
    quality improvement over using an identical embedding process for
    both sides of a search.
    """
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type=task_type,
        output_dimensionality=EMBEDDING_DIM,
    )
    return result["embedding"]