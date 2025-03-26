# Docker Setup for LangChain Chatbot

This document outlines the changes made to containerize the LangChain Chatbot application.

## Files Created or Modified

1. **Docker Configuration**
   - `docker-compose.yml` - Defines services (backend, frontend, MongoDB)
   - `Dockerfile` (backend) - Configures the Python backend container
   - `.dockerignore` - Excludes unnecessary files from Docker builds

2. **Environment Configuration**
   - `chatbot_backend/.env.example` - Template for backend environment variables
   - `chatbot_frontend/.env.example` - Template for frontend environment variables

3. **Setup Helpers**
   - `setup.sh` - Bash script for Unix/macOS users to initialize the environment
   - `setup.bat` - Batch script for Windows users to initialize the environment
   - `Makefile` - Simple commands for common operations

4. **Documentation**
   - Updated root `README.md` - Added Docker Compose instructions
   - This `DOCKER_SETUP.md` file - Details the containerization process

5. **Code Changes**
   - Added `/health` endpoint to the backend API
   - Updated import paths in the chatbot backend

## Service Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │─────▶     Backend     │─────▶     MongoDB     │
│   (Next.js)     │     │    (FastAPI)    │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       Port 3000               Port 8080              Port 27017
```

## Features Added

- **Health Checks** - All services include Docker health checks
- **Dependency Conditions** - Services wait for dependent services to be healthy
- **Volume Persistence** - MongoDB data persists across container restarts
- **Network Isolation** - All services run on a dedicated Docker network
- **Environment Variables** - Configuration via .env files
- **Helper Scripts** - Easy setup for different operating systems

## Running the Application

The simplest way to run the entire application:

```bash
# Clone the repository
git clone <repository-url>
cd <repository-dir>

# Set up environment files and start services
./setup.sh
# Or on Windows:
# setup.bat

# Alternatively, use make:
make setup
make start
```

## Development Workflow

For contributors who prefer to run services individually:

1. **Backend development**: 
   ```bash
   cd chatbot_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m uvicorn chatbot_backend.main:app --reload --host 0.0.0.0 --port 8080
   ```

2. **Frontend development**:
   ```bash
   cd chatbot_frontend
   npm install  # or yarn install
   npm run dev  # or yarn dev
   ```

## Cleanup

To stop all services and clean up:

```bash
make stop    # Just stop services
make clean   # Stop services, remove volumes, and optionally delete .env files
``` 