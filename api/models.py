"""Pydantic models for API requests and responses.

GitHub Copilot Prompt Used:
"Create Pydantic models for FastAPI with request/response schemas
for the chat endpoint including validation and examples"
"""

from pydantic import BaseModel, Field, constr
from typing import Dict, Any, List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat API request."""
    
    session_id: str = Field(
        ...,
        description="Unique session identifier",
        example="user-123",
    )
    message: constr(min_length=1, max_length=2000) = Field(
        ...,
        description="User message",
        example="How do I reset my password?",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context",
        example={"customer_tier": "premium"},
    )


class ChatResponse(BaseModel):
    """Chat API response."""
    
    session_id: str
    message_id: str
    response: str
    sources: List[Dict[str, Any]] = []
    reasoning_chain: List[str] = []
    metrics: Dict[str, float] = {}
    confidence_score: float
    timestamp: datetime
    execution_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="1.0.0")
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Metrics response."""
    
    total_conversations: int
    average_response_time_ms: float
    escalation_count: int
    timestamp: datetime


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
    "MetricsResponse",
]
