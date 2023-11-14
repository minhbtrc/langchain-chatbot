import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from operator import itemgetter
from langchain.schema.runnable import RunnableLambda

from bot import Bot
from models import ModelTypes
from memory import MemoryTypes
from common.objects import ChatRequest

bot = Bot(memory=MemoryTypes.CUSTOM_MEMORY, model=ModelTypes.VERTEX, tools=[])
app = FastAPI(title="Chatbot App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

add_routes(
    app,
    {
        "sentence": itemgetter("input"),
        "conversation_id": itemgetter("conversation_id")
    } | RunnableLambda(bot.call),
    path="/chat",
    input_type=ChatRequest
)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
