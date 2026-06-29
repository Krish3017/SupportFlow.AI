"""
State schema for SupportFlow AI
Defines the master state shared across all agents
"""
from typing import Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Master state for the multi-agent system.
    All fields are optional except customer_message.
    """
    # Required field
    customer_message: str

    # Intent classification fields
    intent: Optional[str]  # Main intent category
    sub_intent: Optional[str]  # More specific intent
    confidence: Optional[float]  # Confidence score 0-1
    sentiment: Optional[str]  # positive, negative, neutral
    language: Optional[str]  # detected language code

    #Knowledge feilds
    retrieved_context: Optional[str]  # knowledge retrieved from vector store

    # Response fields
    final_response: Optional[str]  # The response to send back to user

    # Routing fields
    escalate: Optional[bool]  # Whether to escalate to human
    priority: Optional[str]  # low, medium, high, urgent

    customer_id: Optional[str]
    customer_context: Optional[dict]

    session_id: Optional[str]
    chat_history: Optional[list]
