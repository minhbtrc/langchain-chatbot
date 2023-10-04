import asyncio
import copy
import time
from typing import List, Union
from threading import Thread
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
    def __init__(self, config: Config = None, parameters: dict = None, prompt=CHATBOT_PROMPT):
        super().__init__()
        self.config = config if config is not None else Config()
        self.prompt: Union[PromptTemplate, None] = prompt
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

    @property
    def memory(self):
        return self.chain.memory

    def init(self):
        self._init_chain()
        self.input_queue = Queue(maxsize=self.config.model_max_input_size)
        self.output_queue = Queue(maxsize=self.config.model_max_input_size)
        self.input_worker = Thread(target=self.wrapper, daemon=True)

    def start(self):
        self.input_worker.start()

    def join(self):
        self.input_worker.join()

    def _merge_prompt(self, partial_variables: dict):
        partial_variables = {
            k: v
            for k, v in partial_variables.items() if k in self._prompt.input_variables
        }
        return self._prompt  # .partial(**partial_variables)

    def create_chatbot_memory(self):
        return BaseChatbotMemory.create(config=self.config)

    def create_model(self):
        return ChatVertexAI(model_name=self.config.base_model_name, **self.parameters)

    def _init_chain(self, partial_variables: dict = None):
        if partial_variables is None:
            partial_variables = {"personality": PERSONALITY_PROMPT}

        self._prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["input", "history"],
            partial_variables=partial_variables
        )
        self._cache = ChatbotCache.create(config=self.config)
        self._memory = self.create_chatbot_memory()
        self._base_model = self.create_model()

        _prompt = self._merge_prompt(partial_variables=partial_variables)
        self.chain = ConversationChain(
            llm=self._base_model,
            prompt=_prompt,
            verbose=True,
            memory=self._memory
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

    def _batch_predict(self, messages: List[BaseMessage]):
        sentences = [message.message for message in messages]
        output = self.chain.batch(sentences)
        for out in output:
            self.output_queue.put(BaseMessage(message=out["response"]))

    def wrapper(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(self.process())

    async def process(self):
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
                self._batch_predict(messages=_batch)

    def predict(self, message):
        return self.chain.predict(input=message)
