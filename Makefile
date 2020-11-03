export PIP_INDEX_URL=https://pypi.pacificclimate.org/simple

# Setup venv
ifeq ($(TMPDIR),)
VENV_PATH := /tmp/crmprtd-venv
else
VENV_PATH := $(TMPDIR)/crmprtd-venv
endif

# Makefile Vars
SHELL:=/bin/bash
PYTHON=${VENV_PATH}/bin/python3
PIP=${VENV_PATH}/bin/pip

.PHONY: all
all: apt install test pre-commit-hook

.PHONY: apt
apt:
	sudo apt-get install \
		postgresql-9.5-postgis-2.5

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_PATH)

.PHONY: install
install: venv
	${PIP} install -U pip
	${PIP} install -r requirements.txt -r test_requirements.txt
	${PIP} install -e .

.PHONY: pre-commit-hook
pre-commit-hook: venv
	${PIP} install pre-commit
	pre-commit install

.PHONY: test
test: venv
	${PYTHON} -m pytest -vv

.PHONY: venv
venv:
	test -d $(VENV_PATH) || python3 -m venv $(VENV_PATH)
