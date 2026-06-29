from state.schema import AgentState

ESCALATION_CONDITIONS = {
    "low_confidence": lambda state: (state.get("confidence") or 1.0) < 0.6,
    "negative_complaint": lambda state: state.get("sentiment") == "negative" and state.get("intent") == "complaint",
    "negative_refund": lambda state: state.get("sentiment") == "negative" and state.get("intent") == "refund_request",
    "legal_issue": lambda state: state.get("intent") == "legal_issue",
}

ESCALATION_RESPONSE = "I understand your concern and I'm sorry for the inconvenience. I'm connecting you with a human support agent who will assist you shortly."

async def escalation_agent_node(state: AgentState) -> AgentState:
    for condition in ESCALATION_CONDITIONS.values():
        if condition(state):
            return {
                "escalate": True,
                "priority": "high",
                "final_response": ESCALATION_RESPONSE
            }
    return {
        "escalate": False,
        "priority": "low"
    }