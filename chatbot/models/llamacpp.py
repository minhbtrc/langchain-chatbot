from chatbot.models import CustomLLM


class LlamaCpp(CustomLLM):
    def __init__(self, config: Config):
        super().__init__(config=config)