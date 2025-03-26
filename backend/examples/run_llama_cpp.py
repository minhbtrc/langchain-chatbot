import os

from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from chatbot_backend.gradio_ui import BaseGradioUI
from chatbot_backend.memory import MemoryTypes
from chatbot_backend.models import ModelTypes
from chatbot_backend.common.config import Config
from chatbot_backend.bot import Bot
from chatbot_backend.prompt import LLAMA_PROMPT, BOT_PERSONALITY


if __name__ == "__main__":
    GGML_MODEL_PATH = os.environ["GGML_MODEL_PATH"]
    config = Config()
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    partial_variables = {"personality": BOT_PERSONALITY}
    prompt_template = PromptTemplate(
        template=LLAMA_PROMPT,
        input_variables=["history", "input"],
        partial_variables=partial_variables
    )

    bot = Bot(
        config,
        prompt_template,
        model=ModelTypes.LLAMA_CPP,
        memory=MemoryTypes.CUSTOM_MEMORY,
        model_kwargs={
            "model_path": GGML_MODEL_PATH,
            "n_ctx": 512,
            "temperature": 0.75,
            "max_tokens": 512,
            "top_p": 0.95,
            "callback_manager": callback_manager,
            "verbose": True
        }
    )
    demo = BaseGradioUI(bot=bot)
    demo.start_demo()
