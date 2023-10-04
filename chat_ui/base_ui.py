from typing import Any

import gradio as gr
from langchain.prompts import PromptTemplate

from chatbot.prompt import *
from chatbot.chain import ChainManager
from chatbot.common.config import Config


class BaseGradioUI:
    def __init__(
        self,
        config: Config,
        llm_chain: ChainManager = None,
        llm=None,
        prompt_template: PromptTemplate = CHATBOT_PROMPT
    ):
        self.config = config
        assert llm_chain or (llm and prompt_template), "Must provide llm_chain or llm"
        if llm_chain:
            self.chain = llm_chain
        else:
            self.chain = ChainManager(config=config)

    @staticmethod
    def user_state(message: str, chat_history: Any):
        """Initiate user state and chat history

        Args:
            message (str): user message
            chat_history (Any): chat history
        """

        return "", chat_history + [[message, None]]

    def load_chat_history(self, chat_history: Any):
        self.chain.memory.clear()
        memory = self.chain.memory.chat_memory
        for history in chat_history[:-1]:
            memory.add_user_message(history[0])
            memory.add_ai_message(history[1])

    def respond(self, chat_history):
        message = chat_history[-1][0]
        self.load_chat_history(chat_history)
        bot_message = self.chain.predict(message=message)
        chat_history[-1][-1] = bot_message
        return chat_history

    def start_demo(self, port=8000, debug=False, share=True):
        with gr.Blocks() as demo:
            gr.Markdown("""<h1><center> LLM Assistant </center></h1>""")
            chatbot = gr.Chatbot(label="Assistant").style(height=700)

            with gr.Row():
                message = gr.Textbox(show_label=False,
                                     placeholder="Enter your prompt and press enter",
                                     visible=True)
            message.submit(
                self.user_state,
                [message, chatbot],
                [message, chatbot],
                queue=False
            ).then(
                self.respond,
                inputs=chatbot,
                outputs=chatbot
            )

        demo.queue()
        demo.launch(debug=debug, server_port=port, share=share)
