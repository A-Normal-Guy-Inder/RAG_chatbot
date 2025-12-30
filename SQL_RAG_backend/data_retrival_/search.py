from dotenv import load_dotenv
from .retriever import retrieve_top_k_with_threshold
from .response_generator import ResponseGenerator
from .LLMs import grokllm, ollama3_2_3bmodel

load_dotenv()

llm = ollama3_2_3bmodel

response_generator = ResponseGenerator(llm)


def ask_question(query: str, k: int = 5, threshold: float = 20.0) -> str:
    """
    Ask a question and get an answer based on RAG retrieval.
    
    Args:
        query: The question to ask
        k: Number of top documents to retrieve
        threshold: Minimum similarity score (0-100) for filtering
        
    Returns:
        The generated answer based on retrieved context
    """
    results = retrieve_top_k_with_threshold(
        query=query,
        k=k,
        threshold=threshold
    )

    if not results:
        return "I couldn't find sufficiently relevant information to answer your question."

    # Build context from retrieved documents
    context_parts = []
    for doc in results:
        similarity = doc.metadata.get("similarity_score", "N/A")
        source = doc.metadata.get("source", "Unknown")
        section = doc.metadata.get("section", "Unknown")

        context_parts.append(
            f"[Source: {source} | Section: {section} | Relevance: {similarity}%]\n"
            f"{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    return response_generator.generate_response(
        query=query,
        context=context
    )


if __name__ == "__main__":
    question = input("Enter the question: ")
    answer = ask_question(question)
    print(answer)