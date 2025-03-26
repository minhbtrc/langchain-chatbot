#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up the Modern LangChain Chatbot environment...${NC}\n"

# Create backend .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}Creating backend .env file...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}Backend .env file created. Please edit it to add your OpenAI API key.${NC}"
else
    echo -e "${YELLOW}Backend .env file already exists.${NC}"
fi

# Create frontend .env file if it doesn't exist
if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}Creating frontend .env file...${NC}"
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}Frontend .env file created.${NC}"
else
    echo -e "${YELLOW}Frontend .env file already exists.${NC}"
fi

# Ask user if they want to use Docker or local development
echo -e "\n${YELLOW}Do you want to run the application using Docker or local development?${NC}"
echo "1) Docker Compose (recommended)"
echo "2) Local development"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting with Docker Compose...${NC}"
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d
            echo -e "\n${GREEN}Application is now running!${NC}"
            echo -e "Frontend: http://localhost:3000"
            echo -e "Backend API: http://localhost:8080"
            echo -e "API documentation: http://localhost:8080/docs"
            echo -e "\nTo stop the application, run: ${YELLOW}docker-compose down${NC}"
        else
            echo -e "${RED}Docker Compose is not installed. Please install Docker and Docker Compose first.${NC}"
            exit 1
        fi
        ;;
    2)
        echo -e "\n${GREEN}Setting up for local development...${NC}"
        echo -e "\n${YELLOW}Backend setup instructions:${NC}"
        echo "1. cd backend"
        echo "2. python -m venv venv"
        echo "3. source venv/bin/activate  # On Windows: venv\Scripts\activate"
        echo "4. pip install -r requirements.txt"
        echo "5. python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080"
        
        echo -e "\n${YELLOW}Frontend setup instructions:${NC}"
        echo "1. cd frontend"
        echo "2. npm install # or yarn install"
        echo "3. npm run dev # or yarn dev"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Setup complete!${NC}" 