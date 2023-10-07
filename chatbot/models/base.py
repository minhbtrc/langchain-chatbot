from typing import Any, List, Mapping, Optional, Dict

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

from chatbot.common.config import Config


class CustomLLM(LLM):
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
