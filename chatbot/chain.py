import langchain
from langchain.cache import InMemoryCache, RedisCache
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.chat_models import ChatVertexAI

from common.config import BaseSingleton, Config
from chatbot.prompt import *

CACHE_TYPE = {
    "in_memory": InMemoryCache,
    "redis": RedisCache
}


class ChainManager(BaseSingleton):
    def __init__(self, config: Config = None, parameters: dict = None):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = None
        self.parameters = parameters if parameters is not None else {
            "max_output_tokens": 256,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }

    def init(self):
        base_model = ChatVertexAI(model_name=self.config.base_model_name, **self.parameters)
        self.set_cache()

    def set_cache(self):
        langchain.llm_cache = CACHE_TYPE[self.config.cache_type]()
