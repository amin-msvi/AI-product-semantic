# Variables
PYTHON_VERSION=3.11.13
VENV_DIR=.venv


.PHONY: build-env run clean ruff

build-env:
	@echo ">>> Installing uv if not present..."
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo ">>> Creating virtual environment with Python $(PYTHON_VERSION)..."
	uv venv --python $(PYTHON_VERSION) $(VENV_DIR)
	@echo ">>> Activating venv and installing requirements..."
	. $(VENV_DIR)/bin/activate && uv pip install -r requirements.txt
	@echo ">>> Environment setup complete!"

run:
	@echo ">>> Running project..."
	. $(VENV_DIR)/bin/activate && python src/main.py

ruff:
	ruff check .
	ruff format .

clean:
	@echo ">>> Removing virtual environment..."
	rm -rf $(VENV_DIR)
