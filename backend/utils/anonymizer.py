import langdetect
from typing import Dict, Any, Optional
from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer
from langchain_core.runnables import RunnableLambda

from common.config import BaseObject, Config
from common.constants import ANONYMIZED_FIELDS, NLP_CONFIG


class BotAnonymizer(BaseObject):
    """
    Anonymizer class to handle PII data in chat messages
    Uses Presidio for anonymization and de-anonymization
    """
    def __init__(self, config: Config = None):
        super(BotAnonymizer, self).__init__()
        self.config = config if config is not None else Config()
        self._anonymizer = PresidioReversibleAnonymizer(languages_config=NLP_CONFIG)
        # Custom entities to anonymize can be added here
        self._anonymizer.add_recognizer_for_entities(ANONYMIZED_FIELDS)

    @property
    def anonymizer(self):
        return self._anonymizer

    @property
    def supported_lang(self):
        return ["vi", "en"]

    def _detect_lang(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Detect the language of the input text"""
        try:
            language = langdetect.detect(input_dict["input"])
            if language not in self.supported_lang:
                self.logger.warning(
                    f"Detected language '{language}' is not supported in this Chatbot. "
                    f"Only {self.supported_lang} are supported. Defaulting to English.")
                language = "en"
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            language = "en"  # Default to English if detection fails
            
        return {"language": language, **input_dict}

    def anonymize_func(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize the input text and conversation history"""
        language = input_dict.get("language")
        if not language:
            return {
                "input": input_dict["input"],
                "history": input_dict.get("history", ""),
                "agent_scratchpad": input_dict.get("agent_scratchpad", "")
            }
            
        # Anonymize user input
        anonymized_input = self.anonymizer.anonymize(input_dict["input"], language)
        
        # Anonymize conversation history if available
        history = input_dict.get("history", "")
        anonymized_history = ""
        if history:
            anonymized_history = self.anonymizer.anonymize(history, language)
            
        # Anonymize agent scratchpad if available
        agent_scratchpad = input_dict.get("agent_scratchpad", "")
        anonymized_scratchpad = ""
        if agent_scratchpad:
            anonymized_scratchpad = self.anonymizer.anonymize(agent_scratchpad, language)
            
        return {
            "input": anonymized_input,
            "history": anonymized_history,
            "agent_scratchpad": anonymized_scratchpad
        }

    def get_runnable_anonymizer(self):
        """Create a runnable chain for the anonymizer"""
        return RunnableLambda(self._detect_lang) | RunnableLambda(self.anonymize_func)
