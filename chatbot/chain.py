import asyncio
import copy
import time
from typing import List, Union
from threading import Thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import langchain
from langchain.cache import InMemoryCache, RedisCache
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
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

    def init(self):
        self.prompt = PromptTemplate(
            template=CHATBOT_PROMPT,
            input_variables=["input", "history"],
            partial_variables={"personality": PERSONALITY_PROMPT}
        )
        self.base_model = ChatVertexAI(model_name=self.config.base_model_name, **self.parameters)
        self.set_cache()
        self._init_chain()
        self.input_queue = Queue(maxsize=self.config.model_max_input_size)
        self.output_queue = Queue(maxsize=self.config.model_max_input_size)
        self.input_worker = Thread(target=self.send_message_wrapper, daemon=True)

    def start(self):
        self.input_worker.start()

    def join(self):
        self.input_worker.join()
        pass

    def _merge_prompt(self, partial_variables: dict):
        partial_variables = {
            k: v
            for k, v in partial_variables.items() if k in self.prompt.input_variables
        }
        return self.prompt#.partial(**partial_variables)

    def _init_chain(self, partial_variables: dict = None):
        if partial_variables is None:
            partial_variables = {}

        _prompt = self._merge_prompt(partial_variables=partial_variables)
        memory = ConversationBufferWindowMemory(k=6)
        self.chain = ConversationChain(
            llm=self.base_model,
            prompt=_prompt,
            verbose=False,
            memory=memory
        )

    def set_cache(self):
        langchain.llm_cache = CACHE_TYPE[self.config.cache_type]()

    def reset_prompt(self, personality_prompt: str):
        self._init_chain(partial_variables={"partial_variables": personality_prompt})

    def _predict(self, messages: List[BaseMessage]):
        sentences = [message.message for message in messages]
        output = self.chain.batch(sentences)
        for out in output:
            self.output_queue.put(BaseMessage(message=out["response"]))

    def send_message_wrapper(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(self.send_message())

    async def send_message(self):
        batch = []
        start_waiting_time = time.perf_counter()
        while True:
            if self.input_queue.empty() and (time.perf_counter() - start_waiting_time <= self.config.waiting_time):
                await asyncio.sleep(0.5)
                continue

            if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
                message: BaseMessage = self.input_queue.get_nowait()
                batch.append(message)
                start_waiting_time = time.perf_counter()
                continue

            start_waiting_time = time.perf_counter()
            if batch:
                _batch = copy.deepcopy(batch)
                batch = []
                self._predict(messages=_batch)
