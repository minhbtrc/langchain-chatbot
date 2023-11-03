from gradio_ui.base_ui import BaseGradioUI
from chatbot import MemoryTypes, ModelTypes, CacheTypes

if __name__ == "__main__":
    demo = BaseGradioUI(
        bot_memory=MemoryTypes.CUSTOM_MEMORY,
        bot_model=ModelTypes.OPENAI,
        # bot_cache=CacheTypes.GPTCache
    )
    demo.start_demo()
