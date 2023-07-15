DIRECTORIES = \
	jumia \
	tests

format:
	poetry run black $(DIRECTORIES)
	poetry run isort $(DIRECTORIES)

lint:
	poetry run black --check $(DIRECTORIES)
	poetry run isort --check-only $(DIRECTORIES)
	poetry run mypy $(DIRECTORIES)
	poetry run flake8 $(DIRECTORIES)
	