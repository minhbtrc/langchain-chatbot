from chat_ui.base_ui import BaseGradioUI
from chatbot.common.config import Config

if __name__ == "__main__":
    config = Config()
    demo = BaseGradioUI(config)
    demo.init()
    demo.start_demo()
