import asyncio
import random
from queue import Queue
from typing import Optional, Dict

from langchain.prompts import PromptTemplate

from chatbot.memory import MemoryTypes
from chatbot.models import ModelTypes
from chatbot.common.config import Config, BaseObject
from chatbot.chain import ChainManager
from chatbot.prompt import BOT_PERSONALITY
from chatbot.common.objects import Message


class Bot(BaseObject):
    def __init__(
            self,
            config: Config = None,
            prompt_template: PromptTemplate = None,
            memory: Optional[MemoryTypes] = None,
            model: Optional[ModelTypes] = None,
            chain_kwargs: Optional[dict] = None,
            memory_kwargs: Optional[dict] = None,
            model_kwargs: Optional[dict] = None,
            bot_personality: str = BOT_PERSONALITY
    ):
        """
        Conversation chatbot
        :param config: System configuration
        :type config: Config
        :param prompt_template: Prompt template
        :type prompt_template: PromptTemplate
        :param memory: Conversation memory type
        :type memory: MemoryTypes
        :param model: Model type
        :type model: ModelTypes
        :param chain_kwargs: Keyword arguments for LangChain's chain. Default with verbose
        :type chain_kwargs: Dict
        :param memory_kwargs: Keyword arguments for Memory. Default with ConversationWindowBuffer arguments
        :type memory_kwargs: Dict
        :param model_kwargs: Keyword arguments for Model. Default with VertexAI arguments
        :type model_kwargs: Dict
        """
        super().__init__()
        self.config = config if config is not None else Config()
        self.chain = ChainManager(
            config=self.config,
            prompt_template=prompt_template,
            bot_personality=bot_personality,
            memory=memory,
            model=model,
            chain_kwargs=chain_kwargs if chain_kwargs else {"verbose": True},
            memory_kwargs=memory_kwargs if memory_kwargs else self.default_memory_kwargs,
            model_kwargs=model_kwargs if model_kwargs else self.default_model_kwargs
        )
        self.input_queue = Queue(maxsize=6)

    @property
    def default_model_kwargs(self):
        return {
            "max_output_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "streaming": True
        }

    @property
    def default_memory_kwargs(self):
        return {
            "k": 5
        }

    def set_personality(
            self,
            bot_personalities: str = BOT_PERSONALITY,
            user_personality: str = ""
    ):
        self.chain.set_personality_prompt(
            personality_prompt=bot_personalities,
            user_personality=user_personality
        )

    def reset_history(self, conversation_id: str = None):
        self.chain.reset_history(conversation_id=conversation_id)

    def predict(self, sentence: str, conversation_id: str = None):
        message = Message(message=sentence, role=self.config.human_prefix)
        return asyncio.run(self.chain(message, conversation_id=conversation_id))

    def send(self):
        conversation_id = str(random.randint(10000, 99999))
        while True:
            sentence = input("User:")
            output = self.predict(sentence, conversation_id=conversation_id)
            print("BOT:", output[0].message)


if __name__ == "__main__":
    config = Config()
    bot = Bot(config=config)
    bot.send()
