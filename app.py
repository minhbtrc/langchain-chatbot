from chat_ui.base_ui import BaseGradioUI
from chatbot.common.config import Config
from chatbot.memory import MemoryType

if __name__ == "__main__":
    config = Config()
    demo = BaseGradioUI(config, bot_memory=MemoryType.MONGO_MEMORY)
    demo.bot.reset_history()
    demo.start_demo()
