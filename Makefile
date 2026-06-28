.PHONY: verify test lint format-check format build

verify:
	python scripts/verify_repo.py

test:
	pytest

lint:
	ruff check src tests scripts

format-check:
	ruff format --check src tests scripts

format:
	ruff format src tests scripts

build:
	python -m build
