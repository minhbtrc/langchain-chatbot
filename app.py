from chat_ui.base_ui import BaseGradioUI
from chatbot import MemoryTypes, ModelTypes

if __name__ == "__main__":
    demo = BaseGradioUI(bot_memory=MemoryTypes.CUSTOM_MEMORY,bot_model=ModelTypes.VERTEX)
    demo.start_demo()
