"""
Customer Support AI Agent implementation using LangChain.

This module implements a production-grade conversational AI agent that:
- Uses LangChain for agent orchestration
- Integrates with Azure OpenAI for LLM
- Performs RAG using Azure Cognitive Search
- Maintains conversation context
- Handles errors gracefully

GitHub Copilot Prompt Used:
"Create a production-grade LangChain agent for customer support with:
- Multi-turn conversation support
- RAG integration using Azure Cognitive Search
- Tool use (search, FAQ lookup, escalation)
- Error handling and retry logic
- Conversation memory management
- Proper logging and observability"
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import AzureChatOpenAI
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel, Field
import time

from config.settings import settings
from config.logging_config import ContextualLogger
from rag.retriever import RAGRetriever
from agents.tools import create_tools
from agents.prompts import SYSTEM_PROMPT

logger = ContextualLogger(__name__)


class ConversationMessage(BaseModel):
    """Represents a single conversation message."""
    
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Agent response with metadata."""
    
    session_id: str
    message_id: str
    response: str
    sources: List[Dict[str, Any]] = []
    reasoning_chain: List[str] = []
    metrics: Dict[str, float] = Field(default_factory=dict)
    confidence_score: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: float = 0.0


class SupportAgent:
    """
    Production-grade customer support AI agent.
    
    Features:
    - Multi-turn conversation with context
    - RAG-based knowledge retrieval
    - Tool use for external actions
    - Error handling and fallbacks
    - Performance monitoring
    - Evaluation metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the support agent.
        
        Args:
            config: Optional configuration overrides
        """
        logger.info("Initializing Customer Support Agent")
        
        self.config = config or {}
        self.settings = settings
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize RAG retriever
        self.retriever = RAGRetriever()
        
        # Initialize memory for conversation context
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 messages
            memory_key="chat_history",
            return_messages=True,
        )
        
        # Initialize tools
        self.tools = create_tools(self.retriever)
        
        # Initialize agent
        self.agent_executor = self._initialize_agent()
        
        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            "total_conversations": 0,
            "total_tokens_used": 0,
            "average_response_time_ms": 0,
            "escalation_count": 0,
        }
        
        logger.info("Customer Support Agent initialized successfully")
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """
        Initialize Azure OpenAI LLM.
        
        Returns:
            AzureChatOpenAI: Configured LLM instance
        """
        try:
            llm = AzureChatOpenAI(
                api_key=self.settings.azure_openai.api_key,
                api_version=self.settings.azure_openai.api_version,
                azure_endpoint=self.settings.azure_openai.endpoint,
                deployment_name=self.settings.azure_openai.deployment_name,
                temperature=self.settings.azure_openai.temperature,
                max_tokens=self.settings.azure_openai.max_tokens,
                top_p=self.settings.azure_openai.top_p,
            )
            logger.info("Azure OpenAI LLM initialized")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_agent(self) -> AgentExecutor:
        """
        Initialize LangChain agent.
        
        Returns:
            AgentExecutor: Configured agent executor
        """
        try:
            # Create agent with OpenAI functions
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=SYSTEM_PROMPT,
            )
            
            # Create executor
            executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True,
            )
            
            logger.info("Agent executor initialized")
            return executor
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def chat(
        self,
        message: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Process user message and return agent response.
        
        Args:
            message: User query
            session_id: Unique conversation session ID
            context: Additional context (customer_tier, order_id, etc.)
        
        Returns:
            AgentResponse: Agent response with metadata
        """
        start_time = time.time()
        message_id = f"msg-{int(start_time * 1000)}"
        
        logger.set_context(session_id=session_id, message_id=message_id)
        logger.info(f"Processing user message: {message[:100]}...")
        
        try:
            # Add context to message if provided
            if context:
                context_str = json.dumps(context)
                augmented_message = f"{message}\n\n[Context: {context_str}]"
            else:
                augmented_message = message
            
            # Run agent
            logger.info("Running agent executor")
            result = self.agent_executor.invoke(
                {"input": augmented_message},
                config={"tags": ["customer-support"]},
            )
            
            response_text = result.get("output", "")
            execution_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Agent response generated in {execution_time_ms:.2f}ms")
            
            # Extract sources from retriever
            sources = self._extract_sources()
            
            # Extract reasoning chain
            reasoning_chain = self._extract_reasoning_chain(result)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(result)
            
            # Create response
            agent_response = AgentResponse(
                session_id=session_id,
                message_id=message_id,
                response=response_text,
                sources=sources,
                reasoning_chain=reasoning_chain,
                confidence_score=confidence_score,
                execution_time_ms=execution_time_ms,
            )
            
            logger.info(
                f"Response generated successfully. "
                f"Confidence: {confidence_score:.2f}, "
                f"Sources: {len(sources)}"
            )
            
            # Update metrics
            self._update_metrics(agent_response)
            
            return agent_response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
            # Return fallback response
            return self._create_fallback_response(
                session_id=session_id,
                message_id=message_id,
                error=str(e),
            )
    
    def _extract_sources(self) -> List[Dict[str, Any]]:
        """
        Extract document sources from last retriever call.
        
        Returns:
            List of source documents with metadata
        """
        # This would be populated by the retriever
        # Implementation depends on how retriever stores metadata
        return []
    
    def _extract_reasoning_chain(self, result: Dict) -> List[str]:
        """
        Extract reasoning steps from agent execution.
        
        Args:
            result: Agent executor result
        
        Returns:
            List of reasoning steps
        """
        reasoning = []
        # Parse intermediate steps from result
        if "intermediate_steps" in result:
            for action, observation in result["intermediate_steps"]:
                reasoning.append(f"Tool: {action.tool}")
                reasoning.append(f"Observation: {observation[:100]}...")
        
        return reasoning
    
    def _calculate_confidence(self, result: Dict) -> float:
        """
        Calculate confidence score for response.
        
        Args:
            result: Agent executor result
        
        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence based on:
        # - Number of intermediate steps (more = more confident)
        # - Whether tools were used (yes = more confident)
        
        steps = len(result.get("intermediate_steps", []))
        base_confidence = min(0.5 + (steps * 0.1), 0.95)
        
        return base_confidence
    
    def _update_metrics(self, response: AgentResponse) -> None:
        """Update agent metrics."""
        self.metrics["total_conversations"] += 1
        self.metrics["average_response_time_ms"] = (
            (self.metrics["average_response_time_ms"] * 
             (self.metrics["total_conversations"] - 1) +
             response.execution_time_ms) /
            self.metrics["total_conversations"]
        )
    
    def _create_fallback_response(
        self,
        session_id: str,
        message_id: str,
        error: str,
    ) -> AgentResponse:
        """
        Create fallback response when agent fails.
        
        Args:
            session_id: Session ID
            message_id: Message ID
            error: Error message
        
        Returns:
            Fallback response
        """
        self.metrics["escalation_count"] += 1
        
        return AgentResponse(
            session_id=session_id,
            message_id=message_id,
            response=(
                "I apologize, but I encountered an issue processing your request. "
                "A human specialist will be assigned to help you shortly. "
                f"Reference ID: {message_id}"
            ),
            reasoning_chain=["Error occurred", "Escalating to human agent"],
            confidence_score=0.0,
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()
    
    def reset_session(self, session_id: str) -> None:
        """
        Reset conversation history for a session.
        
        Args:
            session_id: Session to reset
        """
        logger.info(f"Resetting session: {session_id}")
        self.memory.clear()


__all__ = [
    "SupportAgent",
    "AgentResponse",
    "ConversationMessage",
]
