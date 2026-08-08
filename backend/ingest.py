import os
import uuid
from datetime import datetime
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from apps.knowledge.repository import KnowledgeRepository

KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE_PATH", "data/company_knowledge.txt")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def ingest_file(file_path: str = KNOWLEDGE_FILE, title: str = "Company Knowledge"):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Load document based on extension
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    documents = loader.load()

    # Split into chunks (chunk_size=500, chunk_overlap=50)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    doc_id = f"doc_{os.path.basename(file_path).replace('.', '_')}"
    size_bytes = os.path.getsize(file_path)

    repo = KnowledgeRepository()

    # Create document record with status pending
    repo.create_document({
        'id': doc_id,
        'title': title,
        'type': 'policy' if 'policy' in title.lower() else 'uploaded',
        'status': 'pending',
        'chunks': 0,
        'retrieval_count': 0,
        'last_updated': datetime.utcnow().isoformat(),
        'size_bytes': size_bytes,
        'file_path': file_path,
        'metadata': {'source': title, 'doc_id': doc_id}
    })

    # Embed chunks
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    chunks_data = []
    for idx, chunk in enumerate(chunks):
        emb = embeddings.embed_query(chunk.page_content)
        chunks_data.append({
            'id': f"{doc_id}#chunk_{idx}",
            'content': chunk.page_content,
            'embedding': emb,
            'metadata': {'source': title, 'doc_id': doc_id, 'chunk_index': idx}
        })

    # Replace chunks idempotently
    repo.replace_document_chunks(doc_id, chunks_data)
    print(f"✅ Ingested {len(chunks_data)} chunks for '{title}' into Supabase PostgreSQL pgvector!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        provided_path = sys.argv[1]
        base_name = os.path.basename(provided_path)
        name_without_ext = os.path.splitext(base_name)[0]
        generated_title = name_without_ext.replace('_', ' ').replace('-', ' ')
        ingest_file(file_path=provided_path, title=generated_title)
    else:
        ingest_file()