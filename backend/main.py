"""Main entry point for the chatbot application."""
import os
import uvicorn
from .api import create_app
from .config import settings

app = create_app()

if __name__ == "__main__":
    """Run the application."""
    port = int(os.getenv("PORT", str(settings.port)))
    uvicorn.run(
        "chatbot_backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    ) 