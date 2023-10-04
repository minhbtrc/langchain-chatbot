# Personality chatbot with Langchain + Vertex AI.

## Description
- This is a chatbot implementation with Langchain framework.
  - Base LLM: Vertex AI
  - Memory: MongoDB
  - UI: Gradio
  - Cache: PENDING
- User can custom bot's personality by setting bot information like gender, age, ...
- Demo UI:
![Demo UI](/assets/demo_ui.png)

## How to use
- You need Google Cloud credentials to call Vertex API
- You need create mongoDB database and collection to use as Langchain memory

### Development
1. Clone repo: `git clone https://github.com/btrcm00/chatbot-with-langchain.git`
2. Add google-cloud-platform credential file to `secure/vertex.json`
3. Install required packages: `pip install -r requirements.txt`
4. Create MongoDB database and config environment variables to connect Mongo.
5. Run: `python chatbot/bot.py`


### Demo
To run UI demo: `python ./chat_ui/base_ui.py`
