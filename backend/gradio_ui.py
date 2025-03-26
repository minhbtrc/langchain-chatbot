from typing import Any, Optional
import random

import gradio as gr

from bot import Bot
from memory import MemoryTypes
from models import ModelTypes
from utils import CacheTypes


class BaseGradioUI:
    def __init__(
            self,
            bot: Bot = None,
            bot_memory: Optional[MemoryTypes] = None,
            bot_model: Optional[ModelTypes] = None,
            bot_cache: Optional[CacheTypes] = None
    ):
        self.bot = bot if bot is not None else Bot(memory=bot_memory, model=bot_model, cache=bot_cache)
        self._conversation_id = None

    @staticmethod
    def create_conversation_id():
        return str(random.randint(100000000, 999999999))

    def user_state(self, message: str, chat_history: Any, conversation_id):
        """Initiate user state and chat history

        Args:
            message (str): user message
            chat_history (Any): chat history
        """
        if not conversation_id:
            conversation_id = self.create_conversation_id()
        return "", chat_history + [[message, None]], conversation_id

    def respond(self, conversation_id, chat_history):
        message = chat_history[-1][0]
        result = self.bot.predict(sentence=message, conversation_id=conversation_id)
        chat_history[-1][-1] = result.message
        return chat_history

    def start_demo(self, port=8000, debug=False, share=True):
        with gr.Blocks() as demo:
            conversation_id_state = gr.State("")
            gr.Markdown("""<h1><center> LLM Assistant </center></h1>""")
            chatbot = gr.Chatbot(label="Assistant").style(height=700)

            with gr.Row():
                message = gr.Textbox(show_label=False,
                                     placeholder="Enter your prompt and press enter",
                                     visible=True)

            btn_refresh = gr.ClearButton(components=[message, chatbot],
                                         value="Refresh the conversation history")

            def clear_user_state():
                return {conversation_id_state: ""}

            message.submit(
                self.user_state,
                inputs=[message, chatbot, conversation_id_state],
                outputs=[message, chatbot, conversation_id_state],
                queue=False
            ).then(
                self.respond,
                inputs=[conversation_id_state, chatbot],
                outputs=[chatbot]
            )
            btn_refresh.click(clear_user_state, outputs=conversation_id_state)
        demo.queue()
        demo.launch(debug=debug, server_port=port, share=share)


if __name__ == "__main__":
    demo = BaseGradioUI(
        bot_memory=MemoryTypes.CUSTOM_MEMORY,
        bot_model=ModelTypes.OPENAI,
        # bot_cache=CacheTypes.GPTCache
    )
    demo.start_demo()
