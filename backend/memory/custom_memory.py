import json
from typing import List
from pymongo import MongoClient, errors

from common.config import Config, BaseObject
from common.objects import MessageTurn, messages_from_dict


class BaseCustomMongoChatbotMemory(BaseObject):
    def __init__(
            self,
            config: Config = None,
            connection_string: str = None,
            session_id: str = None,
            database_name: str = None,
            collection_name: str = None,
            k: int = 5,
            **kwargs
    ):
        super(BaseCustomMongoChatbotMemory, self).__init__()
        self.config = config if config is not None else Config()

        self.connection_string = connection_string
        self.session_id = session_id
        self.database_name = database_name
        self.collection_name = collection_name

        try:
            self.client: MongoClient = MongoClient(connection_string)
        except errors.ConnectionFailure as error:
            self.logger.error(error)

        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
        self.collection.create_index("SessionId")
        self.k = k

    def add_message(self, message_turn: MessageTurn):
        conversation_id = message_turn.conversation_id
        try:
            self.logger.info(f"Save 1 message turn of conversation <{conversation_id}>")
            self.collection.insert_one(
                {
                    "ConversationId": conversation_id,
                    "SessionId": self.session_id,
                    "History": json.dumps(message_turn.dict(), ensure_ascii=False),
                }
            )
        except errors.WriteError as err:
            self.logger.error(err)

    def clear_history(self, conversation_id: str = None):
        try:
            self.logger.info(f"Deleting the history of conversation <{conversation_id}> at session <{self.session_id}>")
            if conversation_id is None:
                self.logger.warning(f"You are deleting all collection with session: {self.session_id}")
                self.collection.delete_many({"SessionId": self.session_id})
            else:
                self.collection.delete_many({"SessionId": self.session_id, "ConversationId": conversation_id})
        except errors.WriteError as err:
            self.logger.error(err)

    def load_history(self, conversation_id: str) -> str:
        """Retrieve the messages from MongoDB"""
        from pymongo import errors
        cursor = None
        try:
            cursor = self.collection.find({"SessionId": self.session_id, "ConversationId": conversation_id})
        except errors.OperationFailure as error:
            self.logger.error(error)

        if cursor:
            items = [json.loads(document["History"]) for document in cursor][-self.k:]
        else:
            items = []

        messages: List[str] = [messages_from_dict(item) for item in items]
        return "\n".join(messages)


class CustomMongoChatbotMemory(BaseObject):
    def __init__(self, config: Config = None, **kwargs):
        super(CustomMongoChatbotMemory, self).__init__()
        self.memory = BaseCustomMongoChatbotMemory(
            connection_string=config.memory_connection_string,
            session_id=config.session_id,
            database_name=config.memory_database_name,
            collection_name=config.memory_collection_name,
            **kwargs
        )

    def clear(self, conversation_id: str = None):
        self.memory.clear_history(conversation_id=conversation_id)

    def load_history(self, conversation_id: str):
        return self.memory.load_history(conversation_id)

    def add_message(self, message_turn: MessageTurn):
        self.memory.add_message(message_turn)
