import os
import json
import vertexai

from constants import CREDENTIALS_FILE, CHAT_MODEL_NAME
from common_keys import *


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseSingleton(metaclass=Singleton):
    pass


class Config(BaseSingleton):
    def __init__(self, cache_type: str = None, base_model_name: str = None, serp_api_token: str = None):
        super().__init__()
        self.serp_api_token = serp_api_token if serp_api_token is not None else ""
        self.cache_type = cache_type if cache_type is not None else "in_memory"
        self.base_model_name = base_model_name if base_model_name is not None else CHAT_MODEL_NAME
        self.init_env()

    @staticmethod
    def init_env():
        credential_data = json.load(open(CREDENTIALS_FILE, "r"))
        project = credential_data["project_id"]
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
        os.environ["GOOGLE_CLOUD_PROJECT"] = project
        vertexai.init(
            project=project,
            location="us-central1"
        )
