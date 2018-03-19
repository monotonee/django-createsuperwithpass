# A simple Makefile for use in development.

PROJECT_DIR = ./src
PROJECT_MODULES = $(PROJECT_DIR)/management/commands/*.py

.PHONY: build code_tests dependencies lint db_cli tests

build:
	cd src && \
	python setup.py sdist && \
	python setup.py bdist_wheel

dependencies:
	# https://pip.pypa.io/en/stable/reference/pip_install/#install-editable
	pip install --user -e $(PROJECT_DIR)[dev]

db_cli:
	docker-compose exec mariadb mysql

# duplicate-code disabled due to poor implementation in Pylint and unresponsive Pylint config options.
lint:
	pylint --disable=duplicate-code --rcfile=.pylintrc $(PROJECT_MODULES) $(PROJECT_DIR)/tests/*.py

code_tests:
	python $(PROJECT_DIR)/manage.py test $(PROJECT_DIR)/tests --verbosity 2

tests: code_tests lint
