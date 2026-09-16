.PHONY: help install dev-install run train train-quick format lint lint-fix clean clean-all test check

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation (in docs/):"
	@echo "  README.md       - Project overview and quick start"
	@echo "  CLAUDE.md       - Development guidelines and best practices"
	@echo "  GRAPH_GUIDE.md  - Understanding the formation energy curve"
	@echo "  IMPROVEMENTS.md - Code improvements summary"
	@echo "  PROJECT_STRUCTURE.md - File organization guide"

install:  ## Install project dependencies
	uv sync

dev-install:  ## Install project with dev dependencies
	uv sync --extra dev

run:  ## Run the CASTEP parser
	uv run python src/parse_castep.py

train:  ## Train ML model (saves model and predictions)
	uv run python src/train_ml.py --save-model --save-predictions

train-quick:  ## Train ML model without saving
	uv run python src/train_ml.py

format:  ## Format code with black
	uv run black src/ scripts/

lint:  ## Lint code with ruff
	uv run ruff check src/ scripts/

lint-fix:  ## Fix auto-fixable lint issues
	uv run ruff check --fix src/ scripts/

clean:  ## Remove generated files and caches
	rm -rf __pycache__ .pytest_cache .ruff_cache
	rm -rf data/processed/*.csv
	rm -rf outputs/*.png outputs/*.csv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean  ## Remove generated files, caches, and trained models
	rm -rf models/*.pkl models/*.joblib

test:  ## Run tests (when implemented)
	uv run pytest

check: format lint  ## Format and lint code
