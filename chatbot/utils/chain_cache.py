import langchain
from langchain.cache import InMemoryCache, RedisCache

from chatbot.common.config import BaseSingleton, Config

CACHE_TYPE = {
    "in_memory": InMemoryCache,
    "redis": RedisCache
}


class ChatbotCache(BaseSingleton):
    @classmethod
    def create(cls, config: Config = None):
        config = config if config is not None else Config()
        langchain.llm_cache = CACHE_TYPE[config.cache_type]()
