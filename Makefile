# Oroitz Build System

.PHONY: help install build test lint format clean dist

help: ## Show this help message
	@echo "Oroitz Build System"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install all dependencies
	poetry install --with dev

install-minimal: ## Install minimal dependencies (no GUI)
	poetry install

build: ## Build PyInstaller executables
	poetry run python scripts/build_installers.py

test: ## Run all tests
	poetry run pytest tests/

test-core: ## Run core tests only
	poetry run pytest tests/core/ tests/cli/

test-ui: ## Run UI tests only
	poetry run pytest tests/ui/

lint: ## Run linting
	poetry run ruff check .

format: ## Format code
	poetry run black .

fix: ## Auto-fix linting issues
	poetry run ruff check . --fix

benchmark: ## Run benchmark
	poetry run python tools/benchmark.py

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.spec
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

dist: build ## Build and create distribution archives
	@echo "Creating distribution archives..."
	@cd dist && for exe in *.exe; do \
		tar -czf "$${exe%.exe}.tar.gz" "$$exe"; \
	done
	@echo "Distribution archives created in dist/"

release: clean install test lint build dist ## Full release build
	@echo "Release build complete!"
	@echo "Executables and archives are in dist/"