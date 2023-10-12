from pydantic import BaseModel
import json
from typing import Optional, List, Dict, AsyncIterator
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks.tracers.log_stream import RunLogPatch

from chatbot import Bot
from chatbot import MemoryTypes, ModelTypes
from chatbot.common.objects import ChatRequest

bot = Bot(memory=MemoryTypes.CUSTOM_MEMORY, model=ModelTypes.VERTEX)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


async def transform_stream_for_client(
        stream: AsyncIterator[RunLogPatch],
) -> AsyncIterator[str]:
    async for chunk in stream:
        yield f"event: data\ndata: {json.dumps(jsonable_encoder(chunk))}\n\n"
    yield "event: end\n\n"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    sentence = request.message
    chat_history = request.history or []
    converted_chat_history = ""
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history += "Human: {}\n".format(message["human"])
        if message.get("ai") is not None:
            converted_chat_history += "AI: {}\n".format(message["ai"])
    stream = bot.chain.chain.astream_log(
        {"input": sentence, "history": converted_chat_history},
        include_names=["FindDocs"]
    )
    return StreamingResponse(
        transform_stream_for_client(stream),
        headers={"Content-Type": "text/event-stream"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
