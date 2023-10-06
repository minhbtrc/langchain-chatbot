import json
import logging
from langchain.memory import MongoDBChatMessageHistory
from langchain.schema.messages import BaseMessage, _message_to_dict

from chatbot.common.config import Config
from chatbot.memory.base_memory import BaseChatbotMemory

logger = logging.getLogger(__name__)


class ChatbotMongoDBChatMessageHistory(MongoDBChatMessageHistory):
    def __init__(
            self,
            connection_string: str,
            session_id: str,
            database_name: str = None,
            collection_name: str = None,
    ):
        super(ChatbotMongoDBChatMessageHistory, self).__init__(
            connection_string=connection_string,
            session_id=session_id,
            database_name=database_name,
            collection_name=collection_name,
        )

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in MongoDB"""
        from pymongo import errors

        try:
            self.collection.insert_one(
                {
                    "UserId": message.user_id,
                    "SessionId": self.session_id,
                    "History": json.dumps(_message_to_dict(message), ensure_ascii=False),
                }
            )
        except errors.WriteError as err:
            logger.error(err)

    def clear(self) -> None:
        # Not allow to clear all
        return
        # """Clear session memory from MongoDB"""
        # from pymongo import errors
        #
        # try:
        #     self.collection.delete_many({"SessionId": self.session_id})
        # except errors.WriteError as err:
        #     logger.error(err)

    def clear_with_id(self, user_id: str) -> None:
        """Clear session memory from MongoDB"""
        from pymongo import errors

        try:
            self.collection.delete_many({"SessionId": self.session_id, "UserId": user_id})
        except errors.WriteError as err:
            logger.error(err)


class MongoChatbotMemory(BaseChatbotMemory):
    def __init__(self, config: Config = None):
        super(MongoChatbotMemory, self).__init__(config=config)
        self.base_memory = ChatbotMongoDBChatMessageHistory(
            connection_string=self.config.memory_connection_string,
            session_id=self.config.session_id,
            database_name=self.config.memory_database_name,
            collection_name=self.config.memory_collection_name
        )
