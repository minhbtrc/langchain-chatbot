"""Configuration management for the chatbot application."""
import os
from typing import Any, Dict, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    model_type: str = Field(default="OPENAI", description="The type of model to use (OPENAI, VERTEX)")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    base_model_name: str = Field(default="gpt-3.5-turbo", description="Base model name to use")
    
    # MongoDB Configuration
    mongo_uri: str = Field(default="mongodb://localhost:27017/chatbot", 
                         description="MongoDB connection string")
    
    # Anonymizer Configuration
    enable_anonymizer: bool = Field(default=False, description="Enable PII anonymization")
    
    # Server Configuration
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Conversation prefixes for prompts
    human_prefix: str = Field(default="Human", description="Prefix for human messages in the prompt")
    ai_prefix: str = Field(default="AI", description="Prefix for AI messages in the prompt")
    
    # Misc settings
    collection_name: str = Field(default="chat_histories", description="MongoDB collection name")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


# Create global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Application settings object.
    """
    return settings 