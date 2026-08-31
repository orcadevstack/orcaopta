# ============================================
# ORCAOPTA — MAKEFILE
# Cloud-native SRE + Security Automation
# ============================================

PYTHON := python3
PACKAGE := orcaopta
SRC := src/orcaopta

# --------------------------------------------
# ENVIRONMENT
# --------------------------------------------
.PHONY: venv
venv:
    $(PYTHON) -m venv .venv
    . .venv/bin/activate && pip install --upgrade pip setuptools wheel

.PHONY: install
install:
    . .venv/bin/activate && pip install -e .

.PHONY: install-dev
install-dev:
    . .venv/bin/activate && pip install -e .[dev]

# --------------------------------------------
# LINTING & FORMATTING
# --------------------------------------------
.PHONY: lint
lint:
    flake8 $(SRC)

.PHONY: format
format:
    black $(SRC)

.PHONY: typecheck
typecheck:
    mypy $(SRC)

# --------------------------------------------
# TESTING
# --------------------------------------------
.PHONY: test
test:
    pytest -q

.PHONY: coverage
coverage:
    pytest --cov=$(PACKAGE) --cov-report=term-missing

# --------------------------------------------
# BUILD & PACKAGE
# --------------------------------------------
.PHONY: build
build:
    $(PYTHON) -m build

.PHONY: clean
clean:
    rm -rf build dist *.egg-info .pytest_cache .mypy_cache

# --------------------------------------------
# DOCKER
# --------------------------------------------
.PHONY: docker-build
docker-build:
    docker build -t orcaopta .

.PHONY: docker-run
docker-run:
    docker run -p 8000:8000 orcaopta

# --------------------------------------------
# FASTAPI SERVER
# --------------------------------------------
.PHONY: api
api:
    uvicorn orcaopta.api.main:app --host 0.0.0.0 --port 8000 --reload

# --------------------------------------------
# SECURITY PIPELINES
# --------------------------------------------
.PHONY: scan-all
scan-all:
    $(PYTHON) -m orcaopta.cli.vscan_cli scan-all

.PHONY: scan-image
scan-image:
    $(PYTHON) -m orcaopta.cli.vscan_cli image $(IMAGE)

.PHONY: scan-repo
scan-repo:
    $(PYTHON) -m orcaopta.cli.vscan_cli repo .

.PHONY: scan-sbom
scan-sbom:
    $(PYTHON) -m orcaopta.cli.vscan_cli sbom $(IMAGE)

# --------------------------------------------
# REPORT GENERATION
# --------------------------------------------
.PHONY: report-html
report-html:
    $(PYTHON) -m orcaopta.cli.vscan_cli sbom $(IMAGE) --html report.html

# --------------------------------------------
# RELEASE
# --------------------------------------------
.PHONY: release
release:
    $(PYTHON) -m twine upload dist/*
