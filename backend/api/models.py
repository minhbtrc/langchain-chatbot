"""API models for chatbot requests and responses."""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model."""
    
    input: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(default="default", description="Conversation ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    
    output: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID") 