import asyncio
import copy
import time
from typing import List, Union
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatVertexAI

from chatbot.common.config import BaseSingleton, Config
from chatbot.prompt import *
from chatbot.common.objects import BaseMessage
from chatbot.utils import ChatbotCache
from chatbot.memory import BaseChatbotMemory


class ChainManager(BaseSingleton):
    def __init__(
            self,
            config: Config = None,
            parameters: dict = None,
            memory_class: BaseChatbotMemory = None
    ):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = None
        self._base_model = None
        self.input_queue = None
        self.output_queue = None
        self.input_worker = None
        self._parameters = parameters if parameters is not None else {
            "max_output_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }
        self._memory = None
        self._cache = None
        self._predict_executor = ThreadPoolExecutor(max_workers=1)
        memory_class = memory_class if memory_class is not None else BaseChatbotMemory
        self._memory = memory_class(config=self.config)

    def init(self):
        self._memory.init()
        self._init_chain()

    @property
    def memory(self):
        return self._memory.memory

    def create_model(self):
        return ChatVertexAI(model_name=self.config.base_model_name, **self.parameters)

    def _init_chain(self, partial_variables: dict = None, promt_template: str = CHATBOT_PROMPT):
        if partial_variables is None:
            partial_variables = {"personality": PERSONALITY_PROMPT}

        _prompt = PromptTemplate(
            template=promt_template,
            input_variables=["input", "history"],
            partial_variables=partial_variables
        )
        self._cache = ChatbotCache.create(config=self.config)
        self._base_model = self.create_model()

        self.chain = ConversationChain(
            llm=self._base_model,
            prompt=_prompt,
            verbose=True,
            memory=self._memory.memory
        )

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, _params: dict):
        self._parameters = _params
        self._init_chain()

    def reset_history(self):
        self._memory.clear()

    def set_prompt(self, personality_prompt: str):
        self._init_chain(partial_variables={"personality": personality_prompt})

    async def _predict(self, messages: List[BaseMessage]):
        sentences = [message.message for message in messages]
        output = self.chain.batch(sentences)
        output = [
            BaseMessage(message=out["response"], role=self.config.ai_prefix, user_id=messages[idx].user_id)
            for idx, out in enumerate(output)
        ]
        return output

    async def predict(self, messages: List[BaseMessage]):
        output = await self._predict(messages=messages)
        return output

    # def wrapper(self):
    #     try:
    #         loop = asyncio.get_event_loop()
    #     except:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #
    #     loop.run_until_complete(self.process())
    #
    # async def process_batch(self):
    #     batch = []
    #     start_waiting_time = time.perf_counter()
    #     while True:
    #         if self.input_queue.empty() and (time.perf_counter() - start_waiting_time <= self.config.waiting_time):
    #             await asyncio.sleep(0.5)
    #             continue
    #
    #         if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
    #             message: BaseMessage = self.input_queue.get_nowait()
    #             batch.append(message)
    #             start_waiting_time = time.perf_counter()
    #             continue
    #
    #         start_waiting_time = time.perf_counter()
    #         if batch:
    #             _batch = copy.deepcopy(batch)
    #             batch = []
    #             loop = asyncio.get_event_loop()
    #             await loop.run_in_executor(
    #                 executor=self._predict_executor,
    #                 func=lambda: self._predict(messages=_batch)
    #             )
    #
    # async def process(self):
    #     while True:
    #         if self.input_queue.empty():
    #             await asyncio.sleep(0.5)
    #             continue
    #
    #         message: BaseMessage = self.input_queue.get_nowait()
    #         loop = asyncio.get_event_loop()
    #         await loop.run_in_executor(
    #             executor=self._predict_executor,
    #             func=lambda: self._predict(messages=[message])
    #         )
