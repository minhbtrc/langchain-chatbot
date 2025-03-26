import logging
import os
import json
import vertexai
import urllib.parse

from .constants import CHAT_MODEL_NAME
from .common_keys import *


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseSingleton(metaclass=Singleton):
    pass


class BaseObject(BaseSingleton):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.class_name())

    @classmethod
    def class_name(cls):
        return cls.__name__


class Config(BaseObject):
    def __init__(
            self,
            credentials: str = None,
            cache_type: str = None,
            base_model_name: str = None,
            serp_api_token: str = None,
            model_max_input_size: int = 5,
            waiting_time: float = 2,
            memory_connection_string: str = None,
            memory_database_name: str = None,
            memory_collection_name: str = None,
            session_id: str = None,
            mongo_username: str = None,
            mongo_password: str = None,
            mongo_cluster: str = None,
            memory_window_size: int = 5
    ):
        super().__init__()
        self.credentials = credentials if credentials is not None else os.getenv(CREDENTIALS_FILE,
                                                                                 "secure/vertex.json")
        self.init_env()
        self.serp_api_token = serp_api_token if serp_api_token is not None else ""
        self.cache_type = cache_type if cache_type is not None else "in_memory"
        self.base_model_name = base_model_name if base_model_name is not None else CHAT_MODEL_NAME
        self.model_max_input_size = model_max_input_size
        self.waiting_time = waiting_time

        self.mongo_username = mongo_username if mongo_username is not None else os.getenv(MONGO_USERNAME)
        self.mongo_password = mongo_password if mongo_password is not None else os.getenv(MONGO_PASSWORD)
        if self.mongo_password:
            self.mongo_password = urllib.parse.quote_plus(self.mongo_password)
        if self.mongo_username:
            self.mongo_username = urllib.parse.quote_plus(self.mongo_username)
        self.mongo_cluster = mongo_cluster if mongo_cluster is not None else os.getenv(MONGO_CLUSTER)
        self.memory_database_name = memory_database_name if memory_database_name is not None \
            else os.getenv(MONGO_DATABASE, "langchain_bot")
        self.memory_collection_name = memory_collection_name if memory_collection_name is not None \
            else os.getenv(MONGO_COLLECTION, "chatbot")
        self.memory_connection_string = memory_connection_string if memory_connection_string is not None \
            else os.getenv(MONGO_CONNECTION_STRING,
                           f"mongodb+srv://{self.mongo_username}:{self.mongo_password}@{self.mongo_cluster}.xnkswcg.mongodb.net")
        self.session_id = session_id if session_id is not None else "chatbot_backend"
        self.memory_window_size = memory_window_size if memory_window_size is not None else 5
        self.ai_prefix = os.getenv(AI_PREFIX, "AI")
        self.human_prefix = os.getenv(HUMAN_PREFIX, "Human")
        self.memory_key = os.getenv(MEMORY_KEY, "history")
        self.enable_anonymizer = False

    def init_env(self):
        credential_data = json.load(open(self.credentials, "r"))
        project = credential_data["project_id"]
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials
        os.environ["GOOGLE_CLOUD_PROJECT"] = project
        vertexai.init(
            project=project,
            location="us-central1"
        )
