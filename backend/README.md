# LangChain Chatbot Backend

A modern chatbot backend built with LangChain, FastAPI, and MongoDB.

## Project Structure

The project is organized into the following modules:

```
chatbot_backend/
├── api/                  # API layer with FastAPI
│   ├── __init__.py
│   ├── app.py            # FastAPI application
│   └── models.py         # Pydantic models for API
├── chat/                 # Chat logic
│   ├── __init__.py
│   └── manager.py        # Chat manager for LLM interactions
├── database/             # Database layer
│   ├── __init__.py
│   └── mongodb.py        # MongoDB client
├── __init__.py           # Package initialization
├── config.py             # Application configuration
├── main.py               # Application entry point
└── requirements.txt      # Project dependencies
```

## Features

- Modern architecture with clean separation of concerns
- Type hints throughout the codebase
- Proper error handling and resource management
- FastAPI for high-performance API endpoints
- MongoDB for persistent chat history
- LangChain for LLM interactions

## Requirements

- Python 3.11+ (recommended)
- MongoDB
- OpenAI API key (or compatible service)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r chatbot_backend/requirements.txt
```

3. Create a `.env` file with your configuration:
```
# LLM Configuration
MODEL_TYPE=OPENAI
OPENAI_API_KEY=your_openai_api_key

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/chatbot

# Server Configuration
PORT=8080
LOG_LEVEL=INFO
```

## Running the Application

Run the application using:

```bash
python run_chatbot.py
```

Or directly with uvicorn:

```bash
uvicorn chatbot_backend.main:app --reload --host 0.0.0.0 --port 8080
```

## API Endpoints

- `POST /chat` - Send a chat message
- `POST /clear/{conversation_id}` - Clear conversation history
- `GET /health` - Health check endpoint

## Usage Example

```python
import requests

# Send a chat message
response = requests.post(
    "http://localhost:8080/chat",
    json={
        "input": "Hello, how are you?",
        "conversation_id": "my_conversation"
    }
)
print(response.json())

# Clear conversation history
response = requests.post(
    "http://localhost:8080/clear/my_conversation"
)
print(response.json())
``` 