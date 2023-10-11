from typing import Any, Optional
import random

import gradio as gr

from chatbot.bot import Bot
from chatbot import MemoryTypes, ModelTypes


class BaseGradioUI:
    def __init__(
            self,
            bot: Bot = None,
            bot_memory: Optional[MemoryTypes] = None,
            bot_model: Optional[ModelTypes] = None
    ):
        self.bot = bot if bot is not None else Bot(memory=bot_memory, model=bot_model)
        self._user_id = None

    @staticmethod
    def create_user_id():
        return str(random.randint(100000000, 999999999))

    def user_state(self, message: str, chat_history: Any, user_id):
        """Initiate user state and chat history

        Args:
            message (str): user message
            chat_history (Any): chat history
        """
        if not user_id:
            user_id = self.create_user_id()
        return "", chat_history + [[message, None]], user_id

    def respond(self, user_id, chat_history):
        message = chat_history[-1][0]
        result = self.bot.predict(sentence=message, user_id=user_id)
        chat_history[-1][-1] = result.message
        return chat_history

    def start_demo(self, port=8000, debug=False, share=True):
        with gr.Blocks() as demo:
            user_id_state = gr.State("")
            gr.Markdown("""<h1><center> LLM Assistant </center></h1>""")
            chatbot = gr.Chatbot(label="Assistant").style(height=700)

            with gr.Row():
                message = gr.Textbox(show_label=False,
                                     placeholder="Enter your prompt and press enter",
                                     visible=True)

            btn_refresh = gr.ClearButton(components=[message, chatbot],
                                         value="Refresh the conversation history")

            def clear_user_state():
                return {user_id_state: ""}

            message.submit(
                self.user_state,
                inputs=[message, chatbot, user_id_state],
                outputs=[message, chatbot, user_id_state],
                queue=False
            ).then(
                self.respond,
                inputs=[user_id_state, chatbot],
                outputs=[chatbot]
            )
            btn_refresh.click(clear_user_state, outputs=user_id_state)
        demo.queue()
        demo.launch(debug=debug, server_port=port, share=share)
