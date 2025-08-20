.PHONY: clean tests docs

SRC_PYTHON := gqlactioncable docs/code_examples

check:
	isort $(SRC_PYTHON)
	black $(SRC_PYTHON)
	flake8 $(SRC_PYTHON)
	mypy $(SRC_PYTHON)
	check-manifest

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" | xargs -I {} rm -rf {}
	rm -rf ./htmlcov
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache
	rm -rf ./.tox
	rm -rf ./gqlactioncable.egg-info
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./docs/_build
	rm -f ./.coverage
