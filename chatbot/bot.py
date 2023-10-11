import asyncio
import random
from queue import Queue
from typing import Optional, Dict

from langchain.prompts import PromptTemplate

from chatbot.memory import MemoryTypes
from chatbot.models import ModelTypes
from chatbot.common.config import Config, BaseObject
from chatbot.chain import ChainManager
from chatbot.prompt import PERSONALITY_PROMPT
from chatbot.common.objects import Message


class Bot(BaseObject):
    def __init__(
            self,
            config: Config = None,
            prompt_template: PromptTemplate = None,
            memory: Optional[MemoryTypes] = None,
            model: Optional[ModelTypes] = None,
            chain_kwargs: Optional[Dict] = None,
            memory_kwargs: Optional[Dict] = None,
            model_kwargs: Optional[Dict] = None,
    ):
        """
        Conversation chatbot
        :param config: System configuration
        :type config: Config
        :param prompt_template: Prompt template
        :type prompt_template: PromptTemplate
        :param memory: Conversation memory type
        :type memory: MemoryTypes
        :param model: Model type
        :type model: ModelTypes
        :param chain_kwargs: Keyword arguments for LangChain's chain. Default with verbose
        :type chain_kwargs: Dict
        :param memory_kwargs: Keyword arguments for Memory. Default with ConversationWindowBuffer arguments
        :type memory_kwargs: Dict
        :param model_kwargs: Keyword arguments for Model. Default with VertexAI arguments
        :type model_kwargs: Dict
        """
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(
            config=self.config,
            prompt_template=prompt_template,
            memory=memory,
            model=model,
            chain_kwargs=chain_kwargs if chain_kwargs else {"verbose": True},
            memory_kwargs=memory_kwargs if memory_kwargs else self.default_memory_kwargs,
            model_kwargs=model_kwargs if model_kwargs else self.default_model_kwargs
        )
        self.input_queue = Queue(maxsize=6)

    @property
    def default_model_kwargs(self):
        return {
            "max_output_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }

    @property
    def default_memory_kwargs(self):
        return {
            "k": 2
        }

    def set_personality(
            self,
            personalities: str = PERSONALITY_PROMPT
    ):
        self.chain.set_personality_prompt(personality_prompt=personalities)

    def reset_history(self, user_id: str = None):
        self.chain.reset_history(user_id=user_id)

    def predict(self, sentence: str, user_id: str = None):
        message = Message(message=sentence, role=self.config.human_prefix)
        return asyncio.run(self.chain(message, user_id=user_id))

    # async def process_batch(self):
    #     batch = []
    #     start_waiting_time = time.perf_counter()
    #     while True:
    #         if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
    #             await asyncio.sleep(0.5)
    #             continue
    #
    #         if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
    #             message: str = self.input_queue.get_nowait()
    #             batch.append(message)
    #             start_waiting_time = time.perf_counter()
    #             continue
    #
    #         start_waiting_time = time.perf_counter()
    #         if batch:
    #             _batch = "\n".join(batch)
    #             batch = []
    #             loop = asyncio.get_event_loop()
    #             await loop.run_in_executor(
    #                 executor=self._predict_executor,
    #                 func=lambda: self.predict(messages=_batch)
    #             )

    def send(self):
        user_id = str(random.randint(10000, 99999))
        while True:
            sentence = input("User:")
            output = self.predict(sentence, user_id=user_id)
            print("BOT:", output[0].message)

    # def task(self):
    #     while True:
    #         sentence = input("User:")
    #         if sentence:
    #             self.predict(sentence=sentence)
    #
    # def message(self):
    #     while True:
    #         if self.chain.output_queue.empty():
    #             time.sleep(0.5)
    #             continue
    #
    #         message = self.chain.output_queue.get_nowait()
    #         self.send_message_func(message)


if __name__ == "__main__":
    config = Config()
    bot = Bot(config=config)
    bot.send()
