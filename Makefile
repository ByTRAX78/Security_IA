## ENV
SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

## Python command detection
PYTHON := python3
ifeq ($(OS),Windows_NT)
    PYTHON := python
endif

## Define la ruta del entorno virtual en el directorio del proyecto
VENV_PATH := $(CURDIR)/.venv

## Output colors
NO_COLOR=\033[0m
C_GREEN=\033[0;32m
C_LIGHT_GREEN=\033[1;32m
C_LIGHT_BLUE=\033[1;34m
C_YELLOW=\033[0;33m
C_RED=\033[0;31m

F_NORMAL=\033[0m
F_BOLD=\033[1m

SIZE_LINE=85
CHAR_LINE==

print-divider:
	@printf "\n$${COLOR:=$(C_LIGHT_BLUE)}%$${SIZE:=$(SIZE_LINE)}s$(NO_COLOR)\n" | tr ' ' $${CHAR:=$(CHAR_LINE)}

print-header-section: print-divider
	@printf "$(C_GREEN) $(F_BOLD)> $${TEXT}$(F_NORMAL)$(NO_COLOR)"
	@make print-divider
	@printf "\n"

print-done:
	@printf "\n$(C_LIGHT_GREEN)[OK] Done...$(NO_COLOR)\n"
	@[ $${JUMP} ] && printf '\n' ||:

help: ## Show help
	@echo -e 'Usage: make [target]\n'
	@echo -e 'Targets:\n'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

create-env-file: ## Create .env file with configuration if it doesn't exist
	@( \
		if [ ! -f .env ]; then \
			make print-header-section TEXT='Create .env file'; \
			echo "export ROBOFLOW_API_KEY=XvZfPfAfQHKopwxiRSBe" > .env; \
			echo "export CAMERA_ID=CAM_001" >> .env; \
			echo "export API_URL=http://localhost:8000" >> .env; \
			make print-done; \
		else \
			echo "$(C_YELLOW)>>> .env file already exists. Skipping creation.$(NO_COLOR)"; \
		fi \
	)

check-python:
	@$(PYTHON) --version > /dev/null 2>&1 || (echo "$(C_RED)Python not found. Please install Python first.$(NO_COLOR)" && exit 1)

clean: ## Clean virtual environment and cache files
	@make print-header-section TEXT='Cleaning environment'
	@if [ -d "$(VENV_PATH)" ]; then \
		echo "$(C_YELLOW)Removing virtual environment...$(NO_COLOR)"; \
		rm -rf $(VENV_PATH); \
	fi
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@make print-done

start-inference-server: ## Start the inference server
	@( \
		make print-header-section TEXT='Starting inference server'; \
		source $(VENV_PATH)/Scripts/activate && \
		inference server start; \
	)

install: check-python ## Install dependencies
	@( \
		make print-header-section TEXT='Install dependencies'; \
		$(PYTHON) -m venv $(VENV_PATH) && \
		source $(VENV_PATH)/Scripts/activate && \
		$(PYTHON) -m pip install --upgrade pip && \
		$(PYTHON) -m pip install -r requirements.txt && \
		echo "$(C_GREEN)Virtual environment created at $(VENV_PATH)$(NO_COLOR)" && \
		make print-done; \
	)

setup: ## Setup project environment and dependencies
	@make create-env-file
	@make install

fresh-start: ## Clean everything and start fresh
	@make print-header-section TEXT='Starting fresh installation'
	@make clean
	@make setup
	@echo "$(C_GREEN)Fresh installation completed successfully!$(NO_COLOR)"
	@echo "$(C_YELLOW)To activate the virtual environment, run:$(NO_COLOR)"
	@echo "source $(VENV_PATH)/Scripts/activate"

lint-fix: ## Fix code formatting
	@make print-header-section TEXT='Fix code formatting'
	@source $(VENV_PATH)/Scripts/activate && black .
	@source $(VENV_PATH)/Scripts/activate && isort .
	@make print-done

.PHONY: help create-env-file clean install setup fresh-start lint-fix check-python start-inference-server
