from typing import List, Optional
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import PromptTemplate

from chatbot.common.config import BaseObject, Config
from chatbot.prompt import *
from chatbot.common.objects import Message, MessageTurn
from chatbot.utils import ChatbotCache
from chatbot.memory import MemoryType, MEM_TO_CLASS
from chatbot.models import ModelTypes, MODEL_TO_CLASS, CustomLLM


class ChainManager(BaseObject):
    def __init__(
            self,
            config: Config = None,
            llm=None,
            memory: Optional[MemoryType] = None,
            model: Optional[ModelTypes] = None,
            prompt_template: PromptTemplate = None,
            chain_kwargs: Optional[dict] = None,
            memory_kwargs: Optional[dict] = None,
            model_kwargs: Optional[dict] = None
    ):
        super().__init__()
        self.config = config if config is not None else Config()
        if memory is None:
            memory = MemoryType.BASE_MEMORY
        if memory is not None:
            if memory not in MEM_TO_CLASS:
                raise ValueError(
                    f"Got unknown memory type: {memory}. "
                    f"Valid types are: {MEM_TO_CLASS.keys()}."
                )
            memory_class = MEM_TO_CLASS[memory]
        else:
            raise ValueError(
                "Somehow both `memory` is None, "
                "this should never happen."
            )
        self._memory = memory_class(config=self.config, **memory_kwargs)
        self._base_model = CustomLLM.create_model(config=self.config, parameters=model_kwargs)
        if prompt_template:
            self._prompt = prompt_template
        else:
            partial_variables = {"personality": PERSONALITY_PROMPT}
            self._prompt = PromptTemplate(
                template=CHATBOT_PROMPT,
                input_variables=["input", "history"],
                partial_variables=partial_variables
            )
        self._cache = ChatbotCache.create(config=self.config)
        chain_kwargs = chain_kwargs or {}
        self._init_chain(**chain_kwargs)

    @property
    def memory(self):
        return self._memory.memory

    def reset_history(self, user_id: str = None):
        self._memory.clear(user_id=user_id)

    def _init_chain(self, **kwargs):
        if isinstance(self._memory, MEM_TO_CLASS[MemoryType.CUSTOM_MEMORY]):
            self.chain = LLMChain(
                llm=self._base_model,
                prompt=self._prompt,
                **kwargs
            )
        else:
            self.chain = ConversationChain(
                llm=self._base_model,
                prompt=self._prompt,
                memory=self.memory,
                **kwargs
            )

    def _init_prompt_template(self, partial_variables=None):
        self._prompt = PromptTemplate(
            template=CHATBOT_PROMPT,
            input_variables=["input", "history"],
            partial_variables=partial_variables
        )

    def set_personality_prompt(self, personality_prompt: str):
        partial_variables = {"personality": personality_prompt}
        self._init_prompt_template(partial_variables)
        self._init_chain()

    async def _predict(self, message: Message, history: str):
        output = self.chain({"input": message.message, "history": history})
        output = Message(message=output["text"], role=self.config.ai_prefix)
        return output

    async def __call__(self, message: Message, user_id: str):
        history = self.memory.load_history(user_id=user_id)
        output: Message = await self._predict(message=message, history=history)
        turn = MessageTurn(
            human_message=message,
            ai_message=output,
            user_id=user_id
        )
        self.memory.add_message(turn)
        return output

    # def wrapper(self):
    #     try:
    #         loop = asyncio.get_event_loop()
    #     except:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #
    #     loop.run_until_complete(self.process())
    #
    # async def process_batch(self):
    #     batch = []
    #     start_waiting_time = time.perf_counter()
    #     while True:
    #         if self.input_queue.empty() and (time.perf_counter() - start_waiting_time <= self.config.waiting_time):
    #             await asyncio.sleep(0.5)
    #             continue
    #
    #         if time.perf_counter() - start_waiting_time <= self.config.waiting_time:
    #             message: BaseMessage = self.input_queue.get_nowait()
    #             batch.append(message)
    #             start_waiting_time = time.perf_counter()
    #             continue
    #
    #         start_waiting_time = time.perf_counter()
    #         if batch:
    #             _batch = copy.deepcopy(batch)
    #             batch = []
    #             loop = asyncio.get_event_loop()
    #             await loop.run_in_executor(
    #                 executor=self._predict_executor,
    #                 func=lambda: self._predict(messages=_batch)
    #             )
    #
    # async def process(self):
    #     while True:
    #         if self.input_queue.empty():
    #             await asyncio.sleep(0.5)
    #             continue
    #
    #         message: BaseMessage = self.input_queue.get_nowait()
    #         loop = asyncio.get_event_loop()
    #         await loop.run_in_executor(
    #             executor=self._predict_executor,
    #             func=lambda: self._predict(messages=[message])
    #         )
