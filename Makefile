.PHONY: help install dev-install run format lint clean test

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation:"
	@echo "  README.md       - Project overview and quick start"
	@echo "  CLAUDE.md       - Development guidelines and best practices"
	@echo "  GRAPH_GUIDE.md  - Understanding the formation energy curve"
	@echo "  IMPROVEMENTS.md - Code improvements summary"

install:  ## Install project dependencies
	uv sync

dev-install:  ## Install project with dev dependencies
	uv sync --extra dev

run:  ## Run the CASTEP parser
	uv run python parse_castep.py

train:  ## Train ML model
	uv run python train_ml.py --save-model --save-predictions

train-quick:  ## Train ML model without saving
	uv run python train_ml.py

format:  ## Format code with black
	uv run black .

lint:  ## Lint code with ruff
	uv run ruff check .

lint-fix:  ## Fix auto-fixable lint issues
	uv run ruff check --fix .

clean:  ## Remove generated files and caches
	rm -rf __pycache__ .pytest_cache .ruff_cache
	rm -f alloy_ml_dataset.csv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:  ## Run tests (when implemented)
	uv run pytest

check: format lint  ## Format and lint code
