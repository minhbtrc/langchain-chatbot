from enum import Enum
from langchain.chat_models import ChatVertexAI, ChatOpenAI

from chatbot.models import LlamaCpp

class ModelTypes(Enum):
    OPENAI: "OPENAI"
    VERTEX: "VERTEX"
    LLAMA_CPP: "LLAMA-CPP"
    
MODEL_TO_CLASS = {
    "OPENAI": ChatOpenAI,
    "VERTEX": ChatVertexAI,
    "LLAMA-CPP": LlamaCpp
}