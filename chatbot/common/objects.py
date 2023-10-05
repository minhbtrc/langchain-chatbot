from pydantic import BaseModel, field_validator, Field


class BaseMessage(BaseModel):
    message: str = Field(description="User message")
    role: str = Field(description="Message role in conversation", default="USER")
    user_id: str = Field(description="User id to distinguish from others", default="-1")
