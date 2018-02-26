# A simple Makefile for use in development.

SRC_DIR = ./src
SRC_MODULES = $(SRC_DIR)/management/commands/*.py

.PHONY: build dependencies lint db_cli tests unit_tests

build:
	cd src && \
	python setup.py sdist && \
	python setup.py bdist_wheel

dependencies:
	#https://pip.pypa.io/en/stable/reference/pip_install/#install-editable
	pip install --user -e $(SRC_DIR)[dev]

db_cli:
	docker-compose exec mariadb mysql

# duplicate-code disabled due to poor implementation in Pylint and unresponsive Pylint config options.
lint:
	pylint --disable=duplicate-code --rcfile=.pylintrc $(SRC_MODULES) $(SRC_DIR)/tests/*.py

unit_tests:
	python $(SRC_DIR)/manage.py test --verbosity 2

tests: unit_tests lint
