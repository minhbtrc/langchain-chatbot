from queue import Queue
import asyncio
import time
import random

from langchain.prompts import PromptTemplate

from chatbot.common.config import Config, BaseSingleton
from chatbot.chain import ChainManager
from chatbot.prompt import PERSONALITY_PROMPT
from chatbot.common.objects import BaseMessage


class Bot(BaseSingleton):
    def __init__(
            self,
            config: Config = None,
            llm=None,
            parameters: dict = None,
            prompt_template: PromptTemplate = None,
            send_message_func=None,
            memory=None
    ):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(
            config=self.config,
            llm=llm,
            parameters=parameters,
            prompt_template=prompt_template,
            memory=memory,
            chain_kwargs={"verbose": True}
        )
        self.input_queue = Queue(maxsize=6)
        self._send_message_func = send_message_func if send_message_func is not None else print

    def set_personality(
            self,
            personalities: str = PERSONALITY_PROMPT
    ):
        self.chain.set_personality_prompt(personality_prompt=personalities)

    def reset_history(self, user_id: str = None):
        self.chain.reset_history(user_id=user_id)

    def set_parameters(self, params: dict):
        self.chain.parameters = params

    @property
    def send_message_func(self):
        return self._send_message_func

    def predict(self, sentence: str, role: str = None, user_id: str = None):
        if role is None:
            role = self.config.human_prefix
        message = BaseMessage(message=sentence, user_id=user_id, role=role)
        return asyncio.run(self.chain.predict([message]))

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
