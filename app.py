from chat_ui.base_ui import BaseGradioUI
from chatbot import MemoryType

if __name__ == "__main__":
    demo = BaseGradioUI(bot_memory=MemoryType.CUSTOM_MEMORY)
    demo.bot.reset_history()
    demo.start_demo()
