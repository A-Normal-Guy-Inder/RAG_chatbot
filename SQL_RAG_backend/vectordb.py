from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from .database_config import getSqlUrl

def get_vectordb():
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = PGVector(
        collection_name="chatbot",
        embeddings=embeddings,
        connection=getSqlUrl(),
    )
    return vector_store