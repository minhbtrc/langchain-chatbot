from langchain.memory import MongoDBChatMessageHistory, ConversationBufferMemory

from chatbot.common.config import BaseSingleton, Config


class ChatbotMemory(BaseSingleton):
    @classmethod
    def create(cls, config: Config = None):
        config = config if config is not None else Config()
        _mem = MongoDBChatMessageHistory(
            connection_string=config.memory_connection_string,
            session_id=config.session_id,
            database_name=config.memory_database_name,
            collection_name=config.memory_collection_name
        )
        return ConversationBufferMemory(
            chat_memory=_mem
        )
