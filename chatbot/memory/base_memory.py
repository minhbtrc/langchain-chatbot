from langchain.memory import ConversationBufferWindowMemory, ChatMessageHistory

from chatbot.common.config import BaseSingleton, Config


class BaseChatbotMemory(BaseSingleton):
    __slots__ = ["_base_memory", "_memory"]

    def __init__(
            self,
            config: Config = None,
            chat_history_class=ChatMessageHistory,
            memory_class=ConversationBufferWindowMemory,
            **kwargs
    ):
        """
        Base chatbot memory
        :param config: Config object
        :type config: Config
        :param chat_history_class: LangChain's chat history class
        :type chat_history_class:
        :param memory_class: LangChain's memory class
        :type memory_class:
        :param kwargs: Memory class kwargs
        :type kwargs:
        """
        self.config = config if config is not None else Config()
        self._params = kwargs
        self._base_memory = chat_history_class()
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

    def clear(self):
        self._base_memory.clear()
