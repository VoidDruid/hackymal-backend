PYTHONPATH = PYTHONPATH=.

# Executables
PYTHON = $(PYTHONPATH) python3

.PHONY: run-script pretty help

run-script:  ## Запустить скрипты
	${PYTHON} -m scripts

pretty:  ## "Причесать" код - isort, black, пр.
	poetry run isort .
	poetry run black .
	poetry run autoflake --in-place --verbose -r .

help:  ## Показать это сообщение
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
