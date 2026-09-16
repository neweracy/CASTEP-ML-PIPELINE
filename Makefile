.PHONY: help install dev-install parse train train-quick format lint lint-fix \
        typecheck test cov clean clean-all check hooks

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation (in docs/):"
	@echo "  PROJECT_STRUCTURE.md - Repository layout"
	@echo "  GRAPH_GUIDE.md       - Interpreting the formation-energy curve"
	@echo "  IMPROVEMENTS.md      - Engineering changelog"
	@echo "  CLAUDE.md            - Development guidelines"

install:  ## Install runtime dependencies
	uv sync

dev-install:  ## Install with development dependencies
	uv sync --extra dev

parse:  ## Parse CASTEP files into the ML dataset
	uv run dft-parse

train:  ## Train the GPR model and save model + predictions
	uv run dft-train --save-model --save-predictions

train-quick:  ## Train without saving artifacts
	uv run dft-train

format:  ## Format code with black
	uv run black src/ tests/

lint:  ## Lint code with ruff
	uv run ruff check src/ tests/

lint-fix:  ## Auto-fix lint issues
	uv run ruff check --fix src/ tests/

test:  ## Run the test suite
	uv run pytest

cov:  ## Run tests with coverage report
	uv run pytest --cov --cov-report=term-missing

hooks:  ## Install pre-commit hooks
	uv run pre-commit install

clean:  ## Remove generated data, outputs, and caches
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	rm -rf data/processed/*.csv
	rm -rf outputs/*.png outputs/*.csv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean  ## Also remove trained models
	rm -rf models/*.pkl models/*.joblib

check: format lint test  ## Format, lint, and test
