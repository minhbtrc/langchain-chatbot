from common.config import Config, BaseSingleton
from chatbot.chain import ChainManager


class Bot(BaseSingleton):
    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(config=config)

    def init(self):
        self.chain.init()

    def set_personality(
            self,
            gender: str = "auto",
    ):
        pass

    def process_message(self):
        pass


if __name__ == "__main__":
    config = Config(

    )
    bot = Bot(config=config)