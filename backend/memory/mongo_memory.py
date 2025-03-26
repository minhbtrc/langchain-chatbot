import logging
from langchain.memory import MongoDBChatMessageHistory

from common.config import Config
from memory.base_memory import BaseChatbotMemory

logger = logging.getLogger(__name__)


class MongoChatbotMemory(BaseChatbotMemory):
    def __init__(self, config: Config = None, **kwargs):
        config = config if config is not None else Config()
        super(MongoChatbotMemory, self).__init__(
            config=config,
            chat_history_class=MongoDBChatMessageHistory,
            chat_history_kwargs={
                "connection_string": config.memory_connection_string,
                "session_id": config.session_id,
                "database_name": config.memory_database_name,
                "collection_name": config.memory_collection_name
            }
        )
