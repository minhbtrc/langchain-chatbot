# Chatbot with Langchain, LangSmith.

## Requirement

- Python version >= 3.9. Because langchainhub package require it

## Description

- This is a chatbot implementation with Langchain framework.
    - Base LLM: Vertex AI or OpenAI API
    - Memory: MongoDB
    - UI:
        - Gradio
        - Langchain UI: [Chat Langchain](https://github.com/langchain-ai/chat-langchain)
            - Use it to leverages LangChain's streaming support.
    - Prompt versioning and tracing: LangSmith
- User can custom bot's personality by setting bot information like gender, age, ...
- Demo UI:
  ![Demo UI](/assets/demo_ui.png)

### PII for chatbot

- [Data anonymization with Microsoft Presidio](https://python.langchain.com/docs/guides/privacy/presidio_data_anonymization/)
- To protect personally identifiable information (PII), we add `PresidioAnonymizer` to my bot to replace PIIs before
  pass to LLM api. View code in [Anonymizer](//utils/anonymizer.py)
- Steps when using it:
    - User message after anonymize:

      ![anonymized message](/assets/anonymized_output.png)

    - Anonymized prompt before input to LLM:

      ![anonymized_prompt](/assets/anonymized_prompt.png)

    - De-anonymized response to user after LLM call:
  
      ![de-anonymized_output.png](/assets/de-anonymized-output.png)

## How to use

- You need Google Cloud credentials to call Vertex API or OPENAI API KEY to call OpenAI API
- You need create MongoDB database and collection to use as Langchain memory

### Setup tracing with Langsmith

- Langsmith docs: [LangSmith](https://docs.smith.langchain.com/)
- Configure environment to connect to LangSmith.
  ```commandline
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
  export LANGCHAIN_API_KEY="<your-api-key>"
  export LANGCHAIN_PROJECT="chatbot-with-langchain"
  ```

### Running

0. Download the models for the languages to use in anonymizer. PII support.
    1. `python -m spacy download en_core_web_md`
1. RUN backend
    1. Clone repo: `git clone https://github.com/btrcm00/chatbot-with-langchain.git`
    2. Add google-cloud-platform credential file to `secure/vertexai.json`
    3. `cd chatbot`
    4. Install required packages: `pip install -r requirements.txt`
    5. Create MongoDB database and config environment variables to connect Mongo.
    6. Run: `python app.py`
2. RUN frontend
    1. `cd chatbot_frontend`
    2. Install packages: `npm i`
    3. Start frontend: `npm start dev`

