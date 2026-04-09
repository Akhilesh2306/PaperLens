.PHONY: help start stop restart status logs health setup format lint test cleanup

# Default target to show help
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Service Management targets
start: ## Start all services
	docker compose up --build -d

stop: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

status: ## Show service status
	docker compose ps

logs: ## Show service logs
	docker compose logs -f

# Health checks
health: ## Check all services health
	@echo "Checking service health..."
	@curl -s http://localhost:8585/api//health | jq . || echo "API service not responding"
	@curl -s http://localhost:9200/_cluster/health | jq . || echo "OpenSearch service not responding"
	@curl -s http://localhost:11434/api/version | jq . || echo "Ollama service not responding"

# Development targets
setup: ## Install Python dependencies
	uv sync

format: ## Format code
	uv run ruff format

lint: ## Lint and type check
	uv run ruff check --fix
	uv run mypy src/

test: ## Run tests
	uv run pytest

# Cleanup target
cleanup: ## Clean up all services and volumes
	docker compose down -v
	docker system prune -f