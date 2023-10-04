from langchain.memory import ConversationBufferMemory, ChatMessageHistory

from chatbot.common.config import BaseSingleton, Config


class BaseChatbotMemory(BaseSingleton):
    @staticmethod
    def init_chat_memory():
        return ChatMessageHistory()

    @staticmethod
    def parse_params(config: Config, **kwargs):
        return {
            "ai_prefix": config.ai_prefix,
            "human_prefix": config.human_prefix,
            "memory_key": config.memory_key,
            **kwargs
        }

    @classmethod
    def create(cls, config: Config = None):
        config = config if config is not None else Config()
        _mem = cls.init_chat_memory()
        return ConversationBufferMemory(
            **cls.parse_params(config, chat_memory=_mem)
        )
