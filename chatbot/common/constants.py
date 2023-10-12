TEXT_MODEL_NAME = "text-bison@001"
CHAT_MODEL_NAME = "chat-bison@001"

ANONYMIZED_FIELDS = ['US_BANK_NUMBER', 'US_DRIVER_LICENSE', 'US_ITIN', 'US_PASSPORT', 'US_SSN']
NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_md"},
        # {"lang_code": "vi", "model_name": "vi_spacy_model"},
    ],
}