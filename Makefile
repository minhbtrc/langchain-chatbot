.PHONY: setup start stop logs clean help

help:
	@echo "Modern LangChain Chatbot"
	@echo ""
	@echo "Usage:"
	@echo "  make setup          Create environment files from examples"
	@echo "  make start          Start all services with Docker Compose"
	@echo "  make stop           Stop all services"
	@echo "  make logs           Show logs from all containers"
	@echo "  make clean          Remove containers, volumes, and env files"
	@echo "  make help           Show this help message"

setup:
	@echo "Setting up environment files..."
	@if [ ! -f "backend/.env" ]; then \
		cp backend/.env.example backend/.env; \
		echo "Created backend/.env"; \
	else \
		echo "backend/.env already exists"; \
	fi
	@if [ ! -f "frontend/.env" ]; then \
		cp frontend/.env.example frontend/.env; \
		echo "Created frontend/.env"; \
	else \
		echo "frontend/.env already exists"; \
	fi
	@echo "Setup complete. Don't forget to edit .env files with your API keys!"

start:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Services started."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8080"
	@echo "API docs: http://localhost:8080/docs"

stop:
	@echo "Stopping services..."
	docker-compose down
	@echo "Services stopped."

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	@read -p "Remove .env files? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f backend/.env frontend/.env; \
		echo "Removed .env files"; \
	else \
		echo "Kept .env files"; \
	fi
	@echo "Clean up complete." 