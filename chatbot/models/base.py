from typing import Any, List, Mapping, Optional, Dict

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

from chatbot.common.config import BaseObject, Config
from chatbot.models import ModelTypes, MODEL_TO_CLASS


class CustomLLM(LLM, BaseObject):
    def __init__(self, config: Config = None, model_params: Dict = None):
        super().__init__()
        self.config = config if config is not None else Config()
        self.model = None

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError()

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        raise NotImplementedError()

    @classmethod
    def get_model(
        cls,
        config: Config,
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
                model_name = config.base_model_name
            return model_class(model_name=model_name, **parameters)

        return model_class(config=config, **parameters)
