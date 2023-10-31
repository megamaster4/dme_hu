.PHONY: help init run test format lint

DEFAULT_GOAL := help

APP_DIR=$(CURDIR)/app
DB_DIR=$(CURDIR)/data/db_data
PAR_DIR=$(CURDIR)/data/parquet
BACKEND_DIR=$(CURDIR)/backend
TEST_DIR=$(CURDIR)/tests


help:
	@echo "make init"
	@echo "       install dependencies and create .env file"
	@echo "make run"
	@echo "       start database container and run the dashboard"
	@echo "make test"
	@echo "       run pytest"
	@echo "make format"
	@echo "       run black"
	@echo "make lint"
	@echo "       run ruff"

init:
	@echo "Installing dependencies..."
	pdm install
	@echo "Creating .env file..."
	@echo DBNAME='postgres' > .env
	@echo DBUSER='postgres' >> .env
	@echo DBPASS='mypassword' >> .env
	@echo DBPORT='5432' >> .env
	@echo "Please, adjust the .env file with your own preferables!"
	@echo "Creating data folder..."
	mkdir "$(DB_DIR)"
	mkdir "$(PAR_DIR)"


process_data:
	@echo "Processing calling CBS API..."
	pdm run python $(CURDIR)/main.py --callapi --num-processes $(num_processes)
	@echo "Processing data..."
	pdm run python $(CURDIR)/main.py --process-parquet

run:
	@echo "Starting database container..."
	docker-compose up -d
	@echo "Running dashboard..."
	pdm run streamlit run $(APP_DIR)/Project_Introduction.py

test:
	pdm run pytest

format:
	pdm run black $(APP_DIR) $(BACKEND_DIR) $(TEST_DIR)

lint:
	pdm run ruff --fix main.py $(APP_DIR) $(BACKEND_DIR) $(TEST_DIR)