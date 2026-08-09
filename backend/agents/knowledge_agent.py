import os
from langchain_huggingface import HuggingFaceEmbeddings
from apps.knowledge.repository import KnowledgeRepository
from state.schema import AgentState
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings

repo = KnowledgeRepository()


async def knowledge_agent_node(state: AgentState) -> AgentState:
    logger.info("📚 KNOWLEDGE AGENT CALLED")
    message = state.get("customer_message")
    logger.info(f"🔍 Searching knowledge base for: {message}")

    if not message:
        return {"retrieved_context": ""}

    query_vec = get_embeddings().embed_query(message)

    hits = repo.vector_similarity_search(query_vec, top_k=3)

    context = "\n\n".join([h["content"] for h in hits])
    logger.info(f"✅ Retrieved {len(hits)} chunk(s) from Supabase PostgreSQL pgvector")

    return {"retrieved_context": context}