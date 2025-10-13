VENV_NAME=venv
WORKDIR=src
DOCKER_COMPOSE=docker-compose

ifeq ($(OS),Windows_NT)
    ACTIVATE=$(VENV_NAME)\Scripts\activate
else
    ACTIVATE=source $(VENV_NAME)/bin/activate
endif

.PHONY: help
help:
	@echo "make install     => create virtual environment and install dependencies"
	@echo "make up          => start Flask server from src/ and display URL"
	@echo "make docker-up   => start Flask server using Docker Compose"
	@echo "make docker-build=> build Docker image using Docker Compose"

.PHONY: install
install:
	python3 -m venv $(VENV_NAME)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

.PHONY: up
up:
	@echo "Starting Flask server from $(WORKDIR)..."
	@echo "Visit: http://127.0.0.1:5000/"
	$(ACTIVATE) && cd $(WORKDIR) && python3 app.py

.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	$(DOCKER_COMPOSE) -f docker-compose.yml build

.PHONY: docker-up
docker-up:
	@echo "Starting Flask server with Docker Compose..."
	$(DOCKER_COMPOSE) -f docker-compose.yml up

