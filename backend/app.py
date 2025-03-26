import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langserve import add_routes
from operator import itemgetter
from langchain_core.runnables import RunnableLambda

from bot import Bot
from models import ModelTypes
from memory import MemoryTypes
from common.objects import ChatRequest

# Load environment variables
load_dotenv()

# Initialize the bot with the desired configuration
bot = Bot(memory=MemoryTypes.CUSTOM_MEMORY, model=ModelTypes.VERTEX, tools=[])

# Create the FastAPI app
app = FastAPI(
    title="Chatbot App",
    description="Modern chatbot built with LangChain and LangSmith",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add LangServe routes for the chat endpoint
add_routes(
    app,
    {
        "sentence": itemgetter("input"),
        "conversation_id": itemgetter("conversation_id")
    } | RunnableLambda(bot.call),
    path="/chat",
    input_type=ChatRequest
)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Add clear history endpoint
@app.post("/clear/{conversation_id}")
async def clear_history(conversation_id: str):
    bot.reset_history(conversation_id=conversation_id)
    return {"status": "success", "message": f"History for conversation {conversation_id} cleared"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
