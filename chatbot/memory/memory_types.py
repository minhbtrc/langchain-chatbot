from enum import Enum
from chatbot.memory import MongoChatbotMemory, BaseChatbotMemory


class MemoryType(str, Enum):
    """Enumerator with the Memory types."""

    BASE_MEMORY = "base-memory"
    MONGO_MEMORY = "mongodb-memory"


MEM_TO_CLASS = {
    "mongodb-memory": MongoChatbotMemory,
    "base-memory": BaseChatbotMemory
}
