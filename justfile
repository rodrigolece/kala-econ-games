check-format:
    uv run ruff format --diff src tests

check-linter:
    uv run ruff check src tests

check-types:
    uv run mypy src tests

check-all: check-format check-linter check-types

fix-format:
    uv run ruff format src tests

fix-linter:
    uv run ruff check --fix src tests

fix-all: fix-format fix-linter

test:
    uv run pytest tests

preview-readme:
    uv run grip -b

default: fix-all check-all test
