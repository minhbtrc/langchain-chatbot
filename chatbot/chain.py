from typing import Optional, Union
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain import hub
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda

from chatbot.common.config import BaseObject, Config
from chatbot.prompt import *
from chatbot.common.objects import Message, MessageTurn
from chatbot.utils import ChatbotCache, BotAnonymizer
from chatbot.memory import MemoryTypes, MEM_TO_CLASS
from chatbot.models import ModelTypes, MODEL_TO_CLASS


class ChainManager(BaseObject):
    def __init__(
            self,
            config: Config = None,
            memory: Optional[MemoryTypes] = None,
            model: Optional[ModelTypes] = None,
            prompt_template: PromptTemplate = None,
            chain_kwargs: Optional[dict] = None,
            memory_kwargs: Optional[dict] = None,
            model_kwargs: Optional[dict] = None,
            bot_personality: Optional[str] = BOT_PERSONALITY
    ):
        super().__init__()
        self.config = config if config is not None else Config()

        self._memory = self.get_memory(memory_type=memory, parameters=memory_kwargs)
        self._base_model = self.get_model(model_type=model, parameters=model_kwargs)
        if prompt_template:
            self._prompt = prompt_template
        else:
            partial_variables = {
                "bot_personality": bot_personality or BOT_PERSONALITY,
                "user_personality": "",
            }
            self._init_prompt_template(partial_variables=partial_variables)
        chain_kwargs = chain_kwargs or {}
        self._cache = ChatbotCache.create(config=self.config)
        self.anonymizer = BotAnonymizer(config=self.config)
        self._init_chain(**chain_kwargs)

    def get_memory(
            self,
            memory_type: Optional[MemoryTypes] = None,
            parameters: Optional[dict] = None
    ):
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

    def get_model(
            self,
            model_type: Optional[ModelTypes] = None,
            model_name: str = None,
            parameters: Optional[dict] = None
    ):
        if model_type is None:
            model_type = ModelTypes.VERTEX

        if model_type is not None:
            if model_type not in MODEL_TO_CLASS:
                raise ValueError(
                    f"Got unknown model type: {model_type}. "
                    f"Valid types are: {MODEL_TO_CLASS.keys()}."
                )
            model_class = MODEL_TO_CLASS[model_type]
        else:
            raise ValueError(
                "Somehow both `memory` is None, "
                "this should never happen."
            )

        if model_type in [ModelTypes.VERTEX, ModelTypes.OPENAI]:
            if not model_name:
                model_name = self.config.base_model_name
            return model_class(model_name=model_name, **parameters)
        return model_class(**parameters, return_messages=True)

    @property
    def memory(self):
        return self._memory

    def reset_history(self, conversation_id: str = None):
        self.memory.clear(conversation_id=conversation_id)

    def _init_chain(self, **kwargs):
        anonymizer_runnable = self.anonymizer.get_runnable_anonymizer()
        self.chain = ({
                          "input": itemgetter("input"),
                          "history": itemgetter("conversation_id") | RunnableLambda(self.memory.load_history)
                      }
                      | anonymizer_runnable
                      | self._prompt
                      | self._base_model
                      | StrOutputParser()
                      | self.anonymizer.anonymizer.deanonymize).with_config(run_name="GenerateResponse")

        if not isinstance(self._memory, MEM_TO_CLASS[MemoryTypes.CUSTOM_MEMORY]):
            self.chain = self.chain | self.memory.memory

    def _init_prompt_template(self, partial_variables=None):
        _prompt: PromptTemplate = hub.pull("minhi/personality-chatbot-prompt")
        self._prompt = _prompt.partial(**partial_variables)

    def set_personality_prompt(self, bot_personality: str = BOT_PERSONALITY, user_personality: str = ""):
        partial_variables = {
            "bot_personality": bot_personality,
            "user_personality": user_personality
        }
        self._init_prompt_template(partial_variables)
        self._init_chain()

    async def _predict(self, message: Message, conversation_id: str):
        try:
            output = self.chain.invoke({"input": message.message, "conversation_id": conversation_id})
            output = Message(message=output, role=self.config.ai_prefix)
            return output
        finally:
            # Wait for invoke chain finish before push to Langsmith
            wait_for_all_tracers()

    def chain_stream(self, input: str, conversation_id: str):
        # history = self.memory.load_history(conversation_id=conversation_id)
        return self.chain.astream_log(
            {"input": input, "conversation_id": conversation_id},
            include_names=["FindDocs"]
        )

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
        # history = self.memory.load_history(conversation_id=conversation_id)
        output: Message = await self._predict(message=message, conversation_id=conversation_id)
        self.add_message_to_memory(human_message=message, ai_message=output, conversation_id=conversation_id)
        return output
