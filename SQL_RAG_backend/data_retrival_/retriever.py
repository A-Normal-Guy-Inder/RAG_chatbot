from ..vectordb import get_vectordb

def retrieve_top_k_with_threshold(query: str, k: int = 5, threshold: float = 20.0):
    vector_store = get_vectordb()
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

