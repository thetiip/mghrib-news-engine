.PHONY: help install setup run api scrape schedule test clean docker-up docker-down export

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Maghrib News Aggregator - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup: ## Run setup script
	@echo "$(BLUE)Running setup...$(NC)"
	chmod +x setup.sh
	./setup.sh

run: ## Run single scraping session
	@echo "$(BLUE)Running scraper...$(NC)"
	python main.py

api: ## Start API server
	@echo "$(BLUE)Starting API server...$(NC)"
	python api.py

scrape: run ## Alias for run

schedule: ## Run scheduler (periodic scraping)
	@echo "$(BLUE)Starting scheduler...$(NC)"
	python scheduler.py

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=. --cov-report=html --cov-report=term

clean: ## Clean generated files
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "$(GREEN)✓ Cleaned$(NC)"

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers started$(NC)"
	@echo "API: http://localhost:8000"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

export: ## Export articles to JSON
	@echo "$(BLUE)Exporting articles...$(NC)"
	python export.py
	@echo "$(GREEN)✓ Articles exported to data/articles.json$(NC)"

stats: ## Show database statistics
	@echo "$(BLUE)Database Statistics:$(NC)"
	@python -c "from database import SessionLocal; from models import Article; db = SessionLocal(); \
		print(f'Total articles: {db.query(Article).count()}'); \
		print('By source:'); \
		for source, count in db.query(Article.source, db.func.count(Article.id)).group_by(Article.source).all(): \
			print(f'  {source}: {count}'); \
		db.close()"

dev: ## Start development mode (API with auto-reload)
	@echo "$(BLUE)Starting development server...$(NC)"
	uvicorn api:app --reload --host 0.0.0.0 --port 8000

all: install run api ## Setup and run everything
