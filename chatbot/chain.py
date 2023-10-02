from typing import List
import langchain
from langchain.cache import InMemoryCache, RedisCache
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.chat_models import ChatVertexAI

from common.config import BaseSingleton, Config
from chatbot.prompt import *
from common.objects import BaseMessage

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
        self._init_chain()
        
    def _init_chain(self, partial_variables: dict=None):
        if partial_variables is None:
            partial_variables = {}
            
        prompt = PromptTemplate(
            template=PROMPT,
            input_variables=["message", "history"],
            partial_variables=partial_variables
        )
        self.chain = LLMChain(
            llm=self.base_model,
            prompt=self.prompt,
            verbose=True
        )

    def set_cache(self):
        langchain.llm_cache = CACHE_TYPE[self.config.cache_type]()

    def reset_prompt(self, personality_prompt: str):
        self._init_chain(partial_variables={"partial_variables":partial_variables})
        
    async def send_message(self, messages: List[BaseMessage]):
        sentences = [message.message for message in messages]
        output = await self.chain.abatch(sentences)
        return output