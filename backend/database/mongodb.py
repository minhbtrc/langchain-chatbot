"""MongoDB database client for the chatbot application."""
from typing import Dict, List, Any, Optional, cast
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..config import settings


class MongodbClient:
    """MongoDB client for chat history storage."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """Initialize the MongoDB client.
        
        Args:
            collection_name: Optional name of the MongoDB collection to use.
                Defaults to the value in settings.
        """
        self.mongo_uri = settings.mongo_uri
        self.client = MongoClient(self.mongo_uri)
        
        # Extract the database name from the MongoDB URI
        db_name = self.mongo_uri.split("/")[-1]
        
        # Get database and collection
        self.db: Database = self.client[db_name]
        self.collection: Collection = self.db[collection_name or settings.collection_name]
    
    def add_conversation_message(
        self, 
        conversation_id: str, 
        user_message: str, 
        ai_message: str
    ) -> None:
        """Add a message pair to the chat history.
        
        Args:
            conversation_id: ID of the conversation.
            user_message: Message from the user.
            ai_message: Response from the AI.
        """
        # Check if conversation exists
        conversation = self.collection.find_one({"conversation_id": conversation_id})
        
        # Get current UTC time
        current_time = datetime.now(timezone.utc)
        
        if conversation:
            # Update existing conversation
            self.collection.update_one(
                {"conversation_id": conversation_id},
                {"$push": {"messages": {
                    "user": user_message,
                    "ai": ai_message,
                    "timestamp": current_time
                }}}
            )
        else:
            # Create new conversation
            self.collection.insert_one({
                "conversation_id": conversation_id,
                "created_at": current_time,
                "messages": [{
                    "user": user_message,
                    "ai": ai_message,
                    "timestamp": current_time
                }]
            })
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get the chat history for a conversation.
        
        Args:
            conversation_id: ID of the conversation.
            
        Returns:
            List of message pairs.
        """
        conversation = self.collection.find_one({"conversation_id": conversation_id})
        
        if conversation:
            # Cast to the expected type to satisfy the type checker
            messages = cast(List[Dict[str, Any]], conversation.get("messages", []))
            return messages
        
        return []
    
    def clear_conversation_history(self, conversation_id: str) -> None:
        """Clear the chat history for a conversation.
        
        Args:
            conversation_id: ID of the conversation.
        """
        self.collection.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"messages": []}}
        )
    
    def format_history(self, conversation_id: str) -> str:
        """Format the chat history for use in prompts.
        
        Args:
            conversation_id: ID of the conversation.
            
        Returns:
            Formatted history string.
        """
        messages = self.get_conversation_history(conversation_id)
        
        if not messages:
            return ""
        
        formatted_history = ""
        for msg in messages:
            user_msg = msg.get("user", "")
            ai_msg = msg.get("ai", "")
            formatted_history += f"User: {user_msg}\nAI: {ai_msg}\n\n"
        
        return formatted_history.strip()
    
    def close(self) -> None:
        """Close the MongoDB client connection."""
        self.client.close() 