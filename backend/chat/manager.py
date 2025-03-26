"""Chat manager for handling conversations with LLMs."""
from typing import Any, Dict, Optional
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from ..config import settings
from ..database.mongodb import MongodbClient


class ChatManager:
    """Manager for chat interactions with LLMs."""
    
    def __init__(self, 
                 model_name: Optional[str] = None,
                 temperature: float = 0.7):
        """Initialize the chat manager.
        
        Args:
            model_name: Name of the model to use, defaults to configuration.
            temperature: Temperature for generation, higher means more creative.
        """
        self.model_name = model_name or settings.base_model_name
        self.temperature = temperature
        
        # Initialize database client
        self.db = MongodbClient()
        
        # Initialize chat components
        self._init_chat_components()
    
    def _init_chat_components(self) -> None:
        """Initialize chat components."""
        # Create the prompt template
        self.template = ChatPromptTemplate.from_template(
            """
            You are a helpful AI assistant. 
            Be concise, friendly, and helpful.
            
            Chat History:
            {history}
            
            User: {input}
            AI:
            """
        )
        
        # Create the chat model - using OpenAI for now
        self.model = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # Create the output parser
        self.output_parser = StrOutputParser()
        
        # Create the chain
        self.chain = self.template | self.model | self.output_parser
    
    async def process_message(self, user_input: str, conversation_id: str) -> str:
        """Process a user message and return the AI response.
        
        Args:
            user_input: Message from the user.
            conversation_id: ID of the conversation.
        
        Returns:
            Response from the AI.
        """
        # Get conversation history
        history = self.db.format_history(conversation_id)
        
        # Generate response
        response = await self.chain.ainvoke({
            "history": history,
            "input": user_input
        })
        
        # Add message pair to history
        self.db.add_conversation_message(
            conversation_id=conversation_id,
            user_message=user_input,
            ai_message=response
        )
        
        return response
    
    def clear_history(self, conversation_id: str) -> None:
        """Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation.
        """
        self.db.clear_conversation_history(conversation_id)
    
    def close(self) -> None:
        """Close resources."""
        self.db.close() 