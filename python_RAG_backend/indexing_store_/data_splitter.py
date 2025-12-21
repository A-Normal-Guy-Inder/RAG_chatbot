from langchain_text_splitters import RecursiveCharacterTextSplitter


def is_good_chunk(text: str) -> bool:
    """Filter chunks to ensure RAG quality. Less aggressive than before."""
    words = text.split()

    # 1️⃣ Drop tiny chunks (lowered from 30 to 20 words)
    if len(words) < 20:
        return False

    # 2️⃣ Drop navigation-heavy chunks (lowered from 3 to 5 short lines)
    short_lines = sum(
        1 for line in text.splitlines()
        if 1 <= len(line.split()) <= 3
    )
    if short_lines >= 5:
        return False

    # 3️⃣ Drop chunks without enough punctuation (lowered from 2 to 1 period)
    if text.count(".") < 1:
        return False

    # 4️⃣ Drop CTA / instruction-like chunks
    if any(
        phrase in text.lower()
        for phrase in ["scroll", "read more", "learn more", "explore", "click here"]
    ):
        return False
    
    # 5️⃣ Drop code-like or overly formatted chunks (usually noise)
    if text.count("{") > 2 or text.count("[") > 5:
        return False

    return True


def split_docs(docs):
    """Split documents into chunks optimized for RAG retrieval with progress output."""

    print(f"📄 Starting document splitting")
    print(f"🔹 Input documents: {len(docs)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,          # ≈130 words
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
        add_start_index=True,
    )

    # Step 1: Split
    all_splits = text_splitter.split_documents(docs)
    print(f"✂️  Raw chunks created: {len(all_splits)}")

    # Step 2: Filter
    chunks = []
    dropped = 0

    total = len(all_splits)
    for i, split in enumerate(all_splits, 1):
        if is_good_chunk(split.page_content):
            split.metadata.update({
                "chunk_size": len(split.page_content),
                "chunk_words": len(split.page_content.split())
            })
            chunks.append(split)
        else:
            dropped += 1

        # Progress print (every 10% or last item)
        if i % max(1, total // 10) == 0 or i == total:
            print(f"  🔄 Filtering progress: {i}/{total}")

    print(f"✅ Chunk filtering complete")
    print(f"📦 Kept chunks: {len(chunks)}")
    print(f"🗑️  Dropped chunks: {dropped}")

    return chunks
