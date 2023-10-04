from typing import List, Dict

from pydantic import BaseModel, field_validator, Field

class Role:
    User = "USER"
    AI = "AI"
    System = "SYSTEM"

class BaseMessage(BaseModel):
    message: str = Field(description="User message")
    role: str = Field(description="Message role in conversation", default="User")
    id: str = Field(description="User id to distinguish from others", default="0123")
    