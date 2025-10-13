VENV_NAME=venv
WORKDIR=src

ifeq ($(OS),Windows_NT)
    ACTIVATE=$(VENV_NAME)\Scripts\activate
else
    ACTIVATE=source $(VENV_NAME)/bin/activate
endif

.PHONY: help
help:
	@echo "make install   => create virtual environment and install dependencies"
	@echo "make up      => start Flask server from src/ and display URL"

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

