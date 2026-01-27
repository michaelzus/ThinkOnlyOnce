# ThinkOnlyOnce - Stock Market Multi-Agent Analysis System
# Makefile for development tasks

# ============================================================================
# USER CONFIGURATION - Set your Python interpreter here
# ============================================================================
PYTHON := /opt/homebrew/bin/python3.13
# Examples:
#   PYTHON := python3.11
#   PYTHON := /usr/local/bin/python3.12
#   PYTHON := /opt/homebrew/bin/python3.12
#   PYTHON := ~/.pyenv/versions/3.12.0/bin/python
# ============================================================================

# Derived variables
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip
LOGS_DIR := logs

# Colors for terminal output
BOLD := \033[1m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m  # No Color

.PHONY: help venv install install-dev clean clean-all lint format type-check test test-cov run check

# Default target
help:
	@echo "$(BOLD)ThinkOnlyOnce - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make venv         Create virtual environment using $(PYTHON)"
	@echo "  make install      Install project dependencies"
	@echo "  make install-dev  Install project with dev dependencies"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make lint         Run flake8 and pydocstyle linters"
	@echo "  make format       Format code with black"
	@echo "  make type-check   Run mypy type checking"
	@echo "  make check        Run all checks (lint + type-check)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test         Run tests with pytest"
	@echo "  make test-cov     Run tests with coverage report"
	@echo ""
	@echo "$(GREEN)Run:$(NC)"
	@echo "  make run          Run the demo application"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean        Remove build artifacts and cache"
	@echo "  make clean-all    Remove everything including venv"
	@echo ""
	@echo "$(YELLOW)Note: Set your Python interpreter by editing PYTHON variable in Makefile$(NC)"
	@echo "$(YELLOW)Current: PYTHON = $(PYTHON)$(NC)"
	@echo "$(YELLOW)Logs are saved to: $(LOGS_DIR)/<command>.log$(NC)"

# Create virtual environment
venv:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Creating virtual environment with $(PYTHON)...$(NC)"
	@$(PYTHON) -m venv $(VENV) 2>&1 | tee $(LOGS_DIR)/venv.log
	@$(VENV_PIP) install --upgrade pip 2>&1 | tee -a $(LOGS_DIR)/venv.log
	@echo "$(GREEN)Virtual environment created at $(VENV)/$(NC)" | tee -a $(LOGS_DIR)/venv.log
	@echo "$(YELLOW)Activate with: source $(VENV_BIN)/activate$(NC)"

# Install dependencies
install: venv
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Installing project dependencies...$(NC)"
	@$(VENV_PIP) install -e . -q 2>&1 | tee $(LOGS_DIR)/install.log

# Install with dev dependencies
install-dev: venv
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Installing project with dev dependencies...$(NC)"
	@$(VENV_PIP) install -e ".[dev]" -q 2>&1 | tee $(LOGS_DIR)/install-dev.log

# Run linters (all configs read from pyproject.toml)
lint:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Running flake8...$(NC)"
	@$(VENV_BIN)/flake8 src/ tests/ 2>&1 | tee $(LOGS_DIR)/lint.log
	@echo "$(GREEN)Running pydocstyle...$(NC)"
	@$(VENV_BIN)/pydocstyle src/ 2>&1 | tee -a $(LOGS_DIR)/lint.log
	@echo "$(GREEN)Running darglint...$(NC)"
	@$(VENV_BIN)/darglint src/ 2>&1 | tee -a $(LOGS_DIR)/lint.log || true
	@echo "$(GREEN)Linting complete!$(NC)" | tee -a $(LOGS_DIR)/lint.log

# Format code
format:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Formatting code with black...$(NC)"
	@$(VENV_BIN)/black src/ tests/ 2>&1 | tee $(LOGS_DIR)/format.log
	@echo "$(GREEN)Formatting complete!$(NC)" | tee -a $(LOGS_DIR)/format.log

# Type checking
type-check:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Running mypy type checking...$(NC)"
	@$(VENV_BIN)/mypy src/ 2>&1 | tee $(LOGS_DIR)/type-check.log
	@echo "$(GREEN)Type checking complete!$(NC)" | tee -a $(LOGS_DIR)/type-check.log

# Run all checks
check: lint type-check
	@echo "$(GREEN)All checks passed!$(NC)"

# Run tests
test:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Running tests...$(NC)"
	@$(VENV_BIN)/pytest tests/ -v 2>&1 | tee $(LOGS_DIR)/test.log

# Run tests with coverage
test-cov:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@$(VENV_BIN)/pytest tests/ -v --cov=think_only_once --cov-report=term-missing --cov-report=html 2>&1 | tee $(LOGS_DIR)/test-cov.log
	@echo "$(GREEN)Coverage report generated at htmlcov/index.html$(NC)" | tee -a $(LOGS_DIR)/test-cov.log

# Run the demo
run:
	@mkdir -p $(LOGS_DIR)
	@echo "$(GREEN)Running ThinkOnlyOnce demo...$(NC)"
	@$(VENV_BIN)/thinkonlyonce 2>&1 | tee $(LOGS_DIR)/run.log

# Clean build artifacts
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	@rm -rf build/
	@rm -rf dist/
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

# Clean everything including venv
clean-all: clean
	@echo "$(RED)Removing virtual environment...$(NC)"
	@rm -rf $(VENV)/
	@rm -rf $(LOGS_DIR)/
	@echo "$(GREEN)Full clean complete!$(NC)"
