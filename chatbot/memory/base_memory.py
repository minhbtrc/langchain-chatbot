from typing import Optional
from langchain.memory import ConversationBufferWindowMemory, ChatMessageHistory

from chatbot.common.config import BaseObject, Config


class BaseChatbotMemory(BaseObject):
    __slots__ = ["_base_memory", "_memory"]

    def __init__(
            self,
            config: Config = None,
            chat_history_class=ChatMessageHistory,
            memory_class=ConversationBufferWindowMemory,
            chat_history_kwargs: Optional[dict] = None,
            **kwargs
    ):
        """
        Base chatbot memory
        :param config: Config object
        :param chat_history_class: LangChain's chat history class
        :param memory_class: LangChain's memory class
        :param kwargs: Memory class kwargs
        """
        super().__init__()
        self.config = config if config is not None else Config()
        self._params = kwargs
        chat_history_kwargs = chat_history_kwargs or {}
        self._base_memory = chat_history_class(**chat_history_kwargs)
        self._memory = memory_class(chat_memory=self._base_memory, **self.params)

    @property
    def params(self):
        if self._params:
            return self._params
        else:
            return {
                "ai_prefix": self.config.ai_prefix,
                "human_prefix": self.config.human_prefix,
                "memory_key": self.config.memory_key,
                "k": self.config.memory_window_size
            }

    @property
    def memory(self):
        return self._memory

    def clear(self, user_id: str = None):
        self._base_memory.clear()
