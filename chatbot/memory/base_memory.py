from langchain.memory import ConversationBufferWindowMemory, ChatMessageHistory

from chatbot.common.config import BaseSingleton, Config


class BaseChatbotMemory(BaseSingleton):
    def __init__(self, config: Config = None):
        self.config = config if config is not None else Config()
        self.base_memory = ChatMessageHistory()
        self._memory = None

    def init(self):
        self._memory = ConversationBufferWindowMemory(
            chat_memory=self.base_memory,
            **self.params
        )

    @property
    def params(self):
        return {
            "ai_prefix": self.config.ai_prefix,
            "human_prefix": self.config.human_prefix,
            "memory_key": self.config.memory_key,
            "k": self.config.memory_window_size
        }

    @property
    def memory(self):
        return self._memory

    def clear(self):
        self.base_memory.clear()
