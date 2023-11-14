import asyncio
from queue import Queue
from typing import Optional, Dict, Union, List
from operator import itemgetter

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain.schema.runnable import RunnableLambda, RunnableMap
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

from memory import MemoryTypes, MEM_TO_CLASS
from models import ModelTypes
from common.config import Config, BaseObject
from common.objects import Message, MessageTurn
from common.constants import *
from chain import ChainManager
from prompt import BOT_PERSONALITY
from utils import BotAnonymizer, CacheTypes, ChatbotCache
from tools import CustomSearchTool


class Bot(BaseObject):
    def __init__(
            self,
            config: Config = None,
            prompt_template: str = PERSONAL_CHAT_PROMPT_REACT,
            memory: Optional[MemoryTypes] = None,
            cache: Optional[CacheTypes] = None,
            model: Optional[ModelTypes] = None,
            memory_kwargs: Optional[dict] = None,
            model_kwargs: Optional[dict] = None,
            bot_personality: str = BOT_PERSONALITY,
            tools: List[str] = None
    ):
        super().__init__()
        self.config = config if config is not None else Config()
        self.tools = tools or [CustomSearchTool()]
        partial_variables = {
            "bot_personality": bot_personality or BOT_PERSONALITY,
            "user_personality": "",
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
            "tool_names": ", ".join([tool.name for tool in self.tools])
        }
        self.chain = ChainManager(
            config=self.config,
            prompt_template=prompt_template,
            model=model,
            model_kwargs=model_kwargs if model_kwargs else self.get_model_kwargs(model=model),
            partial_variables=partial_variables
        )
        self.input_queue = Queue(maxsize=6)
        self._memory = self.get_memory(memory_type=memory, parameters=memory_kwargs)
        if cache == CacheTypes.GPTCache and model != ModelTypes.OPENAI:
            cache = None
        self._cache = ChatbotCache.create(cache_type=cache)
        self.anonymizer = BotAnonymizer(config=self.config)
        self.brain = None
        self.start()

    @property
    def memory(self):
        return self._memory

    def start(self):
        history_loader = RunnableMap({
            "input": itemgetter("input"),
            "agent_scratchpad": itemgetter("intermediate_steps") | RunnableLambda(format_log_to_str),
            "history": itemgetter("conversation_id") | RunnableLambda(self.memory.load_history)
        }).with_config(run_name="LoadHistory")

        if self.config.enable_anonymizer:
            anonymizer_runnable = self.anonymizer.get_runnable_anonymizer().with_config(run_name="AnonymizeSentence")
            de_anonymizer = RunnableLambda(self.anonymizer.anonymizer.deanonymize).with_config(
                run_name="DeAnonymizeResponse")

            agent = (history_loader
                     | anonymizer_runnable
                     | self.chain.chain
                     | de_anonymizer
                     | ReActSingleInputOutputParser())

        else:
            agent = history_loader | self.chain.chain | ReActSingleInputOutputParser()
        self.brain = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=2,
            return_intermediate_steps=False
        )

    def get_memory(
            self,
            parameters: dict = None,
            memory_type: Optional[MemoryTypes] = None
    ):
        parameters = parameters or {}
        if memory_type is None:
            memory_type = MemoryTypes.BASE_MEMORY
        if memory_type is not None:
            if memory_type not in MEM_TO_CLASS:
                raise ValueError(
                    f"Got unknown memory type: {memory_type}. "
                    f"Valid types are: {MEM_TO_CLASS.keys()}."
                )
            memory_class = MEM_TO_CLASS[memory_type]
        else:
            raise ValueError(
                "Somehow both `memory` is None, "
                "this should never happen."
            )
        return memory_class(config=self.config, **parameters)

    def get_model_kwargs(self, model: Optional[ModelTypes]):
        if model and model == ModelTypes.OPENAI:
            return self.openai_model_kwargs
        else:
            return self.default_model_kwargs

    @property
    def default_model_kwargs(self):
        return {
            "max_output_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }

    @property
    def openai_model_kwargs(self):
        return {
            "temperature": 0.2,
            "model_name": "gpt-3.5-turbo"
        }

    @property
    def streaming_model_kwargs(self):
        return {
            **self.default_model_kwargs,
            "streaming": True,
            "stop": ["\nObservation"],
            "callbacks": [FinalStreamingStdOutCallbackHandler()]  # Use only with agent
        }

    def reset_history(self, conversation_id: str = None):
        self.memory.clear(conversation_id=conversation_id)

    def add_message_to_memory(
            self,
            human_message: Union[Message, str],
            ai_message: Union[Message, str],
            conversation_id: str
    ):
        if isinstance(human_message, str):
            human_message = Message(message=human_message, role=self.config.human_prefix)
        if isinstance(ai_message, str):
            ai_message = Message(message=ai_message, role=self.config.ai_prefix)

        turn = MessageTurn(
            human_message=human_message,
            ai_message=ai_message,
            conversation_id=conversation_id
        )
        self.memory.add_message(turn)

    async def __call__(self, message: Message, conversation_id: str):
        try:
            try:
                output = self.brain.invoke({"input": message.message, "conversation_id": conversation_id})['output']
            except ValueError as e:
                import regex as re
                response = str(e)
                response = re.findall(r".*?Could not parse LLM output: `(.*)`", response)
                if not response:
                    raise e
                output = response[0]

            output = Message(message=output, role=self.config.ai_prefix)
            return output
        finally:
            # Wait for invoke chain finish before push to Langsmith
            wait_for_all_tracers()

    def predict(self, sentence: str, conversation_id: str = None):
        message = Message(message=sentence, role=self.config.human_prefix)
        output = asyncio.run(self(message, conversation_id=conversation_id))
        self.add_message_to_memory(human_message=message, ai_message=output, conversation_id=conversation_id)
        return output

    def call(self, input: dict):
        return self.predict(**input)
