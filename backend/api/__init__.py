"""API module for the chatbot application."""
from fastapi import FastAPI
from .routes import router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Chatbot API",
        description="API for interacting with the LangChain-powered chatbot",
        version="1.0.0",
    )
    
    # Include the routes
    app.include_router(router, prefix="")
    
    return app 