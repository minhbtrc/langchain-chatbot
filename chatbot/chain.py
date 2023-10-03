import asyncio
import time
from typing import List, Union
from threading import Thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
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
        self.prompt: Union[PromptTemplate, None] = None
        self.chain = None
        self.base_model = None
        self.input_queue = None
        self.output_queue = None
        self.input_worker = None
        self.parameters = parameters if parameters is not None else {
            "max_output_tokens": 256,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }
        self.executor = ThreadPoolExecutor(max_workers=1)

    def create_tasks(self):
        return asyncio.run(self.send_message())

    def init(self):
        self.prompt = PromptTemplate(
            template=CHATBOT_PROMPT,
            input_variables=["message", "history", "personality"]
        )
        self.base_model = ChatVertexAI(model_name=self.config.base_model_name, **self.parameters)
        self.set_cache()
        self._init_chain()
        self.input_queue = Queue(maxsize=self.config.model_max_input_size)
        self.output_queue = Queue(maxsize=self.config.model_max_input_size)
        # self.input_worker = Thread(target=self.send_message, daemon=True)

    def start(self):
        # self.input_worker.start()
        self.create_tasks()

    def join(self):
        # self.input_worker.join()
        pass

    def _merge_prompt(self, partial_variables: dict):
        partial_variables = {
            k: v
            for k, v in partial_variables if k in self.prompt.input_variables
        }
        return self.prompt.partial(**partial_variables)

    def _init_chain(self, partial_variables: dict = None):
        if partial_variables is None:
            partial_variables = {}

        _prompt = self._merge_prompt(partial_variables=partial_variables)
        self.chain = LLMChain(
            llm=self.base_model,
            prompt=_prompt,
            verbose=True
        )

    def set_cache(self):
        langchain.llm_cache = CACHE_TYPE[self.config.cache_type]()

    def reset_prompt(self, personality_prompt: str):
        self._init_chain(partial_variables={"partial_variables": personality_prompt})

    async def _predict(self, messages: List[BaseMessage]):
        sentences = [message.message for message in messages]
        output = await self.chain.abatch(sentences)
        for out in output:
            self.output_queue.put(BaseMessage(message=out["generated_text"]))

    async def send_message(self):
        batch = []
        start_waiting_time = time.perf_counter()
        while True:
            print(3333333)
            if self.input_queue.empty():
                await asyncio.sleep(0.5)
                continue

            if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
                message: BaseMessage = self.input_queue.get_nowait()
                batch.append(message)
                continue

            await self._predict(messages=batch)
            batch = []
