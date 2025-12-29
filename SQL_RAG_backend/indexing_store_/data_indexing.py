from SQL_RAG_backend.indexing_store_.web_loader import load_docs 
from SQL_RAG_backend.indexing_store_.pdf_loader import load_pdfs
from data_splitter import split_docs 
from data_embed_store import embed_store

web_docs = load_docs()
pdf_docs = load_pdfs()
docs = web_docs + pdf_docs
chunks = split_docs(docs)
res = embed_store(chunks)