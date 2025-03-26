"""FastAPI application for the chatbot."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..config import get_settings, Settings
from ..chat.manager import ChatManager
from .models import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for setup and teardown."""
    # Startup: create chat manager
    chat_manager = ChatManager()
    app.state.chat_manager = chat_manager
    
    yield
    
    # Shutdown: close resources
    app.state.chat_manager.close()


def create_app() -> FastAPI:
    """Create the FastAPI application.
    
    Returns:
        FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="LangChain Chatbot API",
        description="API for the LangChain chatbot",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
        """Process a chat message.
        
        Args:
            request: Chat request containing user message and conversation ID.
            
        Returns:
            AI response.
        """
        conversation_id = request.conversation_id or "default"
        
        response = await app.state.chat_manager.process_message(
            user_input=request.input,
            conversation_id=conversation_id
        )
        
        return ChatResponse(
            output=response,
            conversation_id=conversation_id
        )
    
    @app.post("/clear/{conversation_id}")
    async def clear_history(conversation_id: str):
        """Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation.
            
        Returns:
            Status message.
        """
        app.state.chat_manager.clear_history(conversation_id)
        return {
            "status": "success",
            "message": f"History for conversation {conversation_id} cleared"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint.
        
        Returns:
            Status message.
        """
        return {"status": "healthy"}
    
    return app 