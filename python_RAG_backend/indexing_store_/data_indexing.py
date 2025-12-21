from data_loader import load_docs 
from data_splitter import split_docs 
from data_embed_store import embed_store

docs = load_docs()
chunks = split_docs(docs)
res = embed_store(chunks)