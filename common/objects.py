from typing import List, Dict, Field

from pydantic import BaseModel, validator

class Role:
    User = "USER"
    AI = "AI"
    System = "SYSTEM"

class BaseMessage(BaseModel):
    message: str = Field(default="User message")
    role: str = Field(default="Message role in conversation")
    
    @validator("role")
    def validate_role(cls, value):
        if value not in Role.__dict__.keys():
            raise ValueError()
    