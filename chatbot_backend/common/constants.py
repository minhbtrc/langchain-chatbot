TEXT_MODEL_NAME = "text-bison@001"
CHAT_MODEL_NAME = "chat-bison@001"

ANONYMIZED_FIELDS = ['US_BANK_NUMBER', 'US_DRIVER_LICENSE', 'US_ITIN', 'US_PASSPORT', 'US_SSN']
NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "vi", "model_name": "vi_core_news_lg"},
        {"lang_code": "en", "model_name": "en_core_web_md"}
    ],
}
PERSONAL_CHAT_PROMPT_REACT = "minhi/personality-chat-react-prompt"
PERSONAL_CHAT_PROMPT = "minhi/personality-chatbot_backend-prompt"
