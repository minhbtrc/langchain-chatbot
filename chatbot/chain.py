from typing import Optional
from langchain.prompts import PromptTemplate
from langchain import hub
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

from chatbot.common.config import BaseObject, Config
from chatbot.common.objects import Message
from chatbot.utils import ChatbotCache
from chatbot.models import ModelTypes, MODEL_TO_CLASS


class ChainManager(BaseObject):
    def __init__(
            self,
            config: Config = None,
            model: Optional[ModelTypes] = None,
            prompt_template: str = None,
            model_kwargs: Optional[dict] = None,
            partial_variables: dict = None
    ):
        super().__init__()
        self.config = config if config is not None else Config()
        self._base_model = self.get_model(model_type=model, parameters=model_kwargs)
        self._init_prompt_template(template_path=prompt_template, partial_variables=partial_variables)
        self._init_chain()

    def get_model(
            self,
            model_type: Optional[ModelTypes] = None,
            parameters: Optional[dict] = None
    ):
        model_name = parameters.pop("model_name", None)
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
                "Somehow both `model_type` is None, "
                "this should never happen."
            )

        if model_type in [ModelTypes.VERTEX, ModelTypes.OPENAI]:
            if not model_name:
                model_name = self.config.base_model_name
            return model_class(model_name=model_name, **parameters)
        return model_class(**parameters, return_messages=True)

    def _init_chain(self):
        self.chain = (self._prompt | self._base_model).with_config(run_name="GenerateResponse")

    def _init_prompt_template(self, template_path: str = None, partial_variables=None):
        prompt: PromptTemplate = hub.pull(template_path)
        self._prompt = prompt.partial(**partial_variables)

    async def _predict(self, message: Message, conversation_id: str):
        try:
            output = self.chain.invoke({"input": message.message, "conversation_id": conversation_id})
            output = Message(message=output, role=self.config.ai_prefix)
            return output
        finally:
            # Wait for invoke chain finish before push to Langsmith
            wait_for_all_tracers()

    def chain_stream(self, input: str, conversation_id: str):
        return self.chain.astream_log(
            {"input": input, "conversation_id": conversation_id},
            include_names=["StreamResponse"]
        )

    async def __call__(self, message: Message, conversation_id: str):
        output: Message = await self._predict(message=message, conversation_id=conversation_id)
        return output
