add-uv:
	@echo "[INFO:] Installing UV ..."	
	# add mac / linux
	curl -LsSf https://astral.sh/uv/0.6.6/install.sh | sh

install:
	@echo "[INFO:] Installing project ..."
	uv sync

format: 
	@echo "[INFO:] Formatting code with ruff ..."
	uv run ruff format . 						           
	uv run ruff check --select I --fix

check-format: # for later automated formats where pre-commit fails if this check fails
	@echo "[INFO:] Checking formatting ..."
	uv run ruff format . --check						
	uv run ruff check

run-api: # artefact from dev times -> remove later
	source .venv/bin/activate && uvicorn app.main:app --reload

dev:
	.venv/bin/uvicorn app.main:app --reload --env-file .env.local

prod:
	sudo .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 80 --env-file .env.prod

setup-prod-linux:
	@echo "[INFO:] Setting up production environment on Linux ..."
	uv sync -e prod
	python -c "import vllm; print('ok')"