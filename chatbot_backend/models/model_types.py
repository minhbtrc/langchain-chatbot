from enum import Enum
from langchain.chat_models import ChatVertexAI, ChatOpenAI
from langchain.llms import LlamaCpp


class ModelTypes(str, Enum):
    OPENAI = "OPENAI"
    VERTEX = "VERTEX"
    LLAMA_CPP = "LLAMA-CPP"


MODEL_TO_CLASS = {
    "OPENAI": ChatOpenAI,
    "VERTEX": ChatVertexAI,
    "LLAMA-CPP": LlamaCpp
}
