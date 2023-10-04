from langchain.memory import ConversationBufferWindowMemory

from chatbot.common.config import Config
from chatbot.memory.base_memory import BaseChatbotMemory


class WindowChatbotMemory(BaseChatbotMemory):
    @classmethod
    def create(cls, config: Config = None):
        config = config if config is not None else Config()
        _mem = cls.init_chat_memory()
        return ConversationBufferWindowMemory(
            **cls.parse_params(config, chat_memory=_mem)
        )
