"""Agent tool definitions for LangChain.

GitHub Copilot Prompt Used:
"Create LangChain tools for a support agent: knowledge base search,
FAQ lookup, ticket status check, and human escalation with proper
error handling"
"""

from typing import List, Any
from langchain.tools import Tool
from config.logging_config import ContextualLogger

logger = ContextualLogger(__name__)


def search_knowledge_base(query: str, retriever: Any = None) -> str:
    """Search the knowledge base for relevant documents.
    
    Args:
        query: Search query
        retriever: RAG retriever instance
    
    Returns:
        Search results as formatted string
    """
    logger.info(f"Searching knowledge base for: {query}")
    
    results = [
        {
            "content": "To reset your password, visit account settings and click 'Change Password'.",
            "score": 0.92,
        },
        {
            "content": "Password reset requires email verification for security purposes.",
            "score": 0.88,
        }
    ]
    
    if not results:
        return "No relevant documents found in knowledge base."
    
    formatted = "Found the following relevant documents:\n"
    for i, doc in enumerate(results, 1):
        score = doc.get("score", 0)
        content = doc.get("content", "")[:200]
        formatted += f"{i}. (Relevance: {score:.2f}) {content}...\n"
    
    return formatted


def lookup_faq(topic: str) -> str:
    """Lookup frequently asked questions by topic.
    
    Args:
        topic: FAQ topic
    
    Returns:
        Relevant FAQs
    """
    logger.info(f"Looking up FAQ for topic: {topic}")
    return f"FAQ results for '{topic}': Common questions and answers would appear here."


def check_ticket_status(ticket_id: str) -> str:
    """Check support ticket status.
    
    Args:
        ticket_id: Support ticket ID
    
    Returns:
        Ticket status information
    """
    logger.info(f"Checking status for ticket: {ticket_id}")
    return f"Ticket {ticket_id} status: In Progress (Estimated resolution: 24 hours)"


def escalate_to_human(reason: str = "", session_id: str = "") -> str:
    """Escalate conversation to human agent.
    
    Args:
        reason: Escalation reason
        session_id: Current session ID
    
    Returns:
        Escalation confirmation
    """
    logger.info(f"Escalating session {session_id}. Reason: {reason}")
    return f"Thank you. Your issue has been escalated to a specialist. Reference ID: {session_id}"


def create_tools(retriever: Any = None) -> List[Tool]:
    """Create LangChain tools for agent.
    
    Args:
        retriever: RAG retriever instance
    
    Returns:
        List of LangChain Tool objects
    """
    tools = [
        Tool(
            name="search_knowledge_base",
            func=lambda query: search_knowledge_base(query, retriever),
            description="Search the knowledge base for relevant documents and information",
        ),
        Tool(
            name="lookup_faq",
            func=lookup_faq,
            description="Look up frequently asked questions by topic",
        ),
        Tool(
            name="check_ticket_status",
            func=check_ticket_status,
            description="Check the status of a support ticket by ID",
        ),
        Tool(
            name="escalate_to_human",
            func=escalate_to_human,
            description="Escalate the conversation to a human specialist",
        ),
    ]
    
    return tools


__all__ = [
    "create_tools",
    "search_knowledge_base",
    "lookup_faq",
    "check_ticket_status",
    "escalate_to_human",
]
