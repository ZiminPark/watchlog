# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WatchLog Insights is a YouTube watch history analysis tool built as a 1-person MVP project. The application helps users understand their YouTube viewing habits through data visualization and insights.

**Tech Stack:** Python backend (FastAPI planned), React/NextJS frontend (planned)

## Development Commands

### Environment Setup
```bash
# Create conda environment
make env

# Install dependencies and setup pre-commit hooks  
make setup
```

### Code Quality
```bash
# Format code
make format          # Runs black and isort

# Lint code
make lint           # Runs pytest with flake8, pylint, and mypy

# Run unit tests with coverage
make utest          # Runs tests with coverage report

# Open coverage report
make cov            # Opens htmlcov/index.html
```

### Project Structure
- `src/` - Main source code
- `test/utest/` - Unit tests
- `main.py` - Application entry point
- `logging.conf` - Logging configuration

## Architecture Notes

The project follows a standard Python package structure with:
- Makefile-based development workflow using conda
- Comprehensive linting setup (black, isort, flake8, pylint, mypy, ruff)
- 100% test coverage requirement
- Structured logging with file and console handlers
- Pre-commit hooks for code quality

The codebase is currently in early development phase with template files and will be expanded to implement YouTube Data API integration and analytics dashboard features.

## Development Standards

- Python 3.13+ required
- 88 character line length limit
- Type hints required (mypy enabled)
- Test coverage must be 100%
- All code must pass linting checks before commit