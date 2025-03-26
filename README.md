# Chatbot with Langchain, LangSmith.

## Requirement

- Python version >= 3.9. Because langchainhub package requires it
- Docker and Docker Compose (for containerized deployment)

## Description

- This is a chatbot implementation with Langchain framework.
    - Base LLM: Vertex AI or OpenAI API
    - Memory: MongoDB
    - UI:
        - Next.js frontend
        - FastAPI backend
    - Prompt versioning and tracing: LangSmith
- User can custom bot's personality by setting bot information like gender, age, ...
- Demo UI:
  ![Demo UI](/assets/demo_ui.png)

## System Architecture

The application follows a modern microservices architecture with containerized components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           Docker Compose Environment                        │
│                                                                             │
│  ┌───────────────┐       ┌────────────────┐        ┌───────────────────┐   │
│  │               │       │                │        │                   │   │
│  │    Next.js    │◄─────►│    FastAPI     │◄──────►│     MongoDB       │   │
│  │   Frontend    │       │    Backend     │        │     Database      │   │
│  │  (Port 3000)  │       │   (Port 8080)  │        │    (Port 27017)   │   │
│  │               │       │                │        │                   │   │
│  └───────────────┘       └────────┬───────┘        └───────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│                          ┌─────────────────┐      ┌──────────────────┐     │
│                          │                 │      │                  │     │
│                          │   LangChain     │─────►│  LangSmith       │     │
│                          │   Framework     │      │  (Tracing)       │     │
│                          │                 │      │                  │     │
│                          └────────┬────────┘      └──────────────────┘     │
│                                   │                                         │
│                                   ▼                                         │
│                          ┌─────────────────┐      ┌──────────────────┐     │
│                          │                 │      │                  │     │
│                          │   LLM Provider  │      │  Presidio        │     │
│                          │ (OpenAI/Vertex) │      │  Anonymizer      │     │
│                          │                 │      │  (PII Protection) │     │
│                          └─────────────────┘      └──────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Interaction**:
   - User sends a message through the Next.js frontend
   - Frontend forwards the request to the FastAPI backend

2. **Message Processing**:
   - Backend optionally anonymizes PII data using Presidio Anonymizer
   - LangChain framework builds the conversation chain
   - Request is sent to the selected LLM provider (OpenAI or Vertex AI)
   - Response is traced using LangSmith for monitoring

3. **Conversation Storage**:
   - Conversations are stored in MongoDB for history
   - Each user session has a unique conversation ID

4. **Response Generation**:
   - LLM response is de-anonymized if PII protection is enabled
   - Backend sends the formatted response back to the frontend
   - Frontend renders the response to the user

### Component Structure

#### Backend Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                             FastAPI Backend                            │
│                                                                        │
│  ┌────────────┐     ┌─────────────┐      ┌────────────────────────┐   │
│  │            │     │             │      │                        │   │
│  │   API      │◄───►│   Bot       │◄────►│     Memory System      │   │
│  │  Routes    │     │  Manager    │      │    (MongoDB/Redis)     │   │
│  │            │     │             │      │                        │   │
│  └────────────┘     └──────┬──────┘      └────────────────────────┘   │
│                            │                                           │
│                            ▼                                           │
│                    ┌───────────────┐                                   │
│                    │               │         ┌────────────────────┐    │
│                    │  Chain        │◄───────►│                    │    │
│                    │  Manager      │         │   Anonymizer       │    │
│                    │               │         │                    │    │
│                    └───────┬───────┘         └────────────────────┘    │
│                            │                                            │
│                            ▼                                            │
│                   ┌────────────────┐        ┌─────────────────────┐    │
│                   │                │        │                     │    │
│                   │  LLM Models    │───────►│  External Tools     │    │
│                   │  Integration   │        │  (Search/etc.)      │    │
│                   │                │        │                     │    │
│                   └────────────────┘        └─────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Backend Components:**

- **API Routes**: FastAPI endpoints for chat, health checks, and conversation management
- **Bot Manager**: Core orchestration layer that handles message processing
- **Memory System**: Stores conversation history with MongoDB integration
- **Chain Manager**: Manages LangChain prompt templates and execution
- **Anonymizer**: Optional PII protection using Microsoft Presidio
- **LLM Integration**: Connects to OpenAI or Vertex AI models
- **External Tools**: Integrates with search and other auxiliary services

