from typing import Optional

from langchain.memory import ConversationBufferWindowMemory, ChatMessageHistory

from common.config import BaseObject, Config
from common.objects import MessageTurn


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
        Base chatbot_backend memory
        :param config: Config object
        :param chat_history_class: LangChain's chat history class
        :param memory_class: LangChain's memory class
        :param kwargs: Memory class kwargs
        """
        super().__init__()
        self.config = config if config is not None else Config()
        self._params = kwargs
        self.chat_history_kwargs = chat_history_kwargs or {}
        self._base_memory_class = chat_history_class
        self._memory = memory_class(**self.params)
        self._user_memory = dict()

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

    @property
    def user_memory(self):
        return self._user_memory

    def clear(self, conversation_id: str):
        if conversation_id in self.user_memory:
            memory = self.user_memory.pop(conversation_id)
            memory.clear()

    def load_history(self, conversation_id: str) -> str:
        if conversation_id not in self._user_memory:
            memory = self._base_memory_class(**self.chat_history_kwargs)
            self.memory.chat_memory = memory
            self.user_memory[conversation_id] = memory
            return ""

        self.memory.chat_memory = self.user_memory.get(conversation_id)
        return self._memory.load_memory_variables({})["history"]

    def add_message(self, message_turn: MessageTurn):
        pass
