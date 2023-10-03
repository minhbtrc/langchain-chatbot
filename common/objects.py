from typing import List, Dict

from pydantic import BaseModel, field_validator, Field

class Role:
    User = "USER"
    AI = "AI"
    System = "SYSTEM"

class BaseMessage(BaseModel):
    message: str = Field(default="User message")
    role: str = Field(default="Message role in conversation")
    
    @field_validator("role")
    def validate_role(cls, value):
        if value not in Role.__dict__.keys():
            raise ValueError()
    