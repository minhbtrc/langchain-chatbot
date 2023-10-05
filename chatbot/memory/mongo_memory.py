from langchain.memory import MongoDBChatMessageHistory

from chatbot.common.config import Config
from chatbot.memory.base_memory import BaseChatbotMemory


class MongoChatbotMemory(BaseChatbotMemory):
    def __init__(self, config: Config = None):
        super(MongoChatbotMemory, self).__init__(config=config)
        self.base_memory = MongoDBChatMessageHistory(
            connection_string=self.config.memory_connection_string,
            session_id=self.config.session_id,
            database_name=self.config.memory_database_name,
            collection_name=self.config.memory_collection_name
        )
