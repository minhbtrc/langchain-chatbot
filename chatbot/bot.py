import asyncio
import time
from queue import Queue
from threading import Thread

from common.config import Config, BaseSingleton
from chatbot.chain import ChainManager
from chatbot.prompt import PERSONALITY_PROMPT
from common.objects import BaseMessage


class Bot(BaseSingleton):
    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(config=config)
        self.input_queue = Queue(maxsize=6)
        self.worker = None
        self.out_worker = None
        self.init()

    def init(self):
        self.chain.init()
        self.worker = Thread(target=self.task, daemon=True)
        self.out_worker = Thread(target=self.message, daemon=True)

    def start(self):
        self.chain.start()
        self.worker.start()
        self.out_worker.start()

    def join(self):
        self.chain.join()
        self.worker.join()
        self.out_worker.join()

    def set_personality(
            self,
            **kwargs
    ):
        personality_prompt = PERSONALITY_PROMPT.format(**kwargs)
        self.chain.reset_prompt(personality_prompt=personality_prompt)

    def task(self):
        while True:
            sentence = input("MESSAGE:")
            self.chain.input_queue.put(BaseMessage(message=sentence))

    def message(self):
        while True:
            if self.chain.output_queue.empty():
                time.sleep(0.5)
                continue
            message = self.chain.output_queue.get_nowait()
            print(message.message)


if __name__ == "__main__":
    config = Config()
    bot = Bot(config=config)
    bot.start()
    bot.join()
