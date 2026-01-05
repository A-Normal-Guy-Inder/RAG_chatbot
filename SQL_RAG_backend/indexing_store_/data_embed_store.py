from ..vectordb import get_vectordb
import math

def embed_store(chunks, batch_size=50):
    vector_store = get_vectordb()
    """
    Add chunks to vector store with progress printing.
    """
    if not chunks:
        print("❌ ERROR: No chunks provided")
        return {"success": False, "error": "No chunks provided"}
    
    vector_store.delete_collection()
    vector_store.create_collection()

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


        print("🎉 Embedding completed successfully!")

        return {
            "success": True,
            "chunks_added": added,
        }

    except Exception as e:
        print(f"❌ ERROR during embedding: {e}")
        return {"success": False, "error": str(e)}
    