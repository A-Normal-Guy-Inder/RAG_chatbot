from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from ..database_config import getSqlUrl
from pathlib import Path
import math

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# Initialize vector store
vector_store = PGVector(
    collection_name="chatbot",
    embeddings=embeddings,
    connection=getSqlUrl(),
)

def embed_store(chunks, batch_size=50):
    """
    Add chunks to vector store with progress printing.
    """
    if not chunks:
        print("❌ ERROR: No chunks provided")
        return {"success": False, "error": "No chunks provided"}

    total = len(chunks)
    total_batches = math.ceil(total / batch_size)

    print(f"🚀 Starting embedding")
    print(f"📦 Total chunks: {total}")
    print(f"🔢 Batch size: {batch_size}")
    print(f"🧩 Total batches: {total_batches}\n")

    try:
        added = 0

        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            batch_no = (i // batch_size) + 1

            print(f"➡️  Processing batch {batch_no}/{total_batches} "
                  f"({i+1}–{min(i+batch_size, total)})")

            vector_store.add_documents(batch)
            added += len(batch)

            print(f"   ✅ Stored {added}/{total} chunks\n")

        # Verify storage
        stored_count = vector_store._collection.count()

        print("🎉 Embedding completed successfully!")
        print(f"📊 Total stored vectors: {stored_count}")

        return {
            "success": True,
            "chunks_added": added,
            "total_stored": stored_count,
        }

    except Exception as e:
        print(f"❌ ERROR during embedding: {e}")
        return {"success": False, "error": str(e)}
    
if __name__ == "__main__":
    print(getSqlUrl())