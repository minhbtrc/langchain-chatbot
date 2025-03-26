@echo off
setlocal enabledelayedexpansion

echo Setting up the Modern LangChain Chatbot environment...
echo.

rem Create backend .env file if it doesn't exist
if not exist backend\.env (
    echo Creating backend .env file...
    copy backend\.env.example backend\.env
    echo Backend .env file created. Please edit it to add your OpenAI API key.
) else (
    echo Backend .env file already exists.
)

rem Create frontend .env file if it doesn't exist
if not exist frontend\.env (
    echo Creating frontend .env file...
    copy frontend\.env.example frontend\.env
    echo Frontend .env file created.
) else (
    echo Frontend .env file already exists.
)

echo.
echo Do you want to run the application using Docker or local development?
echo 1) Docker Compose (recommended)
echo 2) Local development
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting with Docker Compose...
    where docker-compose >nul 2>nul
    if !errorlevel! equ 0 (
        docker-compose up -d
        echo.
        echo Application is now running!
        echo Frontend: http://localhost:3000
        echo Backend API: http://localhost:8080
        echo API documentation: http://localhost:8080/docs
        echo.
        echo To stop the application, run: docker-compose down
    ) else (
        echo Docker Compose is not installed. Please install Docker and Docker Compose first.
        exit /b 1
    )
) else if "%choice%"=="2" (
    echo.
    echo Setting up for local development...
    echo.
    echo Backend setup instructions:
    echo 1. cd backend
    echo 2. python -m venv venv
    echo 3. venv\Scripts\activate
    echo 4. pip install -r requirements.txt
    echo 5. python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
    echo.
    echo Frontend setup instructions:
    echo 1. cd frontend
    echo 2. npm install # or yarn install
    echo 3. npm run dev # or yarn dev
) else (
    echo Invalid choice. Exiting.
    exit /b 1
)

echo.
echo Setup complete!
endlocal 