#### Frontend Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                           Next.js Frontend                             │
│                                                                        │
│  ┌────────────────┐     ┌─────────────────┐    ┌───────────────────┐  │
│  │                │     │                 │    │                   │  │
│  │  Page Layout   │────►│  Chat Window    │───►│  Message Bubbles  │  │
│  │                │     │  Component      │    │                   │  │
│  └────────────────┘     └─────────────────┘    └───────────────────┘  │
│                                │                                       │
│                                ▼                                       │
│                        ┌─────────────────┐    ┌───────────────────┐   │
│                        │                 │    │                   │   │
│                        │  API Services   │───►│  State Management │   │
│                        │                 │    │                   │   │
│                        └─────────────────┘    └───────────────────┘   │
│                                                                        │
│                        ┌─────────────────┐    ┌───────────────────┐   │
│                        │                 │    │                   │   │
│                        │  UI Components  │───►│  Utility Helpers  │   │
│                        │                 │    │                   │   │
│                        └─────────────────┘    └───────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Frontend Components:**

- **Page Layout**: Main application layout and container components
- **Chat Window**: Core component handling conversation display and input
- **Message Bubbles**: Display of user and AI messages with formatting
- **API Services**: REST client for communicating with the backend
- **State Management**: Manages conversation state and UI interactions
- **UI Components**: Reusable elements like buttons, inputs, and modals
- **Utility Helpers**: Support functions for data formatting and processing

### Sequence Flow

Below is a sequence diagram showing how data flows through the system when a user sends a message:

```
User        Frontend        Backend        LangChain       LLM        MongoDB
 |             |              |               |             |            |
 |--message--->|              |               |             |            |
 |             |--POST /chat->|               |             |            |
 |             |              |--load history-|             |            |
 |             |              |               |--query------|----------->|
 |             |              |               |<--history---|------------|
 |             |              |--anonymize--->|             |            |
 |             |              |               |--prompt---->|            |
 |             |              |               |<--response--|            |
 |             |              |<-de-anonymize-|             |            |
 |             |              |--store--------|-------------|----------->|
 |             |<---response--|               |             |            |
 |<--display---|              |               |             |            |
 |             |              |               |             |            |
```

**Key Steps in the Sequence:**

1. **User Interaction:**
   - User types a message in the chat interface
   - Frontend captures the input and sends to backend API

2. **Backend Processing:**
   - Backend loads conversation history from MongoDB
   - If enabled, PII is anonymized using Presidio
   - The conversation chain is constructed with LangChain

3. **LLM Interaction:**
   - The prompt with history and user message is sent to the LLM
   - LLM processes the request and returns a response
   - If PII protection is enabled, the response is de-anonymized

4. **Response Handling:**
   - The conversation is stored in MongoDB
   - Response is returned to the frontend
   - Frontend displays the message to the user

5. **Tracing and Monitoring:**
   - Throughout this process, LangSmith traces the execution
   - Performance metrics and debugging information are collected

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

### Quick Start with Setup Script

The easiest way to run the entire application is using our setup script:

1. **Make the script executable**:
   ```bash
   chmod +x setup.sh
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Follow the prompts**:
   - The script will create necessary .env files if they don't exist
   - Choose between Docker Compose deployment or local development
   - The script will guide you through the rest of the setup process

For Windows users, use `setup.bat` instead.

### Quick Start with Docker Compose Manually

If you prefer to run the commands manually:

1. **Set up environment variables**:
   ```bash
   # For backend
   cp backend/.env.example backend/.env
   # Edit the .env file to add your OpenAI API key
   
   # For frontend
   cp frontend/.env.example frontend/.env
   ```

2. **Start the application**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API documentation: http://localhost:8080/docs

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Setup tracing with Langsmith

- Langsmith docs: [LangSmith](https://docs.smith.langchain.com/)
- Configure environment to connect to LangSmith. Add these to your `backend/.env` file:
  ```
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
  LANGCHAIN_API_KEY="<your-api-key>"
  LANGCHAIN_PROJECT="chatbot-with-langchain"
  ```

### Running Locally (without Docker)

0. Download the models for the languages to use in anonymizer. PII support.
    1. `python -m spacy download en_core_web_md`
1. RUN backend
    1. Clone repo: `git clone https://github.com/btrcm00/chatbot-with-langchain.git`
    2. Add google-cloud-platform credential file to `secure/vertexai.json` or set up OpenAI API key
    3. `cd backend`
    4. Install required packages: `pip install -r requirements.txt`
    5. Create MongoDB database and config environment variables to connect Mongo
    6. Run: `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080`
2. RUN frontend
    1. `cd frontend`
    2. Install packages: `npm install`
    3. Start frontend: `npm run dev`

## Development

For development purposes, you can use the Makefile commands:
```bash
make setup  # Set up environment files
make start  # Start all services
make stop   # Stop all services
make logs   # View logs from all containers
```

