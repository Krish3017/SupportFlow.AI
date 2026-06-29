import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from state.schema import AgentState
from langchain_core.messages import SystemMessage,HumanMessage
import json
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm=ChatGroq(
    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0"))
)

INTENT_SYSTEM_PROMPT = """
                        You are an intent classification expert for a customer support system.

                        Your job is to analyze customer messages and extract:
                        1. Primary intent category
                        2. Sub-intent (more specific)
                        3. Confidence score (0-1)
                        4. Sentiment (positive, negative, neutral)
                        5. Language code (en, es, fr, etc.)

                        **Available Intent Categories:**
                        - order_status: Customer asking about their order
                        - refund_request: Customer wants a refund
                        - technical_issue: Technical problems with product/service
                        - product_question: Questions about products/features
                        - billing_issue: Payment or billing problems
                        - complaint: Customer complaint or dissatisfaction
                        - feature_request: Requesting new features
                        - account_issue: Account access or settings problems
                        - general_inquiry: General questions or information requests

                        **Response Format:**
                        You MUST respond with ONLY a valid JSON object. No explanation, no markdown, just JSON.

                        {
                        "intent": "primary_intent_category",
                        "sub_intent": "more_specific_intent",
                        "confidence": 0.95,
                        "sentiment": "positive|negative|neutral",
                        "language": "en"
                        }

                        **Examples:**

                        Message: "Where is my order? It's been 5 days!"
                        Response:
                        {
                        "intent": "order_status",
                        "sub_intent": "delayed_order",
                        "confidence": 0.98,
                        "sentiment": "negative",
                        "language": "en"
                        }

                        Message: "How do I reset my password?"
                        Response:
                        {
                        "intent": "account_issue",
                        "sub_intent": "password_reset",
                        "confidence": 0.99,
                        "sentiment": "neutral",
                        "language": "en"
                        }

                        Message: "I'd like a refund for order #12345"
                        Response:
                        {
                        "intent": "refund_request",
                        "sub_intent": "order_refund",
                        "confidence": 0.97,
                        "sentiment": "neutral",
                        "language": "en"
                        }

                        Now analyze the customer message and respond with ONLY the JSON object.
                    """


async def intent_agent_node(state: AgentState) -> AgentState:
    logger.info("🎯 INTENT AGENT CALLED")
    message = state.get("customer_message")
    logger.info(f"📩 Input message: {message}")

    response = await llm.ainvoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=message)
    ])
    result = json.loads(response.content)
    logger.info(f"✅ Intent detected: {result.get('intent')} | Sentiment: {result.get('sentiment')} | Confidence: {result.get('confidence')}")

    return result
