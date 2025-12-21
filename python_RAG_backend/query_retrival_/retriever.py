from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

PERSIST_DIR = Path(__file__).parent.parent / "data" / "chroma_langchain_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vector_store = Chroma(
    collection_name="chatbot",
    embedding_function=embeddings,
    persist_directory=str(PERSIST_DIR),
)

def retrieve_top_k_with_threshold(query: str, k: int = 5, threshold: float = 70.0):
    """
    Retrieve top-k documents with similarity >= threshold (%)
    Returns: List of Document objects with similarity score added to metadata
    """
    results = vector_store.similarity_search_with_score(query, k=k)

    filtered = []

    for doc, distance in results:
        similarity = (1 - distance) * 100

        if similarity >= threshold:
            # Add similarity score to metadata for reference
            doc.metadata["similarity_score"] = round(similarity, 2)
            filtered.append(doc)

    return filtered

