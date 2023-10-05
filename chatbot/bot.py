from queue import Queue
import asyncio

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
            clear_first: bool = False,
            send_message_func=None,
            memory_class=None
    ):
        """
        :param config: some configurations for chatbot
        :param clear_first: Whether clear conversation memory in starting or not
        :param send_message_func: Function that display message to user
        """
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(
            config=config,
            llm=llm,
            parameters=parameters,
            prompt_template=prompt_template,
            memory_class=memory_class
        )
        self.input_queue = Queue(maxsize=6)
        self.worker = None
        self.out_worker = None
        if clear_first:
            self.reset_history()
        self._send_message_func = send_message_func if send_message_func is not None else print

    def set_personality(
            self,
            **kwargs
    ):
        personality_prompt = PERSONALITY_PROMPT.format(**kwargs)
        self.chain.set_personality_prompt(personality_prompt=personality_prompt)

    def reset_history(self):
        self.chain.reset_history()

    def set_parameters(self, params: dict):
        self.chain.parameters = params

    @property
    def send_message_func(self):
        return self._send_message_func

    def predict(self, sentence: str, role: str = None, user_id: str = ""):
        if role is None:
            role = self.config.human_prefix
        message = BaseMessage(message=sentence, user_id=user_id, role=role)
        # self.chain.input_queue.put(message)
        return asyncio.run(self.chain.predict([message]))

    def send(self):
        import random
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
