.PHONY: setup lint typecheck test test-cov data-fetch data-update clips demo replay tune dashboard models-discover benchmark-plan benchmark-mock benchmark report paper all-offline clean

PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
PYTEST ?= .venv/bin/pytest
RUFF ?= .venv/bin/ruff
MYPY ?= .venv/bin/mypy

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,tts,dashboard]"

lint:
	$(RUFF) check .

typecheck:
	$(MYPY) src/aircue/trigger

test:
	$(PYTEST) tests/

test-cov:
	$(PYTEST) --cov=aircue --cov-report=term-missing tests/

data-fetch:
	$(PYTHON) -m aircue.cli data fetch

data-update:
	$(PYTHON) -m aircue.cli data update

clips:
	$(PYTHON) -m aircue.cli clips build --backend beep

demo:
	$(PYTHON) -m aircue.cli run --source replay --speed 10.0

replay:
	$(PYTHON) -m aircue.cli replay --location indore

tune:
	$(PYTHON) -m aircue.cli tune --location indore

dashboard:
	streamlit run src/aircue/dashboard/app.py

models-discover:
	$(PYTHON) -m aircue.cli models discover

benchmark-plan:
	$(PYTHON) -m aircue.cli benchmark plan

benchmark-mock:
	$(PYTHON) -m aircue.cli benchmark run --mock --limit 10

benchmark:
	$(PYTHON) -m aircue.cli benchmark run

report:
	$(PYTHON) -m aircue.cli benchmark report

paper:
	$(MAKE) -C paper

all-offline: lint typecheck test clips benchmark-mock report
	@echo "All offline quality checks and mock benchmark pipeline passed successfully."

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .mypy_cache/ .ruff_cache/
