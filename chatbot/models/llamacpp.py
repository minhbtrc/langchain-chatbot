from chatbot.models.base import CustomLLM
from chatbot.common.config import Config

class LlamaCpp(CustomLLM):
    def __init__(self, config: Config):
        super().__init__(config=config)