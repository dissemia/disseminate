#.PHONY: inplace inplace-force clean docs test test-all test-cli build-data develop clean-data help docs profile
.DEFAULT_GOAL := help

PYTHON ?= python

test:  ## Test the package with the current python version
	pip install 'pytest'
	pytest

coverage:  ## Test the coverage of tests
	pip install 'pytest' 'pytest-cov'
	pytest --cov=src --cov-report html

develop: ## Prepare the package for active development
	$(PYTHON) setup.py develop

clean:  ## Safely clean compiled package files, docs and test files
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name __pycache__ -type d -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '*.so' -exec rm -f {} +
	$(MAKE) -C docs clean

docs: develop  ## Build the documentation
	pip install 'Sphinx>=1.5'
	pip install 'sphinxcontrib-napoleon2>=1.0'
	$(MAKE) -C docs cli html latexpdf
	@echo "\033[92m\n\nBuild successful!\033[0m"
	@echo "\033[92mView the html docs at docs/_build/html/index.html.\033[0m"
	@echo "\033[92mView the pdf docs docs/_build/latex/.\n\033[0m"

install:  ## Install disseminate
	python setup.py install

#publish:  # Publish the sdist to pypi
# pip install 'twine>=1.5.0'

help:  ## Print this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'