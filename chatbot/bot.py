from common.config import Config, BaseSingleton
from chatbot.chain import ChainManager
from chatbot.prompt  import PERSONALITY_PROMPT


class Bot(BaseSingleton):
    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(config=config)

    def init(self):
        self.chain.init()

    def set_personality(
            self,
            **kwargs
    ):
        personality_prompt = PERSONALITY_PROMPT.format(**kwargs)
        self.chain.reset_prompt(personality_prompt=personality_prompt)

    def process_message(self):
        pass


if __name__ == "__main__":
    config = Config(

    )
    bot = Bot(config=config)