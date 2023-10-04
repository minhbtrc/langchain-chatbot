from chat_ui.base_ui import BaseGradioUI
from chatbot.common.config import Config
from chatbot.memory import WindowChatbotMemory
from chatbot.chain import ChainManager


class CustomChainManager(ChainManager):
    def create_chatbot_memory(self):
        return WindowChatbotMemory.create(config=self.config)


if __name__ == "__main__":
    config = Config()
    chain = CustomChainManager(config=config)
    chain.init()
    demo = BaseGradioUI(config, llm_chain=chain)
    demo.start_demo()
