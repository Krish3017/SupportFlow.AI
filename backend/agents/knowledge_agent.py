import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from state.schema import AgentState
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embeddings
)

async def knowledge_agent_node(state: AgentState) -> AgentState:
    logger.info("📚 KNOWLEDGE AGENT CALLED")
    message = state.get("customer_message")
    logger.info(f"🔍 Searching knowledge base for: {message}")

    docs = vectorstore.similarity_search(message, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    logger.info(f"✅ Retrieved {len(docs)} documents from knowledge base")

    return {"retrieved_context": context}