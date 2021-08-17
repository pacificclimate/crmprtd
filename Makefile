# Setup venv
ifeq ($(TMPDIR),)
VENV_PATH := /tmp/crmprtd-venv
else
VENV_PATH := $(TMPDIR)/crmprtd-venv
endif

# Makefile Vars
SHELL:=/bin/bash
PYTHON=${VENV_PATH}/bin/python3

.PHONY: all
all: apt install test pre-commit-hook

.PHONY: apt
apt:
	sudo apt-get install \
		postgresql-9.5-postgis-2.5

.PHONY: pipenv
pipenv:
	sudo apt-get install pipenv

.PHONY: install
install: pipenv
	pipenv install --dev
	pipenv install -e .

.PHONY: pre-commit-hook
pre-commit-hook: pipenv
	pipenv install pre-commit
	pipenv run pre-commit install

.PHONY: test
test: pipenv
	pipenv run py.test -vv
