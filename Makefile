.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
PIP_INDEX_URL=https://m.devpi.net/testspace/dev
SOURCE_DIR=src/testspace_colab

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

black: ## Runs black on the source for PEP8 compliance
	black $(SOURCE_DIR) tests

lint: ## check style with flake8
	flake8 --ignore E203,C901,W503 $(SOURCE_DIR)  tests

test: ## run tests quickly with the default Python
	pytest tests -v --junit-xml=pytest-results.xml

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source $(SOURCE_DIR) -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/testspace_colab.rst
	rm -f docs/modules.rst
	python setup.py build_sphinx -a -E
	#sphinx-apidoc -o docs/ $(SOURCE_DIR)
# 	$(MAKE) -C docs clean
# 	$(MAKE) -C docs html
	$(BROWSER) build/sphinx/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	#python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	pip install -U devpi-client
	devpi use $(PIP_INDEX_URL) --always-set-cfg=yes
	pip install -r requirements_dev.txt

pre-commit: clean-test test lint coverage docs test-all ## Full monty before a commit
