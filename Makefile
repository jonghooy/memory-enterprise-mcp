# Memory Agent Enterprise - Makefile

.PHONY: help install dev-install test lint format clean docker-up docker-down poc-google poc-pinecone

# Variables
PYTHON := python3.11
POETRY := poetry
DOCKER_COMPOSE := docker-compose

help: ## Show this help message
	@echo "Memory Agent Enterprise - Development Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(POETRY) install --no-dev

dev-install: ## Install all dependencies including dev
	$(POETRY) install

test: ## Run tests with coverage
	$(POETRY) run pytest --cov=src --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	$(POETRY) run pytest tests/unit -v

test-integration: ## Run integration tests only
	$(POETRY) run pytest tests/integration -v

lint: ## Run linting (black, ruff, mypy)
	$(POETRY) run black --check src tests
	$(POETRY) run ruff check src tests
	$(POETRY) run mypy src

format: ## Format code with black
	$(POETRY) run black src tests
	$(POETRY) run ruff check --fix src tests

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# Docker commands
docker-up: ## Start all services with Docker Compose
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop all services
	$(DOCKER_COMPOSE) down

docker-logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

docker-build: ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-clean: ## Clean up Docker resources
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

# Database commands
db-upgrade: ## Apply database migrations
	$(POETRY) run alembic upgrade head

db-downgrade: ## Rollback database migration
	$(POETRY) run alembic downgrade -1

db-migration: ## Create new migration
	@read -p "Enter migration message: " msg; \
	$(POETRY) run alembic revision --autogenerate -m "$$msg"

db-reset: ## Reset database (WARNING: destroys all data)
	$(DOCKER_COMPOSE) down -v postgres
	$(DOCKER_COMPOSE) up -d postgres
	sleep 5
	$(POETRY) run alembic upgrade head

# PoC commands
poc-google: ## Run Google Docs PoC
	$(POETRY) run python src/poc/google_docs_poc.py

poc-pinecone: ## Run Pinecone isolation PoC
	$(POETRY) run python src/poc/pinecone_isolation_poc.py

# Development server
dev: ## Run development server
	$(POETRY) run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

celery-worker: ## Run Celery worker
	$(POETRY) run celery -A src.services.tasks worker --loglevel=info

celery-beat: ## Run Celery beat scheduler
	$(POETRY) run celery -A src.services.tasks beat --loglevel=info

flower: ## Run Flower (Celery monitoring)
	$(POETRY) run celery -A src.services.tasks flower

# Environment setup
env-setup: ## Copy example env file
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

check-env: ## Validate environment variables
	$(POETRY) run python scripts/check_env.py

# Documentation
docs-serve: ## Serve documentation locally
	$(POETRY) run mkdocs serve

docs-build: ## Build documentation
	$(POETRY) run mkdocs build

# Release commands
version-patch: ## Bump patch version (0.0.X)
	$(POETRY) version patch
	git add pyproject.toml
	git commit -m "Bump version to $$($(POETRY) version -s)"

version-minor: ## Bump minor version (0.X.0)
	$(POETRY) version minor
	git add pyproject.toml
	git commit -m "Bump version to $$($(POETRY) version -s)"

version-major: ## Bump major version (X.0.0)
	$(POETRY) version major
	git add pyproject.toml
	git commit -m "Bump version to $$($(POETRY) version -s)"

release: ## Create a new release tag
	git tag -a v$$($(POETRY) version -s) -m "Release version $$($(POETRY) version -s)"
	git push origin v$$($(POETRY) version -s)